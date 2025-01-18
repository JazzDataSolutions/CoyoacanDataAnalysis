# domain/table_controller.py

from dataclasses import dataclass, field
from typing import Optional, List
from pandas import DataFrame

@dataclass
class TableController:
    poligonos: object = field(init = False)
    demograficos: object = field(init = False)
    edafologicos: object = field(init = False)
    electorales: object = field(init = False)
    servicios: object = field(init = False)
    ambientales: object = field(init = False)

    def __post_init__(self):
        self.poligonos_manzana = {
            "table_name": "poligonos_manzanas_agebs_colonias",
            "geom_column": "GEOM_MANZANA"
        }

        self.poligonos_ageb = {
            "table_name": "poligonos_manzanas_agebs_colonias",
            "geom_column": "GEOM_AGEB"
        }

        self.poligonos_colonia = {
            "table_name": "poligonos_manzanas_agebs_colonias",
            "geom_column": "GEOM_COLONIA"
        }

        self.demograficos = {
            "table_name": "datos_demograficos_particionada",
            "geom_column": "geometry"
        }

        self.edafologicos = {
            "table_name": "datos_edafologicos_particionada",
            "geom_column": "GEOM_MANZANA"
        }
        
        self.economicos = {
            "table_name": "datos_economicos_particionada",
            "geom_column": "geom_manzana"
        }


@dataclass
class TableInfo:
    demografia: str = field(init = False)
    
    def __post_init__(self):
        self.demografia = self.create_demografia()
    
    def create_demografia(self):
        data = {
            "Métrica": [
                "pob", "p_3ymas", "p_12ymas", "p_nacoe", "p_vivoe", "p_hli",
                "p_hli_nhe", "p_hli_he", "p_afromex", "t_nacoe", "t_vivoe",
                "t_hli", "t_hli_nhe", "t_hli_he", "t_afromex", "p_p12ym_sl",
                "p_p12ym_c", "p_p12ym_sp", "p_catlc", "p_criev", "p_trsrl",
                "p_sinrl"
            ],
            "Descripción": [
                "Población", "Población 3 años y más", "Población 12 años y más",
                "Población nacida en otra entidad", "Población que vivía en otra entidad",
                "Población que habla lengua indígena",
                "Población que habla lengua indígena y no habla español",
                "Población que habla lengua indígena y habla español",
                "Población afromexicana",
                "Porcentaje de población nacida en otra entidad",
                "Porcentaje de población que vivía en otra entidad",
                "Porcentaje de población que habla lengua indígena",
                "Porcentaje de población que habla lengua indígena y no habla español",
                "Porcentaje de población que habla lengua indígena y habla español",
                "Porcentaje de población afromexicana",
                "Población de 12 años y más soltera o nunca unida",
                "Población de 12 años y más casada o unida",
                "Población de 12 años y más separada, divorciada o viuda",
                "Población con religión católica",
                "Población con grupo religioso protestante/cristiano evangélico",
                "Población con otras religiones diferentes a las anteriores",
                "Población sin religión o sin adscripción religiosa"
            ]
        }
        return DataFrame(data)