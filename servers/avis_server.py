import sqlite3
from datetime import datetime, timedelta
import calendar

from mcp.server.fastmcp import FastMCP

# Inicializa o servidor MCP com nome "avis_server"
mcp = FastMCP("avis_server")

# Conecta ao banco SQLite e cria a tabela, se necessário
conn = sqlite3.connect("avis.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS agendamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_processo TEXT NOT NULL,
    data_inicio DATETIME NOT NULL,
    data_fim DATETIME NOT NULL,
    data_cadastro DATETIME NOT NULL
)
""")
conn.commit()

# Função utilitária para validar horário e conflito
def pode_agendar(data_inicio: datetime) -> bool:
    # Verifica se é dia útil (segunda a sexta)
    if calendar.weekday(data_inicio.year, data_inicio.month, data_inicio.day) >= 5:
        return False
    # Verifica se está no intervalo entre 08:00 e 17:00 (termina às 18:00)
    if not (8 <= data_inicio.hour < 18):
        return False
    return True

@mcp.tool(name="agendar")
def agendar(numero_processo: str, data_inicio: str) -> str:
    try:
        inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Formato de data inválido. Use: YYYY-MM-DD HH:MM"

    if not pode_agendar(inicio_dt):
        return "Agendamentos devem ser feitos entre 08:00 e 18:00 em dias úteis."

    fim_dt = inicio_dt + timedelta(hours=1)

    # Verifica conflitos
    cursor.execute("""
        SELECT COUNT(*) FROM agendamento
        WHERE (? < data_fim AND ? > data_inicio)
    """, (inicio_dt, fim_dt))
    (conflitos,) = cursor.fetchone()

    if conflitos == 0:
        # Cadastra o agendamento
        cursor.execute("""
            INSERT INTO agendamento (numero_processo, data_inicio, data_fim, data_cadastro)
            VALUES (?, ?, ?, ?)
        """, (numero_processo, inicio_dt, fim_dt, datetime.now()))
        conn.commit()
        return f"Agendamento para processo {numero_processo} cadastrado com sucesso em {inicio_dt}."

    # Caso haja conflito, sugerir próximos 3 horários disponíveis
    horarios_sugeridos = []
    tentativa = inicio_dt + timedelta(minutes=30)

    while len(horarios_sugeridos) < 3:
        if not pode_agendar(tentativa):
            tentativa += timedelta(minutes=30)
            continue

        fim_tentativa = tentativa + timedelta(hours=1)
        cursor.execute("""
            SELECT COUNT(*) FROM agendamento
            WHERE (? < data_fim AND ? > data_inicio)
        """, (tentativa, fim_tentativa))
        (tem_conflito,) = cursor.fetchone()

        if tem_conflito == 0:
            horarios_sugeridos.append(tentativa.strftime("%Y-%m-%d %H:%M"))

        tentativa += timedelta(minutes=30)

    return (
        f"Conflito de horário em {inicio_dt.strftime('%Y-%m-%d %H:%M')}. "
        f"Próximos horários disponíveis:\n" +
        "\n".join(horarios_sugeridos)
    )

if __name__ == "__main__":
    mcp.run(transport='stdio')