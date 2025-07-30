import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from pathlib import Path
import os

# Obtém o caminho absoluto para o diretório do projeto
project_root = Path(__file__).parent.parent
db_path = os.path.join(project_root, "servers", "avis.db")

# Conecta ao banco SQLite usando caminho absoluto
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Realiza o check-in de um participante usando seu código único.
    
    Args:
        update (Update): Objeto Update do Telegram contendo informações da mensagem
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot
        
    Returns:
        None: Envia mensagem de confirmação ou erro via Telegram
    """
    try:
        _, codigo = update.message.text.split()
        cursor = conn.cursor()
        cursor.execute("UPDATE participante SET presente = 1 WHERE codigo_unico = ?", (codigo,))
        if cursor.rowcount:
            conn.commit()
            await update.message.reply_text("Check-in realizado com sucesso.")
        else:
            await update.message.reply_text("Código não encontrado.")
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")