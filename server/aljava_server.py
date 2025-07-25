import sqlite3
from mcp.server.fastmcp import FastMCP

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

conn.commit()

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

if __name__ == "__main__":
    mcp.run(transport="stdio")
