"""
Módulo principal do bot do Telegram que gerencia diferentes funcionalidades através de handlers.

Este módulo configura e inicializa um bot do Telegram usando a biblioteca python-telegram-bot.
Ele carrega variáveis de ambiente, configura os handlers para diferentes comandos e inicia
o polling do bot.

Attributes:
    TOKEN (str): Token de autenticação do bot do Telegram obtido através de variável de ambiente
    app (Application): Instância principal da aplicação do bot
"""

import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from handlers import start, ajuda, agendamentos, checkin, impugnacao, cancela, transcricao
from telegram.ext import CommandHandler

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Inicializa a aplicação do bot
app = Application.builder().token(TOKEN).build()

# Adiciona handlers para comandos básicos
app.add_handler(CommandHandler("start", start.start))
app.add_handler(CommandHandler("ajuda", ajuda.ajuda))
app.add_handler(CommandHandler("checkin", checkin.checkin))
app.add_handler(CommandHandler("agendamentos", agendamentos.agendamentos))
app.add_handler(CommandHandler("transcricao", transcricao.transcricao))
app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, transcricao.processar_audio))

# Configura o conversation handler para o fluxo de impugnação
impugnacao_handler = ConversationHandler(
    entry_points=[CommandHandler("impugnacao", impugnacao.impugnacao_start)],
    states={
        impugnacao.ESCOLHA_TIPO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, impugnacao.escolha_tipo)
        ],
        impugnacao.AGUARDANDO_TEXTO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, impugnacao.receber_texto)
        ],
        impugnacao.AGUARDANDO_AUDIO: [
            MessageHandler(filters.VOICE, impugnacao.receber_audio)
        ],
    },
    fallbacks=[CommandHandler("cancela", cancela.cancela)],
)

app.add_handler(impugnacao_handler)

# Inicia o bot
app.run_polling()