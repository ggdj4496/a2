# 🔧 ARQUITECTURA DE HERRAMIENTAS - CAMASOTS_MASTER

## 🎯 Visión General

CAMASOTS_MASTER se transformará en un **sistema de orquestación de herramientas** donde cada API externa se integra como una herramienta especializada, seleccionable automáticamente según la tarea.

```mermaid
graph TB
    subgraph "Orquestador CAMASOTS"
        O[Orquestador Principal]
        F[Sistema de Fallback]
        P[Priorizador de Herramientas]
    end
    
    subgraph "Herramientas de IA/LLM"
        D[DeepSeek<br/>Code & Reasoning]
        X[XAI/Grok<br/>General Chat]
        G[Gemini<br/>Multimodal]
        GR[Groq<br/>Fast Inference]
        OR[OpenRouter<br/>Multi-Provider]
    end
    
    subgraph "Herramientas de Comunicación"
        T[Telegram Bot<br/>User Interface]
        V[Voice/Whisper<br/>Audio Processing]
        E[ElevenLabs<br/>Text-to-Speech]
    end
    
    subgraph "Herramientas de Control"
        VI[Virgilio<br/>DMX/ArtNet]
        Q[QLC+<br/>Lighting Control]
        C[Controller<br/>System Commands]
    end
    
    O --> F
    O --> P
    F --> D
    F --> X
    F --> G
    F --> GR
    F --> OR
    F --> T
    F --> V
    F --> E
    F --> VI
    F --> Q
    
    P --> D
    P --> X
    P --> G
```

---

## 📋 APIs Identificadas en caja_fuerte.env

### ✅ APIs Principales (Activas)
| Plataforma | API Key | Propósito | Herramienta |
|------------|---------|-----------|-------------|
| **DeepSeek** | sk-aa027041232e46b58d7f78293f2cf18f | Code generation, reasoning | `DeepSeekTool` |
| **Telegram (Virgilio)** | 8486107876:AAGeNFbiCxHEcxcIGn1sT15oEJTakdAPLZg | Bot communication | `TelegramTool` |
| **Telegram (Athenea)** | 8679300161:AAEvC6q6sFuelleFiCuGhqBYq5P5yshoPWDY | Bot communication | `TelegramTool` |

### 🔄 APIs Legacy (Verificar)
| Plataforma | Token/Key | Estado | Herramienta |
|------------|-----------|--------|-------------|
| **XAI** | xai-R2iVHhUUNFKIr6KH4TITZgKbINnJtqzmux3gzDBeqsS9f47AH-LNosvAQiT5vd2JH4YmpNGPGahDPJ | Verificar | `XAITool` |
| **Gemini** | AIzaSyCOQnWUHxrGivmWhA2BzFeUiuIPu7TjSKQ | Verificar | `GeminiTool` |
| **OpenRouter** | sk-or-v1-03cba7ddd71677523e9acb5132a9ff49e5 | Verificar | `OpenRouterTool` |
| **Groq** | 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 | Verificar | `GroqTool` |
| **ElevenLabs** | e1a12d6579c94bf415796052ec1df1ee68608247b66dbdec20d7267a56fe409 | Verificar | `ElevenLabsTool` |
| **Skyscanner** | sk_7f829a5884b014c2c873d3fd96fbdd1f4a1a25/a/527553 | Verificar | `SkyscannerTool` |

### 📱 Legacy Telegram Bots (Verificar)
- `8659106351:AAHmpJLi-y-H6T6-fungD_Bb8afU_z2eSTn78` - Virgilio Pro
- `8749414069:AAHS1CCbkRAi4lX_fh1REh16tVEv-GyeKYLQ` - Delta
- `8349343707:AAH8uCDLrCbmJusOyykCTdqA8hGpDHqUonY` - Sigma
- `8765358799:AAGaj6zZVcxqJoxEURjt6WrZNy9PNBmOst8` - Alpha

---

## 🏗️ DISEÑO DE LA ARQUITECTURA

### 1. Base Class: Tool

