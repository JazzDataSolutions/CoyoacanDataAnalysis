# presentation/dash_app/controller.py

from typing import Optional
import dash
import dash_bootstrap_components as dbc

class DashAppController:
    def __init__(self, data_service, layout_builder, callback_register):
        self.data_service = data_service
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        self.app.layout = layout_builder.create_layout()
        callback_register.register_callbacks(self.app)

    def run(self, debug: bool = True, port: Optional[int] = 8050):
        self.app.run_server(debug=debug, port=port)
