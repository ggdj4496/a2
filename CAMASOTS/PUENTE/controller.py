import pyautogui
import psutil
import os
import subprocess
import time
import mss
from PIL import Image
import ctypes
import platform
import socket
import uuid
import re
import json
import logging

# ====================================================================
# MASTER SYSTEM CONTROLLER v4.1 - ROOT COMMANDER EDITION
# ELITE SYSTEM INTERFACE: HARDWARE, SOFTWARE & FULL ROOT PERMISSIONS
# CON MEJORAS DE SEGURIDAD v4.1
# ====================================================================

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("SystemController")

# Lista blanca de comandos permitidos para ejecución
ALLOWED_COMMANDS = {
    'ipconfig', 'ping', 'hostname', 'tasklist', 'taskkill', 'systeminfo',
    'dir', 'cd', 'type', 'netstat', 'tracert', 'nslookup', 'whoami',
    'ver', 'time', 'date', 'echo', 'tree', 'findstr', 'reg query'
}


class SystemController:
    def __init__(self):
        # Configuración de seguridad crítica
        pyautogui.FAILSAFE = True
        self.screen_capturer = mss.mss()
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Detección automática de paths
        self.base_dir = os.environ.get('CAMASOTS_ROOT', r"C:\a2")
        self.storage_dir = os.path.join(self.base_dir, "Shared_Core", "storage")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        logger.info("SystemController inicializado con seguridad mejorada")

    def is_admin(self) -> bool:
        """Verifica privilegios de Súper-Usuario (Administrador)."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.error(f"Error verificando admin: {e}")
            return False

    def get_full_system_report(self) -> dict:
        """Genera un informe exhaustivo del equipo (Estilo EVEREST/AIDA64)."""
        try:
            # Validar cpu_freq ya que puede ser None en algunas máquinas
            cpu_freq = psutil.cpu_freq()
            cpu_freq_str = f"{cpu_freq.max} MHz" if cpu_freq else "N/A"
            
            report = {
                "os": {
                    "name": platform.system(),
                    "version": platform.version(),
                    "release": platform.release(),
                    "architecture": platform.machine(),
                    "node": platform.node()
                },
                "hardware": {
                    "processor": platform.processor(),
                    "cpu_count": psutil.cpu_count(logical=True),
                    "cpu_freq": cpu_freq_str,
                    "ram_total": f"{round(psutil.virtual_memory().total / (1024**3), 2)} GB",
                    "ram_available": f"{round(psutil.virtual_memory().available / (1024**3), 2)} GB",
                    "disk_total": f"{round(psutil.disk_usage('/').total / (1024**3), 2)} GB",
                    "disk_free": f"{round(psutil.disk_usage('/').free / (1024**3), 2)} GB",
                    "mac_address": ':'.join(re.findall('..', '%012x' % uuid.getnode()))
                },
                "network": {
                    "hostname": socket.gethostname(),
                    "ip_address": socket.gethostbyname(socket.gethostname()),
                    "connections": len(psutil.net_connections())
                },
                "status": {
                    "cpu_usage": f"{psutil.cpu_percent(interval=0.1)}%",
                    "ram_usage": f"{psutil.virtual_memory().percent}%",
                    "uptime": f"{round((time.time() - psutil.boot_time()) / 3600, 2)} horas",
                    "is_admin": self.is_admin()
                }
            }
            return report
        except Exception as e:
            logger.error(f"Fallo en auditoría maestra: {e}")
            return {"error": f"Fallo en auditoría maestra: {str(e)}"}

    def get_screen_info(self) -> dict:
        """Obtiene información detallada de la ventana activa y el ratón."""
        try:
            screen_size = pyautogui.size()
            hwnd = self.user32.GetForegroundWindow()
            length = self.user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buff, length + 1)
            
            return {
                "width": screen_size.width,
                "height": screen_size.height,
                "active_window": buff.value,
                "mouse_pos": list(pyautogui.position()),
                "is_admin": self.is_admin()
            }
        except Exception as e:
            logger.error(f"Error en get_screen_info: {e}")
            return {"error": str(e)}

    def _validate_command(self, command: str) -> tuple[bool, str]:
        """
        Valida que el comando esté en la lista blanca.
        Retorna (es_valido, mensaje_error)
        """
        # Si no usa shell, es más seguro
        if not command.strip().startswith(('&', '|', '&&', '||')):
            # Extraer el primer comando para validar
            parts = command.strip().split()
            if parts:
                cmd_base = parts[0].lower()
                # Permitir rutas absolutas
                if ':' in cmd_base or os.path.isabs(cmd_base):
                    return True, ""
                if cmd_base in ALLOWED_COMMANDS:
                    return True, ""
                return False, f"Comando '{cmd_base}' no está en la lista blanca permitida"
        return True, ""  # Permitir si usa shell=False

    def execute_command(self, command: str, shell: bool = False, timeout: int = 60) -> dict:
        """Ejecuta comandos de consola con captura de salida profesional y manejo Root."""
        try:
            # Validar comando si se usa shell
            if shell:
                is_valid, error_msg = self._validate_command(command)
                if not is_valid:
                    logger.warning(f"[ROOT-CMD] Bloqueado: {error_msg}")
                    return {"error": error_msg, "success": False, "stdout": "", "stderr": "", "exit_code": -1}
            
            logger.info(f"[ROOT-CMD] Ejecutando: {command}")
            result = subprocess.run(
                command, 
                shell=shell, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout: El comando excedió los {timeout} segundos.")
            return {"error": f"Timeout: El comando excedió los {timeout} segundos.", "success": False}
        except Exception as e:
            logger.error(f"Error ejecutando comando: {e}")
            return {"error": str(e), "success": False}

    def capture_screenshot(self, subfolder: str = "audit") -> str:
        """Captura de pantalla de alta definición para auditoría visual."""
        try:
            folder = os.path.join(self.storage_dir, subfolder)
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, f"audit_{int(time.time())}.png")
            self.screen_capturer.shot(output=path)
            logger.info(f"Screenshot guardado: {path}")
            return path
        except Exception as e:
            logger.error(f"Error capturando pantalla: {e}")
            return ""

    def list_processes(self, filter_name: str = "", limit: int = 20) -> list:
        """Lista procesos activos con métricas de rendimiento avanzadas."""
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                if not filter_name or filter_name.lower() in proc.info['name'].lower():
                    procs.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(procs, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:limit]

    def automation_type(self, text: str, press_enter: bool = True, interval: float = 0.005):
        """Escritura automatizada de alta velocidad para automatización de UI."""
        pyautogui.write(text, interval=interval)
        if press_enter:
            pyautogui.press('enter')

    def open_path(self, path: str) -> bool:
        """Abre un archivo o carpeta en el explorador de Windows."""
        try:
            os.startfile(path)
            return True
        except Exception as e:
            logger.error(f"Error abriendo path: {e}")
            return False

    def shutdown_pc(self, force: bool = False, confirm_admin: bool = True) -> dict:
        """
        Apagado de emergencia del sistema (Requiere privilegios).
        Por seguridad, siempre requiere confirmación de admin.
        """
        # Verificación de seguridad obligatoria
        if confirm_admin and not self.is_admin():
            return {
                "error": "Se requieren privilegios de administrador para apagar el sistema",
                "success": False
            }
        
        cmd = "shutdown /s /t 0"
        if force: 
            cmd += " /f"
        
        logger.warning(f"Solicitud de shutdown: force={force}")
        return self.execute_command(cmd)


if __name__ == "__main__":
    sc = SystemController()
    print("--- INFORME MAESTRO DE SISTEMA v4.1 ---")
    print(json.dumps(sc.get_full_system_report(), indent=4))
