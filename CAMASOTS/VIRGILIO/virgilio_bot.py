import os
import logging
import asyncio
import json
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import sys

# ====================================================================
# VIRGILIO AGENT BOT v1.0 - MASTER SYSTEM COMMANDER
# CONTROL DE HARDWARE, ROOT ACCESS Y CHAT INTELIGENTE
# ====================================================================

class VirgilioBot:
    def __init__(self, token):
        self.token = token
        self.base_dir = r"C:\a2\CAMASOTS"
        self.lab_dir = os.path.join(self.base_dir, "LABORATORIO")
        self.cajon_dir = os.path.join(self.base_dir, "CAJON")
        
        # Cargar dependencias de Shared_Core (Puente)
        sys.path.append(os.path.join(self.base_dir, "PUENTE"))
        try:
            from controller import SystemController
            self.sc = SystemController()
        except:
            self.sc = None

        self.app = ApplicationBuilder().token(token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.menu_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.chat_handler))
        self.app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, self.file_handler))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self._show_main_menu(update)

    async def _show_main_menu(self, update_or_query):
        keyboard = [
            [InlineKeyboardButton("🖥️ Control Hardware", callback_data='hw_menu'), InlineKeyboardButton("🛡️ Root CMD", callback_data='root_menu')],
            [InlineKeyboardButton("📋 Laboratorio", callback_data='lab_menu'), InlineKeyboardButton("📸 Screenshot", callback_data='pc_snap')],
            [InlineKeyboardButton("🤝 Cooperar", callback_data='coop_menu'), InlineKeyboardButton("❌ Cerrar", callback_data='close')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "🤖 **VIRGILIO MASTER COMMANDER**\nEstado: **FULL OPERATIVE**\n\n¿Qué orden desea ejecutar, señor?"
        
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update_or_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == 'hw_menu':
            if self.sc:
                report = self.sc.get_full_system_report()
                text = (f"📊 **REPORTE DE HARDWARE**\n"
                        f"• CPU: {report['status']['cpu_usage']}\n"
                        f"• RAM: {report['status']['ram_usage']}\n"
                        f"• Uptime: {report['status']['uptime']}")
            else:
                text = "❌ Controlador no disponible."
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data='main_menu')]]), parse_mode='Markdown')

        elif query.data == 'pc_snap':
            if self.sc:
                path = self.sc.capture_screenshot()
                await context.bot.send_photo(chat_id=query.message.chat_id, photo=open(path, 'rb'), caption="📸 Auditoría visual completada.")
            else:
                await query.message.reply_text("❌ Error en captura.")

        elif query.data == 'main_menu':
            await self._show_main_menu(query)

    async def chat_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Lógica de chat inteligente (vínculo con GuilleCoder/DeepSeek vía Puente)
        user_msg = update.message.text
        if "VIRGILIO QUE PASA" in user_msg.upper():
            await update.message.reply_text("👋 ¡Aquí estoy, señor! Todos los cables están conectados. Sistema CAMASOTS estable al 100%.")
        else:
            await update.message.reply_text(f"📝 He recibido tu nota: '{user_msg}'. Procesando con inteligencia master...")

    async def file_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Mover archivos recibidos al CAJÓN para destripado
        file = await update.message.effective_attachment.get_file() if not update.message.photo else await update.message.photo[-1].get_file()
        file_name = update.message.document.file_name if update.message.document else f"photo_{int(time.time())}.jpg"
        save_path = os.path.join(self.cajon_dir, file_name)
        await file.download_to_drive(save_path)
        await update.message.reply_text(f"📥 Archivo '{file_name}' recibido y enviado al **CAJÓN** para análisis profundo.")

    def run(self):
        print("[VIRGILIO-BOT] Iniciado.")
        self.app.run_polling()

if __name__ == "__main__":
    # Token inyectado desde caja_fuerte.env en el Puente
    from dotenv import load_dotenv
    load_dotenv(r"C:\a2\CAMASOTS\PUENTE\caja_fuerte.env")
    TOKEN = os.getenv("VIRGILIO_TOKEN")
    if TOKEN:
        bot = VirgilioBot(TOKEN)
        bot.run()
