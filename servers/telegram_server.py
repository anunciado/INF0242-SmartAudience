import sqlite3
import os
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from fpdf import FPDF

mcp = FastMCP("telegram_server")

conn = sqlite3.connect("telegram.db", check_same_thread=False)
cursor = conn.cursor()

# Criação das tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS participante (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS audio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL,
    caminho TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS termo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL,
    caminho TEXT NOT NULL
)
""")

conn.commit()

UPLOAD_FOLDER = "audios"
TERMOS_FOLDER = "termos"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TERMOS_FOLDER, exist_ok=True)

@mcp.tool(name="registrar_participante")
def registrar_participante(numero: str, nome: str, cpf: str) -> object:
    try:
        cursor.execute("INSERT INTO participante (numero, nome, cpf) VALUES (?, ?, ?)", (numero, nome, cpf))
        conn.commit()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool(name="upload_audio")
def upload_audio(numero: str, nome_arquivo: str, conteudo: bytes) -> object:
    try:
        caminho = os.path.join(UPLOAD_FOLDER, f"{numero}_{nome_arquivo}")
        with open(caminho, "wb") as f:
            f.write(conteudo)
        cursor.execute("INSERT INTO audio (numero, caminho) VALUES (?, ?)", (numero, caminho))
        conn.commit()
        return {"status": "ok", "arquivo": caminho}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool(name="gerar_termo")
def gerar_termo(numero: str) -> object:
    try:
        cursor.execute("SELECT nome, cpf FROM participante WHERE numero = ?", (numero,))
        participantes = cursor.fetchall()

        if not participantes:
            return {"status": "erro", "mensagem": "Nenhum participante registrado."}

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Termo da audiência do processo {numero}", ln=True, align='C')
        pdf.ln(10)
        for nome, cpf in participantes:
            pdf.cell(200, 10, txt=f"Participante: {nome} - CPF: {cpf}", ln=True)

        data_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        caminho = os.path.join(TERMOS_FOLDER, f"termo_{numero}_{data_atual}.pdf")
        pdf.output(caminho)

        cursor.execute("INSERT INTO termo (numero, caminho) VALUES (?, ?)", (numero, caminho))
        conn.commit()

        return {"status": "ok", "termo": caminho}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

if __name__ == "__main__":
    mcp.run(transport="stdio")