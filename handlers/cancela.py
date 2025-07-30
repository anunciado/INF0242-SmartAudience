from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
import speech_recognition as sr

async def cancela(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela a operação atual"""
    await update.message.reply_text(
        'Operação cancelada.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END