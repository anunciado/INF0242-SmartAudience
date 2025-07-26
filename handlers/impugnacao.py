from telegram import Update
from telegram.ext import ContextTypes
from utils.database import conn
from utils.date import agora

async def impugnacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        partes = texto.split(maxsplit=2)
        numero, descricao = partes[1], partes[2]
        cursor = conn.cursor()
        cursor.execute("INSERT INTO impugnacao (numero_processo, descricao, data_cadastro) VALUES (?, ?, ?)",
                       (numero, descricao, agora()))
        conn.commit()
        await update.message.reply_text("Impugnação registrada.")
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")
