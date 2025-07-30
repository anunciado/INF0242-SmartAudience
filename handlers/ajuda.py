from telegram import Update
from telegram.ext import ContextTypes

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Exibe a lista de comandos disponíveis no bot.
    
    Args:
        update (Update): Objeto Update do Telegram contendo informações da mensagem
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot
        
    Returns:
        None: Envia uma mensagem via Telegram com a lista de comandos disponíveis
    """
    await update.message.reply_text("""
Comandos disponíveis:
/start – Mensagem de boas-vindas
/ajuda – Lista de comandos
/checkin <código> – Check-in do participante
/impugnacao <número> – Registra impugnação (escolha entre texto ou áudio)
/agendamentos <cpf> – Busca agendamentos futuros por CPF
/cancela - Cancela a operação atual
""")