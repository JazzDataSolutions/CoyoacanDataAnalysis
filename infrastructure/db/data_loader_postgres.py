# infrastructure/db/data_loader_postgres.py

import logging
import geopandas as gpd
from geopandas import GeoDataFrame
from sqlalchemy.engine import Engine

from core.interfaces.data_loader_interface import DataLoaderInterface

logger = logging.getLogger(__name__)

class PostgresGeoDataLoader(DataLoaderInterface):
    """
    Implementación concreta que usa GeoPandas + SQLAlchemy para leer de PostgreSQL.
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def load_dataset(self, table_name: str, geom_column: str) -> GeoDataFrame:
        try:
            query = f"SELECT * FROM {table_name}"
            gdf = gpd.read_postgis(query, con=self.engine, geom_col=geom_column)
            logger.info(f"Cargado dataset '{table_name}' con {len(gdf)} filas.")
            return gdf
        except Exception as ex:
            logger.error(f"Error al cargar dataset '{table_name}': {ex}")
            return gpd.GeoDataFrame()
