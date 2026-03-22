from __future__ import annotations

from typing import Dict

from models.project import ComponenteEnvelopeInput, ProjectInput, ProjectResult
from services.data_service import DataRepository

RHO_AR_KG_M3 = 1.2
CP_AR_KJ_KG_K = 1.006
HFG_AGUA_KJ_KG = 2501.0
W_TO_BTUH = 3.412
W_POR_TR = 3516.85
R_SUPERFICIAIS = {
    "parede": (0.13, 0.04),
    "cobertura": (0.10, 0.04),
    "piso": (0.17, 0.04),
}


class CalculationService:
    def __init__(self, repository: DataRepository) -> None:
        self.repository = repository

    def calcular_u_componente(self, categoria: str, componente: ComponenteEnvelopeInput) -> float:
        if componente.modo == "simples":
            if not componente.elemento_nome:
                raise ValueError(f"Selecione um elemento completo para {categoria}.")
            return self.repository.elementos[componente.elemento_nome].u_w_m2k

        if not componente.camadas:
            raise ValueError(f"Cadastre ao menos uma camada para {categoria} no modo avançado.")

        rsi, rse = R_SUPERFICIAIS[categoria]
        r_total = rsi + rse
        for camada in componente.camadas:
            material = self.repository.materiais[camada.material_nome]
            r_total += material.resistencia(camada.espessura_m)
        return 1.0 / r_total

    def calcular(self, dados: ProjectInput) -> ProjectResult:
        u_parede = self.calcular_u_componente("parede", dados.parede)
        u_cobertura = self.calcular_u_componente("cobertura", dados.cobertura)
        u_piso = self.calcular_u_componente("piso", dados.piso)
        vidro = self.repository.vidros[dados.vidro.vidro_nome]
        u_vidro = vidro.u_w_m2k

        q_parede = u_parede * dados.parede.area_m2 * dados.delta_t_c
        q_cobertura = u_cobertura * dados.cobertura.area_m2 * dados.delta_t_c
        q_piso = u_piso * dados.piso.area_m2 * dados.delta_t_c
        q_vidro_trans = u_vidro * dados.vidro.area_m2 * dados.delta_t_c
        q_vidro_solar = dados.vidro.area_m2 * vidro.shgc * max(dados.vidro.sc, 0.0) * dados.vidro.radiacao_w_m2
        q_pessoas_sens = dados.pessoas * dados.calor_sensivel_pessoa_w
        q_pessoas_lat = dados.pessoas * dados.calor_latente_pessoa_w
        q_iluminacao = dados.iluminacao_w
        q_equipamentos = dados.equipamentos_w

        vazao_m3s = dados.ventilacao_m3h / 3600.0
        q_vent_sens = RHO_AR_KG_M3 * CP_AR_KJ_KG_K * 1000.0 * vazao_m3s * dados.delta_t_c
        delta_w = max(0.0, (dados.umidade_externa_gkg - dados.umidade_interna_gkg) / 1000.0)
        q_vent_lat = RHO_AR_KG_M3 * HFG_AGUA_KJ_KG * 1000.0 * vazao_m3s * delta_w

        cargas = {
            "Transmissão paredes": q_parede,
            "Transmissão cobertura": q_cobertura,
            "Transmissão piso": q_piso,
            "Vidros por transmissão": q_vidro_trans,
            "Vidros por carga solar": q_vidro_solar,
            "Pessoas sensível": q_pessoas_sens,
            "Pessoas latente": q_pessoas_lat,
            "Iluminação": q_iluminacao,
            "Equipamentos": q_equipamentos,
            "Ventilação sensível": q_vent_sens,
            "Ventilação latente": q_vent_lat,
        }

        sensivel = q_parede + q_cobertura + q_piso + q_vidro_trans + q_vidro_solar + q_pessoas_sens + q_iluminacao + q_equipamentos + q_vent_sens
        latente = q_pessoas_lat + q_vent_lat
        total = sensivel + latente
        percentuais = {k: (v / total * 100.0 if total > 0 else 0.0) for k, v in cargas.items()}

        return ProjectResult(
            u_parede=u_parede,
            u_cobertura=u_cobertura,
            u_piso=u_piso,
            u_vidro=u_vidro,
            cargas_w=cargas,
            sensivel_w=sensivel,
            latente_w=latente,
            total_w=total,
            total_btuh=total * W_TO_BTUH,
            total_tr=total / W_POR_TR,
            percentual_sensivel=(sensivel / total * 100.0 if total > 0 else 0.0),
            percentual_latente=(latente / total * 100.0 if total > 0 else 0.0),
            percentuais_parcela=percentuais,
        )
