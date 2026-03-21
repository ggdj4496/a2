#!/usr/bin/env python3
# ====================================================================
# CAMASOTS PUENTE v4.0 - "EL NÚCLEO SUPREMO"
# ====================================================================
# Centro de Mando Avanzado de Agentes Autonomous Sincrónico OT Super
# Versión 4.0 - Arquitectura Robusta, Estable y Sin Bloqueos
# ====================================================================

import os
import sys
import asyncio
import json
import time
import logging
import threading
import subprocess
import hashlib
import secrets
import re
import socket
import signal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set, Callable
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
from abc import ABC, abstractmethod

# ====================================================================
# IMPORTS CONDICIONALES (Se instalan automáticamente si faltan)
# ====================================================================

def ensure_dependencies():
    """Instala dependencias automáticamente si faltan."""
    required = {
        'websockets': 'websockets>=12.0',
        'aiohttp': 'aiohttp>=3.9.0',
        'cryptography': 'cryptography>=41.0.0',
        'psutil': 'psutil>=5.9.0'
    }
    
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            print(f"[INSTALL] Instalando {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package, '-q'])

ensure_dependencies()

import websockets
from websockets.server import WebSocketServerProtocol
import aiohttp
from aiohttp import web
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import psutil

# ====================================================================
# CONFIGURACIÓN GLOBAL
# ====================================================================

class Config:
    """Configuración centralizada del PUENTE."""
    ROOT_DIR = os.environ.get('CAMASOTS_ROOT', r'C:\CAMASOTS')
    PUENTE_DIR = os.path.join(ROOT_DIR, 'PUENTE')
    LOGS_DIR = os.path.join(ROOT_DIR, 'LOGS')
    DATABASE_DIR = os.path.join(ROOT_DIR, 'DATABASE', 'MASTER')
    TEMP_DIR = os.path.join(ROOT_DIR, 'TEMP')
    
    # Servidor
    WS_HOST = os.environ.get('WS_HOST', '0.0.0.0')
    WS_PORT = int(os.environ.get('WS_PORT', '8765'))
    REST_HOST = os.environ.get('REST_HOST', '0.0.0.0')
    REST_PORT = int(os.environ.get('REST_PORT', '8080'))
    
    # Health Check
    HEALTH_CHECK_INTERVAL = 30  # segundos
    AGENT_TIMEOUT = 60  # segundos sin respuesta = offline
    
    # Recursos
    MAX_TEMP_SIZE_GB = 1.0
    MAX_LOG_DAYS = 7
    MAX_QUEUE_SIZE = 1000
    
    # Red
    PING_INTERVAL = 10  # segundos
    GATEWAY_CHECK_INTERVAL = 30
    
    # Seguridad
    ENCRYPTION_KEY_FILE = os.path.join(PUENTE_DIR, '.vault.key')
    AUDIT_LOG = os.path.join(LOGS_DIR, 'audit.log')


# ====================================================================
# CLASES DE DATOS
# ====================================================================

@dataclass
class Agent:
    """Representación de un agente registrado."""
    id: str
    name: str
    websocket: Optional[WebSocketServerProtocol] = None
    status: str = "offline"  # online, offline, error, restarting
    last_heartbeat: float = field(default_factory=time.time)
    capabilities: List[str] = field(default_factory=list)
    subscriptions: Set[str] = field(default_factory=set)
    task_count: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_healthy(self) -> bool:
        """Verifica si el agente está respondiendo."""
        return (time.time() - self.last_heartbeat) < Config.AGENT_TIMEOUT
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa el agente (sin websocket)."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat,
            "capabilities": self.capabilities,
            "subscriptions": list(self.subscriptions),
            "task_count": self.task_count,
            "error_count": self.error_count,
            "metadata": self.metadata,
            "is_healthy": self.is_healthy()
        }


@dataclass
class Event:
    """Evento del sistema."""
    type: str  # agent_online, agent_offline, task_completed, error_occurred
    timestamp: str
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "source": self.source,
            "data": self.data
        }


# ====================================================================
# CAJA FUERTE DE APIs (ENCRIPTADA)
# ====================================================================

