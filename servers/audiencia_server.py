import sqlite3
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import os
from utils.pdf import gerar_termo_pdf

# Inicializa o servidor FastMCP
mcp = FastMCP("audiencia_server")

# Conexões com os bancos de dados
aljava_conn = sqlite3.connect("aljava.db", check_same_thread=False)
audiencia_conn = sqlite3.connect("audiencia.db", check_same_thread=False)

# Cursores
aljava_cursor = aljava_conn.cursor()
audiencia_cursor = audiencia_conn.cursor()

def buscar_dados_audiencia(agendamento_id: int) -> dict:
    # Busca dados do agendamento
    audiencia_cursor.execute("""
        SELECT numero_processo, data_audiencia
        FROM agendamento 
        WHERE id = ?
    """, (agendamento_id,))
    agendamento = audiencia_cursor.fetchone()
    
    if not agendamento:
        return None
    
    # Busca participantes
    audiencia_cursor.execute("""
        SELECT nome, tipo, presente
        FROM participante
        WHERE agendamento_id = ?
    """, (agendamento_id,))
    participantes = audiencia_cursor.fetchall()
    
    # Busca impugnações
    audiencia_cursor.execute("""
        SELECT texto
        FROM impugnacao
        WHERE agendamento_id = ?
    """, (agendamento_id,))
    impugnacoes = [imp[0] for imp in audiencia_cursor.fetchall()]
    
    # Busca transcrição do aljava
    aljava_cursor.execute("""
        SELECT texto
        FROM transcricao
        WHERE agendamento_id = ?
    """, (agendamento_id,))
    transcricao = aljava_cursor.fetchone()
    
    # Busca arquivos do processo no aljava
    aljava_cursor.execute("""
        SELECT a.nome
        FROM arquivo a
        JOIN processo_arquivo pa ON pa.arquivo_id = a.id
        JOIN processo p ON p.id = pa.processo_id
        WHERE p.numero = ?
    """, (agendamento[0],))
    arquivos = [arq[0] for arq in aljava_cursor.fetchall()]
    
    # Organiza participantes presentes e ausentes
    presentes = []
    ausentes = []
    for nome, tipo, presente in participantes:
        if presente:
            presentes.append({"nome": nome, "tipo": tipo, "codigo": f"{tipo[:3]}{len(presentes)+1}"})
        else:
            ausentes.append({"nome": nome, "tipo": tipo})
    
    return {
        "numero_processo": agendamento[0],
        "data": agendamento[1],
        "participantes": presentes,
        "ausentes": ausentes,
        "transcricao": transcricao[0] if transcricao else None,
        "impugnacoes": impugnacoes,
        "arquivos": arquivos
    }

@mcp.tool(name="gerar_termo_audiencia")
def gerar_termo_audiencia(agendamento_id: int) -> object:
    try:
        dados = buscar_dados_audiencia(agendamento_id)
        if not dados:
            return {
                "sucesso": False,
                "erro": f"Agendamento {agendamento_id} não encontrado."
            }
        
        # Cria diretório para os termos se não existir
        os.makedirs("termos", exist_ok=True)
        
        # Define o caminho do arquivo PDF
        caminho_pdf = f"termos/termo_audiencia_{agendamento_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Gera o PDF
        gerar_termo_pdf(dados, caminho_pdf)
        
        return {
            "sucesso": True,
            "mensagem": "Termo de audiência gerado com sucesso",
            "caminho": caminho_pdf
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e)
        }

if __name__ == "__main__":
    mcp.run(transport="stdio")
