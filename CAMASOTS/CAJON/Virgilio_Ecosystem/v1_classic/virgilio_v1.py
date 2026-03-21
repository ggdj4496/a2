import os
import sys
import json
import time

# Añadir Shared_Core al path
sys.path.append(r"C:\a2\Shared_Core")
try:
    from controller import SystemController
except ImportError:
    print("Error: No se pudo cargar Shared_Core/controller.py")
    sys.exit(1)

# ====================================================================
# VIRGILIO v1 CLASSIC - HIGH PERFORMANCE CLI
# CONTROL TOTAL POR CONSOLA: RÁPIDO, LIGERO Y EFICIENTE
# ====================================================================

class VirgilioClassic:
    def __init__(self):
        self.sc = SystemController()
        self.version = "1.0.0-Classic"

    def show_banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""
        █░█ █ █▀█ █▀▀ █ █░░ █ █▀█   █░█ ▄▄
        ▀▄▀ █ █▀▄ █▄█ █ █▄▄ █ █▄█   ▀▄▀ ░░ {self.version}
        -------------------------------------------
        [1] Reporte de Sistema (Everest Mode)
        [2] Captura de Pantalla
        [3] Listar Procesos (Top 10)
        [4] Abrir Explorador en C:\\a2
        [5] Ejecutar Comando Personalizado
        [0] Salir
        -------------------------------------------
        """)

    def run(self):
        while True:
            self.show_banner()
            choice = input("Seleccione una opción: ")
            
            if choice == "1":
                report = self.sc.get_full_system_report()
                print(json.dumps(report, indent=4))
                input("\nPresione Enter para continuar...")
            elif choice == "2":
                path = self.sc.capture_screenshot()
                print(f"Captura guardada en: {path}")
                time.sleep(2)
            elif choice == "3":
                procs = self.sc.list_processes()
                print(f"{'PID':<8} {'NOMBRE':<25} {'CPU%':<8} {'MEM%':<8}")
                for p in procs[:10]:
                    print(f"{p['pid']:<8} {p['name']:<25} {p['cpu_percent']:<8} {p['memory_percent']:<8.2f}")
                input("\nPresione Enter para continuar...")
            elif choice == "4":
                self.sc.execute_command("explorer C:\\a2")
            elif choice == "5":
                cmd = input("Ingrese comando: ")
                res = self.sc.execute_command(cmd)
                print(f"STDOUT: {res.get('stdout')}\nSTDERR: {res.get('stderr')}")
                input("\nPresione Enter para continuar...")
            elif choice == "0":
                print("Cerrando Virgilio Classic...")
                break

if __name__ == "__main__":
    app = VirgilioClassic()
    app.run()