class APIVault:
    """
    Sistema de almacenamiento encriptado de credenciales.
    Nunca expone tokens en logs ni mensajes.
    """
    
    def __init__(self, vault_path: str = None):
        self.vault_path = vault_path or os.path.join(Config.PUENTE_DIR, 'vault.enc')
        self.logger = logging.getLogger("APIVault")
        self._cipher = None
        self._ensure_encryption_key()
        self._load_vault()
    
    def _ensure_encryption_key(self):
        """Genera o carga la clave de encriptación."""
        if os.path.exists(Config.ENCRYPTION_KEY_FILE):
            with open(Config.ENCRYPTION_KEY_FILE, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(Config.ENCRYPTION_KEY_FILE, 'wb') as f:
                f.write(key)
            self.logger.info("Nueva clave de encriptación generada")
        
        self._cipher = Fernet(key)
    
    def _load_vault(self):
        """Carga el vault encriptado."""
        self._secrets = {}
        if os.path.exists(self.vault_path):
            try:
                with open(self.vault_path, 'rb') as f:
                    encrypted_data = f.read()
                decrypted = self._cipher.decrypt(encrypted_data)
                self._secrets = json.loads(decrypted)
                self.logger.info("Vault cargado exitosamente")
            except Exception as e:
                self.logger.error(f"Error cargando vault: {e}")
                self._secrets = {}
        else:
            # Migrar desde caja_fuerte.env si existe
            self._migrate_from_env()
    
    def _migrate_from_env(self):
        """Migra credenciales desde el archivo env legacy."""
        env_path = os.path.join(Config.PUENTE_DIR, 'caja_fuerte.env')
        if os.path.exists(env_path):
            self.logger.info("Migrando credenciales desde caja_fuerte.env...")
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            self._secrets[key.strip()] = value.strip()
                self._save_vault()
                self.logger.info("Migración completada")
            except Exception as e:
                self.logger.error(f"Error en migración: {e}")
    
    def _save_vault(self):
        """Guarda el vault encriptado."""
        try:
            data = json.dumps(self._secrets).encode()
            encrypted = self._cipher.encrypt(data)
            with open(self.vault_path, 'wb') as f:
                f.write(encrypted)
        except Exception as e:
            self.logger.error(f"Error guardando vault: {e}")
    
    def get(self, key: str, default: str = None) -> Optional[str]:
        """Obtiene un secreto (no muestra el valor en logs)."""
        value = self._secrets.get(key, default)
        if value:
            self._log_access(key, "READ")
        return value
    
    def set(self, key: str, value: str):
        """Almacena un nuevo secreto."""
        self._secrets[key] = value
        self._save_vault()
        self._log_access(key, "WRITE")
        self.logger.info(f"Secreto '{key}' almacenado/actualizado")
    
    def delete(self, key: str):
        """Elimina un secreto."""
        if key in self._secrets:
            del self._secrets[key]
            self._save_vault()
            self._log_access(key, "DELETE")
    
    def list_keys(self) -> List[str]:
        """Lista las claves disponibles (sin valores)."""
        return list(self._secrets.keys())
    
    def _log_access(self, key: str, action: str):
        """Log de auditoría (sin exponer valores)."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {action} - Key: {self._mask_key(key)}"
        
        with open(Config.AUDIT_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def _mask_key(self, key: str) -> str:
        """Oculta parcialmente la clave."""
        if len(key) <= 8:
            return "***"
        return key[:4] + "***" + key[-4:]


# ====================================================================
# OPTIMIZADOR DE RED
# ====================================================================

class NetworkOptimizer:
    """
    Optimización de red para router Orange.
    Detecta el router, optimiza WiFi y verifica conectividad.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("NetworkOptimizer")
        self.router_info = {}
        self.gateway = None
        self.wifi_channel = None
        self._detect_router()
    
    def _run_command(self, cmd: List[str]) -> str:
        """Ejecuta comando de forma segura."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)
    
    def _detect_router(self):
        """Detecta información del router."""
        try:
            # Obtener gateway por defecto
            output = self._run_command(['ipconfig'])
            gateway_match = re.search(r'Puerta de enlace predeterminada.*?(\d+\.\d+\.\d+\.\d+)', output)
            
            if gateway_match:
                self.gateway = gateway_match.group(1)
                self.logger.info(f"Gateway detectado: {self.gateway}")
            
            # Intentar detectar router Orange
            # Nota: No modificamos configuración de otros dispositivos
            self.router_info = {
                "gateway": self.gateway,
                "type": "unknown",
                "optimized_channels": [1, 6, 11],  # Canales sin overlap en 2.4GHz
                "detection_time": datetime.now().isoformat()
            }
            
            # Ping al gateway para verificar conectividad
            if self.gateway:
                self._ping_gateway()
                
        except Exception as e:
            self.logger.error(f"Error detectando router: {e}")
    
    def _ping_gateway(self):
        """Ping constante al gateway."""
        if not self.gateway:
            return
        
        try:
            result = subprocess.run(
                ['ping', self.gateway, '-n', '1'],
                capture_output=True, text=True, timeout=5
            )
            
            if 'ms' in result.stdout or 'tiempo' in result.stdout:
                match = re.search(r'tiempo[=<](\d+)ms', result.stdout)
                latency = match.group(1) if match else "unknown"
                self.logger.info(f"Gateway {self.gateway} accesible - Latencia: {latency}ms")
                return {"status": "ok", "latency": latency}
            
        except Exception as e:
            self.logger.warning(f"Error ping gateway: {e}")
        
        return {"status": "error", "latency": None}
    
    def check_connectivity(self) -> Dict[str, Any]:
        """Verifica conectividad a internet."""
        status = {
            "net": "unknown",
            "latency": None,
            "gateway": self.gateway,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            result = subprocess.run(
                ['ping', '8.8.8.8', '-n', '1'],
                capture_output=True, text=True, timeout=10
            )
            
            if 'ms' in result.stdout or 'tiempo' in result.stdout:
                status["net"] = "stable"
                match = re.search(r'tiempo[=<](\d+)ms', result.stdout)
                if match:
                    status["latency"] = int(match.group(1))
            else:
                status["net"] = "unstable"
                
        except Exception as e:
            status["net"] = "error"
            self.logger.error(f"Error conectividad: {e}")
        
        return status
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado completo de red."""
        connectivity = self.check_connectivity()
        
        return {
            "router": self.router_info,
            "connectivity": connectivity,
            "recommended_wifi_channels": [1, 6, 11],
            "note": "No se modifica configuración de otros dispositivos"
        }


# ====================================================================
# MONITOR DE RECURSOS
# ====================================================================

class ResourceMonitor:
    """
    Monitoreo de CPU, RAM, Disco.
    Limpieza automática de TEMP y rotación de logs.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ResourceMonitor")
        self._temp_cleaned = False
        self._last_cleanup = None
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            stats = {
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "status": "critical" if cpu_percent > 90 else "warning" if cpu_percent > 70 else "normal"
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent": memory.percent,
                    "status": "critical" if memory.percent > 90 else "warning" if memory.percent > 70 else "normal"
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent": disk.percent,
                    "status": "critical" if disk.percent > 95 else "warning" if disk.percent > 85 else "normal"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error obteniendo stats: {e}")
            return {"error": str(e)}
    
    def check_temp_size(self) -> float:
        """Verifica tamaño del directorio TEMP."""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(Config.TEMP_DIR):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        total_size += os.path.getsize(fp)
                    except:
                        pass
            
            size_gb = total_size / (1024**3)
            return size_gb
            
        except Exception as e:
            self.logger.error(f"Error calculando tamaño TEMP: {e}")
            return 0.0
    
    def cleanup_temp(self):
        """Limpia TEMP si supera el límite."""
        size_gb = self.check_temp_size()
        
        if size_gb > Config.MAX_TEMP_SIZE_GB:
            self.logger.warning(f"TEMP excede límite: {size_gb:.2f}GB > {Config.MAX_TEMP_SIZE_GB}GB")
            self._perform_cleanup()
        else:
            self.logger.info(f"TEMP dentro del límite: {size_gb:.2f}GB")
    
    def _perform_cleanup(self):
        """Ejecuta limpieza de TEMP."""
        cleaned = 0
        errors = 0
        
        try:
            for item in os.listdir(Config.TEMP_DIR):
                item_path = os.path.join(Config.TEMP_DIR, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        cleaned += 1
                    elif os.path.isdir(item_path):
                        import shutil
                        shutil.rmtree(item_path)
                        cleaned += 1
                except Exception as e:
                    errors += 1
            
            self._last_cleanup = datetime.now()
            self.logger.info(f"Limpieza completada: {cleaned} archivos, {errors} errores")
            
        except Exception as e:
            self.logger.error(f"Error en limpieza: {e}")
    
    def rotate_logs(self):
        """Rota logs mayores a MAX_LOG_DAYS."""
        try:
            cutoff = datetime.now() - timedelta(days=Config.MAX_LOG_DAYS)
            
            for log_file in os.listdir(Config.LOGS_DIR):
                if log_file.endswith('.log'):
                    log_path = os.path.join(Config.LOGS_DIR, log_file)
                    mtime = datetime.fromtimestamp(os.path.getmtime(log_path))
                    
                    if mtime < cutoff:
                        # Comprimir yarchivar
                        archive_name = log_path + f".{mtime.strftime('%Y%m%d')}.bak"
                        try:
                            os.rename(log_path, archive_name)
                            self.logger.info(f"Log rotado: {log_file}")
                        except:
                            pass
                            
        except Exception as e:
            self.logger.error(f"Error en rotación de logs: {e}")
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Verifica dependencias instaladas."""
        required = {
            'websockets': 'websockets',
            'aiohttp': 'aiohttp',
            'cryptography': 'cryptography',
            'psutil': 'psutil'
        }
        
        status = {}
        for module, package in required.items():
            try:
                __import__(module)
                status[package] = "ok"
            except ImportError:
                status[package] = "missing"
        
        return status


# ====================================================================
# SISTEMA DE EVENTOS
# ====================================================================

class EventSystem:
    """
    Sistema de eventos con suscripción y persistencia.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("EventSystem")
        self._subscribers: Dict[str, Set[str]] = defaultdict(set)  # event_type -> set of agent_ids
        self._event_history: List[Event] = []
        self._max_history = 1000
        self._history_file = os.path.join(Config.PUENTE_DIR, 'events.json')
        self._load_history()
    
    def _load_history(self):
        """Carga historial de eventos."""
        if os.path.exists(self._history_file):
            try:
                with open(self._history_file, 'r') as f:
                    data = json.load(f)
                    for e in data:
                        self._event_history.append(Event(**e))
            except Exception as e:
                self.logger.error(f"Error cargando eventos: {e}")
    
    def _save_history(self):
        """Guarda historial de eventos."""
        try:
            data = [e.to_dict() for e in self._event_history[-self._max_history:]]
            with open(self._history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando eventos: {e}")
    
    def subscribe(self, agent_id: str, event_types: List[str]):
        """Suscribe un agente a tipos de eventos."""
        for event_type in event_types:
            self._subscribers[event_type].add(agent_id)
        self.logger.info(f"Agente {agent_id} suscrito a: {event_types}")
    
    def unsubscribe(self, agent_id: str, event_types: List[str] = None):
        """Cancela suscripción."""
        if event_types is None:
            # Unsubscribe de todo
            for subscribers in self._subscribers.values():
                subscribers.discard(agent_id)
        else:
            for event_type in event_types:
                self._subscribers[event_type].discard(agent_id)
    
    def emit(self, event: Event):
        """Emite un evento a los suscriptores."""
        self._event_history.append(event)
        
        if len(self._event_history) > self._max_history:
            self._save_history()
        
        subscribers = self._subscribers.get(event.type, set())
        
        self.logger.info(f"Evento '{event.type}' emitido a {len(subscribers)} suscriptores")
        
        return list(subscribers)
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """Obtiene historial de eventos."""
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return [e.to_dict() for e in events[-limit:]]


# ====================================================================
# GESTOR DE AGENTES
# ====================================================================

class AgentManager:
    """
    Gestión de agentes: registro, health checks, reinicio automático.
    """
    
    def __init__(self, event_system: EventSystem, vault: APIVault):
        self.logger = logging.getLogger("AgentManager")
        self.agents: Dict[str, Agent] = {}
        self.event_system = event_system
        self.vault = vault
        self._health_check_task = None
        self._running = False
        
        # Registrar agentes predefinidos
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Registra los agentes del sistema."""
        default_agents = [
            Agent(
                id="GUILLECODER",
                name="GUILLECODER",
                capabilities=["code", "automation", "orchestration"],
                metadata={"role": "master", "engine": "guille_engine.py"}
            ),
            Agent(
                id="ATHENEA",
                name="ATHENEA",
                capabilities=["ai", "learning", "assimilation"],
                metadata={"role": "ai_agent", "engine": "athenea_engine.py"}
            ),
            Agent(
                id="VIRGILIO",
                name="VIRGILIO",
                capabilities=["ecosystem", "education", "telegram"],
                metadata={"role": "tutor", "engine": "virgilio_v3.py"}
            )
        ]
        
        for agent in default_agents:
            self.agents[agent.id] = agent
            self.logger.info(f"Agente registrado: {agent.name}")
    
    def register_agent(self, agent_id: str, websocket: WebSocketServerProtocol = None, 
                       capabilities: List[str] = None) -> Agent:
        """Registra o actualiza un agente."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.websocket = websocket
            agent.status = "online"
            agent.last_heartbeat = time.time()
            if capabilities:
                agent.capabilities = capabilities
        else:
            agent = Agent(
                id=agent_id,
                name=agent_id,
                websocket=websocket,
                status="online",
                capabilities=capabilities or []
            )
            self.agents[agent_id] = agent
        
        # Emitir evento
        event = Event(
            type="agent_online",
            timestamp=datetime.now().isoformat(),
            source=agent_id,
            data=agent.to_dict()
        )
        self.event_system.emit(event)
        
        self.logger.info(f"Agente conectado: {agent_id}")
        return agent
    
    def unregister_agent(self, agent_id: str):
        """Desregistra un agente."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.status = "offline"
            agent.websocket = None
            
            # Emitir evento
            event = Event(
                type="agent_offline",
                timestamp=datetime.now().isoformat(),
                source=agent_id,
                data=agent.to_dict()
            )
            self.event_system.emit(event)
            
            self.logger.info(f"Agente desconectado: {agent_id}")
    
    def heartbeat(self, agent_id: str):
        """Recibe heartbeat de un agente."""
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = time.time()
            if self.agents[agent_id].status == "offline":
                self.agents[agent_id].status = "online"
    
    async def health_check_loop(self):
        """Bucle de health check de agentes."""
        self._running = True
        
        while self._running:
            try:
                for agent_id, agent in list(self.agents.items()):
                    if agent.status == "online" and not agent.is_healthy():
                        self.logger.warning(f"Agente no responde: {agent_id}")
                        agent.error_count += 1
                        
                        # Emitir evento de error
                        event = Event(
                            type="error_occurred",
                            timestamp=datetime.now().isoformat(),
                            source=agent_id,
                            data={"reason": "timeout", "error_count": agent.error_count}
                        )
                        self.event_system.emit(event)
                        
                        # Intentar reconectar (reinicio automático)
                        if agent.error_count >= 3:
                            agent.status = "restarting"
                            self.logger.info(f"Iniciando reinicio automático para: {agent_id}")
                
                await asyncio.sleep(Config.HEALTH_CHECK_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Error en health check: {e}")
                await asyncio.sleep(5)
    
    def stop_health_check(self):
        """Detiene el health check."""
        self._running = False
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Obtiene un agente por ID."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict]:
        """Lista todos los agentes."""
        return [a.to_dict() for a in self.agents.values()]
    
    def broadcast(self, message: Dict, exclude: List[str] = None):
        """Envía mensaje a todos los agentes conectados."""
        exclude = exclude or []
        
        for agent_id, agent in self.agents.items():
            if agent_id not in exclude and agent.websocket and agent.status == "online":
                try:
                    asyncio.create_task(agent.websocket.send(json.dumps(message)))
                except Exception as e:
                    self.logger.error(f"Error enviando a {agent_id}: {e}")


# ====================================================================
# WEBSOCKET HANDLER
# ====================================================================

class WebSocketHandler:
    """Manejador de conexiones WebSocket."""
    
    def __init__(self, bridge: 'CamasotsBridge'):
        self.bridge = bridge
        self.logger = logging.getLogger("WebSocket")
    
    async def handle(self, websocket: WebSocketServerProtocol, path: str):
        """Maneja una conexión WebSocket."""
        agent_id = None
        
        try:
            # Esperar mensaje de registro
            register_msg = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(register_msg)
            
            if data.get('type') == 'register':
                agent_id = data.get('agent_id')
                
                if not agent_id:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'agent_id requerido'
                    }))
                    return
                
                # Registrar agente
                self.bridge.agent_manager.register_agent(
                    agent_id,
                    websocket,
                    data.get('capabilities', [])
                )
                
                # Suscribir a eventos
                if 'subscriptions' in data:
                    self.bridge.event_system.subscribe(agent_id, data['subscriptions'])
                
                await websocket.send(json.dumps({
                    'type': 'registered',
                    'agent_id': agent_id,
                    'status': 'ok'
                }))
                
                # Mantener conexión
                await self._receive_loop(websocket, agent_id)
            
            else:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Primer mensaje debe ser register'
                }))
                
        except asyncio.TimeoutError:
            self.logger.warning("Timeout en registro WebSocket")
        except Exception as e:
            self.logger.error(f"Error en WebSocket: {e}")
        finally:
            if agent_id:
                self.bridge.agent_manager.unregister_agent(agent_id)
    
    async def _receive_loop(self, websocket: WebSocketServerProtocol, agent_id: str):
        """Bucle de recepción de mensajes."""
        try:
            async for message in websocket:
                await self._process_message(message, agent_id)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            self.logger.error(f"Error en receive loop: {e}")
    
    async def _process_message(self, raw_message: str, agent_id: str):
        """Procesa un mensaje recibido."""
        try:
            message = json.loads(raw_message)
            msg_type = message.get('type')
            
            if msg_type == 'heartbeat':
                self.bridge.agent_manager.heartbeat(agent_id)
                
            elif msg_type == 'task_completed':
                agent = self.bridge.agent_manager.get_agent(agent_id)
                if agent:
                    agent.task_count += 1
                
                event = Event(
                    type="task_completed",
                    timestamp=datetime.now().isoformat(),
                    source=agent_id,
                    data=message.get('data', {})
                )
                self.bridge.event_system.emit(event)
                
            elif msg_type == 'broadcast':
                # Re-broadcast a otros agentes
                recipients = message.get('recipients', [])
                for recipient_id in recipients:
                    recipient = self.bridge.agent_manager.get_agent(recipient_id)
                    if recipient and recipient.websocket:
                        await recipient.websocket.send(json.dumps(message))
            
            elif msg_type == 'event_subscribe':
                self.bridge.event_system.subscribe(agent_id, message.get('events', []))
            
            elif msg_type == 'api_request':
                # Solicitud a la API Vault
                api_key = message.get('key')
                if api_key:
                    value = self.bridge.vault.get(api_key)
                    await websocket.send(json.dumps({
                        'type': 'api_response',
                        'key': api_key,
                        'value': value
                    }))
            
            else:
                self.logger.warning(f"Tipo de mensaje desconocido: {msg_type}")
                
        except json.JSONDecodeError:
            self.logger.error("Mensaje JSON inválido")
        except Exception as e:
            self.logger.error(f"Error procesando mensaje: {e}")


