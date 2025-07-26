from telegram import Update
from telegram.ext import ContextTypes
from utils.database import conn

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, codigo = update.message.text.split()
        cursor = conn.cursor()
        cursor.execute("UPDATE participante SET participou = 1 WHERE codigo_unico = ?", (codigo,))
        if cursor.rowcount:
            conn.commit()
            await update.message.reply_text("Check-in realizado com sucesso.")
        else:
            await update.message.reply_text("Código não encontrado.")
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")