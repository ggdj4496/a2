# ====================================================================
# CAMASOTS SYSTEM PURGE v1.0
# Limpieza profunda de residuos de instalaciones conflictivas
# ====================================================================

$ErrorActionPreference = "SilentlyContinue"

function Clean-Path {
    param($path)
    if (Test-Path $path) {
        Write-Host "Eliminando residuo: $path" -ForegroundColor Yellow
        Remove-Item -Path $path -Recurse -Force
    }
}

Write-Host "--- INICIANDO PURGA DE RESIDUOS DEL SISTEMA ---" -ForegroundColor Cyan

# 1. Rutas de Usuario (AppData/Roaming/Local)
$userPaths = @(
    "$env:APPDATA\Python",
    "$env:APPDATA\Ollama",
    "$env:APPDATA\npm",
    "$env:APPDATA\npm-cache",
    "$env:LOCALAPPDATA\Programs\Python",
    "$env:LOCALAPPDATA\Ollama",
    "$env:LOCALAPPDATA\pip",
    "$env:USERPROFILE\.ollama",
    "$env:USERPROFILE\.npmrc"
)

foreach ($path in $userPaths) {
    Clean-Path $path
}

# 2. Limpieza de variables de entorno (Opcional, manual recomendado para PATH)
Write-Host "Limpieza de carpetas temporales..." -ForegroundColor Cyan
Clean-Path "$env:TEMP\Ollama*"
Clean-Path "$env:TEMP\pip-*"

Write-Host "Purga completada. El sistema está listo para instalaciones limpias en Program Files." -ForegroundColor Green
