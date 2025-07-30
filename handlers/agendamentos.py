from telegram import Update
from telegram.ext import ContextTypes
from utils.database import conn
from datetime import datetime
from utils.validator import InputValidator

async def agendamentos(update: Update, context: ContextTypes.DEFAULT_TYPE):
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