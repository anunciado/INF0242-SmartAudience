import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from handlers import start, ajuda, agendamentos, checkin, impugnacao, cancela

load_dotenv()
TOKEN = ""

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start.start))
app.add_handler(CommandHandler("ajuda", ajuda.ajuda))
app.add_handler(CommandHandler("checkin", checkin.checkin))
app.add_handler(CommandHandler("agendamentos", agendamentos.agendamentos)) # Adicione esta linha junto com os outros handlers

# Conversation handler para impugnação
impugnacao_handler = ConversationHandler(
    entry_points=[CommandHandler("impugnacao", impugnacao.impugnacao_start)],
    states={
        impugnacao.ESCOLHA_TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, impugnacao.escolha_tipo)],
        impugnacao.AGUARDANDO_TEXTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, impugnacao.receber_texto)],
        impugnacao.AGUARDANDO_AUDIO: [MessageHandler(filters.VOICE, impugnacao.receber_audio)],
    },
    fallbacks=[CommandHandler("cancela", cancela.cancela)],
)

app.add_handler(impugnacao_handler)

app.run_polling()