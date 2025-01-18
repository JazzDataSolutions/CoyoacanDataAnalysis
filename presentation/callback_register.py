# presentation/dash_app/callback_register.py

import logging
from dash import Dash, html, dcc, Input, Output
from presentation.figures_utils import FiguresGenerator
from domain.models import DashboardFilters, MapVisualizationConfig, AVAILABLE_COLOR_SCHEMES
from random import choice

logger = logging.getLogger(__name__)

class CallbackRegister:
    def __init__(self, data_service, layout_builder):
        self.data_service = data_service
        self.layout_builder = layout_builder

    def _get_dataset_key(self, pathname: str) -> str:
        if pathname == "/demograficos":
            return "demograficos"
        elif pathname == "/edafologicos":
            return "edafologicos"
        elif pathname == '/economicos':
            return "economicos"
        
        logger.debug(f"[CallbackRegister] Pathname {pathname} no reconocido, usando 'demograficos' por defecto.")

        return "demograficos"  # default

    def register_callbacks(self, app: Dash):
        self._register_page_callback(app)
        self._register_map_callback(app)
        self._register_anio_metrica_callbacks(app)

    def _register_page_callback(self, app: Dash):
        @app.callback(
            Output("page-content", "children"),
            [Input("url", "pathname")]
        )
        def render_page_content(pathname: str):
            if pathname == "/demograficos":
                return self.layout_builder.create_demograficos_page()
            elif pathname == "/edafologicos":
                return self.layout_builder.create_edafologicos_page()
            elif pathname == "/economicos":
                return self.layout_builder.create_economicos_page()
            else:
                return html.Div("Página por defecto o 404")
            
    def _register_anio_metrica_callbacks(self, app: Dash):
        @app.callback(
            Output("anio", "options"),
            [Input("url", "pathname")]
        )
        def update_anios(pathname):
            dataset_key = self._get_dataset_key(pathname)
            anios = self.data_service.get_anios_disponibles(dataset_key)
            print(f"anios: {anios}")
            # Regresamos la lista como [{"label": str(a), "value": a}, ...]
            return [{"label": str(a), "value": a} for a in anios]

        @app.callback(
            Output("metrica", "options"),
            [Input("anio", "value"), Input("url", "pathname")]
        )
        def update_metricas(anio, pathname):
            dataset_key = self._get_dataset_key(pathname)
            # Llamada al DataService (o proxy)
            metricas = self.data_service.get_metrica_options(dataset_key, anio)
            print(f"metricas: {metricas}")
            return [{"label": m, "value": m} for m in metricas]
       
    def _register_map_callback(self, app: Dash):
        @app.callback(
            Output("mapa-plotly", "children"),
            [Input("anio", "value"),
             Input("granularidad", "value"),
             Input("metrica", "value"),
             Input("url", "pathname")]
        )
        def actualizar_mapa(anio, gran, metrica, pathname):
            logger.debug(f"[CallbackRegister] Enter actualizar_mapa: anio={anio}, gran={gran}, metrica={metrica}, pathname={pathname}")

            if not metrica:
                logger.debug("[CallbackRegister] No metrica selected, returning prompt.")
                return html.Div("Seleccione una métrica.")

            dataset_key = self._get_dataset_key(pathname)

            # Creamos los filtros
            filters = DashboardFilters(
                type_data = dataset_key,
                anio = anio,
                granularidad = gran,
                metrica = metrica
            )

            logger.debug(f"[CallbackRegister] Created DashboardFilters: {filters}")

            # Obtenemos el DataFrame filtrado
            gdf_filtrado = self.data_service.get_filtered_data(dataset_key, filters)
            if gdf_filtrado.empty:
                logger.warning("[CallbackRegister] gdf_filtrado is empty. No data found.")
                return html.Div("No se encontraron datos.")
            
            esquema_color = choice(AVAILABLE_COLOR_SCHEMES)

            # Creamos el objeto de configuración de mapa
            map_config = MapVisualizationConfig(
                titulo=f"Distribución de {metrica} (Año {anio})",
                columna_metrica = metrica,
                hover_columns = filters.tooltip_cols,  # usar tooltip_cols
                nombre_hover = None,    # o pones "Columna X"
                esquema_color = esquema_color,
                titulo_colorbar = f"Nivel de {metrica}"
            )
            
            logger.debug("[CallbackRegister] Generating the map .....")
            # Generamos la figura con FiguresGenerator
            fig = FiguresGenerator.generar_mapa_coropletico(
                data=gdf_filtrado,
                config=map_config
            )

            logger.debug("[CallbackRegister] Mapa coroplético generado, returning figure.")
            return dcc.Graph(figure=fig, style={"width": "100%", "height": "800px"})