import os
import sys
import subprocess
import json
import time
import logging
import threading
from datetime import datetime
from typing import Dict, Any, Optional

# ====================================================================
# CAMASOTS MASTER BRIDGE v3.0 - "EL NÚCLEO SUPREMO"
# Arquitectura de Nivel Senior Master - GuilleCoder Elite
# Gestión de Conectividad, Seguridad Root y Sincronía Proactiva
# ====================================================================

class CamasotsBridge:
    def __init__(self):
        # Rutas Base Absolutas
        self.root_dir = r"C:\a2\CAMASOTS"
        self.puente_dir = os.path.join(self.root_dir, "PUENTE")
        self.log_dir = os.path.join(self.root_dir, "LOGS")
        self.db_dir = os.path.join(self.root_dir, "DATABASE", "MASTER")
        
        # Archivos Críticos
        self.env_path = os.path.join(self.puente_dir, "caja_fuerte.env")
        self.db_master = os.path.join(self.db_dir, "master_db.json")
        self.state_file = os.path.join(self.puente_dir, "system_state.json")
        self.walkie_file = os.path.join(self.puente_dir, "walkie_sync.txt")
        
        # Entorno Python
        self.venv_py = os.path.join(self.root_dir, "venv", "Scripts", "python.exe")
        
        # Inicialización de Estructura
        for d in [self.log_dir, self.db_dir, self.puente_dir]:
            os.makedirs(d, exist_ok=True)
            
        # Configuración de Logging Profesional
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.log_dir, "bridge.log"), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("BridgeCore")
        self.logger.info("--- Iniciando CAMASOTS MASTER BRIDGE v3.0 ---")

        self.running = False
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            except:
                self.state = {"active_agents": [], "last_sync": None, "network": "Unknown"}
        else:
            self.state = {"active_agents": [], "last_sync": None, "network": "Unknown"}

    def _save_state(self):
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error guardando estado: {e}")

    def unlock_system_blocks(self) -> bool:
        """Libera Firewall, UAC y otorga permisos ROOT totales."""
        self.logger.info("Ejecutando liberación total de bloqueos...")
        try:
            # Reglas de Firewall (Entrada/Salida)
            subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name=CAMASOTS_OUT', 'dir=out', 'action=allow', f'program={self.venv_py}', 'enable=yes'], capture_output=True)
            subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name=CAMASOTS_IN', 'dir=in', 'action=allow', f'program={self.venv_py}', 'enable=yes'], capture_output=True)
            
            # Permisos ICACLS (Control Total)
            subprocess.run(['icacls', r'C:\a2', '/grant', 'Administradores:(OI)(CI)F', '/T', '/C', '/Q'], capture_output=True)
            
            self.logger.info("Sistema liberado con éxito.")
            return True
        except Exception as e:
            self.logger.error(f"Fallo en liberación: {e}")
            return False

    def check_connectivity(self) -> Dict[str, Any]:
        """Verifica red y latencia."""
        status = {"net": "Inestable", "latency": "---"}
        try:
            res = subprocess.run(['ping', '8.8.8.8', '-n', '1'], capture_output=True, text=True)
            if "ms" in res.stdout:
                status["net"] = "Estable"
                import re
                match = re.search(r'tiempo[=<](\d+)ms', res.stdout)
                if match: status["latency"] = f"{match.group(1)}ms"
        except: pass
        self.state["network"] = status["net"]
        return status

    async def notify_telegram(self, message: str):
        """Envía notificaciones proactivas a través del Bot Master."""
        # Esta función será llamada por los agentes para hablar por Telegram
        token = None
        if os.path.exists(self.env_path):
            with open(self.env_path, 'r') as f:
                for line in f:
                    if "VIRGILIO_TOKEN=" in line:
                        token = line.split('=')[1].strip()
        
        if token:
            try:
                import requests
                # Necesitamos el ID del usuario master (guardado en master_db)
                with open(self.db_master, 'r') as f:
                    db = json.load(f)
                    master_id = db.get("config", {}).get("master_id")
                
                if master_id:
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    requests.post(url, json={"chat_id": master_id, "text": f"🔔 **CAMASOTS ALERT**\n{message}", "parse_mode": "Markdown"})
            except: pass

    def sync_loop(self):
        self.logger.info("Hilo de sincronía activo.")
        while self.running:
            try:
                self.check_connectivity()
                self.state["last_sync"] = datetime.now().isoformat()
                self._save_state()
                time.sleep(30)
            except Exception as e:
                self.logger.error(f"Error en sincronía: {e}")
                time.sleep(10)

    def start(self):
        if not self.running:
            self.running = True
            self.unlock_system_blocks()
            threading.Thread(target=self.sync_loop, daemon=True).start()
            self.logger.info("PUENTE MASTER TOTALMENTE OPERATIVO.")

if __name__ == "__main__":
    bridge = CamasotsBridge()
    bridge.start()
    while True: time.sleep(1)
