from fpdf import FPDF
import os

def gerar_termo_pdf(dados: dict, caminho: str) -> None:
    """
    Gera um PDF com o termo de audiência.
    
    Args:
        dados (dict): Dicionário contendo os dados da audiência:
            - numero_processo (str): Número do processo
            - data (str): Data da audiência
            - participantes (list): Lista de participantes com nome e código
            - transcricao (str): Texto da transcrição
            - impugnacoes (list): Lista de impugnações
            - arquivos (list): Lista de arquivos da Aljava
        caminho (str): Caminho onde o arquivo PDF será salvo
        
    Returns:
        None: Salva o arquivo PDF no caminho especificado
    """
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