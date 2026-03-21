import os
import sys
import json
import time
import logging
import psutil
import subprocess
import threading
import webview
from datetime import datetime
from queue import Queue, Empty

# ====================================================================
# CAMASOTS COMMANDER CENTER v4.1 - SUPREME DEBUGGED EDITION
# Interfaz Gráfica Corregida - Captura de Consola en Tiempo Real
# Garantía de Ejecución de GuilleCoder x2
# ====================================================================

class CommanderCenter:
    def __init__(self):
        self.root_dir = r"C:\a2\CAMASOTS"
        self.puente_dir = os.path.join(self.root_dir, "PUENTE")
        self.env_path = os.path.join(self.puente_dir, "caja_fuerte.env")
        self.db_master = os.path.join(self.root_dir, "DATABASE", "MASTER", "master_db.json")
        self.venv_py = os.path.join(self.root_dir, "venv", "Scripts", "python.exe")
        
        self.output_queues = {
            "guillecoder": Queue(),
            "virgilio": Queue(),
            "athenea": Queue(),
            "telegram": Queue()
        }
        self.processes = {}
        
        # Logging interno para depurar la propia interfaz
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("CommanderUI")

    def get_config(self):
        """Carga toda la configuración y métricas para el frontend."""
        apis = {}
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.split('=', 1)
                        apis[k.strip()] = v.strip()
        
        metrics = {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('C:').percent,
            "uptime": datetime.now().strftime("%H:%M:%S")
        }
        
        # Verificar si los procesos están realmente vivos
        process_status = {}
        for name, proc in self.processes.items():
            process_status[name] = proc.poll() is None
            
        return {"apis": apis, "metrics": metrics, "status": "ONLINE", "process_status": process_status}

    def update_api(self, key, value):
        """Actualiza una API Key en la caja fuerte."""
        lines = []
        updated = False
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            new_lines.append(f"{key}={value}\n")
            
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return f"API {key} inyectada con éxito."

    def launch_agent(self, name):
        """Lanza un agente con captura forzada de STDOUT y STDERR."""
        script_map = {
            "guillecoder": os.path.join(self.root_dir, "GUILLECODER", "guille_engine.py"),
            "virgilio": os.path.join(self.root_dir, "VIRGILIO", "virgilio_v3.py"),
            "athenea": os.path.join(self.root_dir, "ATHENEA", "athenea_engine.py"),
            "telegram": os.path.join(self.root_dir, "PUENTE", "telegram_bot.py")
        }
        
        if name in script_map:
            # Si ya existe y está vivo, no relanzar
            if name in self.processes and self.processes[name].poll() is None:
                return f"Agente {name.upper()} ya está activo."
                
            path = script_map[name]
            # Usamos PYTHONUNBUFFERED=1 para asegurar que los logs salgan al instante
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            
            try:
                proc = subprocess.Popen(
                    [self.venv_py, "-u", path], # -u para modo unbuffered
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW # Evitar ventanas negras externas
                )
                self.processes[name] = proc
                
                # Hilo de lectura dedicado para esta cola
                def reader(p, q):
                    self.logger.info(f"Iniciando lector para {name}")
                    try:
                        while True:
                            line = p.stdout.readline()
                            if not line:
                                break
                            # Limpiar y enviar a la cola
                            clean_line = line.strip() + "\n"
                            q.put(clean_line)
                            # También loguear internamente para depuración
                            self.logger.info(f"[{name}] {clean_line.strip()}")
                    except Exception as e:
                        self.logger.error(f"Error en lector de {name}: {e}")
                    finally:
                        p.stdout.close()
                        self.logger.info(f"Lector de {name} finalizado")
                
                t = threading.Thread(target=reader, args=(proc, self.output_queues[name]), daemon=True)
                t.start()
                
                return f"🛰️ {name.upper()} Lanzado correctamente."
            except Exception as e:
                return f"❌ Error lanzando {name}: {str(e)}"
        return "Agente no reconocido."

    def get_logs(self, name):
        """Devuelve los logs acumulados para la UI de forma segura."""
        logs = []
        if name in self.output_queues:
            try:
                # Sacar todo lo que haya en la cola en este momento
                while True:
                    logs.append(self.output_queues[name].get_nowait())
            except Empty:
                pass
        return logs

