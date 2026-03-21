import os
import logging
import asyncio
import json
import sys
import threading
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import requests

# ====================================================================
# MASTER TELEGRAM BOT v6.1 - CAMASOTS EVOLUTIVE
# MANOS LIBRES (WHISPER) + MEMORIA RAG + PERMANENCIA 24/7
# Version 6.1 - Mejoras de seguridad y manejo de archivos
# ====================================================================

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("TelegramMaster")


class TelegramMaster:
    def __init__(self, token: str):
        self.token = token
        # Detección automática de paths
        self.root_dir = os.environ.get('CAMASOTS_ROOT', r"C:\a2\CAMASOTS")
        self.db_path = os.path.join(self.root_dir, "DATABASE", "MASTER", "master_db.json")
        self.temp_dir = os.path.join(self.root_dir, "TEMP")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self._load_db()
        self.app = ApplicationBuilder().token(token).build()
        self._setup_handlers()
        
        # Whisper cargado condicionalmente (puede fallar si no está instalado)
        self.voice_model = None
        self._load_whisper()

    def _load_whisper(self):
        """Carga Whisper solo si está disponible, usa modelo tiny para menor consumo."""
        try:
            import whisper
            print("[SISTEMA] Cargando motor de voz Whisper (modelo tiny)...")
            self.voice_model = whisper.load_model("tiny")  # ~75MB vs 140MB de "base"
            print("[SISTEMA] Motor de voz listo.")
        except ImportError:
            print("[SISTEMA] Whisper no disponible. Modo voz desactivado.")
            logger.warning("Whisper no está instalado.voice disabled")
        except Exception as e:
            print(f"[SISTEMA] Error cargando Whisper: {e}")
            logger.error(f"Error cargando Whisper: {e}")

    def _load_db(self):
        """Carga la base de datos master."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.db = json.load(f)
            except Exception as e:
                logger.error(f"Error cargando DB: {e}")
                self.db = {"config": {"master_id": None}, "memory": [], "users": {}}
        else:
            self.db = {"config": {"master_id": None}, "memory": [], "users": {}}
            self._save_db()

    def _save_db(self):
        """Guarda la base de datos."""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.db, f, indent=4)
        except Exception as e:
            logger.error(f"Error guardando DB: {e}")

    def _setup_handlers(self):
        """Configura los handlers del bot."""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.menu_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler))
        self.app.add_handler(MessageHandler(filters.VOICE, self.voice_handler))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.file_handler))

    def _cleanup_temp_files(self, *file_paths):
        """Limpia archivos temporales de forma segura."""
        for path in file_paths:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
                    logger.debug(f"Archivo temporal eliminado: {path}")
            except Exception as e:
                logger.warning(f"No se pudo eliminar {path}: {e}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler del comando /start."""
        uid = update.effective_user.id
        if not self.db["config"]["master_id"]:
            self.db["config"]["master_id"] = uid
            self._save_db()
            await update.message.reply_text("👑 **SISTEMA VINCULADO AL MASTER**\nIdentidad Root establecida.")
        await self._show_main_menu(update)

    async def _show_main_menu(self, update_or_query):
        """Muestra el menú principal."""
        keyboard = [
            [InlineKeyboardButton("🖥️ Master OS", callback_data='sys_status'), 
             InlineKeyboardButton("🎙️ Manos Libres", callback_data='voice_mode')],
            [InlineKeyboardButton("🧠 Memoria IA", callback_data='memory'), 
             InlineKeyboardButton("🔗 OpenRouter", callback_data='proxy')],
            [InlineKeyboardButton("🔗 Alexa Sync", callback_data='alexa'), 
             InlineKeyboardButton("❌ Cerrar", callback_data='close')]
        ]
        text = "🛰️ **CAMASOTS EVOLUTIVE v6.1**\n*Sincronía Permanente y Manos Libres Activa*\n\n¿Qué canal de mando deseas abrir?"
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update_or_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def voice_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa mensajes de voz usando Whisper."""
        # Verificar si Whisper está disponible
        if not self.voice_model:
            await update.message.reply_text("⚠️ *Motor de voz no disponible*", parse_mode='Markdown')
            return
        
        sent_msg = await update.message.reply_text("🎙️ *Procesando audio...*", parse_mode='Markdown')
        
        ogg_path = None
        wav_path = None
        
        try:
            file = await update.message.voice.get_file()
            ogg_path = os.path.join(self.temp_dir, f"voice_{update.effective_user.id}_{int(datetime.now().timestamp())}.ogg")
            wav_path = ogg_path.replace(".ogg", ".wav")
            
            await file.download_to_drive(ogg_path)
            
            # Convertir OGG a WAV para Whisper
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_ogg(ogg_path)
                audio.export(wav_path, format="wav")
            except ImportError:
                await sent_msg.edit_text("⚠️ *pydub no instalado. No se puede procesar audio.*", parse_mode='Markdown')
                return
            
            # Transcribir
            result = self.voice_model.transcribe(wav_path)
            text = result["text"]
            
            await sent_msg.edit_text(f"🗣️ **Dijiste:**\n`{text}`\n\n*Procesando orden...*", parse_mode='Markdown')
            
            # Procesar la orden
            await self.process_master_order(text, update)
            
        except Exception as e:
            logger.error(f"Error procesando voz: {e}")
            await sent_msg.edit_text(f"❌ *Error procesando audio:* `{str(e)}`", parse_mode='Markdown')
        
        finally:
            # Limpiar archivos temporales
            self._cleanup_temp_files(ogg_path, wav_path)

    async def process_master_order(self, text: str, update: Update):
        """Procesa la orden del usuario."""
        # Aquí se integraría la lógica de GuilleCoder para ejecutar comandos en el PC
        response = f"✅ Orden recibida: '{text}'. Ejecutando en núcleo CAMASOTS..."
        await update.message.reply_text(response)

    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja mensajes de texto."""
        msg = update.message.text
        # Guardar en memoria evolutiva
        self.db["memory"].append({"time": datetime.now().isoformat(), "msg": msg})
        # Limitar memoria a 1000 entradas para evitar crecimiento infinito
        if len(self.db["memory"]) > 1000:
            self.db["memory"] = self.db["memory"][-1000:]
        self._save_db()
        await update.message.reply_text(f"📡 *Sincronizado:* `{msg}`")

    async def menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja callbacks de menú."""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'main_menu':
            await self._show_main_menu(query)
        elif query.data == 'sys_status':
            text = "📊 **ESTADO 24/7**\n" \
                   "Uptime: 100%\n" \
                   "Motor: Evolutivo\n" \
                   "Root: OK"
            await query.edit_message_text(
                text, 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data='main_menu')]]), 
                parse_mode='Markdown'
            )
        elif query.data == 'voice_mode':
            if self.voice_model:
                text = "🎙️ **MODO MANOS LIBRES ACTIVADO**\nEnvía un mensaje de voz y lo transcribiré instantáneamente."
            else:
                text = "⚠️ **MODO VOZ NO DISPONIBLE**\nInstala Whisper para activar."
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data='main_menu')]]),
                parse_mode='Markdown'
            )

    async def file_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja archivos recibidos."""
        try:
            file = await update.message.document.get_file()
            path = os.path.join(self.root_dir, "CAJON", update.message.document.file_name)
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            await file.download_to_drive(path)
            await update.message.reply_text(f"📥 *Archivo asimilado:* `{update.message.document.file_name}`")
        except Exception as e:
            logger.error(f"Error guardando archivo: {e}")
            await update.message.reply_text(f"❌ *Error:* `{str(e)}`")

    def run(self):
        """Inicia el bot."""
        print(f"[CAMASOTS] Iniciando ciclo de vida permanente...")
        self.app.run_polling()


if __name__ == "__main__":
    # Cargar Token de forma segura
    token = None
    env_path = os.environ.get('CAMASOTS_ENV', r"C:\a2\CAMASOTS\PUENTE\caja_fuerte.env")
    
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if "VIRGILIO_TOKEN=" in line:
                        token = line.split('=')[1].strip()
                        break
        except Exception as e:
            print(f"Error leyendo token: {e}")
    
    if token:
        bot = TelegramMaster(token)
        bot.run()
    else:
        print("ERROR: No se encontró VIRGILIO_TOKEN en caja_fuerte.env")
