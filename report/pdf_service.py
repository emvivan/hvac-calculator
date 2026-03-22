from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import List, Tuple

from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from models.project import ProjectInput, ProjectResult

PIE_COLORS = [
    colors.HexColor("#1f77b4"),
    colors.HexColor("#ff7f0e"),
    colors.HexColor("#2ca02c"),
    colors.HexColor("#d62728"),
    colors.HexColor("#9467bd"),
    colors.HexColor("#8c564b"),
    colors.HexColor("#e377c2"),
    colors.HexColor("#7f7f7f"),
    colors.HexColor("#bcbd22"),
    colors.HexColor("#17becf"),
    colors.HexColor("#4e79a7"),
]


def _fmt(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _table(data: List[List[str]], widths: List[float]) -> Table:
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def build_pie_chart(cargas: List[Tuple[str, float]]) -> Drawing:
    drawing = Drawing(460, 240)
    pie = Pie()
    pie.x = 30
    pie.y = 35
    pie.width = 180
    pie.height = 180
    valores = [valor for _, valor in cargas if valor > 0]
    labels = [nome for nome, valor in cargas if valor > 0]
    total = sum(valores) or 1.0
    pie.data = valores
    pie.labels = [f"{valor / total * 100:.1f}%" for valor in valores]
    pie.sideLabels = True
    pie.startAngle = 90
    pie.simpleLabels = False
    for idx in range(len(valores)):
        pie.slices[idx].fillColor = PIE_COLORS[idx % len(PIE_COLORS)]
        if idx < 2:
            pie.slices[idx].popout = 8
    drawing.add(pie)

    legend = Legend()
    legend.x = 240
    legend.y = 200
    legend.dx = 10
    legend.dy = 10
    legend.columnMaximum = 11
    legend.colorNamePairs = [(PIE_COLORS[idx % len(PIE_COLORS)], f"{labels[idx]} - {_fmt(valores[idx], 1)} W") for idx in range(len(labels))]
    drawing.add(legend)
    return drawing


def gerar_relatorio_pdf(path: Path, dados: ProjectInput, resultado: ProjectResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=1.2 * cm, rightMargin=1.2 * cm, topMargin=1.0 * cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Relatório de Carga Térmica HVAC", styles["Title"]))
    story.append(Paragraph("Pré-dimensionamento com biblioteca construtiva e gráfico de participação", styles["Heading3"]))
    story.append(Spacer(1, 10))

    projeto = [
        ["Item", "Valor", "Unidade"],
        ["Projeto", dados.nome_projeto, "-"],
        ["Cidade", dados.cidade_label, "-"],
        ["Data", dt.datetime.now().strftime("%d/%m/%Y %H:%M"), "-"],
        ["Ambiente", dados.nome_ambiente, "-"],
    ]
    ambiente = [
        ["Item", "Valor", "Unidade"],
        ["Área", _fmt(dados.area_m2), "m²"],
        ["Altura", _fmt(dados.altura_m), "m"],
        ["Volume", _fmt(dados.volume_m3), "m³"],
        ["ΔT", _fmt(dados.delta_t_c), "°C"],
    ]
    parametros = [
        ["Item", "Valor", "Unidade"],
        ["TBS externa", _fmt(dados.tbs_externa_c), "°C"],
        ["UR externa", _fmt(dados.ur_externa_pct), "%"],
        ["Umidade externa", _fmt(dados.umidade_externa_gkg), "g/kg"],
        ["Umidade interna", _fmt(dados.umidade_interna_gkg), "g/kg"],
        ["U parede", _fmt(resultado.u_parede, 3), "W/m²K"],
        ["U cobertura", _fmt(resultado.u_cobertura, 3), "W/m²K"],
        ["U piso", _fmt(resultado.u_piso, 3), "W/m²K"],
        ["U vidro", _fmt(resultado.u_vidro, 3), "W/m²K"],
    ]
    parcelas = [["Item", "Valor", "Unidade", "Participação %"]]
    for nome, valor in resultado.cargas_w.items():
        parcelas.append([nome, _fmt(valor, 1), "W", _fmt(resultado.percentuais_parcela[nome], 1)])
    resumo = [
        ["Item", "Valor", "Unidade", "Participação %"],
        ["Carga sensível", _fmt(resultado.sensivel_w, 1), "W", _fmt(resultado.percentual_sensivel, 1)],
        ["Carga latente", _fmt(resultado.latente_w, 1), "W", _fmt(resultado.percentual_latente, 1)],
        ["Carga total", _fmt(resultado.total_w, 1), "W", _fmt(100.0, 1)],
        ["Carga total", _fmt(resultado.total_btuh, 1), "BTU/h", "-"],
        ["Carga total", _fmt(resultado.total_tr, 3), "TR", "-"],
    ]

    story.append(Paragraph("Dados do projeto", styles["Heading2"]))
    story.append(_table(projeto, [5.0 * cm, 9.0 * cm, 2.5 * cm]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Resumo do ambiente", styles["Heading2"]))
    story.append(_table(ambiente, [5.0 * cm, 6.0 * cm, 3.0 * cm]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Parâmetros de entrada", styles["Heading2"]))
    story.append(_table(parametros, [5.5 * cm, 5.5 * cm, 3.0 * cm]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Tabela de cargas por parcela", styles["Heading2"]))
    story.append(_table(parcelas, [7.3 * cm, 3.2 * cm, 2.0 * cm, 3.2 * cm]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Resumo final", styles["Heading2"]))
    story.append(_table(resumo, [6.0 * cm, 4.0 * cm, 2.4 * cm, 3.3 * cm]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Gráfico de pizza das parcelas", styles["Heading2"]))
    story.append(build_pie_chart(list(resultado.cargas_w.items())))
    doc.build(story)
