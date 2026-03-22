from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from models.project import CamadaMaterial, ComponenteEnvelopeInput, ProjectInput, VidroInput
from report.pdf_service import gerar_relatorio_pdf
from services.calculation_service import CalculationService
from services.data_service import DataRepository

LABEL_STYLE = {"padx": 4, "pady": 3, "sticky": "w"}
ENTRY_STYLE = {"padx": 4, "pady": 3, "sticky": "w"}


class HVACApp:
    def __init__(self, repository: DataRepository, calc_service: CalculationService) -> None:
        self.repository = repository
        self.calc_service = calc_service
        self.root = tk.Tk()
        self.root.title("HVAC - Cálculo de Carga Térmica")
        self.root.geometry("1380x940")
        self.root.minsize(1240, 860)
        self.camadas: Dict[str, List[CamadaMaterial]] = {"parede": [], "cobertura": [], "piso": []}
        self.resultado_atual = None
        self._configure_style()
        self._build_ui()
        self._preencher_cidade_inicial()

    def _configure_style(self) -> None:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1F4E78")
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("SummaryTitle.TLabel", font=("Segoe UI", 11, "bold"), foreground="#1F4E78")
        style.configure("SummaryValue.TLabel", font=("Segoe UI", 11, "bold"))

    def _build_ui(self) -> None:
        root_frame = ttk.Frame(self.root, padding=10)
        root_frame.pack(fill="both", expand=True)
        ttk.Label(root_frame, text="Calculadora de Carga Térmica HVAC", style="Title.TLabel").pack(anchor="w", pady=(0, 10))

        top_frame = ttk.LabelFrame(root_frame, text="Dados gerais do projeto", padding=10, style="Section.TLabelframe")
        top_frame.pack(fill="x", pady=(0, 8))

        self.project_name_var = tk.StringVar(value="Projeto HVAC")
        self.city_var = tk.StringVar()
        self.tbs_var = tk.StringVar()
        self.ur_var = tk.StringVar()
        self.umidade_ext_var = tk.StringVar()
        self.delta_t_var = tk.StringVar(value="8")
        self.umidade_int_var = tk.StringVar(value="9")

        ttk.Label(top_frame, text="Nome do projeto").grid(row=0, column=0, **LABEL_STYLE)
        ttk.Entry(top_frame, textvariable=self.project_name_var, width=28).grid(row=0, column=1, **ENTRY_STYLE)
        ttk.Label(top_frame, text="Cidade").grid(row=0, column=2, **LABEL_STYLE)
        self.city_combo = ttk.Combobox(top_frame, textvariable=self.city_var, width=28, state="readonly")
        self.city_combo["values"] = list(self.repository.cidades.keys())
        self.city_combo.grid(row=0, column=3, **ENTRY_STYLE)
        self.city_combo.bind("<<ComboboxSelected>>", self._city_selected)

        ttk.Label(top_frame, text="TBS externa (°C)").grid(row=1, column=0, **LABEL_STYLE)
        ttk.Entry(top_frame, textvariable=self.tbs_var, width=16).grid(row=1, column=1, **ENTRY_STYLE)
        ttk.Label(top_frame, text="UR externa (%)").grid(row=1, column=2, **LABEL_STYLE)
        ttk.Entry(top_frame, textvariable=self.ur_var, width=16).grid(row=1, column=3, **ENTRY_STYLE)
        ttk.Label(top_frame, text="Umidade externa (g/kg)").grid(row=1, column=4, **LABEL_STYLE)
        ttk.Entry(top_frame, textvariable=self.umidade_ext_var, width=16).grid(row=1, column=5, **ENTRY_STYLE)

        body = ttk.Panedwindow(root_frame, orient="horizontal")
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body)
        right = ttk.Frame(body)
        body.add(left, weight=3)
        body.add(right, weight=2)

        notebook = ttk.Notebook(left)
        notebook.pack(fill="both", expand=True)

        self.tab_ambiente = ttk.Frame(notebook)
        self.tab_envoltoria = ttk.Frame(notebook)
        self.tab_resultados = ttk.Frame(notebook)
        notebook.add(self.tab_ambiente, text="Ambiente e cargas")
        notebook.add(self.tab_envoltoria, text="Envoltória")
        notebook.add(self.tab_resultados, text="Resultados")

        self._build_tab_ambiente()
        self._build_tab_envoltoria()
        self._build_tab_resultados()
        self._build_sidebar(right)

    def _build_tab_ambiente(self) -> None:
        frame = ttk.LabelFrame(self.tab_ambiente, text="Ambiente", padding=10, style="Section.TLabelframe")
        frame.pack(fill="x", padx=8, pady=8)
        self.ambiente_nome_var = tk.StringVar(value="Escritório")
        self.area_var = tk.StringVar(value="50")
        self.altura_var = tk.StringVar(value="2.8")

        ttk.Label(frame, text="Nome do ambiente").grid(row=0, column=0, **LABEL_STYLE)
        ttk.Entry(frame, textvariable=self.ambiente_nome_var, width=26).grid(row=0, column=1, **ENTRY_STYLE)
        ttk.Label(frame, text="Área (m²)").grid(row=0, column=2, **LABEL_STYLE)
        ttk.Entry(frame, textvariable=self.area_var, width=16).grid(row=0, column=3, **ENTRY_STYLE)
        ttk.Label(frame, text="Altura (m)").grid(row=0, column=4, **LABEL_STYLE)
        ttk.Entry(frame, textvariable=self.altura_var, width=16).grid(row=0, column=5, **ENTRY_STYLE)
        ttk.Label(frame, text="ΔT externo/interno (°C)").grid(row=1, column=0, **LABEL_STYLE)
        ttk.Entry(frame, textvariable=self.delta_t_var, width=16).grid(row=1, column=1, **ENTRY_STYLE)
        ttk.Label(frame, text="Umidade interna (g/kg)").grid(row=1, column=2, **LABEL_STYLE)
        ttk.Entry(frame, textvariable=self.umidade_int_var, width=16).grid(row=1, column=3, **ENTRY_STYLE)

        cargas = ttk.LabelFrame(self.tab_ambiente, text="Cargas internas", padding=10, style="Section.TLabelframe")
        cargas.pack(fill="x", padx=8, pady=8)
        self.pessoas_var = tk.StringVar(value="8")
        self.sens_pessoa_var = tk.StringVar(value="75")
        self.lat_pessoa_var = tk.StringVar(value="55")
        self.iluminacao_var = tk.StringVar(value="700")
        self.equipamentos_var = tk.StringVar(value="1400")
        self.ventilacao_var = tk.StringVar(value="270")

        labels = [
            ("Pessoas", self.pessoas_var),
            ("Calor sensível por pessoa (W)", self.sens_pessoa_var),
            ("Calor latente por pessoa (W)", self.lat_pessoa_var),
            ("Iluminação (W)", self.iluminacao_var),
            ("Equipamentos (W)", self.equipamentos_var),
            ("Ventilação (m³/h)", self.ventilacao_var),
        ]
        for idx, (text, variable) in enumerate(labels):
            ttk.Label(cargas, text=text).grid(row=idx // 2, column=(idx % 2) * 2, **LABEL_STYLE)
            ttk.Entry(cargas, textvariable=variable, width=20).grid(row=idx // 2, column=(idx % 2) * 2 + 1, **ENTRY_STYLE)

    def _build_component_simple(self, parent, row, titulo, categoria):
        ttk.Label(parent, text=f"{titulo} - Área (m²)").grid(row=row, column=0, **LABEL_STYLE)
        area_var = tk.StringVar(value="40" if categoria == "parede" else "50")
        ttk.Entry(parent, textvariable=area_var, width=14).grid(row=row, column=1, **ENTRY_STYLE)
        ttk.Label(parent, text=f"{titulo} - Modo").grid(row=row, column=2, **LABEL_STYLE)
        modo_var = tk.StringVar(value="simples")
        modo_combo = ttk.Combobox(parent, textvariable=modo_var, values=["simples", "avançado"], state="readonly", width=14)
        modo_combo.grid(row=row, column=3, **ENTRY_STYLE)
        ttk.Label(parent, text=f"{titulo} - Elemento completo").grid(row=row, column=4, **LABEL_STYLE)
        elemento_var = tk.StringVar()
        elemento_combo = ttk.Combobox(parent, textvariable=elemento_var, width=34, state="readonly")
        elemento_combo["values"] = [item.nome for item in self.repository.elementos_por_categoria(categoria)]
        if elemento_combo["values"]:
            elemento_var.set(elemento_combo["values"][0])
        elemento_combo.grid(row=row, column=5, **ENTRY_STYLE)
        return area_var, modo_var, elemento_var

    def _build_tab_envoltoria(self) -> None:
        simples = ttk.LabelFrame(self.tab_envoltoria, text="Modo simples e avançado da envoltória", padding=10, style="Section.TLabelframe")
        simples.pack(fill="x", padx=8, pady=8)
        self.parede_area_var, self.parede_modo_var, self.parede_elemento_var = self._build_component_simple(simples, 0, "Parede", "parede")
        self.cobertura_area_var, self.cobertura_modo_var, self.cobertura_elemento_var = self._build_component_simple(simples, 1, "Cobertura", "cobertura")
        self.piso_area_var, self.piso_modo_var, self.piso_elemento_var = self._build_component_simple(simples, 2, "Piso", "piso")

        avancado = ttk.LabelFrame(self.tab_envoltoria, text="Montagem de camadas (modo avançado)", padding=10, style="Section.TLabelframe")
        avancado.pack(fill="x", padx=8, pady=8)
        self.comp_target_var = tk.StringVar(value="parede")
        self.material_var = tk.StringVar()
        self.espessura_var = tk.StringVar(value="0.02")

        ttk.Label(avancado, text="Componente").grid(row=0, column=0, **LABEL_STYLE)
        ttk.Combobox(avancado, textvariable=self.comp_target_var, values=["parede", "cobertura", "piso"], state="readonly", width=12).grid(row=0, column=1, **ENTRY_STYLE)
        ttk.Label(avancado, text="Material").grid(row=0, column=2, **LABEL_STYLE)
        mat_combo = ttk.Combobox(avancado, textvariable=self.material_var, values=list(self.repository.materiais.keys()), state="readonly", width=28)
        mat_combo.grid(row=0, column=3, **ENTRY_STYLE)
        if mat_combo["values"]:
            self.material_var.set(mat_combo["values"][0])
        ttk.Label(avancado, text="Espessura (m)").grid(row=0, column=4, **LABEL_STYLE)
        ttk.Entry(avancado, textvariable=self.espessura_var, width=14).grid(row=0, column=5, **ENTRY_STYLE)
        ttk.Button(avancado, text="Adicionar camada", command=self._add_layer).grid(row=0, column=6, padx=6, pady=4)

        self.layer_boxes = {}
        for idx, comp in enumerate(["parede", "cobertura", "piso"]):
            frame = ttk.LabelFrame(avancado, text=comp.capitalize(), padding=6)
            frame.grid(row=1, column=idx, padx=6, pady=6, sticky="nsew")
            box = tk.Listbox(frame, width=34, height=8)
            box.pack()
            self.layer_boxes[comp] = box

        vidro = ttk.LabelFrame(self.tab_envoltoria, text="Vidros", padding=10, style="Section.TLabelframe")
        vidro.pack(fill="x", padx=8, pady=8)
        self.vidro_area_var = tk.StringVar(value="8")
        self.vidro_nome_var = tk.StringVar()
        self.vidro_sc_var = tk.StringVar(value="1.0")
        self.vidro_radiacao_var = tk.StringVar(value="220")

        ttk.Label(vidro, text="Área de vidro (m²)").grid(row=0, column=0, **LABEL_STYLE)
        ttk.Entry(vidro, textvariable=self.vidro_area_var, width=16).grid(row=0, column=1, **ENTRY_STYLE)
        ttk.Label(vidro, text="Tipo de vidro").grid(row=0, column=2, **LABEL_STYLE)
        vidro_combo = ttk.Combobox(vidro, textvariable=self.vidro_nome_var, values=list(self.repository.vidros.keys()), state="readonly", width=30)
        vidro_combo.grid(row=0, column=3, **ENTRY_STYLE)
        if vidro_combo["values"]:
            self.vidro_nome_var.set(vidro_combo["values"][0])
        ttk.Label(vidro, text="SC (opcional)").grid(row=1, column=0, **LABEL_STYLE)
        ttk.Entry(vidro, textvariable=self.vidro_sc_var, width=16).grid(row=1, column=1, **ENTRY_STYLE)
        ttk.Label(vidro, text="Radiação solar (W/m²)").grid(row=1, column=2, **LABEL_STYLE)
        ttk.Entry(vidro, textvariable=self.vidro_radiacao_var, width=16).grid(row=1, column=3, **ENTRY_STYLE)

    def _build_tab_resultados(self) -> None:
        resumo = ttk.LabelFrame(self.tab_resultados, text="Resultados consolidados", padding=10, style="Section.TLabelframe")
        resumo.pack(fill="x", padx=8, pady=8)
        self.summary_vars = {
            "sensivel": tk.StringVar(value="0,0 W"),
            "latente": tk.StringVar(value="0,0 W"),
            "total": tk.StringVar(value="0,0 W"),
            "btuh": tk.StringVar(value="0,0 BTU/h"),
            "tr": tk.StringVar(value="0,000 TR"),
            "pct_sensivel": tk.StringVar(value="0,0 %"),
            "pct_latente": tk.StringVar(value="0,0 %"),
        }
        fields = [
            ("Carga sensível", "sensivel"),
            ("Carga latente", "latente"),
            ("Carga total", "total"),
            ("BTU/h", "btuh"),
            ("TR", "tr"),
            ("% sensível", "pct_sensivel"),
            ("% latente", "pct_latente"),
        ]
        for idx, (title, key) in enumerate(fields):
            ttk.Label(resumo, text=title, style="SummaryTitle.TLabel").grid(row=idx, column=0, **LABEL_STYLE)
            ttk.Label(resumo, textvariable=self.summary_vars[key], style="SummaryValue.TLabel").grid(row=idx, column=1, padx=6, pady=3, sticky="e")

        parcelas = ttk.LabelFrame(self.tab_resultados, text="Cargas por parcela", padding=10, style="Section.TLabelframe")
        parcelas.pack(fill="both", expand=True, padx=8, pady=8)
        self.parcel_tree = ttk.Treeview(parcelas, columns=("parcela", "valor", "pct"), show="headings", height=16)
        self.parcel_tree.heading("parcela", text="Parcela")
        self.parcel_tree.heading("valor", text="Valor (W)")
        self.parcel_tree.heading("pct", text="Participação (%)")
        self.parcel_tree.column("parcela", width=290, anchor="w")
        self.parcel_tree.column("valor", width=120, anchor="e")
        self.parcel_tree.column("pct", width=120, anchor="e")
        self.parcel_tree.pack(fill="both", expand=True)

    def _build_sidebar(self, parent) -> None:
        acoes = ttk.LabelFrame(parent, text="Ações", padding=10, style="Section.TLabelframe")
        acoes.pack(fill="x", pady=(0, 8))
        ttk.Button(acoes, text="Calcular", command=self.calcular).pack(fill="x", pady=4)
        ttk.Button(acoes, text="Gerar PDF", command=self.gerar_pdf).pack(fill="x", pady=4)
        ttk.Button(acoes, text="Limpar camadas", command=self._clear_layers).pack(fill="x", pady=4)

        biblioteca = ttk.LabelFrame(parent, text="Biblioteca carregada", padding=10, style="Section.TLabelframe")
        biblioteca.pack(fill="both", expand=True)
        self.repo_info = tk.Text(biblioteca, height=30, wrap="word")
        self.repo_info.pack(fill="both", expand=True)
        self.repo_info.insert("1.0", self._repository_summary())
        self.repo_info.configure(state="disabled")

    def _repository_summary(self) -> str:
        linhas = ["Materiais simples:"]
        for nome in self.repository.materiais.keys():
            linhas.append(f"- {nome}")
        linhas.append("\nElementos completos:")
        for item in self.repository.elementos.values():
            linhas.append(f"- {item.categoria}: {item.nome} (U={item.u_w_m2k})")
        linhas.append("\nVidros:")
        for vidro in self.repository.vidros.values():
            linhas.append(f"- {vidro.nome} (U={vidro.u_w_m2k}, SHGC={vidro.shgc})")
        return "\n".join(linhas)

    def _preencher_cidade_inicial(self) -> None:
        valores = self.city_combo["values"]
        if valores:
            self.city_var.set(valores[0])
            self._city_selected()

    def _city_selected(self, _event=None) -> None:
        cidade = self.repository.cidades[self.city_var.get()]
        self.tbs_var.set(str(cidade.tbs_verao_c))
        self.ur_var.set(str(cidade.ur_verao_pct))
        self.umidade_ext_var.set(str(cidade.umidade_absoluta_gkg))
        self.vidro_radiacao_var.set(str(cidade.radiacao_solar_vidro_w_m2))

    def _add_layer(self) -> None:
        try:
            material_nome = self.material_var.get()
            espessura = float(self.espessura_var.get().replace(",", "."))
            target = self.comp_target_var.get()
            camada = CamadaMaterial(material_nome=material_nome, espessura_m=espessura)
            self.camadas[target].append(camada)
            self.layer_boxes[target].insert(tk.END, f"{material_nome} | e={espessura:.3f} m")
        except ValueError:
            messagebox.showerror("Erro", "Informe uma espessura válida para a camada.")

    def _clear_layers(self) -> None:
        for key in self.camadas:
            self.camadas[key].clear()
            self.layer_boxes[key].delete(0, tk.END)

    def _to_float(self, variable: tk.StringVar) -> float:
        return float(variable.get().strip().replace(",", "."))

    def _to_int(self, variable: tk.StringVar) -> int:
        return int(float(variable.get().strip().replace(",", ".")))

    def _build_input(self) -> ProjectInput:
        parede = ComponenteEnvelopeInput(
            area_m2=self._to_float(self.parede_area_var),
            modo=self.parede_modo_var.get(),
            elemento_nome=self.parede_elemento_var.get(),
            camadas=list(self.camadas["parede"]),
        )
        cobertura = ComponenteEnvelopeInput(
            area_m2=self._to_float(self.cobertura_area_var),
            modo=self.cobertura_modo_var.get(),
            elemento_nome=self.cobertura_elemento_var.get(),
            camadas=list(self.camadas["cobertura"]),
        )
        piso = ComponenteEnvelopeInput(
            area_m2=self._to_float(self.piso_area_var),
            modo=self.piso_modo_var.get(),
            elemento_nome=self.piso_elemento_var.get(),
            camadas=list(self.camadas["piso"]),
        )
        vidro = VidroInput(
            area_m2=self._to_float(self.vidro_area_var),
            vidro_nome=self.vidro_nome_var.get(),
            sc=max(self._to_float(self.vidro_sc_var), 0.0),
            radiacao_w_m2=self._to_float(self.vidro_radiacao_var),
        )
        return ProjectInput(
            nome_projeto=self.project_name_var.get().strip() or "Projeto HVAC",
            cidade_label=self.city_var.get(),
            tbs_externa_c=self._to_float(self.tbs_var),
            ur_externa_pct=self._to_float(self.ur_var),
            umidade_externa_gkg=self._to_float(self.umidade_ext_var),
            nome_ambiente=self.ambiente_nome_var.get().strip() or "Ambiente",
            area_m2=self._to_float(self.area_var),
            altura_m=self._to_float(self.altura_var),
            delta_t_c=self._to_float(self.delta_t_var),
            umidade_interna_gkg=self._to_float(self.umidade_int_var),
            pessoas=self._to_int(self.pessoas_var),
            calor_sensivel_pessoa_w=self._to_float(self.sens_pessoa_var),
            calor_latente_pessoa_w=self._to_float(self.lat_pessoa_var),
            iluminacao_w=self._to_float(self.iluminacao_var),
            equipamentos_w=self._to_float(self.equipamentos_var),
            ventilacao_m3h=self._to_float(self.ventilacao_var),
            parede=parede,
            cobertura=cobertura,
            piso=piso,
            vidro=vidro,
        )

    def calcular(self) -> None:
        try:
            dados = self._build_input()
            self.resultado_atual = self.calc_service.calcular(dados)
        except Exception as exc:
            messagebox.showerror("Erro de cálculo", str(exc))
            return
        self._render_resultados()
        messagebox.showinfo("Cálculo concluído", "Resumo atualizado com sucesso.")

    def _fmt(self, value: float, digits: int = 1) -> str:
        return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _render_resultados(self) -> None:
        if self.resultado_atual is None:
            return
        r = self.resultado_atual
        self.summary_vars["sensivel"].set(f"{self._fmt(r.sensivel_w)} W")
        self.summary_vars["latente"].set(f"{self._fmt(r.latente_w)} W")
        self.summary_vars["total"].set(f"{self._fmt(r.total_w)} W")
        self.summary_vars["btuh"].set(f"{self._fmt(r.total_btuh)} BTU/h")
        self.summary_vars["tr"].set(f"{self._fmt(r.total_tr, 3)} TR")
        self.summary_vars["pct_sensivel"].set(f"{self._fmt(r.percentual_sensivel)} %")
        self.summary_vars["pct_latente"].set(f"{self._fmt(r.percentual_latente)} %")

        for item in self.parcel_tree.get_children():
            self.parcel_tree.delete(item)
        for nome, valor in r.cargas_w.items():
            self.parcel_tree.insert("", tk.END, values=(nome, self._fmt(valor), self._fmt(r.percentuais_parcela[nome])))

    def gerar_pdf(self) -> None:
        try:
            dados = self._build_input()
            resultado = self.resultado_atual or self.calc_service.calcular(dados)
            self.resultado_atual = resultado
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))
            return

        path = filedialog.asksaveasfilename(
            title="Salvar relatório",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            initialfile="relatorio_hvac.pdf",
        )
        if not path:
            return
        gerar_relatorio_pdf(Path(path), dados, resultado)
        self._render_resultados()
        messagebox.showinfo("PDF gerado", f"Relatório salvo em:\n{path}")

    def run(self) -> None:
        self.root.mainloop()
