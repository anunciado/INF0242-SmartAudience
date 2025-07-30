import sqlite3
import os
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from utils.validator import InputValidator
from pathlib import Path

# Obtém o caminho absoluto para o diretório do projeto
project_root = Path(__file__).parent.parent
db_path = os.path.join(project_root, "servers", "avis.db")

# Conecta ao banco SQLite usando caminho absoluto
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

async def agendamentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Busca e exibe os agendamentos futuros para um determinado CPF.
    
    Args:
        update (Update): Objeto Update do Telegram contendo informações da mensagem
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot contendo os argumentos passados
                                           no comando (/agendamentos <cpf>)
        
    Returns:
        None: A função envia mensagens diretamente ao usuário via Telegram:
            - Mensagem de erro se o CPF não for fornecido
            - Mensagem de erro se o CPF for inválido
            - Mensagem informando que não há agendamentos futuros
            - Lista formatada com os agendamentos encontrados
            - Mensagem de erro em caso de exceção
    """
    try:
        # Verifica se o CPF foi fornecido
        if not context.args:
            await update.message.reply_text(
                "Por favor, forneça o CPF: /agendamentos <cpf>"
            )
            return
        
        cpf = context.args[0]
        
        # Valida o CPF
        validator = InputValidator()
        cpf_valido, resultado = validator.validar_cpf(cpf)
        
        if not cpf_valido:
            await update.message.reply_text(
                f"CPF inválido: {resultado}"
            )
            return
            
        # Usa o CPF formatado retornado pela validação
        cpf = resultado
        hoje = datetime.now()
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.numero_processo, a.data_inicio, a.data_fim
            FROM agendamento a
            INNER JOIN participante p ON p.agendamento_id = a.id
            WHERE p.cpf = ? AND a.data_inicio >= ?
            ORDER BY a.data_inicio
        """, (cpf, hoje))
        
        agendamentos = cursor.fetchall()
        
        if not agendamentos:
            await update.message.reply_text(
                f"Nenhum agendamento futuro encontrado para o CPF {cpf}"
            )
            return
        
        mensagem = f"📅 *Agendamentos futuros para o CPF {cpf}:*\n\n"
        for processo, data_inicio, data_fim in agendamentos:
            inicio = datetime.strptime(data_inicio, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            fim = datetime.strptime(data_fim, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
            mensagem += f"*Processo:* `{processo}`\n"
            mensagem += f"*Início:* {inicio}\n"
            mensagem += f"*Fim:* {fim}\n\n"
        
        await update.message.reply_text(
            mensagem,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        await update.message.reply_text(f"Erro ao buscar agendamentos: {str(e)}")