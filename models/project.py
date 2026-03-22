from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CidadeClimatica:
    cidade: str
    estado: str
    tbs_verao_c: float
    ur_verao_pct: float
    umidade_absoluta_gkg: float
    radiacao_solar_vidro_w_m2: float

    @property
    def label(self) -> str:
        return f"{self.cidade} - {self.estado}"


@dataclass
class CamadaMaterial:
    material_nome: str
    espessura_m: float


@dataclass
class ComponenteEnvelopeInput:
    area_m2: float
    modo: str
    elemento_nome: str = ""
    camadas: List[CamadaMaterial] = field(default_factory=list)


@dataclass
class VidroInput:
    area_m2: float
    vidro_nome: str
    sc: float
    radiacao_w_m2: float


@dataclass
class ProjectInput:
    nome_projeto: str
    cidade_label: str
    tbs_externa_c: float
    ur_externa_pct: float
    umidade_externa_gkg: float
    nome_ambiente: str
    area_m2: float
    altura_m: float
    delta_t_c: float
    umidade_interna_gkg: float
    pessoas: int
    calor_sensivel_pessoa_w: float
    calor_latente_pessoa_w: float
    iluminacao_w: float
    equipamentos_w: float
    ventilacao_m3h: float
    parede: ComponenteEnvelopeInput
    cobertura: ComponenteEnvelopeInput
    piso: ComponenteEnvelopeInput
    vidro: VidroInput

    @property
    def volume_m3(self) -> float:
        return self.area_m2 * self.altura_m


@dataclass
class ProjectResult:
    u_parede: float
    u_cobertura: float
    u_piso: float
    u_vidro: float
    cargas_w: Dict[str, float]
    sensivel_w: float
    latente_w: float
    total_w: float
    total_btuh: float
    total_tr: float
    percentual_sensivel: float
    percentual_latente: float
    percentuais_parcela: Dict[str, float]
