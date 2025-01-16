# app.py

import logging
from os import environ
from dotenv import load_dotenv
from src.data_access.data_connection import DatabaseCredentials, DatabaseConnectionManager
from src.data_access.data_loader import PostgresGeoDataLoader
from src.domain.domain_models import TableController

from src.services.data_service import DataService
from src.presentation.controller import DashAppController
from src.presentation.callback_register import CallbackRegister
from src.presentation.layout_builder import LayoutBuilder

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    load_dotenv(".env")
    DB_HOST = environ.get("DB_HOST")
    DB_PORT = environ.get("DB_PORT")
    DB_NAME = environ.get("DB_NAME")
    DB_USER = environ.get("DB_USER")
    DB_PASSWORD = environ.get("DB_PASSWORD")

    # 1. Preparar credenciales
    credentials = DatabaseCredentials(
        host = DB_HOST,
        port = DB_PORT,
        database = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD
    )
    
    connection_manager = DatabaseConnectionManager(credentials)

    # 2. Instanciar loader y data service
    loader = PostgresGeoDataLoader(connection_manager)
    data_service = DataService(loader)
    table_controller = TableController()
    
    # 3. Generar el Frontend iniciarl
    layout_builder = LayoutBuilder()

    # 4. Generar la serie de callbacks iniciales
    callbacks = CallbackRegister(table_controller,
                                 data_service, 
                                 layout_builder)

    # 5. Crear la clase controladora de la app Dash
    dash_controller = DashAppController(data_service,
                            layout_builder,
                            callbacks)

    # 6. Iniciar servidor
    dash_controller.run(debug = True)

if __name__ == "__main__":
    main()
