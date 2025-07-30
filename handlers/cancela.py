from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
import speech_recognition as sr

async def cancela(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancela a operação atual em andamento no bot.

    Args:
        update (Update): Objeto Update do Telegram contendo informações da mensagem
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot
        
    Returns:
        ConversationHandler.END: Constante que indica o fim da conversa com o usuário,
                               encerrando o fluxo atual de interação
    """
    await update.message.reply_text(
        'Operação cancelada.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END