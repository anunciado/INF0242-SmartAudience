from telegram import Update
from telegram.ext import ContextTypes
from utils.database import conn

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
        cursor.execute("UPDATE participante SET participou = 1 WHERE codigo_unico = ?", (codigo,))
        if cursor.rowcount:
            conn.commit()
            await update.message.reply_text("Check-in realizado com sucesso.")
        else:
            await update.message.reply_text("Código não encontrado.")
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")