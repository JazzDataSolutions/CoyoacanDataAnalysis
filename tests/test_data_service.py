# tests/test_data_service.py

import unittest
from unittest.mock import MagicMock
from geopandas import GeoDataFrame
from core.services.data_service import DataService
from domain.models import DashboardFilters

class TestDataService(unittest.TestCase):
    def setUp(self):
        # Mock del loader
        self.mock_loader = MagicMock()
        self.service = DataService(self.mock_loader)

    def test_get_filtered_data_vacio(self):
        # Simular que load_dataset retorna un gdf vacío
        self.mock_loader.load_dataset.return_value = GeoDataFrame()

        filters = DashboardFilters(type_data="demograficos", anio=2020)
        gdf = self.service.get_filtered_data("demograficos", filters)
        self.assertTrue(gdf.empty)

    # Agregar más tests...
