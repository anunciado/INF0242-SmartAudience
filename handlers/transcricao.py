from telegram import Update
from telegram.ext import ContextTypes
import os
import speech_recognition as sr
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
from pydub import AudioSegment  # Adicione esta importação

# Obtém o caminho absoluto para o diretório do projeto
project_root = Path(__file__).parent.parent
db_aljava_path = os.path.join(project_root, "servers", "aljava.db")
db_avis_path = os.path.join(project_root, "servers", "avis.db")

# Conexões com os bancos de dados
aljava_conn = sqlite3.connect(db_aljava_path, check_same_thread=False)
avis_conn = sqlite3.connect(db_avis_path, check_same_thread=False)

# Cursores
aljava_cursor = aljava_conn.cursor()
avis_cursor = avis_conn.cursor()

async def transcricao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler do Telegram para transcrever áudio e salvar no banco de dados.
    
    Args:
        update (Update): Objeto de atualização do Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot
    """
    try:
        # Obtém número do processo e agendamento_id dos argumentos do comando
        try:
            args = context.args
            agendamento_id = int(args[0])
            
            # Salva o agendamento_id no contexto do usuário
            context.user_data['agendamento_id'] = agendamento_id
            
            # Solicita o áudio ao usuário
            await update.message.reply_text(
                "Por favor, envie agora o arquivo de áudio ou mensagem de voz que deseja transcrever."
            )
            return
            
        except (IndexError, ValueError):
            await update.message.reply_text(
                "Formato incorreto. Use: /transcricao <agendamento_id>"
            )
            return

    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao iniciar transcrição: {str(e)}")

async def processar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para processar o áudio enviado após o comando de transcrição.
    
    Args:
        update (Update): Objeto de atualização do Telegram
        context (ContextTypes.DEFAULT_TYPE): Contexto do bot
    """
    try:
        # Verifica se há um agendamento_id salvo no contexto
        agendamento_id = context.user_data.get('agendamento_id')
        if not agendamento_id:
            await update.message.reply_text(
                "Por favor, primeiro use o comando /transcricao <agendamento_id>"
            )
            return

        # Verifica se há mensagem de voz ou arquivo de áudio
        message = update.message
        if message.voice:
            file = message.voice
        elif message.audio:
            file = message.audio
        else:
            await update.message.reply_text("Por favor, envie uma mensagem de voz ou arquivo de áudio.")
            return

        # Cria o diretório midias se não existir
        midias_dir = os.path.join(project_root, "midias")
        os.makedirs(midias_dir, exist_ok=True)

        # Baixa o arquivo de áudio
        audio_file = await context.bot.get_file(file.file_id)
        
        # Gera nome único para o arquivo temporário original
        temp_filename = f"temp_{uuid.uuid4()}"
        if message.voice:
            temp_original = f"{temp_filename}.ogg"
        elif message.audio:
            original_name = file.file_name
            extension = original_name.split('.')[-1] if '.' in original_name else 'mp3'
            temp_original = f"{temp_filename}.{extension}"
        
        temp_wav = f"{temp_filename}.wav"
        
        temp_original_path = os.path.join(midias_dir, temp_original)
        temp_wav_path = os.path.join(midias_dir, temp_wav)
        
        try:
            # Baixa o arquivo original
            await audio_file.download_to_drive(temp_original_path)
            
            # Converte para WAV
            audio = AudioSegment.from_file(temp_original_path)
            audio.export(temp_wav_path, format="wav")
            
            # Realiza a transcrição
            await update.message.reply_text("Transcrevendo áudio, por favor aguarde...")
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_wav_path) as source:
                audio_data = recognizer.record(source)
                texto_transcrito = recognizer.recognize_google(audio_data, language='pt-BR')
            
            # Salva a transcrição
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            aljava_cursor.execute("""
                INSERT INTO transcricao (texto, agendamento_id, data_cadastro)
                VALUES (?, ?, ?)
            """, (texto_transcrito, agendamento_id, data_atual))
            
            aljava_conn.commit()
            
            # Limpa o agendamento_id do contexto
            context.user_data.pop('agendamento_id', None)
            
            # Envia a resposta
            await update.message.reply_text(
                f"🎯 Áudio transcrito com sucesso!\n\n"
                f"📝 Transcrição:\n{texto_transcrito}"
            )
            
        finally:
            # Limpa os arquivos temporários
            if os.path.exists(temp_original_path):
                os.remove(temp_original_path)
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)

        avis_cursor.execute("SELECT numero_processo FROM agendamento WHERE id = ?", (agendamento_id,))
        resultado = avis_cursor.fetchone()

        if not resultado:
            await update.message.reply_text(f"Agendamento ID '{agendamento_id}' não encontrado.")
            return

        numero_processo = resultado[0]

        # Verifica se o processo existe
        aljava_cursor.execute("SELECT id FROM processo WHERE numero = ?", (numero_processo,))
        processo = aljava_cursor.fetchone()
        
        if not processo:
            await update.message.reply_text(f"Processo '{numero_processo}' não encontrado.")
            return
            
        processo_id = processo[0]
        
        # Gera nome único para o arquivo mantendo a extensão original
        if message.voice:
            # Mensagens de voz do Telegram são normalmente OGG
            audio_filename = f"audio_{uuid.uuid4()}.ogg"
        elif message.audio:
            # Para arquivos de áudio, pegar a extensão original ou usar mp3 como padrão
            original_name = file.file_name
            extension = original_name.split('.')[-1] if '.' in original_name else 'mp3'
            audio_filename = f"audio_{uuid.uuid4()}.{extension}"
        
        audio_path = os.path.join(midias_dir, audio_filename)
        
        # Registra o arquivo no banco
        aljava_cursor.execute(
            "INSERT INTO arquivo (nome, caminho) VALUES (?, ?)",
            (audio_filename, audio_path)
        )
        arquivo_id = aljava_cursor.lastrowid
        
        # Relaciona o arquivo ao processo
        aljava_cursor.execute(
            "INSERT INTO processo_arquivo (processo_id, arquivo_id) VALUES (?, ?)",
            (processo_id, arquivo_id)
        )
        
    except Exception as e:
        if 'conn' in locals():
            aljava_conn.rollback()
        await update.message.reply_text(f"❌ Erro ao processar áudio: {str(e)}")