def start_ui():
    center = CommanderCenter()
    
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            :root { 
                --bg: #0d1117; --sidebar: #161b22; --card: #21262d; 
                --accent: #58a6ff; --text: #c9d1d9; --subtext: #8b949e;
                --border: #30363d; --success: #3fb950; --error: #f85149;
                --console-bg: #010409;
            }
            body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; height: 100vh; overflow: hidden; }
            
            .sidebar { width: 260px; background: var(--sidebar); border-right: 1px solid var(--border); display: flex; flex-direction: column; padding: 20px; flex-shrink: 0; }
            .logo { font-size: 20px; font-weight: bold; color: var(--accent); letter-spacing: 2px; margin-bottom: 30px; border-bottom: 1px solid var(--border); padding-bottom: 15px; }
            .nav-item { padding: 12px 15px; border-radius: 6px; cursor: pointer; transition: 0.2s; margin-bottom: 5px; font-size: 14px; color: var(--subtext); display: flex; align-items: center; gap: 10px; }
            .nav-item:hover { background: #30363d; color: var(--text); }
            .nav-item.active { background: #1f6feb; color: white; }

            .main { flex-grow: 1; padding: 30px; overflow-y: auto; display: flex; flex-direction: column; min-width: 0; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
            .header h1 { margin: 0; font-size: 24px; font-weight: 600; }
            
            .metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }
            .metric-card { background: var(--card); padding: 15px; border-radius: 8px; border: 1px solid var(--border); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .m-label { font-size: 11px; color: var(--subtext); text-transform: uppercase; letter-spacing: 1px; }
            .m-value { font-size: 18px; font-weight: 600; color: var(--accent); margin-top: 5px; }

            .content-grid { display: grid; grid-template-columns: 380px 1fr; gap: 20px; flex-grow: 1; min-height: 0; }
            
            .config-panel { background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 20px; display: flex; flex-direction: column; overflow-y: auto; }
            .config-group { margin-bottom: 15px; }
            .config-group label { display: block; font-size: 11px; color: var(--subtext); margin-bottom: 5px; font-weight: bold; }
            .config-input { width: 100%; background: var(--console-bg); border: 1px solid var(--border); color: #7ee787; padding: 10px; border-radius: 6px; box-sizing: border-box; font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12px; }
            .btn-save { background: var(--success); color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; margin-top: 10px; transition: 0.2s; }
            .btn-save:hover { filter: brightness(1.1); }

            .console-area { display: flex; flex-direction: column; gap: 15px; min-height: 0; }
            .console-box { background: var(--console-bg); border: 1px solid var(--border); border-radius: 8px; display: flex; flex-direction: column; height: 350px; overflow: hidden; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); }
            .console-head { background: #161b22; padding: 8px 15px; font-size: 11px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
            .console-body { flex-grow: 1; padding: 12px; font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12px; color: #3fb950; overflow-y: auto; white-space: pre-wrap; line-height: 1.4; }
            
            .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 5px; }
            .status-online { background: var(--success); box-shadow: 0 0 8px var(--success); }
            .status-offline { background: var(--error); }

            .agent-controls { margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
            .btn-launch { background: #30363d; color: var(--text); border: 1px solid var(--border); padding: 10px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: 600; text-transform: uppercase; }
            .btn-launch:hover { border-color: var(--accent); background: #3d444d; }
            
            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
            ::-webkit-scrollbar-thumb:hover { background: #484f58; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="logo">🛰️ CAMASOTS SUPREME</div>
            <div class="nav-item active">Dashboard</div>
            <div class="nav-item">Agentes Élite</div>
            <div class="nav-item">Caja Fuerte</div>
            <div class="nav-item">Laboratorio IA</div>
            <div class="nav-item" style="margin-top: auto;">Logs Maestro</div>
        </div>

        <div class="main">
            <div class="header">
                <h1>Command Center <span style="color: var(--subtext); font-weight: 300; font-size: 16px;">v4.1 PRO</span></h1>
                <div id="sys-status" style="color: var(--success); font-size: 12px; font-weight: bold;">● SISTEMA SINCRONIZADO</div>
            </div>

            <div class="metrics">
                <div class="metric-card"><div class="m-label">CPU LOAD</div><div class="m-value" id="cpu">0%</div></div>
                <div class="metric-card"><div class="m-label">RAM USAGE</div><div class="m-value" id="ram">0%</div></div>
                <div class="metric-card"><div class="m-label">SYSTEM ROOT</div><div class="m-value" id="root-status" style="color: #3fb950;">ACTIVE</div></div>
                <div class="metric-card"><div class="m-label">SESSION UPTIME</div><div class="m-value" id="uptime">00:00:00</div></div>
            </div>

            <div class="content-grid">
                <div class="config-panel">
                    <h3 style="margin-top:0; font-size: 16px; border-bottom: 1px solid var(--border); padding-bottom: 10px;">Configurador de APIs</h3>
                    <div id="api-list">
                        <!-- Cargado dinámicamente -->
                    </div>
                    <button class="btn-save" onclick="saveAllAPIs()">ACTUALIZAR CAJA FUERTE</button>
                    
                    <h3 style="margin-top:25px; font-size: 14px; color: var(--subtext);">Lanzador de Agentes</h3>
                    <div class="agent-controls">
                        <button class="btn-launch" onclick="launch('guillecoder')">GUILLE x2</button>
                        <button class="btn-launch" onclick="launch('telegram')">TG BRIDGE</button>
                        <button class="btn-launch" onclick="launch('virgilio')">VIRGILIO</button>
                        <button class="btn-launch" onclick="launch('athenea')">ATHENEA</button>
                    </div>
                </div>

                <div class="console-area">
                    <div class="console-box">
                        <div class="console-head">
                            <span><span class="status-dot" id="dot-guillecoder"></span> GUILLECODER x2 CORE</span>
                            <span style="color: var(--accent); font-weight: bold;">MASTER ENGINE</span>
                        </div>
                        <div class="console-body" id="log-guillecoder"></div>
                    </div>
                    <div class="console-box">
                        <div class="console-head">
                            <span><span class="status-dot" id="dot-telegram"></span> TELEGRAM SUPREME BRIDGE</span>
                            <span style="color: var(--success); font-weight: bold;">SYNC ACTIVE</span>
                        </div>
                        <div class="console-body" id="log-telegram"></div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let firstLoad = true;

            async function update() {
                const data = await pywebview.api.get_config();
                
                // Actualizar Métricas
                document.getElementById('cpu').innerText = data.metrics.cpu + "%";
                document.getElementById('ram').innerText = data.metrics.ram + "%";
                document.getElementById('uptime').innerText = data.metrics.uptime;
                
                // Actualizar Dots de Estado
                const agents = ['guillecoder', 'telegram', 'virgilio', 'athenea'];
                agents.forEach(a => {
                    const dot = document.getElementById('dot-' + a);
                    if (dot) {
                        dot.className = 'status-dot ' + (data.process_status[a] ? 'status-online' : 'status-offline');
                    }
                });

                // Cargar APIs solo la primera vez
                const apiList = document.getElementById('api-list');
                if (firstLoad) {
                    apiList.innerHTML = "";
                    for (const [key, val] of Object.entries(data.apis)) {
                        apiList.innerHTML += `
                            <div class="config-group">
                                <label>${key}</label>
                                <input type="text" class="config-input" id="api-${key}" value="${val}">
                            </div>
                        `;
                    }
                    firstLoad = false;
                }

                // Capturar Logs en tiempo real
                for (const a of agents) {
                    const logs = await pywebview.api.get_logs(a);
                    if (logs && logs.length > 0) {
                        const box = document.getElementById('log-' + a);
                        if (box) {
                            box.innerText += logs.join('');
                            box.scrollTop = box.scrollHeight;
                        }
                    }
                }
            }

            function launch(name) {
                const box = document.getElementById('log-' + name);
                if(box) box.innerText += `\\n[SISTEMA] Solicitando arranque de ${name.upper()}...\\n`;
                pywebview.api.launch_agent(name).then(res => {
                    if(box) box.innerText += `[SISTEMA] ${res}\\n`;
                });
            }

            async function saveAllAPIs() {
                const inputs = document.querySelectorAll('.config-input');
                let count = 0;
                for (const input of inputs) {
                    const key = input.id.replace('api-', '');
                    const val = input.value;
                    await pywebview.api.update_api(key, val);
                    count++;
                }
                alert(`Éxito: ${count} credenciales actualizadas en la Caja Fuerte.`);
            }

            // Intervalo de actualización rápido para logs
            setInterval(update, 800);
        </script>
    </body>
    </html>
    """
    
    # Iniciar ventana principal
    window = webview.create_window(
        'CAMASOTS COMMANDER CENTER v4.1 PRO', 
        html=html, 
        js_api=center, 
        width=1450, 
        height=980, 
        background_color='#0d1117'
    )
    webview.start(debug=True)

if __name__ == "__main__":
    start_ui()
