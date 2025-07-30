import sqlite3
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import os
import speech_recognition as sr
import uuid

# Inicializa o servidor FastMCP com nome "aljava_server"
mcp = FastMCP("aljava_server")

# Conecta ou cria o banco SQLite
conn = sqlite3.connect("aljava.db", check_same_thread=False)
cursor = conn.cursor()

# Cria as tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS processo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT UNIQUE NOT NULL,
    data_cadastro TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS arquivo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    caminho TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS processo_arquivo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    processo_id INTEGER NOT NULL,
    arquivo_id INTEGER NOT NULL,
    FOREIGN KEY(processo_id) REFERENCES processo(id),
    FOREIGN KEY(arquivo_id) REFERENCES arquivo(id)
)
""")

# Nova tabela de Transcrição
cursor.execute("""
CREATE TABLE IF NOT EXISTS transcricao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT NOT NULL,
    agendamento_id INTEGER NOT NULL,
    data_cadastro TEXT NOT NULL
)
""")

conn.commit()

# Cria as tabelas (mantendo as tabelas existentes...)

# Garante que a pasta de mídias existe
os.makedirs("midias", exist_ok=True)

# MCP tool: buscar arquivos do processo
@mcp.tool(name="buscar_arquivos_do_processo")
def buscar_arquivos_do_processo(numero_processo: str) -> object:
    cursor.execute("SELECT id FROM processo WHERE numero = ?", (numero_processo,))
    processo = cursor.fetchone()

    if not processo:
        return {"erro": f"Processo '{numero_processo}' não encontrado."}

    processo_id = processo[0]
    cursor.execute("""
                   SELECT a.nome, a.caminho
                   FROM arquivo a
                            JOIN processo_arquivo pa ON pa.arquivo_id = a.id
                   WHERE pa.processo_id = ?
                   """, (processo_id,))

    arquivos = cursor.fetchall()

    if not arquivos:
        return {"mensagem": f"Não há arquivos cadastrados para o processo '{numero_processo}'."}

    return [{"nome": nome, "caminho": caminho} for nome, caminho in arquivos]

# MCP tool: transcrever_audio
@mcp.tool(name="transcrever_audio")
def transcrever_audio(numero_processo: str, agendamento_id: int, audio: bytes) -> object:
    try:
        # Verifica se o processo existe
        cursor.execute("SELECT id FROM processo WHERE numero = ?", (numero_processo,))
        processo = cursor.fetchone()
        
        if not processo:
            return {
                "sucesso": False,
                "erro": f"Processo '{numero_processo}' não encontrado."
            }
            
        processo_id = processo[0]
        
        # Gera um nome único para o arquivo de áudio
        audio_filename = f"audio_{uuid.uuid4()}.wav"
        audio_path = os.path.join("midias", audio_filename)
        
        # Salva o arquivo de áudio
        with open(audio_path, "wb") as f:
            f.write(audio)
        
        # Registra o arquivo no banco
        cursor.execute(
            "INSERT INTO arquivo (nome, caminho) VALUES (?, ?)",
            (audio_filename, audio_path)
        )
        arquivo_id = cursor.lastrowid
        
        # Relaciona o arquivo ao processo
        cursor.execute(
            "INSERT INTO processo_arquivo (processo_id, arquivo_id) VALUES (?, ?)",
            (processo_id, arquivo_id)
        )
        
        # Realiza a transcrição do áudio
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                texto_transcrito = recognizer.recognize_google(audio_data, language='pt-BR')
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro na transcrição do áudio: {str(e)}"
            }
        
        # Salva a transcrição
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO transcricao (texto, agendamento_id, data_cadastro)
            VALUES (?, ?, ?)
        """, (texto_transcrito, agendamento_id, data_atual))
        
        conn.commit()
        
        return {
            "sucesso": True,
            "mensagem": "Áudio transcrito com sucesso",
            "texto": texto_transcrito,
            "arquivo": {
                "nome": audio_filename,
                "caminho": audio_path
            }
        }
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        return {
            "sucesso": False,
            "erro": str(e)
        }

if __name__ == "__main__":
    mcp.run(transport="stdio")