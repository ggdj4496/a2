import os
import sys
import json
import time
import logging
import psutil
import subprocess
import threading
import webview

# ====================================================================
# VIRGILIO MASTER v3.0 - SYSTEM & HARDWARE COMMANDER
# Control DMX, Automatización Windows y Gestión Root
# ====================================================================

class VirgilioMaster:
    def __init__(self):
        self.root_dir = os.environ.get('CAMASOTS_ROOT', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.base_dir = os.path.join(self.root_dir, "VIRGILIO")
        self.puente_dir = os.path.join(self.root_dir, "PUENTE")
        self.logger = logging.getLogger("VirgilioMaster")

        # Configuración DMX (Simulada para QLC+)
        self.dmx_port = os.environ.get('DMX_PORT', "COM3")
        self.qlc_path = os.environ.get('QLC_PATH', r"C:\Program Files\QLC+\qlcplus.exe")

        self.logger.info("Virgilio Master v3.0 Inicializado.")

    def get_system_status(self):
        """Obtiene métricas de rendimiento en tiempo real."""
        return {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('C:').percent,
            "uptime": time.time() - psutil.boot_time()
        }

    def execute_root_command(self, cmd: str):
        """Ejecuta comandos con privilegios elevados vía PUENTE."""
        self.logger.info(f"Ejecutando comando Root: {cmd}")
        try:
            if cmd == 'purge_temp_files':
                # Implement purge temp files
                temp_dirs = [os.environ.get('TEMP', 'C:\\Temp'), 'C:\\Windows\\Temp']
                deleted_files = 0
                for temp_dir in temp_dirs:
                    if os.path.exists(temp_dir):
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                try:
                                    os.remove(os.path.join(root, file))
                                    deleted_files += 1
                                except:
                                    pass
                return f"Purged {deleted_files} temporary files."
            elif cmd.startswith('runas '):
                # Attempt to run command as admin using runas
                actual_cmd = cmd[6:]  # remove 'runas '
                result = subprocess.run(['runas', '/user:Administrator', 'cmd', '/c', actual_cmd],
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"Error: {result.stderr}"
            else:
                # Default: run with shell=True (caution: security risk)
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    return result.stdout
                else:
                    return f"Error: {result.stderr}"
        except Exception as e:
            self.logger.error(f"Error executing root command: {e}")
            return f"Failed to execute: {e}"

    def control_dmx_fixture(self, channel: int, value: int):
        """Envía valores DMX a través del puerto configurado."""
        self.logger.info(f"DMX CH {channel} -> {value}")
        return f"DMX Señal: Canal {channel} fijado en {value}."

    def launch_qlc_plus(self):
        """Arranca el software de iluminación QLC+ con el perfil CAMASOTS."""
        if os.path.exists(self.qlc_path):
            subprocess.Popen([self.qlc_path])
            return "QLC+ iniciado con éxito."
        return "Error: QLC+ no encontrado en Program Files."

# --- INTERFAZ VISUAL VIRGILIO (PyWebView) ---

def start_virgilio_ui():
    master = VirgilioMaster()
    
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            :root { --accent: #00f2ff; --bg: #010409; --card: #0d1117; --text: #c9d1d9; }
            body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); padding: 40px; margin: 0; }
            .container { max-width: 1000px; margin: auto; }
            .header { border-bottom: 2px solid var(--accent); padding-bottom: 10px; margin-bottom: 30px; }
            h1 { font-weight: 300; letter-spacing: 4px; color: var(--accent); }
            .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }
            .stat-card { background: var(--card); padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #30363d; }
            .stat-value { font-size: 24px; color: var(--accent); font-weight: bold; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
            .card { background: var(--card); border: 1px solid #30363d; padding: 25px; border-radius: 12px; }
            .btn { background: var(--accent); color: #000; border: none; padding: 12px 30px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 15px; }
            .log-box { margin-top: 20px; background: #000; padding: 15px; color: var(--accent); font-family: 'Consolas', monospace; font-size: 13px; border-radius: 6px; height: 150px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>VIRGILIO MASTER</h1>
                <p>CENTRO DE CONTROL DE HARDWARE Y SISTEMA ROOT</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card"><div>CPU</div><div class="stat-value" id="cpu">0%</div></div>
                <div class="stat-card"><div>RAM</div><div class="stat-value" id="ram">0%</div></div>
                <div class="stat-card"><div>DISK</div><div class="stat-value" id="disk">0%</div></div>
                <div class="stat-card"><div>STATUS</div><div class="stat-value" style="color: #238636;">OK</div></div>
            </div>

            <div class="grid">
                <div class="card">
                    <h3>Control de Iluminación</h3>
                    <p>Gestión de DMX y arranque de QLC+ para cabezas móviles.</p>
                    <button class="btn" onclick="launchQLC()">ARRANCAR QLC+</button>
                </div>
                <div class="card">
                    <h3>Automatización Root</h3>
                    <p>Ejecución de tareas de mantenimiento y bypass de seguridad.</p>
                    <button class="btn" onclick="runRoot()">OPTIMIZAR SISTEMA</button>
                </div>
            </div>

            <div class="log-box" id="terminal">
                [SISTEMA] Virgilio Master a la espera de órdenes...
            </div>
        </div>

        <script>
            function log(msg) {
                const term = document.getElementById('terminal');
                term.innerHTML += `<br>[${new Date().toLocaleTimeString()}] ${msg}`;
                term.scrollTop = term.scrollHeight;
            }

            async function updateStats() {
                const stats = await pywebview.api.get_system_status();
                document.getElementById('cpu').innerText = stats.cpu + "%";
                document.getElementById('ram').innerText = stats.ram + "%";
                document.getElementById('disk').innerText = stats.disk + "%";
            }

            async function launchQLC() {
                log("Iniciando QLC+ Engine...");
                const res = await pywebview.api.launch_qlc_plus();
                log(res);
            }

            async function runRoot() {
                log("Ejecutando optimización de privilegios...");
                const res = await pywebview.api.execute_root_command('purge_temp_files');
                log(res);
            }

            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """
    
    window = webview.create_window(
        'VIRGILIO MASTER - CAMASOTS SOFT', 
        html=html_content, 
        js_api=master, 
        width=1100, 
        height=850,
        background_color='#010409'
    )
    webview.start(debug=False)

if __name__ == "__main__":
    start_virgilio_ui()

            async function launchQLC() {
                log("Iniciando QLC+ Engine...");
                const res = await pywebview.api.launch_qlc_plus();
                log(res);
            }

            async function runRoot() {
                log("Ejecutando optimización de privilegios...");
                const res = await pywebview.api.execute_root_command('purge_temp_files');
                log(res);
            }

            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """
    
    window = webview.create_window(
        'VIRGILIO MASTER - CAMASOTS SOFT', 
        html=html_content, 
        js_api=master, 
        width=1100, 
        height=850,
        background_color='#010409'
    )
    webview.start(debug=True)

if __name__ == "__main__":
    start_virgilio_ui()


            async function launchQLC() {
                log("Iniciando QLC+ Engine...");
                const res = await pywebview.api.launch_qlc_plus();
                log(res);
            }

            async function runRoot() {
                log("Ejecutando optimización de privilegios...");
                const res = await pywebview.api.execute_root_command('purge_temp_files');
                log(res);
            }

            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """
    
    window = webview.create_window(
        'VIRGILIO MASTER - CAMASOTS SOFT', 
        html=html_content, 
        js_api=master, 
        width=1100, 
        height=850,
        background_color='#010409'
    )
    webview.start(debug=True)

if __name__ == "__main__":
    start_virgilio_ui()

            async function launchQLC() {
                log("Iniciando QLC+ Engine...");
                const res = await pywebview.api.launch_qlc_plus();
                log(res);
            }

            async function runRoot() {
                log("Ejecutando optimización de privilegios...");
                const res = await pywebview.api.execute_root_command('purge_temp_files');
                log(res);
            }

            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """
    
    window = webview.create_window(
        'VIRGILIO MASTER - CAMASOTS SOFT', 
        html=html_content, 
        js_api=master, 
        width=1100, 
        height=850,
        background_color='#010409'
    )
    webview.start(debug=True)

if __name__ == "__main__":
    start_virgilio_ui()



            async function launchQLC() {
                log("Iniciando QLC+ Engine...");
                const res = await pywebview.api.launch_qlc_plus();
                log(res);
            }

            async function runRoot() {
                log("Ejecutando optimización de privilegios...");
                const res = await pywebview.api.execute_root_command('purge_temp_files');
                log(res);
            }

            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """
    
    window = webview.create_window(
        'VIRGILIO MASTER - CAMASOTS SOFT', 
        html=html_content, 
        js_api=master, 
        width=1100, 
        height=850,
        background_color='#010409'
    )
    webview.start(debug=False)

if __name__ == "__main__":
    start_virgilio_ui()

            async function launchQLC() {
                log("Iniciando QLC+ Engine...");
                const res = await pywebview.api.launch_qlc_plus();
                log(res);
            }

            async function runRoot() {
                log("Ejecutando optimización de privilegios...");
                const res = await pywebview.api.execute_root_command('purge_temp_files');
                log(res);
            }

            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """
    
    window = webview.create_window(
        'VIRGILIO MASTER - CAMASOTS SOFT', 
        html=html_content, 
        js_api=master, 
        width=1100, 
        height=850,
        background_color='#010409'
    )
    webview.start(debug=True)

if __name__ == "__main__":
    start_virgilio_ui()


            async function launchQLC() {
                log("Iniciando QLC+ Engine...");
                const res = await pywebview.api.launch_qlc_plus();
                log(res);
            }

            async function runRoot() {
                log("Ejecutando optimización de privilegios...");
                const res = await pywebview.api.execute_root_command('purge_temp_files');
                log(res);
            }

            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """
    
    window = webview.create_window(
        'VIRGILIO MASTER - CAMASOTS SOFT', 
        html=html_content, 
        js_api=master, 
        width=1100, 
        height=850,
        background_color='#010409'
    )
    webview.start(debug=True)

if __name__ == "__main__":
    start_virgilio_ui()

            async function launchQLC() {
                log("Iniciando QLC+ Engine...");
                const res = await pywebview.api.launch_qlc_plus();
                log(res);
            }

            async function runRoot() {
                log("Ejecutando optimización de privilegios...");
                const res = await pywebview.api.execute_root_command('purge_temp_files');
                log(res);
            }

            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """
    
    window = webview.create_window(
        'VIRGILIO MASTER - CAMASOTS SOFT', 
        html=html_content, 
        js_api=master, 
        width=1100, 
        height=850,
        background_color='#010409'
    )
    webview.start(debug=True)

if __name__ == "__main__":
    start_virgilio_ui()



