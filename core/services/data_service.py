# core/services/data_service.py

import logging
from typing import Optional

import geopandas as gpd
from geopandas import GeoDataFrame
from pandas import merge

from core.interfaces.data_loader_interface import DataLoaderInterface
from domain.models import DashboardFilters
from domain.table_controller import TableController

logger = logging.getLogger(__name__)

class DataService:
    """
    Orquesta la carga de datos (con un DataLoaderInterface)
    y la posterior lógica de merges y filtrado.
    """

    def __init__(self, loader: DataLoaderInterface) -> None:
        self.loader = loader
        self.table_controller = TableController()

    def _obtener_table_info(self, dataset_key: str) -> dict:
        """
        Retorna la configuración de la tabla asociada a 'dataset_key'.
        """
        if dataset_key == "demograficos":
            return self.table_controller.demograficos
        elif dataset_key == "edafologicos":
            return self.table_controller.edafologicos
        elif dataset_key == "economicos":
            return self.table_controller.economicos

        logger.warning(
            f"[DataService] dataset_key '{dataset_key}' no reconocido. "
            "Usando 'demograficos' por defecto."
        )
        return self.table_controller.demograficos

    def get_anios_disponibles(self, dataset_key: str) -> list[int]:
        """
        Devuelve la lista de años disponibles en la tabla
        asociada a 'dataset_key'. Se asume que la columna se llama 'anio'.
        """
        table_info = self._obtener_table_info(dataset_key)
        gdf_data = self.loader.load_dataset(
            table_name=table_info["table_name"],
            geom_column=table_info["geom_column"]
        )

        if "anio" not in gdf_data.columns or gdf_data.empty:
            return []
        return sorted(gdf_data["anio"].unique())

    def get_metrica_options(self, dataset_key: str, anio: Optional[int] = None) -> list[str]:
        """
        Regresa la lista de columnas numéricas que pueden usarse como 'métrica'.
        Si 'anio' está definido, se filtra el DataFrame primero por ese año.
        """
        table_info = self._obtener_table_info(dataset_key)
        gdf_data = self.loader.load_dataset(
            table_name=table_info["table_name"],
            geom_column=table_info["geom_column"]
        )

        # Filtra por año si se especifica y la columna existe
        if anio is not None and "anio" in gdf_data.columns:
            gdf_data = gdf_data[gdf_data["anio"] == anio]

        # Excluir 'geometry' y columnas que no sean numéricas
        numeric_cols = [
            col for col in gdf_data.columns
            if col not in ("geometry", "anio") and gdf_data[col].dtype.kind in ("i", "f")
        ]
        return numeric_cols

    def _obtener_poligono(self, granularidad: str) -> GeoDataFrame:
        """
        Carga y devuelve el GeoDataFrame de polígonos
        según la granularidad especificada.
        """
        if granularidad == "manzana":
            return self.loader.load_dataset(
                self.table_controller.poligonos_manzana["table_name"],
                self.table_controller.poligonos_manzana["geom_column"]
            )
        elif granularidad == "ageb":
            return self.loader.load_dataset(
                self.table_controller.poligonos_ageb["table_name"],
                self.table_controller.poligonos_ageb["geom_column"]
            )
        elif granularidad == "colonia":
            return self.loader.load_dataset(
                self.table_controller.poligonos_colonia["table_name"],
                self.table_controller.poligonos_colonia["geom_column"]
            )

        logger.warning(
            f"[DataService] Granularidad '{granularidad}' no reconocida. "
            "Usando 'manzana' por defecto."
        )
        return self.loader.load_dataset(
            self.table_controller.poligonos_manzana["table_name"],
            self.table_controller.poligonos_manzana["geom_column"]
        )

    def get_filtered_data(self, dataset_key: str, filters: DashboardFilters) -> GeoDataFrame:
        """
        1) Determina la tabla/geom según dataset_key.
        2) Carga el dataset principal.
        3) Filtra por año (si corresponde).
        4) Carga el polígono según granularidad.
        5) Hace el merge apropiado.
        6) Aplica la lógica de post-filtrado/agrupación.
        7) Retorna el GeoDataFrame final.
        """
        table_info = self._obtener_table_info(dataset_key)
        logger.debug(f"[DataService] table_info={table_info}")

        # Cargar dataset principal
        gdf_data = self.loader.load_dataset(
            table_name=table_info["table_name"],
            geom_column=table_info["geom_column"]
        )
        logger.debug(
            f"[DataService] DF Data ({dataset_key}) loaded: "
            f"{len(gdf_data)} rows, columns={list(gdf_data.columns)}"
        )

        # Filtrar por año
        if filters.anio and "anio" in gdf_data.columns:
            logger.debug(f"[DataService] Filtering by anio={filters.anio}")
            gdf_data = gdf_data[gdf_data["anio"] == filters.anio].copy()
            logger.debug(f"[DataService] After filtering, rows={len(gdf_data)}")

        # Cargar polígono
        gdf_poligono = self._obtener_poligono(filters.granularidad)
        logger.debug(
            f"[DataService] DF Polígono {filters.granularidad} loaded: "
            f"{len(gdf_poligono)} rows, columns={list(gdf_poligono.columns)}"
        )

        # Hacer el merge
        gdf_merged = self._hacer_merge(gdf_poligono, gdf_data, dataset_key, filters)
        logger.debug(
            f"[DataService] Merged DF has {len(gdf_merged)} rows. "
            f"Columns={list(gdf_merged.columns)}"
        )

        # Aplicar lógica de post-merge (agrupaciones, métricas, tooltips, etc.)
        gdf_final = self._apply_granular_aggregation(dataset_key, gdf_merged, filters)
        logger.debug(
            f"[DataService] Final DF after aggregation: "
            f"{len(gdf_final)} rows, columns={list(gdf_final.columns)}"
        )
        return gdf_final

    def _hacer_merge(
        self,
        gdf_pol: GeoDataFrame,
        gdf_data: GeoDataFrame,
        dataset_key: str,
        filters: DashboardFilters
    ) -> GeoDataFrame:
        """
        Ajusta los merges (left_on/right_on) según granularidad y dataset.
        """
        if filters.granularidad == "manzana":
            if dataset_key == "demograficos":
                logger.debug("[DataService] Merging manzana + demograficos via ID_AGEB <-> ageb")
                return merge(
                    gdf_pol,
                    gdf_data,
                    left_on="ID_AGEB",
                    right_on="ageb",
                    how="left"
                )
            elif dataset_key == "edafologicos":
                logger.debug("[DataService] Merging manzana + edafologicos via ID_MANZANA+GEOM_MANZANA")
                return merge(
                    gdf_pol,
                    gdf_data,
                    left_on=["ID_MANZANA", "GEOM_MANZANA"],
                    right_on=["ID_MANZANA", "GEOM_MANZANA"],
                    how="left"
                )
            
            elif dataset_key == "economicos":
                logger.debug("[DataService] Merging manzana + economicos via ID_MANZANA+GEOM_MANZANA")
                return gdf_data
            logger.warning(f"[DataService] Merge manzana+{dataset_key} not defined.")
            return gdf_pol

        elif filters.granularidad == "colonia":
            if dataset_key == "demograficos":
                logger.debug("[DataService] Merging colonia + demograficos via ID_AGEB <-> ageb")
                return merge(
                    gdf_pol,
                    gdf_data,
                    left_on="ID_AGEB",
                    right_on="ageb",
                    how="left"
                )
            elif dataset_key == "edafologicos":
                logger.debug("[DataService] Merging colonia + edafologicos via GEOM_COLONIA")
                gdf_pol = gdf_pol[["ID_COLONIA", "GEOM_COLONIA", "NOMBRE_COLONIA"]].drop_duplicates()
                merged = gpd.sjoin(gdf_pol, gdf_data, how="left", predicate="contains")
                return merged[
                    [
                        "ID_COLONIA",
                        "NOMBRE_COLONIA",
                        "GEOM_COLONIA",
                        "USO_SUELO",
                        "SUPERFICIE",
                        "DNSDD_D",
                        "NIVELES",
                        "ALTURA",
                    ]
                ].drop_duplicates()
            logger.warning(f"[DataService] Merge colonia+{dataset_key} not defined.")
            return gdf_pol

        elif filters.granularidad == "ageb":
            if dataset_key == "demograficos":
                logger.debug("[DataService] Merging ageb + demograficos via ID_AGEB <-> ageb")
                return merge(
                    gdf_pol,
                    gdf_data,
                    left_on="ID_AGEB",
                    right_on="ageb",
                    how="left"
                )
            elif dataset_key == "edafologicos":
                logger.debug("[DataService] Merging ageb + edafologicos via sjoin (contains)")
                gdf_pol = gdf_pol[["GID_AGEB", "ID_AGEB", "GEOM_AGEB", "NOMBRE_COLONIA"]].drop_duplicates()
                merged = gpd.sjoin(gdf_pol, gdf_data, how="left", predicate="contains")
                return merged[
                    [
                        "GID_AGEB",
                        "ID_AGEB",
                        "NOMBRE_COLONIA",
                        "GEOM_AGEB",
                        "USO_SUELO",
                        "SUPERFICIE",
                        "DNSDD_D",
                        "NIVELES",
                        "ALTURA",
                    ]
                ].drop_duplicates()
            logger.warning(f"[DataService] Merge ageb+{dataset_key} not defined.")
            return gdf_pol

        logger.warning(f"[DataService] Granularidad '{filters.granularidad}' no reconocida.")
        return gdf_pol

    def _apply_granular_aggregation(
        self,
        dataset_key: str,
        gdf: GeoDataFrame,
        filters: DashboardFilters
    ) -> GeoDataFrame:
        """
        Aplica la lógica de agrupación y selección de columnas
        según la granularidad y el tipo de dataset.
        """
        if gdf is None or gdf.empty:
            logger.warning("[DataService] GDF is empty before applying aggregation.")
            return gdf

        logger.debug(
            f"[DataService] _apply_granular_aggregation - Start. "
            f"granularidad={filters.granularidad}, dataset_key={dataset_key}, "
            f"metrica={filters.metrica}"
        )

        # Columnas fijas (métrica + tooltips)
        metricas = [filters.metrica] if filters.metrica else []
        columnas_fijas = metricas + filters.tooltip_cols

        if filters.granularidad == "ageb":
            if filters.type_data == "demograficos":
                agrupa = list(set(columnas_fijas + ["ID_AGEB", "GEOM_AGEB"]))
                gdf = gdf.groupby(agrupa).first().reset_index()
                gdf = gdf[list(set(agrupa))]
                if "GEOM_AGEB" in gdf.columns:
                    gdf = gdf.set_geometry("GEOM_AGEB", crs=gdf.crs)

            elif filters.type_data == "edafologicos":
                gdf = (
                    gdf.groupby(["GID_AGEB", "ID_AGEB", "USO_SUELO", "GEOM_AGEB"], as_index=False)
                    .agg(
                        {
                            "SUPERFICIE": "sum",
                            "NOMBRE_COLONIA": "first",
                            "DNSDD_D": "first",
                            "NIVELES": "mean",
                            "ALTURA": "mean",
                        }
                    )
                    .set_geometry("GEOM_AGEB", crs=gdf.crs)
                )
                gdf = gdf.drop_duplicates(subset=["GID_AGEB", "ID_AGEB", "GEOM_AGEB"])

        elif filters.granularidad == "colonia":
            if filters.type_data == "demograficos":
                agrupa = list(set(columnas_fijas + ["ID_COLONIA", "GEOM_COLONIA"]))
                gdf = gdf.groupby(agrupa).first().reset_index()
                gdf = gdf[list(set(agrupa))]
                if "GEOM_COLONIA" in gdf.columns:
                    gdf = gdf.set_geometry("GEOM_COLONIA", crs=gdf.crs)

            elif filters.type_data == "edafologicos":
                gdf = (
                    gdf.groupby(["ID_COLONIA", "USO_SUELO", "GEOM_COLONIA"], as_index=False)
                    .agg(
                        {
                            "SUPERFICIE": "sum",
                            "NOMBRE_COLONIA": "first",
                            "DNSDD_D": "first",
                            "NIVELES": "mean",
                            "ALTURA": "mean",
                        }
                    )
                    .set_geometry("GEOM_COLONIA", crs=gdf.crs)
                )
                gdf = gdf.drop_duplicates(subset=["ID_COLONIA", "GEOM_COLONIA"])

        else:
            # Se asume granularidad 'manzana' por defecto
            agrupa = list(set(columnas_fijas + ["ID_MANZANA", "GEOM_MANZANA"]))
            subset_cols = [col for col in agrupa if col in gdf.columns]
            gdf = gdf[subset_cols]
            if "GEOM_MANZANA" in gdf.columns:
                gdf = gdf.set_geometry("GEOM_MANZANA", crs=gdf.crs)

        logger.debug(
            f"[DataService] _apply_granular_aggregation - End. "
            f"gdf.shape={gdf.shape}, columns={list(gdf.columns)}"
        )
        return gdf
