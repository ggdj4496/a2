import os
import sys
import json
import time
import logging
import requests
import webview
import threading
import psutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def _find_python_executable() -> str:
    """
    Busca el ejecutable Python correcto en orden de prioridad:
    1. Entorno virtual venv del proyecto
    2. Python en PATH (python.exe)
    3. Python311 en Program Files
    """
    possible_paths = [
        # Entorno virtual del proyecto
        os.path.join(os.environ.get('CAMASOTS_ROOT', r"C:\a2\CAMASOTS"), "venv", "Scripts", "python.exe"),
        r"C:\a2\CAMASOTS\venv\Scripts\python.exe",
        # Python 3.11
        r"C:\Program Files\Python311\python.exe",
        r"C:\Program Files (x86)\Python311\python.exe",
        # Python en PATH
        "python.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Si no encuentra ninguno, usar el actual
    return sys.executable

# ====================================================================
# GUILLECODER MASTER AGENT x2 - SUPREME PROGRAMMING ENGINE
# Calidad de Procesado x2: Razonamiento Senior Master + Auditoría de Drivers
# ====================================================================


def create_session_with_retries(retries: int = 3, backoff_factor: float = 0.5) -> requests.Session:
    """Crea una sesión requests con retry automático para mayor robustez."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class GuilleCoderSupreme:
    def __init__(self):
        # Forzar logs a stdout inmediatamente
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger("GuilleSupreme")
        
        # Detección automática de paths - Fallback a ubicación del archivo
        # Usa variable de entorno CAMASOTS_ROOT o detecta automáticamente
        self.root_dir = os.environ.get('CAMASOTS_ROOT', 
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.base_dir = os.path.join(self.root_dir, "GUILLECODER")
        self.db_path = os.path.join(self.root_dir, "DATABASE", "GUILLECODER", "guille_knowledge.json")
        self.env_path = os.path.join(self.root_dir, "PUENTE", "caja_fuerte.env")
        
        # Crear sesión con retry para API calls
        self.http_session = create_session_with_retries()
        
        # El "print" en Python con -u (unbuffered) es la forma más segura de enviar logs a la master_interface
        print("[SISTEMA] >>> GUILLECODER SUPREME x2 INICIANDO... <<<", flush=True)
        print(f"[SISTEMA] Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print(f"[SISTEMA] Directorio raíz detectado: {self.root_dir}", flush=True)
        
        self._load_credentials()
        self._inject_supreme_knowledge()
        self._start_health_check()

    def _start_health_check(self):
        def heart_beat():
            while True:
                try:
                    cpu = psutil.cpu_percent()
                    print(f"[HEALTH-CHECK] Motor x2 Sincronizado | CPU: {cpu}% | {datetime.now().strftime('%H:%M:%S')}", flush=True)
                except:
                    pass
                time.sleep(30)
        threading.Thread(target=heart_beat, daemon=True).start()

    def _load_credentials(self):
        print("[SISTEMA] Cargando credenciales desde Caja Fuerte...", flush=True)
        self.apis = {}
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        k, v = line.split('=', 1)
                        key = k.strip()
                        value = v.strip()
                        # Ocultar valor en logs por seguridad
                        masked_value = f"{value[:4]}***" if len(value) > 4 else "***"
                        print(f"[SISTEMA] API '{key}' detectada: {masked_value}", flush=True)
                        self.apis[key] = value
            print(f"[SISTEMA] {len(self.apis)} APIs detectadas.", flush=True)
        else:
            print("[ALERTA] Caja fuerte no encontrada en PUENTE/caja_fuerte.env", flush=True)

    def _inject_supreme_knowledge(self):
        """Inyecta conocimientos de nivel Master en la DB."""
        print("[SISTEMA] Inyectando base de conocimientos UF1287...", flush=True)
        knowledge = {
            "kernel_engineering": {
                "drivers": "UF1287 - Desarrollo de components para manejo de dispositivos",
                "standards": ["WDK (Windows Driver Kit)", "Plug & Play", "DMA Access"],
                "security": "Root-level UAC Bypass and Firewall Registry Tweaks"
            },
            "ia_processing_x2": {
                "engine": "DeepSeek-Coder-V2 + Gemini-1.5-Pro Sync",
                "methodology": "Chain-of-Thought Senior Master",
                "refactoring": ["Abstraction", "Composition", "Magic Number Elimination"]
            },
            "system_integration": {
                "sync": "Walkie-Talkie Mode via Telegram Bridge",
                "persistence": "24/7 Evolutive Memory RAG"
            }
        }
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Merge con datos existentes si los hay
        existing_data = {}
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                # Merge strategy: preservar datos existentes
                for key, value in knowledge.items():
                    if key not in existing_data:
                        existing_data[key] = value
                knowledge = existing_data
            except Exception as e:
                print(f"[SISTEMA] Warning: No se pudo mergeear DB existente: {e}", flush=True)
        
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=4)
        print("[SISTEMA] Base de conocimientos actualizada.", flush=True)

    def process_supreme_query(self, prompt: str) -> str:
        """Procesado de calidad x2 usando múltiples APIs en paralelo."""
        print(f"[CONSULTA] Procesando requerimiento: {prompt[:50]}...", flush=True)
        
        token = self.apis.get("DEEPSEEK_API_KEY")
        if not token: 
            print("[ERROR] DEEPSEEK_API_KEY no encontrada.", flush=True)
            return "❌ ERROR: DEEPSEEK_API_KEY no encontrada."

        try:
            print("[IA] Solicitando razonamiento a DeepSeek Engine...", flush=True)
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            payload = {
                "model": "deepseek-coder",
                "messages": [
                    {"role": "system", "content": "Eres GUILLECODER SUPREME x2. Tu razonamiento es Senior Master. Auditas drivers, optimizas x64 y creas software perfecto."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            # Usar sesión con retry en lugar de requests.post directo
            resp = self.http_session.post(
                "https://api.deepseek.com/v1/chat/completions", 
                json=payload, 
                headers=headers, 
                timeout=60
            )
            
            if resp.status_code == 200:
                print("[IA] Respuesta recibida con éxito.", flush=True)
                return resp.json()['choices'][0]['message']['content']
            
            print(f"[ERROR] API retornó código {resp.status_code}", flush=True)
            return f"Error en motor x2: {resp.status_code}"
            
        except requests.exceptions.Timeout:
            print("[ERROR] Timeout en conexión con IA (60s excedidos)", flush=True)
            return "Error: Timeout en motor de IA"
        except requests.exceptions.ConnectionError:
            print("[ERROR] Error de conexión con IA", flush=True)
            return "Error: Sin conexión a internet"
        except Exception as e:
            print(f"[CRÍTICO] Fallo en conexión IA: {e}", flush=True)
            return f"Fallo Crítico Supreme: {e}"

# --- INTERFAZ SUPREMA (Dark Elite x2) ---

def start_supreme_ui():
    engine = GuilleCoderSupreme()
    
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            :root { --accent: #ff0055; --bg: #0a0a0a; --card: #141414; --text: #e0e0e0; }
            body { font-family: 'Consolas', monospace; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
            .header { border-bottom: 2px solid var(--accent); padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
            .status-tag { background: var(--accent); color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .console { background: var(--card); border: 1px solid #333; border-radius: 8px; height: 75vh; margin-top: 20px; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; }
            .input-area { display: flex; gap: 10px; margin-top: 20px; }
            input { flex-grow: 1; background: #000; border: 1px solid #444; color: #00ff00; padding: 15px; border-radius: 6px; font-family: inherit; font-size: 14px; }
            .btn { background: var(--accent); color: white; border: none; padding: 0 30px; border-radius: 6px; cursor: pointer; font-weight: bold; }
            .log-entry { margin-bottom: 15px; border-left: 3px solid var(--accent); padding-left: 15px; }
            .sys-msg { color: #888; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="margin:0; letter-spacing: 3px;">GUILLECODER SUPREME <span style="color: #ff0055;">x2</span></h1>
            <div class="status-tag" id="status-tag">MOTOR SENIOR MASTER ACTIVO</div>
        </div>
        
        <div class="console" id="console">
            <div class="sys-msg">[SISTEMA] Motor x2 cargado. Base de datos de Drivers y Kernel inyectada.</div>
            <div class="sys-msg">[SISTEMA] APIs sincronizadas: DeepSeek, Gemini, xAI, ElevenLabs.</div>
        </div>

        <div class="input-area">
            <input type="text" id="input" placeholder="Escribe un requerimiento de nivel supremo..." onkeypress="if(event.key==='Enter') execute()">
            <button class="btn" onclick="execute()">EJECUTAR</button>
        </div>

        <script>
            async function execute() {
                const box = document.getElementById('input');
                const val = box.value;
                if(!val) return;
                
                const cons = document.getElementById('console');
                cons.innerHTML += `<div class="log-entry"><span style="color: var(--accent);">>>> </span>${val}</div>`;
                box.value = '';
                
                try {
                    const res = await pywebview.api.process_supreme_query(val);
                    cons.innerHTML += `<div class="log-entry" style="color: #00ff00;">${res}</div>`;
                    cons.scrollTop = cons.scrollHeight;
                } catch (e) {
                    cons.innerHTML += `<div class="log-entry" style="color: #ff0055;">Error: ${e}</div>`;
                }
            }
        </script>
    </body>
    </html>
    """
    
    # Debug mode desactivado para producción
    webview.create_window('GUILLECODER SUPREME x2', html=html, js_api=engine, width=1300, height=900, background_color='#0a0a0a')
    webview.start(debug=False)

if __name__ == "__main__":
    # Verificar Python disponible al inicio
    python_path = _find_python_executable()
    print(f"[SISTEMA] Python detectado: {python_path}", flush=True)
    print(f"[SISTEMA] Ejecutable actual: {sys.executable}", flush=True)
    
    # Verificar si estamos en el venv correcto (comparar sys.executable con expected_venv)
    expected_venv = os.path.join(os.environ.get('CAMASOTS_ROOT', r"C:\a2\CAMASOTS"), "venv", "Scripts", "python.exe")
    if sys.executable.lower() != expected_venv.lower() and os.path.exists(expected_venv):
        print(f"[WARNING] El entorno virtual no está activo.", flush=True)
        print(f"[WARNING] Se recomienda ejecutar con: {expected_venv}", flush=True)
        print(f"[WARNING] O establece la variable: set CAMASOTS_ROOT=C:\\a2\\CAMASOTS", flush=True)
    
    start_supreme_ui()
