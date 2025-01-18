# app.py

import logging
from os import environ
from dotenv import load_dotenv

# Infraestructura
from infrastructure.db.singleton_connection import SingletonConnectionManager
from infrastructure.db.data_loader_postgres import PostgresGeoDataLoader

# Core
from core.services.data_service import DataService
from core.services.data_service_proxy import DataServiceProxy

# Presentation
from presentation.controller import DashAppController
from presentation.layout_builder import LayoutBuilder
from presentation.callback_register import CallbackRegister

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    load_dotenv(".env")
    DB_HOST = environ.get("DB_HOST")
    DB_PORT = environ.get("DB_PORT")
    DB_NAME = environ.get("DB_NAME")
    DB_USER = environ.get("DB_USER")
    DB_PASSWORD = environ.get("DB_PASSWORD")

   # 1. SingletonConnectionManager
    conn_manager = SingletonConnectionManager(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        db_name=DB_NAME
    )

    engine = conn_manager.get_engine()

    # 2. Crear Loader con el engine
    loader = PostgresGeoDataLoader(engine)

    # 3. Instanciar DataService "real"
    data_service_real = DataService(loader)

    # 4. Envolver con Proxy para caching
    data_service_proxy = DataServiceProxy(data_service_real)

    # 5. Construir layout y callbacks
    layout_builder = LayoutBuilder()
    callbacks = CallbackRegister(data_service_proxy, layout_builder)

    # 6. Controlador principal de la app Dash
    dash_controller = DashAppController(data_service_proxy,
                                        layout_builder,
                                        callbacks)

    # 7. Iniciar servidor
    dash_controller.run(debug=True)

if __name__ == "__main__":
    main()
