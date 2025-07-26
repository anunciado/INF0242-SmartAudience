from fpdf import FPDF
import os

def gerar_termo_pdf(dados, caminho):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Termo de Audiência", ln=True, align="C")
    pdf.ln(10)

    pdf.multi_cell(0, 10, f"Processo: {dados['numero_processo']}")
    pdf.multi_cell(0, 10, f"Data: {dados['data']}")

    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, "Participantes:", ln=True)
    pdf.set_font("Arial", size=12)
    for p in dados["participantes"]:
        pdf.cell(0, 10, f"{p['nome']} - Código: {p['codigo']}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, "Transcrição:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, dados["transcricao"] or "Sem transcrição.")

    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, "Impugnações:", ln=True)
    pdf.set_font("Arial", size=12)
    for imp in dados["impugnacoes"]:
        pdf.multi_cell(0, 10, f"- {imp}")

    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, "Arquivos (Aljava):", ln=True)
    pdf.set_font("Arial", size=12)
    for arq in dados["arquivos"]:
        pdf.cell(0, 10, f"- {arq}", ln=True)

    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    pdf.output(caminho)