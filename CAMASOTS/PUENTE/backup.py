import os
import shutil
import schedule
import time
import threading
from datetime import datetime
import zipfile

class BackupSystem:
    def __init__(self, base_path="c:\\a2\\virgilio"):
        self.base_path = base_path
        self.storage_path = os.path.join(base_path, "app", "storage")
        self.backup_root = os.path.join(base_path, "backups")
        self.running = False
        
        # Asegurar que los directorios existen
        os.makedirs(self.backup_root, exist_ok=True)
        os.makedirs(self.storage_path, exist_ok=True)

    def create_full_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_root, f"virgilio_full_backup_{timestamp}.zip")
        
        print(f"[VIRGILIO-BACKUP] Iniciando respaldo completo en: {backup_file}")
        
        try:
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Respaldar almacenamiento (DBs, aprendizaje, config)
                if os.path.exists(self.storage_path):
                    self._zip_directory(self.storage_path, zipf, "storage")
                
                # Respaldar el laboratorio
                lab_path = os.path.join(self.base_path, "laboratorio")
                if os.path.exists(lab_path):
                    self._zip_directory(lab_path, zipf, "laboratorio")
                
            print(f"[VIRGILIO-BACKUP] Respaldo completado con exito.")
            return True
        except Exception as e:
            print(f"[VIRGILIO-BACKUP-ERROR] Error al crear respaldo: {e}")
            return False

    def _zip_directory(self, path, ziph, arcname_prefix):
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                # Crear una ruta relativa dentro del ZIP
                rel_path = os.path.relpath(file_path, os.path.join(path, ".."))
                ziph.write(file_path, rel_path)

    def start_scheduler(self):
        self.running = True
        # Programar respaldo cada 6 horas
        schedule.every(6).hours.do(self.create_full_backup)
        
        def run_schedule():
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        
        self.thread = threading.Thread(target=run_schedule, daemon=True)
        self.thread.start()
        print("[VIRGILIO-BACKUP] Programador de respaldos activado (Cada 6 horas).")

    def stop(self):
        self.running = False

if __name__ == "__main__":
    # Prueba rapida
    bs = BackupSystem()
    bs.create_full_backup()
