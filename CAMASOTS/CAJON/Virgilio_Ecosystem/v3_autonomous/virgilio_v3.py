import os
import sys
import json
import time
import threading
from datetime import datetime

# Añadir Shared_Core al path
sys.path.append(r"C:\a2\Shared_Core")
try:
    from evolution import EvolutionEngine
    from controller import SystemController
except ImportError:
    print("Error: No se pudo cargar Shared_Core modules.")
    sys.exit(1)

# ====================================================================
# VIRGILIO v3 AUTONOMOUS - AI AGENTIC & EVOLUTION ENGINE
# ASIMILACIÓN DE PATRONES, AUTO-OPTIMIZACIÓN Y APRENDIZAJE
# ====================================================================

class VirgilioAutonomous:
    def __init__(self):
        self.ee = EvolutionEngine(base_path=r"C:\a2\Shared_Core")
        self.sc = SystemController()
        self.version = "3.0.0-Autonomous"
        self.running = False

    def start(self):
        self.running = True
        self.ee.start()
        print(f"[VIRGILIO-v3] Motor evolutivo activo.")
        threading.Thread(target=self._background_tasks, daemon=True).start()

    def stop(self):
        self.running = False
        self.ee.stop()

    def _background_tasks(self):
        """Tareas autónomas de mantenimiento y auditoría."""
        while self.running:
            # Auditoría de hardware cada 10 minutos
            report = self.sc.get_full_system_report()
            log_path = r"C:\a2\Shared_Core\storage\system_logs.json"
            
            logs = []
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    try: logs = json.load(f)
                    except: logs = []
            
            logs.append({"timestamp": datetime.now().isoformat(), "report": report})
            # Mantener solo los últimos 100 logs
            logs = logs[-100:]
            
            with open(log_path, 'w') as f:
                json.dump(logs, f, indent=4)
            
            print(f"[VIRGILIO-v3] Auditoría autónoma completada. Logs actualizados.")
            time.sleep(600)

def main():
    v3 = VirgilioAutonomous()
    v3.start()
    print("--- VIRGILIO v3 AUTONOMOUS RUNNING ---")
    print("Pulse Ctrl+C para detener el motor de aprendizaje.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        v3.stop()
        print("Virgilio v3 detenido.")

if __name__ == "__main__":
    main()