```python
# src/camasots/tools/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class ToolCategory(Enum):
    """Categorías de herramientas."""
    AI_LLM = "ai_llm"
    COMMUNICATION = "communication"
    AUDIO = "audio"
    CONTROL = "control"
    SEARCH = "search"


class ToolPriority(Enum):
    """Prioridad de herramientas para fallback."""
    PRIMARY = 1
    SECONDARY = 2
    FALLBACK = 3


@dataclass
class ToolResult:
    """Resultado estandarizado de una herramienta."""
    success: bool
    data: Any
    error: Optional[str] = None
    tool_name: str = ""
    latency_ms: float = 0.0


@dataclass
class ToolCapability:
    """Capacidad que puede realizar una herramienta."""
    name: str
    description: str
    parameters: Dict[str, Any]


class BaseTool(ABC):
    """
    Clase base para todas las herramientas de CAMASOTS.
    
    Cada herramienta debe implementar:
    - validate(): Verificar si la herramienta está disponible
    - execute(): Ejecutar la acción principal
    - get_capabilities(): Listar capacidades
    """
    
    name: str = ""
    category: ToolCategory = ToolCategory.AI_LLM
    priority: ToolPriority = ToolPriority.SECONDARY
    description: str = ""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._available: Optional[bool] = None
        self._last_error: Optional[str] = None
    
    @abstractmethod
    async def validate(self) -> bool:
        """
        Verifica si la herramienta está disponible y funcionando.
        
        Returns:
            True si la herramienta puede usarse
        """
        pass
    
    @abstractmethod
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """
        Ejecuta una acción en la herramienta.
        
        Args:
            action: Nombre de la acción a ejecutar
            **kwargs: Parámetros específicos de la acción
            
        Returns:
            ToolResult estandarizado
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[ToolCapability]:
        """
        Retorna la lista de capacidades de esta herramienta.
        
        Returns:
            Lista de ToolCapability
        """
        pass
    
    def is_available(self) -> bool:
        """Retorna el estado de disponibilidad cacheado."""
        return self._available if self._available is not None else False
    
    async def check_availability(self) -> bool:
        """Verifica y cachea la disponibilidad."""
        try:
            self._available = await self.validate()
        except Exception as e:
            self._available = False
            self._last_error = str(e)
        return self._available
```

### 2. Implementación: DeepSeekTool

```python
# src/camasots/tools/deepseek_tool.py
import aiohttp
import time
from typing import Any, Dict, List

from .base import BaseTool, ToolCategory, ToolPriority, ToolResult, ToolCapability


class DeepSeekTool(BaseTool):
    """
    Herramienta de integración con DeepSeek API.
    
    Capacidades:
    - code_generation: Generar código en múltiples lenguajes
    - code_review: Revisar y analizar código
    - reasoning: Razonamiento lógico y resolución de problemas
    - chat: Conversación general
    """
    
    name = "deepseek"
    category = ToolCategory.AI_LLM
    priority = ToolPriority.PRIMARY
    description = "DeepSeek Coder v2 - Especializado en código y razonamiento"
    
    API_URL = "https://api.deepseek.com/v1/chat/completions"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('DEEPSEEK_API_KEY')
        self.model = config.get('DEEPSEEK_MODEL', 'deepseek-coder')
    
    async def validate(self) -> bool:
        """Verifica que la API key sea válida."""
        if not self.api_key:
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Test simple
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.API_URL,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            self._last_error = f"Validation failed: {str(e)}"
            return False
    
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """Ejecuta acciones de DeepSeek."""
        start_time = time.time()
        
        try:
            if action == "code_generation":
                result = await self._generate_code(**kwargs)
            elif action == "code_review":
                result = await self._review_code(**kwargs)
            elif action == "chat":
                result = await self._chat(**kwargs)
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Unknown action: {action}",
                    tool_name=self.name
                )
            
            latency = (time.time() - start_time) * 1000
            return ToolResult(
                success=True,
                data=result,
                tool_name=self.name,
                latency_ms=latency
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                tool_name=self.name,
                latency_ms=(time.time() - start_time) * 1000
            )
    
    async def _generate_code(self, prompt: str, language: str = "python") -> Dict:
        """Genera código basado en un prompt."""
        system_msg = f"You are an expert {language} programmer. Generate clean, well-documented code."
        
        return await self._call_api(system_msg, prompt)
    
    async def _review_code(self, code: str) -> Dict:
        """Revisa código y proporciona feedback."""
        system_msg = "You are a code reviewer. Analyze the code for bugs, improvements, and best practices."
        prompt = f"Review this code:\n\n```\n{code}\n```"
        
        return await self._call_api(system_msg, prompt)
    
    async def _chat(self, message: str, context: List[Dict] = None) -> Dict:
        """Chat general."""
        return await self._call_api(
            "You are a helpful assistant.",
            message,
            context
        )
    
    async def _call_api(self, system: str, user: str, context: List[Dict] = None) -> Dict:
        """Llama a la API de DeepSeek."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [{"role": "system", "content": system}]
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": user})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
                
                data = await response.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "usage": data.get("usage", {}),
                    "model": data.get("model", self.model)
                }
    
    def get_capabilities(self) -> List[ToolCapability]:
        """Retorna capacidades de DeepSeek."""
        return [
            ToolCapability(
                name="code_generation",
                description="Generate code in various programming languages",
                parameters={
                    "prompt": "Description of what to generate",
                    "language": "Programming language (python, javascript, etc.)"
                }
            ),
            ToolCapability(
                name="code_review",
                description="Review code and provide feedback",
                parameters={
                    "code": "Code to review"
                }
            ),
            ToolCapability(
                name="chat",
                description="General conversation",
                parameters={
                    "message": "User message",
                    "context": "Optional conversation history"
                }
            )
        ]
```

