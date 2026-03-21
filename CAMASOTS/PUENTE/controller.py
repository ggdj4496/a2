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

# ====================================================================
# MASTER SYSTEM CONTROLLER v4.0 - ROOT COMMANDER EDITION
# ELITE SYSTEM INTERFACE: HARDWARE, SOFTWARE & FULL ROOT PERMISSIONS
# ====================================================================

class SystemController:
    def __init__(self):
        # Configuración de seguridad crítica
        pyautogui.FAILSAFE = True
        self.screen_capturer = mss.mss()
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.base_dir = r"C:\a2"
        self.storage_dir = os.path.join(self.base_dir, "Shared_Core", "storage")
        os.makedirs(self.storage_dir, exist_ok=True)

    def is_admin(self):
        """Verifica privilegios de Súper-Usuario (Administrador)."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def get_full_system_report(self):
        """Genera un informe exhaustivo del equipo (Estilo EVEREST/AIDA64)."""
        try:
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
                    "cpu_freq": f"{psutil.cpu_freq().max} MHz",
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
            return {"error": f"Fallo en auditoría maestra: {str(e)}"}

    def get_screen_info(self):
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
            return {"error": str(e)}

    def execute_command(self, command, shell=True, timeout=60):
        """Ejecuta comandos de consola con captura de salida profesional y manejo Root."""
        try:
            print(f"[ROOT-CMD] Ejecutando: {command}")
            result = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=timeout)
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Timeout: El comando excedió los {timeout} segundos.", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def capture_screenshot(self, subfolder="audit"):
        """Captura de pantalla de alta definición para auditoría visual."""
        folder = os.path.join(self.storage_dir, subfolder)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"audit_{int(time.time())}.png")
        self.screen_capturer.shot(output=path)
        return path

    def list_processes(self, filter_name="", limit=20):
        """Lista procesos activos con métricas de rendimiento avanzadas."""
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
            try:
                if not filter_name or filter_name.lower() in proc.info['name'].lower():
                    procs.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(procs, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:limit]

    def automation_type(self, text, press_enter=True, interval=0.005):
        """Escritura automatizada de alta velocidad para automatización de UI."""
        pyautogui.write(text, interval=interval)
        if press_enter:
            pyautogui.press('enter')

    def open_path(self, path):
        """Abre un archivo o carpeta en el explorador de Windows."""
        try:
            os.startfile(path)
            return True
        except:
            return False

    def shutdown_pc(self, force=False):
        """Apagado de emergencia del sistema (Requiere privilegios)."""
        cmd = "shutdown /s /t 0"
        if force: cmd += " /f"
        return self.execute_command(cmd)

if __name__ == "__main__":
    sc = SystemController()
    print("--- INFORME MAESTRO DE SISTEMA v4.0 ---")
    print(json.dumps(sc.get_full_system_report(), indent=4))
