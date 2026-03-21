import os
import logging
import asyncio
import json
import sys
import threading
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import whisper
from pydub import AudioSegment
import requests

# ====================================================================
# MASTER TELEGRAM BOT v6.0 - CAMASOTS EVOLUTIVE
# MANOS LIBRES (WHISPER) + MEMORIA RAG + PERMANENCIA 24/7
# ====================================================================

class TelegramMaster:
    def __init__(self, token):
        self.token = token
        self.root_dir = r"C:\a2\CAMASOTS"
        self.db_path = os.path.join(self.root_dir, "DATABASE", "MASTER", "master_db.json")
        self.temp_dir = os.path.join(self.root_dir, "TEMP")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self._load_db()
        self.app = ApplicationBuilder().token(token).build()
        self._setup_handlers()
        
        # Carga de Whisper para Manos Libres (Modelo base para velocidad)
        print("[SISTEMA] Cargando motor de voz Whisper...")
        self.voice_model = whisper.load_model("base")
        print("[SISTEMA] Motor de voz listo.")

    def _load_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
        else:
            self.db = {"config": {"master_id": None}, "memory": [], "users": {}}
            self._save_db()

    def _save_db(self):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=4)

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.menu_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler))
        self.app.add_handler(MessageHandler(filters.VOICE, self.voice_handler))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self.file_handler))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if not self.db["config"]["master_id"]:
            self.db["config"]["master_id"] = uid
            self._save_db()
            await update.message.reply_text("👑 **SISTEMA VINCULADO AL MASTER**\nIdentidad Root establecida.")
        await self._show_main_menu(update)

    async def _show_main_menu(self, update_or_query):
        keyboard = [
            [InlineKeyboardButton("🖥️ Master OS", callback_data='sys_status'), InlineKeyboardButton("🎙️ Manos Libres", callback_data='voice_mode')],
            [InlineKeyboardButton("🧠 Memoria IA", callback_data='memory'), InlineKeyboardButton("� OpenRouter", callback_data='proxy')],
            [InlineKeyboardButton("🔗 Alexa Sync", callback_data='alexa'), InlineKeyboardButton("❌ Cerrar", callback_data='close')]
        ]
        text = "🛰️ **CAMASOTS EVOLUTIVE v6.0**\n*Sincronía Permanente y Manos Libres Activa*\n\n¿Qué canal de mando deseas abrir?"
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        else:
            await update_or_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    async def voice_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Procesa mensajes de voz usando Whisper."""
        sent_msg = await update.message.reply_text("🎙️ *Procesando audio...*", parse_mode='Markdown')
        
        file = await update.message.voice.get_file()
        ogg_path = os.path.join(self.temp_dir, f"voice_{update.effective_user.id}.ogg")
        wav_path = ogg_path.replace(".ogg", ".wav")
        
        await file.download_to_drive(ogg_path)
        
        # Convertir OGG a WAV para Whisper
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")
        
        # Transcribir
        result = self.voice_model.transcribe(wav_path)
        text = result["text"]
        
        await sent_msg.edit_text(f"🗣️ **Dijiste:**\n`{text}`\n\n*Procesando orden...*", parse_mode='Markdown')
        
        # Simular procesamiento de orden técnica
        await self.process_master_order(text, update)

    async def process_master_order(self, text, update):
        # Aquí se integraría la lógica de GuilleCoder para ejecutar comandos en el PC
        response = f"✅ Orden recibida: '{text}'. Ejecutando en núcleo CAMASOTS..."
        await update.message.reply_text(response)

    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = update.message.text
        # Guardar en memoria evolutiva
        self.db["memory"].append({"time": datetime.now().isoformat(), "msg": msg})
        self._save_db()
        await update.message.reply_text(f"📡 *Sincronizado:* `{msg}`")

    async def menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        if query.data == 'main_menu':
            await self._show_main_menu(query)
        elif query.data == 'sys_status':
            await query.edit_message_text("� **ESTADO 24/7**\nUptime: 100%\nMotor: Evolutivo\nRoot: OK", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data='main_menu')]]), parse_mode='Markdown')

    async def file_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        file = await update.message.document.get_file()
        path = os.path.join(self.root_dir, "CAJON", update.message.document.file_name)
        await file.download_to_drive(path)
        await update.message.reply_text(f"📥 *Archivo asimilado:* `{update.message.document.file_name}`")

    def run(self):
        print(f"[CAMASOTS] Iniciando ciclo de vida permanente...")
        self.app.run_polling()

if __name__ == "__main__":
    # Cargar Token
    token = None
    env_path = r"C:\a2\CAMASOTS\PUENTE\caja_fuerte.env"
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if "VIRGILIO_TOKEN=" in line:
                    token = line.split('=')[1].strip()
    if token:
        bot = TelegramMaster(token)
        bot.run()
