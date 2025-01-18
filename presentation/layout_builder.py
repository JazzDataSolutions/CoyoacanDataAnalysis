# presentation/dash_app/layout_builder.py

from dash import html, dcc, dash_table
from domain.table_controller import TableInfo
import dash_bootstrap_components as dbc

class LayoutBuilder:
    table_info = TableInfo()

    def create_layout(self) -> html.Div:
        sidebar_style = {
            "position": "fixed",
            "top": 0,
            "left": 0,
            "bottom": 0,
            "width": "16rem",
            "padding": "2rem 1rem",
            "background-color": "#f8f9fa",
            "overflow-y": "auto",
        }
        content_style = {
            "margin-left": "18rem",
            "margin-right": "2rem",
            "padding": "2rem 1rem",
        }

        sidebar = html.Div([
            html.H2("Coyoacán", className = "display-4"),
            html.Hr(),
            html.P("Análisis de Datos Georeferenciados", className="lead"),
            dbc.Nav(
                [
                    dbc.NavLink("Demográficos", href="/demograficos", active="exact"),
                    dbc.NavLink("Edafológicos", href="/edafologicos", active="exact"),
                    dbc.NavLink("Economicos", href="/economicos", active="exact"),
                    dbc.NavLink("Empleos", href="/empleos", active="exact"),
                    dbc.NavLink("Ambiental", href="/ambiental", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
        ], style=sidebar_style)

        content = html.Div(id="page-content", style=content_style)

        return html.Div([
            dcc.Location(id="url"),
            sidebar,
            content
        ])

    def create_demograficos_page(self):
        """
        Layout para la página de Demográficos.
        """
        df = self.table_info.demografia

        page = dbc.Row([
            # Columna del mapa
            dbc.Col(
                dcc.Loading(
                    id="loading-1",
                    overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                    type="cube",
                    children = html.Div(
                        id="mapa-plotly", 
                        style={"height": "100%"})
                    ),
                    width=9,
                    style={"padding": "0px"}
            ),
            # Columna de la tabla
            dbc.Col(
                 self._create_metric_desc(df),
                width = 3,  # Bootstrap: 3 columnas
                style = {"padding": "10px"}
            ) 
        ], style={"height": "100%"}) 

        return html.Div([
            html.H3("Tablero Demográfico"),
            self._create_filter_row(),
            page
        ])

    def create_edafologicos_page(self):
        """
        Layout para la página de Edafológicos.
        """
        return html.Div([
            html.H3("Tablero Edafológico"),
            self._create_filter_row(),
            dbc.Col(
                dcc.Loading(
                    id="loading-1",
                    overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                    type="cube",
                    children = html.Div(
                        id="mapa-plotly", 
                        style={"height": "100%"})
                    ),
                    width=9,
                    style={"padding": "0px"}
            )
        ])
    def create_economicos_page(self):
        """
        Layout para la página de Edafológicos.
        """
        return html.Div([
            html.H3("Tablero Economicos"),
            self._create_filter_row(),
            dbc.Col(
                dcc.Loading(
                    id="loading-1",
                    overlay_style={"visibility":"visible", "filter": "blur(2px)"},
                    type="cube",
                    children = html.Div(
                        id="mapa-plotly", 
                        style={"height": "100%"})
                    ),
                    width=9,
                    style={"padding": "0px"}
            )
        ])

    def _create_metric_desc(self, df):
        table = dash_table.DataTable(
                    id="data-table",
                    columns=[
                        {"name": col, "id": col, "presentation": "markdown"} for col in df.columns
                    ],
                    data=df.to_dict("records"),
                    style_table={
                        "overflowX": "auto",  # Habilita scroll horizontal
                        "maxHeight": "900px",  # Limita la altura de la tabla
                    },
                    style_cell={
                        "textAlign": "left",
                        "padding": "0px",
                    },
                    style_header={
                        "backgroundColor": "#f8f9fa",
                        "fontWeight": "bold",
                        "textAlign": "center",
                    },
                    style_data_conditional=[
                        # Alterna colores de filas
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#f9f9f9",
                        },
                        {
                            "if": {"row_index": "even"},
                            "backgroundColor": "#ffffff",
                        },
                    ],
                    page_size=15,  # Activa paginación
                    sort_action="native",  # Activa ordenación de columnas
                )
        return table

    def _create_filter_row(self):
        """
        Fila con 3 dropdowns:
          - Año
          - Granularidad
          - Métrica

        Notar que 'anio' y 'metrica' no tienen opciones hardcodeadas,
        se rellenan dinámicamente en los callbacks.
        """
        return html.Div([
            # Dropdown de Año
            html.Div([
                html.Label("Año:"),
                dcc.Dropdown(
                    id="anio",
                    options=[],       # Se cargan dinámicamente
                    value=None        # Sin valor inicial
                )
            ], style={"width": "20%", 
                      "display": "inline-block", 
                      "marginRight": "10px"}),

            # Dropdown de Granularidad
            html.Div([
                html.Label("Granularidad:"),
                dcc.Dropdown(
                    id="granularidad",
                    # Este sí puede tener opciones estáticas (si no cambian):
                    options=[
                        {"label": "Manzana", "value": "manzana"},
                        {"label": "AGEB", "value": "ageb"},
                        {"label": "Colonia", "value": "colonia"}
                    ],
                    value="manzana"   # Valor por defecto
                )
            ], style={"width": "20%", 
                      "display": "inline-block", 
                      "marginRight": "10px"}),

            # Dropdown de Métrica
            html.Div([
                html.Label("Métrica:"),
                dcc.Dropdown(
                    id="metrica",
                    options=[],       # Se cargan dinámicamente
                    value=None
                )
            ], style={"width": "20%", 
                      "display": "inline-block"})
        ], style={"display": "flex", "flexDirection": "row"})
