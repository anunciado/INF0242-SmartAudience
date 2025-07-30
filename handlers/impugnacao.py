from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from utils.database import conn
from datetime import datetime
import speech_recognition as sr
import os

# Estados da conversa
ESCOLHA_TIPO = 0
AGUARDANDO_TEXTO = 1
AGUARDANDO_AUDIO = 2

async def impugnacao_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia o processo de impugnação.

    Args:
        update (Update): Objeto Update do Telegram contendo informações da mensagem
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot contendo os argumentos passados 
                                          no comando (/impugnacao <número>)

    Returns:
        ESCOLHA_TIPO: Estado para aguardar escolha do tipo de entrada
        ConversationHandler.END: Se ocorrer erro ou argumentos não forem fornecidos
    """
    try:
        args = context.args
        if not args:
            await update.message.reply_text("Por favor, forneça o número do processo: /impugnacao <número>")
            return ConversationHandler.END
        
        numero = args[0]
        context.user_data['numero'] = numero
        
        reply_keyboard = [['Texto', 'Áudio']]
        await update.message.reply_text(
            'Como você deseja registrar a impugnação?',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True
            )
        )
        return ESCOLHA_TIPO
    
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")
        return ConversationHandler.END

async def escolha_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processa a escolha do tipo de entrada (texto ou áudio).

    Args:
        update (Update): Objeto Update do Telegram contendo informações da mensagem
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot

    Returns:
        AGUARDANDO_TEXTO: Estado para aguardar entrada de texto
        AGUARDANDO_AUDIO: Estado para aguardar entrada de áudio
        ConversationHandler.END: Se opção inválida for escolhida
    """
    escolha = update.message.text
    
    if escolha == 'Texto':
        await update.message.reply_text(
            "Por favor, digite o texto da impugnação:",
            reply_markup=ReplyKeyboardRemove()
        )
        return AGUARDANDO_TEXTO
    
    elif escolha == 'Áudio':
        await update.message.reply_text(
            "Por favor, envie sua mensagem de voz:",
            reply_markup=ReplyKeyboardRemove()
        )
        return AGUARDANDO_AUDIO
    
    else:
        await update.message.reply_text(
            "Opção inválida. Por favor, escolha Texto ou Áudio.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

async def receber_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processa a entrada de texto da impugnação.

    Args:
        update (Update): Objeto Update do Telegram contendo informações da mensagem
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot contendo o número do processo

    Returns:
        ConversationHandler.END: Finaliza a conversa após processar o texto ou em caso de erro
    """
    try:
        numero = context.user_data['numero']
        descricao = update.message.text
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO impugnacao (numero_processo, descricao, data_cadastro) VALUES (?, ?, ?)",
            (numero, descricao, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        conn.commit()
        
        await update.message.reply_text("Impugnação registrada com sucesso!")
        return ConversationHandler.END
    
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")
        return ConversationHandler.END

async def receber_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processa a entrada de áudio da impugnação.
    
    Args:
        update (Update): Objeto Update do Telegram contendo a mensagem com o arquivo de áudio
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot contendo o número do processo

    Returns:
        ConversationHandler.END: Finaliza a conversa após processar o áudio ou em caso de erro
    """
    try:
        numero = context.user_data['numero']
        
        # Download do arquivo de áudio
        audio_file = await update.message.voice.get_file()
        audio_path = f"temp_{update.message.from_user.id}.ogg"
        await audio_file.download_to_drive(audio_path)
        
        # Converter áudio para texto
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                descricao = recognizer.recognize_google(audio_data, language='pt-BR')
                
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO impugnacao (numero_processo, descricao, data_cadastro) VALUES (?, ?, ?)",
                (numero, descricao, datetime.now().strftime("%Y-%m-%d %H:%M"))
            )
            conn.commit()
            
            await update.message.reply_text(
                f"Impugnação registrada com sucesso!\nTexto reconhecido: {descricao}"
            )
            
        except Exception as e:
            await update.message.reply_text("Erro ao converter áudio para texto. Tente novamente.")
            return ConversationHandler.END
            
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
        return ConversationHandler.END
        
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")
        return ConversationHandler.END