### 3. Implementación: TelegramTool

```python
# src/camasots/tools/telegram_tool.py
import asyncio
from typing import Any, Dict, List, Optional
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

from .base import BaseTool, ToolCategory, ToolPriority, ToolResult, ToolCapability


class TelegramTool(BaseTool):
    """
    Herramienta de integración con Telegram Bot API.
    
    Capacidades:
    - send_message: Enviar mensajes
    - send_photo: Enviar imágenes
    - send_document: Enviar documentos
    - receive_commands: Recibir y procesar comandos
    """
    
    name = "telegram"
    category = ToolCategory.COMMUNICATION
    priority = ToolPriority.PRIMARY
    description = "Telegram Bot API - Comunicación con usuarios"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.token = config.get('TELEGRAM_TOKEN') or config.get('VIRGILIO_TOKEN')
        self.bot: Optional[Bot] = None
        self.application: Optional[Application] = None
    
    async def validate(self) -> bool:
        """Verifica que el token de Telegram sea válido."""
        if not self.token:
            return False
        
        try:
            self.bot = Bot(token=self.token)
            me = await self.bot.get_me()
            return me is not None and me.username is not None
        except Exception as e:
            self._last_error = f"Validation failed: {str(e)}"
            return False
    
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """Ejecuta acciones de Telegram."""
        if not self.bot:
            return ToolResult(
                success=False,
                data=None,
                error="Bot not initialized",
                tool_name=self.name
            )
        
        try:
            if action == "send_message":
                result = await self._send_message(**kwargs)
            elif action == "send_photo":
                result = await self._send_photo(**kwargs)
            elif action == "send_document":
                result = await self._send_document(**kwargs)
            elif action == "start_polling":
                result = await self._start_polling(**kwargs)
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Unknown action: {action}",
                    tool_name=self.name
                )
            
            return ToolResult(
                success=True,
                data=result,
                tool_name=self.name
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                tool_name=self.name
            )
    
    async def _send_message(self, chat_id: int, text: str, **kwargs) -> Dict:
        """Envía un mensaje de texto."""
        message = await self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=kwargs.get('parse_mode', 'HTML'),
            reply_markup=kwargs.get('reply_markup')
        )
        return {
            "message_id": message.message_id,
            "chat_id": message.chat_id,
            "text": message.text
        }
    
    async def _send_photo(self, chat_id: int, photo: str, caption: str = None) -> Dict:
        """Envía una foto."""
        message = await self.bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption
        )
        return {
            "message_id": message.message_id,
            "photo_id": message.photo[-1].file_id if message.photo else None
        }
    
    async def _send_document(self, chat_id: int, document: str, caption: str = None) -> Dict:
        """Envía un documento."""
        message = await self.bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption
        )
        return {
            "message_id": message.message_id,
            "document_id": message.document.file_id if message.document else None
        }
    
    async def _start_polling(self, handlers: Dict[str, callable]) -> Dict:
        """Inicia el polling para recibir actualizaciones."""
        self.application = Application.builder().token(self.token).build()
        
        # Registrar handlers
        for command, callback in handlers.items():
            self.application.add_handler(CommandHandler(command, callback))
        
        # Iniciar polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        return {"status": "polling_started"}
    
    def get_capabilities(self) -> List[ToolCapability]:
        """Retorna capacidades de Telegram."""
        return [
            ToolCapability(
                name="send_message",
                description="Send text messages to users",
                parameters={
                    "chat_id": "Target chat ID",
                    "text": "Message text",
                    "parse_mode": "HTML or Markdown"
                }
            ),
            ToolCapability(
                name="send_photo",
                description="Send photos",
                parameters={
                    "chat_id": "Target chat ID",
                    "photo": "Photo URL or file path",
                    "caption": "Optional caption"
                }
            ),
            ToolCapability(
                name="receive_commands",
                description="Receive and process bot commands",
                parameters={
                    "handlers": "Dictionary of command handlers"
                }
            )
        ]
```

