# DOCUMENTACIÓN DE CARPETA - PUENTE (THE BRIDGE)
## FUNCIÓN: Núcleo de Sincronía y Seguridad
Gestiona la comunicación entre Telegram y el PC, libera bloqueos de Firewall/UAC y protege la Caja Fuerte (.env).

## COMPONENTS:
- bridge_core.py: Lógica multihilo de sincronización.
- telegram_bot.py: Interfaz Walkie-Talkie y recepción de archivos.
- caja_fuerte.env: Almacén de API Keys y Tokens.
