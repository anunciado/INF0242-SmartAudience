import sqlite3
from datetime import datetime, timedelta
import calendar
from utils.validator import InputValidator

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

# Adicione este código após a criação da tabela agendamento
cursor.execute("""
CREATE TABLE IF NOT EXISTS participante (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL,
    agendamento_id INTEGER NOT NULL,
    FOREIGN KEY (agendamento_id) REFERENCES agendamento (id)
)
""")
conn.commit()

# Função utilitária para validar horário e conflito
def pode_agendar(data_inicio: datetime) -> bool:
    """
    Verifica se é possível realizar agendamento na data/hora especificada.
    
    Args:
        data_inicio (datetime): Data e hora do agendamento
        
    Returns:
        bool: True se é possível agendar, False caso contrário
    """
    # Verifica se é dia útil (segunda a sexta)
    if calendar.weekday(data_inicio.year, data_inicio.month, data_inicio.day) >= 5:
        return False
    # Verifica se está no intervalo entre 08:00 e 17:00 (termina às 18:00)
    if not (8 <= data_inicio.hour < 18):
        return False
    return True

@mcp.tool(name="agendar")
def agendar(numero_processo: str, data_inicio: str) -> str:
    """
    Agenda uma audiência para um processo.
    
    Args:
        numero_processo (str): Número do processo
        data_inicio (str): Data e hora de início no formato "YYYY-MM-DD HH:MM"
        
    Returns:
        str: Mensagem de sucesso ou erro, incluindo sugestões de horários em caso de conflito
    """
    try:
        inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d %H:%M")
    except ValueError:
        return "Formato de data inválido. Use: YYYY-MM-DD HH:MM"

    if not pode_agendar(inicio_dt):
        return "Agendamentos devem ser feitos entre 08:00 e 18:00 em dias úteis."

    fim_dt = inicio_dt + timedelta(hours=1)

    # Valida o Número do Processo
    validator = InputValidator()
    numero_processo_valido, resultado = validator.validar_processo(numero_processo)

    if not numero_processo_valido:
        return resultado

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

@mcp.tool(name="listar_agendamentos_periodo")
def listar_agendamentos_periodo(data_inicio: str, data_fim: str) -> str:
    """
    Lista agendamentos em um período específico.
    
    Args:
        data_inicio (str): Data inicial no formato "YYYY-MM-DD"
        data_fim (str): Data final no formato "YYYY-MM-DD"
        
    Returns:
        str: Lista formatada de agendamentos ou mensagem de que nada foi encontrado
    """
    try:
        inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        fim = datetime.strptime(data_fim, "%Y-%m-%d")
    except ValueError:
        return "Formato de data inválido. Use: YYYY-MM-DD"

    cursor.execute("""
        SELECT numero_processo, data_inicio FROM agendamento
        WHERE date(data_inicio) BETWEEN date(?) AND date(?)
        ORDER BY data_inicio
    """, (inicio, fim))
    
    agendamentos = cursor.fetchall()
    
    if not agendamentos:
        return f"Nenhum agendamento encontrado no período de {data_inicio} a {data_fim}"
    
    resultado = f"Agendamentos de {data_inicio} a {data_fim}:\n"
    for processo, data in agendamentos:
        data_formatada = datetime.strptime(data, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        resultado += f"Processo: {processo} - Horário: {data_formatada}\n"
    
    return resultado

@mcp.tool(name="listar_agendamentos_hoje")
def listar_agendamentos_hoje() -> str:
    """
    Lista todos os agendamentos do dia atual.
    
    Returns:
        str: Lista formatada de agendamentos ou mensagem de que nada foi encontrado
    """
    hoje = datetime.now().date()
    
    cursor.execute("""
        SELECT numero_processo, data_inicio FROM agendamento
        WHERE date(data_inicio) = date(?)
        ORDER BY data_inicio
    """, (hoje,))
    
    agendamentos = cursor.fetchall()
    
    if not agendamentos:
        return "Nenhum agendamento para hoje"
    
    resultado = "Agendamentos de hoje:\n"
    for processo, data in agendamentos:
        data_formatada = datetime.strptime(data, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
        resultado += f"Processo: {processo} - Horário: {data_formatada}\n"
    
    return resultado

@mcp.tool(name="buscar_agendamento_processo")
def buscar_agendamento_processo(numero_processo: str) -> str:
    """
    Busca agendamentos de um processo específico.
    
    Args:
        numero_processo (str): Número do processo
        
    Returns:
        str: Lista formatada de agendamentos ou mensagem de que nada foi encontrado
    """
    # Valida o Número do Processo
    validator = InputValidator()
    numero_processo_valido, resultado = validator.validar_processo(numero_processo)

    if not numero_processo_valido:
        return resultado

    cursor.execute("""
        SELECT id, data_inicio, data_fim FROM agendamento
        WHERE numero_processo = ?
        ORDER BY data_inicio
    """, (numero_processo,))
    
    agendamentos = cursor.fetchall()
    
    if not agendamentos:
        return f"Nenhum agendamento encontrado para o processo {numero_processo}"
    
    resultado = f"Agendamentos para o processo {numero_processo}:\n"
    for id_agendamento, data_inicio, data_fim in agendamentos:
        inicio_formatado = datetime.strptime(data_inicio, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        fim_formatado = datetime.strptime(data_fim, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
        resultado += f"ID: {id_agendamento} - Início: {inicio_formatado} - Fim: {fim_formatado}\n"
    
    return resultado

@mcp.tool(name="inserir_participante")
def inserir_participante(nome: str, cpf: str, agendamento_id: int) -> str:
    """
    Insere um novo participante em um agendamento.
    
    Args:
        nome (str): Nome do participante
        cpf (str): CPF do participante
        agendamento_id (int): ID do agendamento
        
    Returns:
        str: Mensagem de sucesso ou erro
    """
    # Valida CPF
    validator = InputValidator()
    cpf_valido, resultado = validator.validar_cpf(cpf)

    if not cpf_valido:
        return resultado

    # Verifica se o agendamento existe
    cursor.execute("""
        SELECT COUNT(*) FROM agendamento WHERE id = ?
    """, (agendamento_id,))
    (existe_agendamento,) = cursor.fetchone()
    
    if not existe_agendamento:
        return f"Erro: Agendamento com ID {agendamento_id} não encontrado."
    
    # Verifica se o CPF já está cadastrado para este agendamento
    cursor.execute("""
        SELECT COUNT(*) FROM participante 
        WHERE cpf = ? AND agendamento_id = ?
    """, (cpf, agendamento_id))
    (participante_existe,) = cursor.fetchone()
    
    if participante_existe > 0:
        return f"Erro: Participante com CPF {cpf} já está cadastrado neste agendamento."
    
    try:
        # Insere o novo participante
        cursor.execute("""
            INSERT INTO participante (nome, cpf, agendamento_id)
            VALUES (?, ?, ?)
        """, (nome, cpf, agendamento_id))
        conn.commit()
        
        return f"Participante {nome} (CPF: {cpf}) cadastrado com sucesso no agendamento {agendamento_id}."
    except sqlite3.Error as e:
        conn.rollback()
        return f"Erro ao cadastrar participante: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')