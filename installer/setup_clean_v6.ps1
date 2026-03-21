# ====================================================================
# CAMASOTS MASTER INSTALLER v8.0 - "EL DESPLIEGUE FINAL"
# Edición Senior Master - GuilleCoder Elite
# Bypass Total de UAC, Control ROOT y Configuración de Alto Rendimiento
# ====================================================================

$ErrorActionPreference = "SilentlyContinue"
$ProgressPreference = "SilentlyContinue"

function Write-Elite { param($msg, $color="Cyan") Write-Host "[CAMASOTS] $msg" -ForegroundColor $color }

Write-Elite "--- INICIANDO DESPLIEGUE MAESTRO CAMASOTS v8.0 ---" "Green"

# 1. ELEVACIÓN Y BYPASS DE UAC (User Account Control)
Write-Elite "Configurando bypass de UAC y políticas de ejecución..."
try {
    # Desactivar avisos de consentimiento para administradores
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "ConsentPromptBehaviorAdmin" -Value 0
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "PromptOnSecureDesktop" -Value 0
    Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Force -Scope LocalMachine
} catch {
    Write-Elite "Fallo en bypass de UAC." "Red"
}

# 2. PURGA DE RESIDUOS
Write-Elite "Limpiando residuos de instalaciones antiguas en AppData..."
powershell -ExecutionPolicy Bypass -File "c:\a2\installer\purge_system.ps1"

# 3. INSTALACIÓN DE PYTHON 3.11 EN PROGRAM FILES
$pyDir = "C:\Program Files\Python311"
if (-not (Test-Path $pyDir)) {
    Write-Elite "Instalando Python 3.11 en Program Files..."
    $pyUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $pyInstaller = "$env:TEMP\python_installer.exe"
    Invoke-WebRequest -Uri $pyUrl -OutFile $pyInstaller
    Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 TargetDir='$pyDir'" -Wait
}

# 4. INSTALACIÓN DE OLLAMA EN PROGRAM FILES
$ollamaDir = "C:\Program Files\Ollama"
if (-not (Test-Path $ollamaDir)) {
    Write-Elite "Instalando Ollama en Program Files..."
    $url = "https://ollama.com/download/OllamaSetup.exe"
    $installer = "$env:TEMP\OllamaSetup.exe"
    Invoke-WebRequest -Uri $url -OutFile $installer
    Start-Process -FilePath $installer -ArgumentList "/S /ALLUSERS" -Wait
}

# 5. GESTIÓN PROFESIONAL DE PERMISOS (ROOT CONTROL)
Write-Elite "Otorgando Control Total (ROOT) a la estructura del proyecto..."
$targetPaths = @("C:\a2", $pyDir, $ollamaDir)
foreach ($path in $targetPaths) {
    if (Test-Path $path) {
        & icacls "$path" /grant "Administradores:(OI)(CI)F" /T /C /Q
        & icacls "$path" /grant "SYSTEM:(OI)(CI)F" /T /C /Q
        & icacls "$path" /grant "$($env:USERNAME):(OI)(CI)F" /T /C /Q
    }
}

# 6. DESPLIEGUE DE VENV Y DEPENDENCIAS ELITE
Write-Elite "Sincronizando entorno virtual CAMASOTS..."
cd "C:\a2\CAMASOTS"
if (-not (Test-Path "venv")) {
    & "$pyDir\python.exe" -m venv venv
}
& "C:\a2\CAMASOTS\venv\Scripts\python.exe" -m pip install --upgrade pip
& "C:\a2\CAMASOTS\venv\Scripts\python.exe" -m pip install pywebview pytesseract Pillow python-telegram-bot httpx mss psutil requests

Write-Elite "==========================================================" "Green"
Write-Elite "   DESPLIEGUE CAMASOTS v8.0 COMPLETADO CON ÉXITO" "Green"
Write-Elite "==========================================================" "Green"
