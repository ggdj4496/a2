import os
import shutil
import time
import threading
import json
import ast
import re
from datetime import datetime
import hashlib

# ====================================================================
# MASTER EVOLUTION ENGINE v3.0 - APRENDIZAJE AUTÓNOMO TOTAL
# ANALIZA, COMPRENDE Y CONECTA PATRONES DE CÓDIGO GLOBALES
# ====================================================================

class EvolutionEngine:
    def __init__(self, base_path=r"C:\a2\Shared_Core"):
        self.base_path = base_path
        self.cajon_path = os.path.join(base_path, "cajon")
        self.chimenea_path = os.path.join(base_path, "chimenea")
        self.storage_dir = os.path.join(base_path, "storage", "learning")
        self.learning_db = os.path.join(self.storage_dir, "master_patterns.json")
        self.running = False
        
        os.makedirs(self.cajon_path, exist_ok=True)
        os.makedirs(self.chimenea_path, exist_ok=True)
        os.makedirs(self.storage_dir, exist_ok=True)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_cajon, daemon=True)
        self.thread.start()
        print(f"[EVOLUTION-v3] Motor iniciado. Auditando: {self.cajon_path}")

    def stop(self):
        self.running = False

    def _monitor_cajon(self):
        while self.running:
            try:
                files = os.listdir(self.cajon_path)
                for file_name in files:
                    file_path = os.path.join(self.cajon_path, file_name)
                    if os.path.isfile(file_path):
                        self._process_file(file_path, file_name)
                time.sleep(3) # Más rápido para una asimilación inmediata
            except Exception as e:
                print(f"[EVOLUTION-ERROR] Fallo en monitoreo: {e}")
                time.sleep(10)

    def _process_file(self, file_path, file_name):
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            file_hash = hashlib.sha256(raw_data).hexdigest()
            content_text = ""
            is_binary = False
            
            try:
                content_text = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                is_binary = True
                content_text = f"Binary content: {len(raw_data)} bytes"

            analysis = self._deep_analysis(content_text, file_name, is_binary)
            analysis["hash"] = file_hash

            self._update_master_db(file_name, analysis)

            # Archivar con estructura de fecha profesional
            date_str = datetime.now().strftime("%Y/%m/%d")
            dest_dir = os.path.join(self.chimenea_path, date_str)
            os.makedirs(dest_dir, exist_ok=True)
            
            shutil.move(file_path, os.path.join(dest_dir, f"{int(time.time())}_{file_name}"))
            print(f"[EVOLUTION] Archivo '{file_name}' asimilado correctamente.")

        except Exception as e:
            print(f"[EVOLUTION-ERROR] Error procesando '{file_name}': {e}")

    def _deep_analysis(self, content, name, is_binary):
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "file_type": "unknown",
            "metrics": {"lines": 0, "chars": len(content)},
            "structures": {}
        }

        if is_binary:
            analysis["file_type"] = "binary"
            return analysis

        analysis["metrics"]["lines"] = len(content.splitlines())
        ext = os.path.splitext(name)[1].lower()

        # Motor de detección por extensión y contenido
        if ext == '.py':
            self._analyze_python(content, analysis)
        elif ext in ['.js', '.ts']:
            self._analyze_js(content, analysis)
        elif ext in ['.html', '.css']:
            analysis["file_type"] = "web_ui"
            analysis["structures"]["tags_or_classes"] = len(re.findall(r'[.#]\w+\s*\{|<[a-zA-Z]+', content))
        elif ext in ['.cpp', '.c', '.h']:
            analysis["file_type"] = "c_family"
            analysis["structures"]["functions"] = re.findall(r'\w+\s+\w+\s*\(.*?\)\s*\{', content)

        return analysis

    def _analyze_python(self, content, analysis):
        analysis["file_type"] = "python"
        try:
            tree = ast.parse(content)
            analysis["structures"] = {
                "classes": [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
                "functions": [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)],
                "imports": list(set(n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import)) | 
                           set(n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) if n.module))
            }
        except:
            # Fallback a Regex si hay errores de sintaxis
            analysis["structures"]["functions"] = re.findall(r'def\s+(\w+)\s*\(', content)
            analysis["structures"]["classes"] = re.findall(r'class\s+(\w+)', content)

    def _analyze_js(self, content, analysis):
        analysis["file_type"] = "javascript"
        analysis["structures"] = {
            "functions": re.findall(r'function\s+(\w+)|(\w+)\s*=\s*\([^)]*\)\s*=>|(\w+)\s*\([^)]*\)\s*\{', content),
            "imports": re.findall(r'import\s+.*?\s+from\s+[\'"](.*?)[\'"]|require\([\'"](.*?)[\'"]\)', content)
        }

    def _update_master_db(self, name, analysis):
        db = {}
        if os.path.exists(self.learning_db):
            try:
                with open(self.learning_db, 'r', encoding='utf-8') as f:
                    db = json.load(f)
            except: pass
        
        db[name] = analysis
        with open(self.learning_db, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=4)

if __name__ == "__main__":
    ee = EvolutionEngine()
    ee.start()
    while True: time.sleep(1)
