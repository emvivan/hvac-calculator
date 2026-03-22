from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from models.library import ElementoCompleto, MaterialSimples, Vidro
from models.project import CidadeClimatica


class DataRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.materiais = self._load_materiais()
        self.elementos = self._load_elementos()
        self.vidros = self._load_vidros()
        self.cidades = self._load_cidades()

    def _load_json(self, name: str) -> List[Dict]:
        path = self.data_dir / name
        return json.loads(path.read_text(encoding="utf-8"))

    def _load_materiais(self) -> Dict[str, MaterialSimples]:
        return {item["nome"]: MaterialSimples(**item) for item in self._load_json("materiais_simples.json")}

    def _load_elementos(self) -> Dict[str, ElementoCompleto]:
        return {item["nome"]: ElementoCompleto(**item) for item in self._load_json("elementos_completos.json")}

    def _load_vidros(self) -> Dict[str, Vidro]:
        return {item["nome"]: Vidro(**item) for item in self._load_json("vidros.json")}

    def _load_cidades(self) -> Dict[str, CidadeClimatica]:
        cidades = [CidadeClimatica(**item) for item in self._load_json("cidades.json")]
        return {cidade.label: cidade for cidade in cidades}

    def elementos_por_categoria(self, categoria: str) -> List[ElementoCompleto]:
        return [item for item in self.elementos.values() if item.categoria == categoria]
