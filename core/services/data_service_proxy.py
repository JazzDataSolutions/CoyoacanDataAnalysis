# core/services/data_service_proxy.py

import logging
from typing import Dict, Tuple
from geopandas import GeoDataFrame

from core.services.data_service import DataService
from domain.models import DashboardFilters

logger = logging.getLogger(__name__)

class DataServiceProxy:
    """
    Proxy que cachea las llamadas a get_filtered_data 
    para optimizar consultas repetitivas.
    """

    def __init__(self, real_service: DataService) -> None:
        self._real_service = real_service
        self._cache: Dict[Tuple, GeoDataFrame] = {}

    def get_filtered_data(self, dataset_key: str, filters: DashboardFilters) -> GeoDataFrame:
        # Definimos una llave (hash) para el cache
        cache_key = (
            dataset_key,
            filters.type_data,
            filters.anio,
            filters.granularidad,
            filters.metrica,
        )

        if cache_key in self._cache:
            logger.debug(f"[Cache Hit] {cache_key}")
            return self._cache[cache_key]

        logger.debug(f"[Cache Miss] {cache_key}")
        gdf_result = self._real_service.get_filtered_data(dataset_key, filters)
        self._cache[cache_key] = gdf_result
        return gdf_result

    def clear_cache(self):
        logger.debug("Limpiando caché del DataServiceProxy.")
        self._cache.clear()

    def get_anios_disponibles(self, dataset_key: str) -> list[int]:
        """
        Cacheamos la lista de años por dataset_key 
        (sin necesidad de filters).
        """
        cache_key = ("_anios", dataset_key)
        if cache_key in self._cache:
            return self._cache[cache_key]

        anios = self._real_service.get_anios_disponibles(dataset_key)
        self._cache[cache_key] = anios
        return anios

    def get_metrica_options(self, dataset_key: str, anio: int = None) -> list[str]:
        """
        Cacheamos la lista de métricas por (dataset_key, anio).
        """
        cache_key = ("_metrica_options", dataset_key, anio)
        if cache_key in self._cache:
            return self._cache[cache_key]

        metricas = self._real_service.get_metrica_options(dataset_key, anio)
        self._cache[cache_key] = metricas
        return metricas
