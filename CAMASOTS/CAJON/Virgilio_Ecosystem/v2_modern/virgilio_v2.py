import webview
import sys
import os
import json
import threading
from datetime import datetime

# Añadir Shared_Core al path
sys.path.append(r"C:\a2\Shared_Core")
try:
    from controller import SystemController
    from telegram_bot import TelegramMaster
except ImportError:
    print("Error: No se pudo cargar Shared_Core modules.")
    sys.exit(1)

# ====================================================================
# VIRGILIO v2 MODERN - ADVANCED DASHBOARD & TELEGRAM-FIRST
# INTEGRACIÓN TOTAL CON REDES SOCIALES, CRÉDITOS Y CONTROL REMOTO
# ====================================================================

class VirgilioModern:
    def __init__(self):
        self.sc = SystemController()
        self.tg = None # Se inicializa si hay token
        self.version = "2.0.0-Modern"
        self._window = None

    def get_status(self):
        report = self.sc.get_full_system_report()
        screen = self.sc.get_screen_info()
        return {
            "os": report['os']['name'],
            "cpu": report['status']['cpu_usage'],
            "ram": report['status']['ram_usage'],
            "active_window": screen.get('active_window', 'N/D'),
            "time": datetime.now().strftime("%H:%M:%S"),
            "is_admin": self.sc.is_admin()
        }

    def start_telegram(self, token):
        if not self.tg:
            self.tg = TelegramMaster(token)
            threading.Thread(target=self.tg.run, daemon=True).start()
            return "✅ Bot de Telegram iniciado."
        return "⚠️ Bot ya en ejecución."

    def capture_and_show(self):
        path = self.sc.capture_screenshot()
        return f"📸 Captura guardada en: {path}"

def run_gui():
    vm = VirgilioModern()
    
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>VIRGILIO v2.0 MODERN</title>
        <style>
            :root { --bg: #0d1117; --card: #161b22; --accent: #58a6ff; --text: #c9d1d9; --border: #30363d; }
            body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 30px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .card { background: var(--card); border: 1px solid var(--border); padding: 25px; border-radius: 12px; }
            .card h3 { margin: 0 0 15px 0; color: var(--accent); font-size: 0.9rem; text-transform: uppercase; }
            .value { font-size: 1.8rem; font-weight: bold; }
            .btn { background: #238636; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 15px; width: 100%; }
            .btn:hover { background: #2ea043; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
            .status-badge { background: #238636; padding: 4px 10px; border-radius: 20px; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>VIRGILIO v2.0 <span class="status-badge">ONLINE</span></h1>
            <div id="clock">00:00:00</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>CPU USAGE</h3>
                <div class="value" id="cpu">0%</div>
            </div>
            <div class="card">
                <h3>RAM USAGE</h3>
                <div class="value" id="ram">0%</div>
            </div>
            <div class="card">
                <h3>SISTEMA OPERATIVO</h3>
                <div class="value" id="os">Windows</div>
            </div>
            <div class="card">
                <h3>SÚPER-USUARIO</h3>
                <div class="value" id="admin">SÍ</div>
            </div>
        </div>

        <div class="grid" style="margin-top: 30px;">
            <div class="card">
                <h3>CONTROL DE TELEGRAM</h3>
                <input type="password" id="tgToken" placeholder="Token del Bot..." style="width:100%; background:#0d1117; border:1px solid var(--border); color:white; padding:8px; margin-top:10px;">
                <button class="btn" onclick="startTG()">ACTIVAR BOT</button>
            </div>
            <div class="card">
                <h3>AUDITORÍA RÁPIDA</h3>
                <button class="btn" style="background:#1f6feb" onclick="capture()">CAPTURAR PANTALLA</button>
            </div>
        </div>

        <script>
            async function update() {
                const status = await pywebview.api.get_status();
                document.getElementById('cpu').innerText = status.cpu;
                document.getElementById('ram').innerText = status.ram;
                document.getElementById('os').innerText = status.os;
                document.getElementById('admin').innerText = status.is_admin ? 'SÍ' : 'NO';
                document.getElementById('clock').innerText = status.time;
            }

            async function startTG() {
                const token = document.getElementById('tgToken').value;
                const res = await pywebview.api.start_telegram(token);
                alert(res);
            }

            async function capture() {
                const res = await pywebview.api.capture_and_show();
                alert(res);
            }

            setInterval(update, 1000);
            update();
        </script>
    </body>
    </html>
    """
    
    window = webview.create_window('VIRGILIO v2.0 MODERN', html=html, js_api=vm, width=1100, height=800)
    webview.start(debug=True)

if __name__ == "__main__":
    run_gui()
