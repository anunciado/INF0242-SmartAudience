from telegram import Update, InputFile
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Envia uma mensagem de boas-vindas quando o bot é iniciado.

    Args:
        update (Update): Objeto Update do Telegram contendo informações da mensagem
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot

    Returns:
        None: Envia mensagem de boas-vindas via Telegram
    """
    await update.message.reply_text("""
Bem-vindo ao Bot da Audiência Inteligente!
Use /ajuda para ver os comandos disponíveis.
""")