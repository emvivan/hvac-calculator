from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MaterialSimples:
    nome: str
    condutividade: float
    densidade: float
    calor_especifico: float

    def resistencia(self, espessura_m: float) -> float:
        if self.condutividade <= 0:
            raise ValueError(f"Condutividade inválida para o material {self.nome}.")
        return espessura_m / self.condutividade


@dataclass
class ElementoCompleto:
    categoria: str
    nome: str
    u_w_m2k: float
    descricao: str


@dataclass
class Vidro:
    nome: str
    u_w_m2k: float
    shgc: float
    transmissao_luminosa: float
