import sqlite3
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime
import speech_recognition as sr
import os

# Conexões com os bancos de dados
aljava_conn = sqlite3.connect("aljava.db", check_same_thread=False)
avis_conn = sqlite3.connect("avis.db", check_same_thread=False)

# Cursores
aljava_cursor = aljava_conn.cursor()
avis_cursor = avis_conn.cursor()

# Estados da conversa
ESCOLHA_TIPO = 0
AGUARDANDO_TEXTO = 1
AGUARDANDO_AUDIO = 2

async def impugnacao_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Inicia o processo de impugnação.

    Args:
        update (Update): Objeto Update do Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot

    Returns:
        ESCOLHA_TIPO: Estado para aguardar escolha do tipo de entrada
        ConversationHandler.END: Se ocorrer erro ou código não for fornecido
    """
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "Por favor, forneça o código único do participante: /impugnacao <código>"
            )
            return ConversationHandler.END
        
        codigo = args[0]
        
        # Busca o agendamento relacionado ao participante
        avis_cursor.execute("""
            SELECT a.id, p.id
            FROM agendamento a
            INNER JOIN participante p ON p.agendamento_id = a.id
            WHERE p.codigo = ?
        """, (codigo,))
        
        resultado = avis_cursor.fetchone()
        
        if not resultado:
            await update.message.reply_text(
                "Código inválido ou participante não encontrado."
            )
            return ConversationHandler.END
            
        agendamento_id, participante_id = resultado
        context.user_data['agendamento_id'] = agendamento_id
        context.user_data['participante_id'] = participante_id

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

async def receber_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processa a entrada de texto da impugnação.

    Args:
        update (Update): Objeto Update do Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot

    Returns:
        ConversationHandler.END: Finaliza a conversa
    """
    try:
        agendamento_id = context.user_data['agendamento_id']
        participante_id = context.user_data['participante_id']
        descricao = update.message.text
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        aljava_conn.execute(
            "INSERT INTO impugnacao (texto, participante_id, agendamento_id, data_cadastro) VALUES (?, ?, ?)",
            (descricao, participante_id, agendamento_id, data_atual)
        )
        aljava_conn.commit()
        
        await update.message.reply_text("Impugnação registrada com sucesso!")
        return ConversationHandler.END
    
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")
        return ConversationHandler.END

async def receber_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processa a entrada de áudio da impugnação.
    
    Args:
        update (Update): Objeto Update do Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot

    Returns:
        ConversationHandler.END: Finaliza a conversa
    """
    try:
        agendamento_id = context.user_data['agendamento_id']
        participante_id = context.user_data['participante_id']
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M")

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
                
            aljava_conn.execute(
                "INSERT INTO impugnacao (texto, participante_id, agendamento_id, data_cadastro) VALUES (?, ?, ?)",
                (descricao, participante_id, agendamento_id, data_atual)
            )
            aljava_conn.commit()
            
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