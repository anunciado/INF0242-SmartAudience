import sqlite3
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.pdf import gerar_termo_pdf

# Inicializa o servidor FastMCP
mcp = FastMCP("avis_server")

# Conexões com os bancos de dados
aljava_conn = sqlite3.connect("aljava.db", check_same_thread=False)
avis_conn = sqlite3.connect("avis.db", check_same_thread=False)

# Garante que a pasta de termos existe
os.makedirs("termos", exist_ok=True)

# Cursores
aljava_cursor = aljava_conn.cursor()
avis_cursor = avis_conn.cursor()

def buscar_dados_audiencia(agendamento_id: int) -> dict:
    """
    Busca todos os dados relacionados a uma audiência.
    
    Args:
        agendamento_id (int): ID do agendamento da audiência
        
    Returns:
        dict: Dicionário com os dados da audiência ou None se não encontrado
    """
    # Busca dados do agendamento
    avis_cursor.execute("""
        SELECT numero_processo, data_inicio, data_fim
        FROM agendamento 
        WHERE id = ?
    """, (agendamento_id,))
    agendamento = avis_cursor.fetchone()
    
    if not agendamento:
        return None
    
    # Busca participantes
    avis_cursor.execute("""
        SELECT nome, cpf, presente
        FROM participante
        WHERE agendamento_id = ?
    """, (agendamento_id,))
    participantes = avis_cursor.fetchall()
    
    # Busca impugnações
    aljava_cursor.execute("""
        SELECT texto
        FROM impugnacao
        WHERE agendamento_id = ?
    """, (agendamento_id,))
    impugnacoes = aljava_cursor.fetchall()
    
    # Busca transcrição do aljava
    aljava_cursor.execute("""
        SELECT texto
        FROM transcricao
        WHERE agendamento_id = ?
    """, (agendamento_id,))
    transcricoes = aljava_cursor.fetchall()
    
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
    for nome, cpf, presente in participantes:
        if presente:
            presentes.append({"nome": nome, "cpf": cpf})
        else:
            ausentes.append({"nome": nome, "cpf": cpf})
    
    return {
        "numero_processo": agendamento[0],
        "data_inicio": agendamento[1],
        "data_fim": agendamento[2],
        "participantes": presentes,
        "ausentes": ausentes,
        "transcricoes": transcricoes,
        "impugnacoes": impugnacoes,
        "arquivos": arquivos
    }

@mcp.tool(name="dados_audiencia")
def dados_audiencia(agendamento_id: int) -> object:
    """
    Ferramenta MCP para buscar dados de uma audiência.
    
    Args:
        agendamento_id (int): ID do agendamento da audiência
        
    Returns:
        object: Dicionário com status de sucesso e dados ou erro
    """
    try:
        dados = buscar_dados_audiencia(agendamento_id)
        if not dados:
            return {
                "sucesso": False,
                "erro": f"Agendamento {agendamento_id} não encontrado."
            }
            
        return {
            "sucesso": True,
            "dados": dados
        }
        
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e)
        }

if __name__ == "__main__":
    mcp.run(transport="stdio")