### 4. Tool Manager

```python
# src/camasots/tools/manager.py
import asyncio
from typing import Dict, List, Optional, Type, Any
from collections import defaultdict

from .base import BaseTool, ToolCategory, ToolPriority, ToolResult


class ToolManager:
    """
    Gestor central de herramientas de CAMASOTS.
    
    Responsabilidades:
    - Registrar y gestionar todas las herramientas
    - Seleccionar la mejor herramienta para cada tarea
    - Implementar fallback entre herramientas
    - Monitorear disponibilidad
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._tools: Dict[str, BaseTool] = {}
        self._tools_by_category: Dict[ToolCategory, List[BaseTool]] = defaultdict(list)
        self._initialized = False
    
    def register_tool(self, tool_class: Type[BaseTool]) -> None:
        """Registra una nueva herramienta."""
        tool_instance = tool_class(self.config)
        self._tools[tool_instance.name] = tool_instance
        self._tools_by_category[tool_instance.category].append(tool_instance)
        
        # Ordenar por prioridad
        self._tools_by_category[tool_instance.category].sort(
            key=lambda t: t.priority.value
        )
    
    async def initialize(self) -> Dict[str, bool]:
        """
        Inicializa y verifica todas las herramientas.
        
        Returns:
            Diccionario con el estado de cada herramienta
        """
        results = {}
        
        for name, tool in self._tools.items():
            is_available = await tool.check_availability()
            results[name] = is_available
            
            status = "✅ Available" if is_available else "❌ Unavailable"
            print(f"  {tool.name}: {status}")
            
            if not is_available and tool._last_error:
                print(f"     Error: {tool._last_error}")
        
        self._initialized = True
        return results
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Obtiene una herramienta por nombre."""
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: ToolCategory) -> List[BaseTool]:
        """Obtiene todas las herramientas de una categoría."""
        return self._tools_by_category.get(category, [])
    
    async def execute_with_fallback(
        self,
        category: ToolCategory,
        action: str,
        **kwargs
    ) -> ToolResult:
        """
        Ejecuta una acción intentando múltiples herramientas en orden de prioridad.
        
        Args:
            category: Categoría de herramientas a usar
            action: Acción a ejecutar
            **kwargs: Parámetros de la acción
            
        Returns:
            ToolResult de la primera herramienta exitosa
        """
        tools = self.get_tools_by_category(category)
        
        if not tools:
            return ToolResult(
                success=False,
                data=None,
                error=f"No tools available for category: {category}"
            )
        
        errors = []
        
        for tool in tools:
            if not tool.is_available():
                continue
            
            result = await tool.execute(action, **kwargs)
            
            if result.success:
                return result
            
            errors.append(f"{tool.name}: {result.error}")
        
        # Ninguna herramienta funcionó
        return ToolResult(
            success=False,
            data=None,
            error=f"All tools failed. Errors: {'; '.join(errors)}"
        )
    
    def list_capabilities(self) -> Dict[str, List[str]]:
        """Lista todas las capacidades disponibles."""
        capabilities = {}
        
        for name, tool in self._tools.items():
            if tool.is_available():
                caps = tool.get_capabilities()
                capabilities[name] = [cap.name for cap in caps]
        
        return capabilities
    
    async def health_check(self) -> Dict[str, Any]:
        """Realiza un health check de todas las herramientas."""
        health = {
            "total_tools": len(self._tools),
            "available_tools": 0,
            "tools": {}
        }
        
        for name, tool in self._tools.items():
            is_available = await tool.check_availability()
            health["tools"][name] = {
                "available": is_available,
                "category": tool.category.value,
                "priority": tool.priority.value,
                "error": tool._last_error
            }
            
            if is_available:
                health["available_tools"] += 1
        
        return health


# Factory para crear el manager con todas las herramientas
def create_tool_manager(config: Dict[str, Any]) -> ToolManager:
    """Crea un ToolManager con todas las herramientas registradas."""
    from .deepseek_tool import DeepSeekTool
    from .telegram_tool import TelegramTool
    # Importar más herramientas aquí...
    
    manager = ToolManager(config)
    
    # Registrar herramientas
    manager.register_tool(DeepSeekTool)
    manager.register_tool(TelegramTool)
    # Registrar más...
    
    return manager
```