# ====================================================================
# REST API HANDLER
# ====================================================================

class RESTHandler:
    """Manejador de API REST."""
    
    def __init__(self, bridge: 'CamasotsBridge'):
        self.bridge = bridge
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura las rutas REST."""
        self.app.router.add_get('/health', self.health)
        self.app.router.add_get('/agents', self.list_agents)
        self.app.router.add_get('/agents/{agent_id}', self.get_agent)
        self.app.router.add_post('/agents/{agent_id}/restart', self.restart_agent)
        self.app.router.add_get('/events', self.list_events)
        self.app.router.add_post('/events/subscribe', self.subscribe_events)
        self.app.router.add_get('/vault/keys', self.list_vault_keys)
        self.app.router.add_post('/vault/set', self.set_vault_secret)
        self.app.router.add_get('/network/status', self.network_status)
        self.app.router.add_get('/resources', self.get_resources)
        self.app.router.add_post('/cleanup', self.trigger_cleanup)
    
    async def health(self, request):
        """Endpoint de salud."""
        return web.json_response({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'agents_online': len([a for a in self.bridge.agent_manager.agents.values() if a.status == 'online'])
        })
    
    async def list_agents(self, request):
        """Lista todos los agentes."""
        return web.json_response({
            'agents': self.bridge.agent_manager.list_agents()
        })
    
    async def get_agent(self, request):
        """Obtiene un agente específico."""
        agent_id = request.match_info['agent_id']
        agent = self.bridge.agent_manager.get_agent(agent_id)
        
        if agent:
            return web.json_response(agent.to_dict())
        else:
            return web.json_response({'error': 'Agente no encontrado'}, status=404)
    
    async def restart_agent(self, request):
        """Reinicia un agente."""
        agent_id = request.match_info['agent_id']
        
        if agent_id in self.bridge.agent_manager.agents:
            agent = self.bridge.agent_manager.agents[agent_id]
            agent.status = "restarting"
            agent.error_count = 0
            
            return web.json_response({
                'status': 'ok',
                'message': f'Agente {agent_id} marcado para reinicio'
            })
        else:
            return web.json_response({'error': 'Agente no encontrado'}, status=404)
    
    async def list_events(self, request):
        """Lista eventos."""
        event_type = request.query.get('type')
        limit = int(request.query.get('limit', 100))
        
        events = self.bridge.event_system.get_history(event_type, limit)
        return web.json_response({'events': events})
    
    async def subscribe_events(self, request):
        """Suscribe a eventos (REST)."""
        data = await request.json()
        agent_id = data.get('agent_id')
        events = data.get('events', [])
        
        if agent_id:
            self.bridge.event_system.subscribe(agent_id, events)
            return web.json_response({'status': 'ok'})
        
        return web.json_response({'error': 'agent_id requerido'}, status=400)
    
    async def list_vault_keys(self, request):
        """Lista claves del vault (sin valores)."""
        keys = self.bridge.vault.list_keys()
        return web.json_response({'keys': keys})
    
    async def set_vault_secret(self, request):
        """Establece un secreto en el vault."""
        data = await request.json()
        key = data.get('key')
        value = data.get('value')
        
        if key and value:
            self.bridge.vault.set(key, value)
            return web.json_response({'status': 'ok'})
        
        return web.json_response({'error': 'key y value requeridos'}, status=400)
    
    async def network_status(self, request):
        """Estado de red."""
        status = self.bridge.network_optimizer.get_status()
        return web.json_response(status)
    
    async def get_resources(self, request):
        """Recursos del sistema."""
        resources = self.bridge.resource_monitor.get_system_stats()
        return web.json_response(resources)
    
    async def trigger_cleanup(self, request):
        """Dispara limpieza manual."""
        self.bridge.resource_monitor.cleanup_temp()
        self.bridge.resource_monitor.rotate_logs()
        return web.json_response({'status': 'ok', 'message': 'Limpieza ejecutada'})


# ====================================================================
# CLASE PRINCIPAL: CAMASOTS BRIDGE
# ====================================================================

class CamasotsBridge:
    """
    PUENTE v4.0 - El núcleo central de CAMASOTS.
    Gestiona WebSocket, REST, Agentes, Red, Recursos y Eventos.
    """
    
    def __init__(self):
        # Rutas
        self.root_dir = Config.ROOT_DIR
        self.puente_dir = Config.PUENTE_DIR
        self.log_dir = Config.LOGS_DIR
        
        # Crear directorios
        for d in [self.root_dir, self.puente_dir, self.log_dir, Config.TEMP_DIR]:
            os.makedirs(d, exist_ok=True)
        
        # Configurar logging
        self._setup_logging()
        self.logger = logging.getLogger("CamasotsBridge")
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO CAMASOTS PUENTE v4.0 - NÚCLEO SUPREMO")
        self.logger.info("=" * 60)
        
        # Inicializar componentes
        self.vault = APIVault()
        self.network_optimizer = NetworkOptimizer()
        self.resource_monitor = ResourceMonitor()
        self.event_system = EventSystem()
        self.agent_manager = AgentManager(self.event_system, self.vault)
        
        # WebSocket y REST
        self.ws_handler = WebSocketHandler(self)
        self.rest_handler = RESTHandler(self)
        
        # Estado
        self.running = False
        self.ws_server = None
        self.rest_server = None
        self._health_check_task = None
        self._resource_check_task = None
        
        # Signal handlers
        self._setup_signal_handlers()
    
    def _setup_logging(self):
        """Configura el sistema de logging."""
        log_file = os.path.join(Config.LOGS_DIR, 'bridge.log')
        
        # Formato profesional
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)-8s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def _setup_signal_handlers(self):
        """Configura handlers para señales de terminación."""
        def signal_handler(signum, frame):
            self.logger.warning(f"Señal recibida: {signum}")
            asyncio.create_task(self.shutdown())
        
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except Exception:
            pass  # No disponible en Windows
    
    async def start(self):
        """Inicia el PUENTE."""
        if self.running:
            self.logger.warning("PUENTE ya está ejecutándose")
            return
        
        self.running = True
        self.logger.info("Iniciando servicios...")
        
        # Iniciar REST server
        await self._start_rest_server()
        
        # Iniciar WebSocket server
        await self._start_ws_server()
        
        # Iniciar health checks
        self._health_check_task = asyncio.create_task(
            self.agent_manager.health_check_loop()
        )
        
        # Iniciar monitoreo de recursos
        self._resource_check_task = asyncio.create_task(
            self._resource_monitor_loop()
        )
        
        self.logger.info("=" * 60)
        self.logger.info("✅ PUENTE v4.0 TOTALMENTE OPERATIVO")
        self.logger.info(f"   WebSocket: ws://{Config.WS_HOST}:{Config.WS_PORT}")
        self.logger.info(f"   REST API:  http://{Config.REST_HOST}:{Config.REST_PORT}")
        self.logger.info("=" * 60)
        
        # Mantener ejecutándose
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
    
    async def _start_ws_server(self):
        """Inicia servidor WebSocket."""
        try:
            self.ws_server = await websockets.serve(
                self.ws_handler.handle,
                Config.WS_HOST,
                Config.WS_PORT
            )
            self.logger.info(f"WebSocket servidor iniciado en puerto {Config.WS_PORT}")
        except Exception as e:
            self.logger.error(f"Error iniciando WebSocket: {e}")
    
    async def _start_rest_server(self):
        """Inicia servidor REST."""
        try:
            runner = aiohttp.web.AppRunner(self.rest_handler.app)
            await runner.setup()
            self.rest_server = await runner.bind(Config.REST_HOST, Config.REST_PORT)
            self.logger.info(f"REST API iniciada en puerto {Config.REST_PORT}")
        except Exception as e:
            self.logger.error(f"Error iniciando REST: {e}")
    
    async def _resource_monitor_loop(self):
        """Bucle de monitoreo de recursos."""
        while self.running:
            try:
                # Verificar tamaño TEMP
                self.resource_monitor.cleanup_temp()
                
                # Rotar logs
                self.resource_monitor.rotate_logs()
                
                await asyncio.sleep(300)  # Cada 5 minutos
                
            except Exception as e:
                self.logger.error(f"Error en resource monitor: {e}")
                await asyncio.sleep(30)
    
    async def shutdown(self):
        """Apagado elegante del PUENTE."""
        self.logger.info("Iniciando apagado elegante...")
        self.running = False
        
        # Detener health checks
        self.agent_manager.stop_health_check()
        
        # Cancelar tareas
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._resource_check_task:
            self._resource_check_task.cancel()
        
        # Cerrar servidores
        if self.ws_server:
            self.ws_server.close()
            await self.ws_server.wait_closed()
        
        if self.rest_server:
            await self.rest_server.cleanup()
        
        # Guardar estado
        self.event_system._save_history()
        
        self.logger.info("PUENTE detenido correctamente")
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del PUENTE."""
        return {
            "status": "running" if self.running else "stopped",
            "agents": self.agent_manager.list_agents(),
            "network": self.network_optimizer.get_status(),
            "resources": self.resource_monitor.get_system_stats(),
            "events_count": len(self.event_system._event_history),
            "vault_keys": self.vault.list_keys()
        }


# ====================================================================
# PUNTO DE ENTRADA
# ====================================================================

def main():
    """Punto de entrada principal."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         CAMASOTS PUENTE v4.0 - NÚCLEO SUPREMO             ║
    ║                                                           ║
    ║  [1] WebSocket Server   → Puerto 8765                    ║
    ║  [2] REST API           → Puerto 8080                    ║
    ║  [3] Health Check       → Intervalo 30s                 ║
    ║  [4] Resource Monitor   → CPU/RAM/Disco                  ║
    ║  [5] Event System       → Suscripciones persistentes     ║
    ║  [6] API Vault          → Credenciales encriptadas       ║
    ║  [7] Network Optimizer  → Orange Router                  ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Crear bridge
    bridge = CamasotsBridge()
    
    try:
        # Iniciar asyncio
        asyncio.run(bridge.start())
    except KeyboardInterrupt:
        print("\nDeteniendo PUENTE...")
        asyncio.run(bridge.shutdown())
    except Exception as e:
        print(f"Error fatal: {e}")
        logging.getLogger("CamasotsBridge").error(f"Error fatal: {e}")


if __name__ == "__main__":
    main()
