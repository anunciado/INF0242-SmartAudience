from telegram import Update, InputFile
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Bem-vindo ao Bot de Audiências!
Use /ajuda para ver os comandos disponíveis.
""")