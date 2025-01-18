# presentation/figures_utils.py

import geopandas as gpd
from geopandas import GeoDataFrame
import plotly.express as px
from typing import Any, Optional
from domain.models import MapVisualizationConfig

class FiguresGenerator:
    """
    Clase con métodos estáticos para crear figuras usando Plotly.
    """
    
    @staticmethod
    def generar_mapa_coropletico(
        data: GeoDataFrame, 
        config: MapVisualizationConfig
    ) -> Optional[Any]:
        """
        Genera un mapa coroplético con Plotly Express, o None si data está vacío.
        """
        if data.empty:
            return None

        # Preparar las columnas para el tooltip
        custom_data_cols = [
            col for col in config.hover_columns
            if col in data.columns and col != config.columna_metrica
        ]

        fig = px.choropleth_mapbox(
            data_frame = data,
            geojson = data.__geo_interface__,
            locations = data.index,
            color = config.columna_metrica,
            mapbox_style = config.mapbox_style,
            zoom = config.zoom,
            center = {"lat": config.latitud_centro, "lon": config.longitud_centro},
            color_continuous_scale=config.esquema_color,
            opacity = 0.7,
            hover_name = (
                config.nombre_hover if config.nombre_hover 
                else config.columna_metrica
            ),
            custom_data = custom_data_cols  
        )

        # Construir un hover_template
        hover_template = f"• <b>{config.columna_metrica}:</b> %{{z}}<br>"
        for i, col in enumerate(custom_data_cols):
            hover_template += f"• <b>{col}:</b> %{{customdata[{i}]}}<br>"
        hover_template += "<extra></extra>"

        fig.update_traces(
            hovertemplate=hover_template,
            marker_line_color='white',
            marker_line_width=0.5
        )

        # Ajustes finales de diseño
        fig.update_layout(
            template='plotly_white',
            title={
                'text': config.titulo,
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            margin={"r": 0, "t": 60, "l": 0, "b": 0},
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title=(
                    config.titulo_colorbar 
                    if config.titulo_colorbar 
                    else config.columna_metrica
                ),
                titleside='right',
                ticks='outside',
                lenmode='fraction',
                len=0.75,
                y=0.5
            )
        )

        return fig
