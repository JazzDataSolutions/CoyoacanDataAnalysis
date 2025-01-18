# core/interfaces/data_loader_interface.py

from abc import ABC, abstractmethod
from geopandas import GeoDataFrame

class DataLoaderInterface(ABC):
    @abstractmethod
    def load_dataset(self, table_name: str, geom_column: str) -> GeoDataFrame:
        pass