---

## 📊 MAPEO DE TAREAS A HERRAMIENTAS

```mermaid
graph LR
    subgraph "Tareas de Usuario"
        T1[Escribir código]
        T2[Revisar código]
        T3[Chat general]
        T4[Enviar mensaje]
        T5[Controlar luces]
        T6[Procesar voz]
    end
    
    subgraph "Herramientas"
        H1[DeepSeek]
        H2[XAI/Grok]
        H3[Gemini]
        H4[Telegram]
        H5[Virgilio/DMX]
        H6[Whisper]
    end
    
    T1 --> H1
    T1 --> H2
    T2 --> H1
    T3 --> H2
    T3 --> H3
    T4 --> H4
    T5 --> H5
    T6 --> H6
```

---

## 🔄 FLUJO DE FALLBACK

```python
# Ejemplo de uso del sistema de fallback

async def main():
    # Configuración con todas las APIs
    config = {
        'DEEPSEEK_API_KEY': 'sk-...',
        'VIRGILIO_TOKEN': '8486...',
        'ATHENEA_TOKEN': '8679...',
        'XAI_API_KEY': 'xai-...',
        'GEMINI_API_KEY': 'AIza...',
        # ... más APIs
    }
    
    # Crear manager
    manager = create_tool_manager(config)
    
    # Inicializar y verificar herramientas
    print("🔍 Verificando herramientas...")
    status = await manager.initialize()
    
    # Ejemplo: Generar código con fallback automático
    result = await manager.execute_with_fallback(
        category=ToolCategory.AI_LLM,
        action="code_generation",
        prompt="Create a function to calculate fibonacci",
        language="python"
    )
    
    if result.success:
        print(f"✅ Código generado con {result.tool_name}")
        print(result.data["content"])
    else:
        print(f"❌ Error: {result.error}")
    
    # Ejemplo: Enviar mensaje por Telegram
    telegram = manager.get_tool("telegram")
    if telegram and telegram.is_available():
        result = await telegram.execute(
            action="send_message",
            chat_id=123456789,
            text="¡Hola desde CAMASOTS!"
        )
```

---

## 📋 IMPLEMENTACIÓN POR PRIORIDAD

### FASE 1: Core (Semana 1)
- [x] Diseñar arquitectura base (Tool, ToolManager)
- [ ] Implementar DeepSeekTool
- [ ] Implementar TelegramTool
- [ ] Crear sistema de verificación de APIs

### FASE 2: LLMs Adicionales (Semana 2)
- [ ] Implementar XAITool
- [ ] Implementar GeminiTool
- [ ] Implementar GroqTool
- [ ] Implementar OpenRouterTool

### FASE 3: Audio y Comunicación (Semana 3)
- [ ] Implementar WhisperTool
- [ ] Implementar ElevenLabsTool
- [ ] Integrar con Virgilio (Voice)

### FASE 4: Control (Semana 4)
- [ ] Implementar VirgilioTool (DMX)
- [ ] Implementar QLCTool
- [ ] Integrar con Controller

### FASE 5: Testing y Release (Semana 5)
- [ ] Tests para todas las herramientas
- [ ] Documentación
- [ ] Release v1.0

---

*Arquitectura de Herramientas v1.0 - CAMASOTS_MASTER*
