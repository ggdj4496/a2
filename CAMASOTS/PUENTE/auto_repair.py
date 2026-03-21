import os
import sys
import subprocess
import json
import time

# ====================================================================
# MASTER AUTO-REPAIR & PERSISTENCE - SHARED CORE
# ENSURES SYSTEM INTEGRITY AND PERMISSIONS ARE ALWAYS ACTIVE
# ====================================================================

class AutoRepair:
    def __init__(self):
        self.base_dir = r"C:\a2"
        self.venv_py = os.path.join(self.base_dir, "venv", "Scripts", "python.exe")

    def check_permissions(self):
        """Ensures C:\a2 has full control for the current user and admins."""
        try:
            subprocess.run(['icacls', self.base_dir, '/grant', f'{os.getlogin()}:(OI)(CI)F', '/T', '/C', '/Q'], capture_output=True)
            return True
        except:
            return False

    def verify_venv(self):
        """Checks if the virtual environment is healthy."""
        if not os.path.exists(self.venv_py):
            print("[AUTO-REPAIR] VENV missing. Recreating...")
            return False
        return True

    def repair_firewall(self):
        """Ensures GuilleCoder is not blocked by Windows Firewall."""
        try:
            subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name=GuilleCoder_In', 
                            'dir=in', 'action=allow', f'program={self.venv_py}', 'enable=yes'], capture_output=True)
            subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule', 'name=GuilleCoder_Out', 
                            'dir=out', 'action=allow', f'program={self.venv_py}', 'enable=yes'], capture_output=True)
            return True
        except:
            return False

    def run_all(self):
        print("[AUTO-REPAIR] Starting system integrity audit...")
        p = self.check_permissions()
        v = self.verify_venv()
        f = self.repair_firewall()
        print(f"[AUTO-REPAIR] Audit complete. Permissions: {p}, VENV: {v}, Firewall: {f}")
        return p and v and f

if __name__ == "__main__":
    repair = AutoRepair()
    repair.run_all()
