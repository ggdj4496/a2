"""
CAMASOTS COMMAND CENTER - INTERFAZ PRINCIPAL
Windows 11 Dark Theme - Professional UI

Author: CAMASOTS System
Version: 1.0.0
"""

import sys
import json
import os
import threading
import time
import asyncio
from datetime import datetime
from pathlib import Path

# PyQt6 Imports
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QListWidget,
    QTextEdit, QProgressBar, QFrame, QScrollArea,
    QGridLayout, QLineEdit, QComboBox, QDialog,
    QListWidgetItem, QTableWidget, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem, QTabWidget,
    QDialogButtonBox, QFormLayout, QGroupBox,
    QSplitter, QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QMimeData
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction, QPainter, QLinearGradient

# WebSocket client
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Warning: websockets library not available. Using mock mode.")

# =============================================================================
# WINDOWS 11 DARK THEME STYLESHEET
# =============================================================================

WINDOWS11_STYLESHEET = """
QMainWindow {
    background-color: #202020;
    color: #FFFFFF;
    border: none;
}

QWidget {
    background-color: #202020;
    color: #FFFFFF;
    font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif;
    font-size: 13px;
}

/* Titles */
QLabel#title_label {
    font-size: 18px;
    font-weight: 600;
    color: #FFFFFF;
}

QLabel#section_title {
    font-size: 16px;
    font-weight: 600;
    color: #FFFFFF;
    padding-bottom: 8px;
}

/* Sidebar */
QWidget#sidebar {
    background-color: #1A1A1A;
    border-right: 1px solid #2D2D2D;
}

/* Navigation Buttons */
QPushButton#nav_button {
    background-color: transparent;
    color: #A0A0A0;
    border: none;
    border-radius: 4px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    transition: all 0.2s ease;
}

QPushButton#nav_button:hover {
    background-color: #2D2D2D;
    color: #FFFFFF;
}

QPushButton#nav_button:pressed {
    background-color: #383838;
}

QPushButton#nav_button:checked {
    background-color: #0078D4;
    color: #FFFFFF;
}

/* Primary Buttons */
QPushButton#primary_button {
    background-color: #0078D4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
}

QPushButton#primary_button:hover {
    background-color: #106EBE;
}

QPushButton#primary_button:pressed {
    background-color: #005A9E;
}

QPushButton#primary_button:disabled {
    background-color: #3D3D3D;
    color: #666666;
}

/* Secondary Buttons */
QPushButton#secondary_button {
    background-color: #3D3D3D;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 13px;
}

QPushButton#secondary_button:hover {
    background-color: #4D4D4D;
}

/* Danger Buttons */
QPushButton#danger_button {
    background-color: #D13438;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
}

QPushButton#danger_button:hover {
    background-color: #C42B1C;
}

/* Cards / Frames */
QFrame#card {
    background-color: #2D2D2D;
    border-radius: 8px;
    border: 1px solid #3D3D3D;
    padding: 16px;
}

QFrame#card_elevated {
    background-color: #333333;
    border-radius: 8px;
    border: 1px solid #404040;
    padding: 16px;
}

/* Status Indicators */
QLabel#status_online {
    color: #6CCB5F;
    font-weight: 600;
}

QLabel#status_offline {
    color: #D13438;
    font-weight: 600;
}

QLabel#status_working {
    color: #FCE100;
    font-weight: 600;
}

QLabel#status_indicator {
    border-radius: 4px;
    padding: 4px 8px;
}

/* Input Fields */
QLineEdit {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border: 1px solid #3D3D3D;
    border-radius: 4px;
    padding: 8px 12px;
    selection-background-color: #0078D4;
}

QLineEdit:focus {
    border: 1px solid #0078D4;
}

QLineEdit:disabled {
    background-color: #252525;
    color: #666666;
}

/* ComboBox */
QComboBox {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border: 1px solid #3D3D3D;
    border-radius: 4px;
    padding: 8px 12px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #A0A0A0;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #2D2D2D;
    border: 1px solid #3D3D3D;
    selection-background-color: #0078D4;
    color: #FFFFFF;
}

/* Lists */
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget::item {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border-radius: 4px;
    padding: 8px;
    margin: 2px;
}

QListWidget::item:selected {
    background-color: #0078D4;
}

QListWidget::item:hover {
    background-color: #383838;
}

/* Tree Widget */
QTreeWidget {
    background-color: transparent;
    border: none;
    color: #FFFFFF;
    outline: none;
}

QTreeWidget::item {
    padding: 6px;
}

QTreeWidget::item:selected {
    background-color: #0078D4;
}

QTreeWidget::item:hover {
    background-color: #383838;
}

QHeaderView::section {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border: none;
    padding: 8px;
    font-weight: 500;
}

/* Tables */
QTableWidget {
    background-color: transparent;
    border: 1px solid #3D3D3D;
    gridline-color: #3D3D3D;
    border-radius: 4px;
}

QTableWidget::item {
    padding: 8px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #0078D4;
}

/* Progress Bars */
QProgressBar {
    background-color: #3D3D3D;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #0078D4;
    border-radius: 4px;
}

/* Scroll Areas */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: transparent;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #555555;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666666;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #555555;
    border-radius: 5px;
    min-width: 30px;
}

/* Text Edit / Logs */
QTextEdit {
    background-color: #1A1A1A;
    color: #CCCCCC;
    border: 1px solid #3D3D3D;
    border-radius: 4px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 12px;
}

QTextEdit#log_viewer {
    background-color: #0C0C0C;
    color: #00FF00;
    border: 1px solid #2D2D2D;
}

/* Tabs */
QTabWidget::pane {
    background-color: #2D2D2D;
    border: 1px solid #3D3D3D;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #2D2D2D;
    color: #A0A0A0;
    border: none;
    padding: 10px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: #0078D4;
    color: #FFFFFF;
}

QTabBar::tab:hover:!selected {
    background-color: #383838;
}

/* Menu Bar */
QMenuBar {
    background-color: #1A1A1A;
    color: #FFFFFF;
    border-bottom: 1px solid #2D2D2D;
}

QMenuBar::item:selected {
    background-color: #0078D4;
}

QMenu {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border: 1px solid #3D3D3D;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #0078D4;
}

/* Status Bar */
QStatusBar {
    background-color: #1A1A1A;
    color: #A0A0A0;
    border-top: 1px solid #2D2D2D;
}

/* Group Boxes */
QGroupBox {
    background-color: #2D2D2D;
    border: 1px solid #3D3D3D;
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 500;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #FFFFFF;
}

/* ToolTip */
QToolTip {
    background-color: #333333;
    color: #FFFFFF;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px 8px;
}

/* Splitter */
QSplitter::handle {
    background-color: #3D3D3D;
}

QSplitter::handle:horizontal {
    width: 1px;
}

QSplitter::handle:vertical {
    height: 1px;
}
"""

# =============================================================================
# WEBSOCKET CLIENT THREAD
# =============================================================================

class WebSocketClient(QThread):
    """WebSocket client for communicating with PUERTO bridge"""
    message_received = pyqtSignal(dict)
    connection_status = pyqtSignal(bool)
    
    def __init__(self, url="ws://localhost:8765"):
        super().__init__()
        self.url = url
        self.running = True
        self.connected = False
        self.reconnect_delay = 2
        self._websocket = None
        
    def run(self):
        """Main thread loop for WebSocket connection"""
        while self.running:
            try:
                if WEBSOCKETS_AVAILABLE:
                    asyncio.run(self._connect())
                else:
                    # Mock mode for testing without websockets
                    self.connected = True
                    self.connection_status.emit(True)
                    self._mock_loop()
            except Exception as e:
                print(f"WebSocket error: {e}")
                self.connected = False
                self.connection_status.emit(False)
                time.sleep(self.reconnect_delay)
    
    async def _connect(self):
        """Async connection method"""
        try:
            async with websockets.connect(self.url, ping_interval=30) as websocket:
                self._websocket = websocket
                self.connected = True
                self.connection_status.emit(True)
                
                # Register as INTERFAZ
                await websocket.send(json.dumps({
                    "type": "register",
                    "agent": "INTERFAZ"
                }))
                
                # Listen for messages
                while self.running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1)
                        data = json.loads(message)
                        self.message_received.emit(data)
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"Receive error: {e}")
                        break
                        
        except Exception as e:
            print(f"Connection error: {e}")
            self.connected = False
            self.connection_status.emit(False)
    
    def _mock_loop(self):
        """Mock loop for testing without WebSocket"""
        while self.running and not self.connected:
            time.sleep(1)
        
        # Send mock data periodically
        while self.running:
            time.sleep(3)
            if self.connected:
                self.message_received.emit({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "agents": {
                        "GUILLECODER": {"status": "online", "tasks": 2},
                        "ATHENEA": {"status": "working", "tasks": 1},
                        "VIRGILIO": {"status": "online", "tasks": 0}
                    }
                })
    
    def send_message(self, message: dict):
        """Send message to bridge"""
        if self.connected and self._websocket:
            try:
                asyncio.run(self._websocket.send(json.dumps(message)))
            except Exception as e:
                print(f"Send error: {e}")
    
    def stop(self):
        """Stop the WebSocket client"""
        self.running = False
        if self._websocket:
            try:
                asyncio.run(self._websocket.close())
            except:
                pass


# =============================================================================
# AGENT STATUS WIDGET
# =============================================================================

class AgentStatusCard(QFrame):
    """Individual agent status card"""
    
    def __init__(self, agent_name: str, icon: str = "🤖", parent=None):
        super().__init__(parent)
        self.agent_name = agent_name
        self.icon = icon
        self._setup_ui()
        
    def _setup_ui(self):
        self.setObjectName("card")
        self.setFixedHeight(140)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header
        header = QHBoxLayout()
        
        # Icon and Name
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        
        name_label = QLabel(self.agent_name)
        name_label.setObjectName("section_title")
        name_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        
        header.addWidget(icon_label)
        header.addWidget(name_label)
        header.addStretch()
        
        # Status
        self.status_label = QLabel("OFFLINE")
        self.status_label.setObjectName("status_offline")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #D13438;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11px;
        """)
        
        header.addWidget(self.status_label)
        layout.addLayout(header)
        
        # Info row
        info_layout = QHBoxLayout()
        
        self.tasks_label = QLabel("Tareas: 0")
        self.tasks_label.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        
        self.activity_label = QLabel("Última actividad: --")
        self.activity_label.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        
        info_layout.addWidget(self.tasks_label)
        info_layout.addStretch()
        info_layout.addWidget(self.activity_label)
        
        layout.addLayout(info_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Iniciar")
        self.start_btn.setObjectName("primary_button")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.stop_btn = QPushButton("■ Detener")
        self.stop_btn.setObjectName("secondary_button")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.restart_btn = QPushButton("↻ Reiniciar")
        self.restart_btn.setObjectName("secondary_button")
        self.restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.restart_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
    def update_status(self, status: str, tasks: int = 0, last_activity: str = None):
        """Update agent status display"""
        self.tasks_label.setText(f"Tareas: {tasks}")
        
        if last_activity:
            self.activity_label.setText(f"Última actividad: {last_activity}")
        
        status_styles = {
            "online": "background-color: #6CCB5F; color: white;",
            "working": "background-color: #FCE100; color: #202020;",
            "offline": "background-color: #D13438; color: white;",
            "error": "background-color: #FF6B6B; color: white;"
        }
        
        status_text = {
            "online": "EN LÍNEA",
            "working": "TRABAJANDO",
            "offline": "DESCONECTADO",
            "error": "ERROR"
        }
        
        self.status_label.setText(status_text.get(status, "DESCONECTADO"))
        self.status_label.setStyleSheet(f"""
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11px;
            {status_styles.get(status, status_styles["offline"])}
        """)


# =============================================================================
# RESOURCE GAUGE WIDGET
# =============================================================================

class ResourceGauge(QFrame):
    """Circular resource usage gauge"""
    
    def __init__(self, label: str, color: str = "#0078D4", parent=None):
        super().__init__(parent)
        self.label = label
        self.color = color
        self.value = 0
        self._setup_ui()
        
    def _setup_ui(self):
        self.setObjectName("card")
        self.setFixedSize(120, 120)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        
        # Value label
        self.value_label = QLabel("0%")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {self.color};
        """)
        
        # Name label
        name_label = QLabel(self.label)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #A0A0A0; font-size: 11px;")
        
        # Progress bar (simulated gauge)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        
        layout.addStretch()
        layout.addWidget(self.value_label)
        layout.addWidget(name_label)
        layout.addWidget(self.progress)
        layout.addStretch()
        
    def set_value(self, value: int):
        """Update gauge value"""
        self.value = max(0, min(100, value))
        self.value_label.setText(f"{self.value}%")
        self.progress.setValue(self.value)


# =============================================================================
# DASHBOARD WIDGET
# =============================================================================

class DashboardWidget(QWidget):
    """Dashboard - System overview"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("📊 DASHBOARD")
        title.setObjectName("section_title")
        title.setStyleSheet("font-size: 20px; font-weight: 600; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Quick status row
        status_row = QHBoxLayout()
        
        # Connection status card
        self.connection_card = QFrame()
        self.connection_card.setObjectName("card")
        conn_layout = QVBoxLayout(self.connection_card)
        
        conn_header = QLabel("🔗 PUERTO BRIDGE")
        conn_header.setStyleSheet("font-weight: 600; font-size: 13px;")
        
        self.conn_status = QLabel("● CONECTANDO...")
        self.conn_status.setObjectName("status_indicator")
        self.conn_status.setStyleSheet("color: #FCE100; font-weight: 600;")
        
        conn_layout.addWidget(conn_header)
        conn_layout.addWidget(self.conn_status)
        
        status_row.addWidget(self.connection_card)
        
        # System time card
        time_card = QFrame()
        time_card.setObjectName("card")
        time_layout = QVBoxLayout(time_card)
        
        time_header = QLabel("🕐 HORA DEL SISTEMA")
        time_header.setStyleSheet("font-weight: 600; font-size: 13px;")
        
        self.time_label = QLabel("--:--:--")
        self.time_label.setStyleSheet("font-size: 24px; font-weight: 600; color: #0078D4;")
        
        time_layout.addWidget(time_header)
        time_layout.addWidget(self.time_label)
        
        status_row.addWidget(time_card)
        
        # Active agents card
        agents_card = QFrame()
        agents_card.setObjectName("card")
        agents_layout = QVBoxLayout(agents_card)
        
        agents_header = QLabel("🤖 AGENTES ACTIVOS")
        agents_header.setStyleSheet("font-weight: 600; font-size: 13px;")
        
        self.agents_count = QLabel("0 / 3")
        self.agents_count.setStyleSheet("font-size: 24px; font-weight: 600; color: #6CCB5F;")
        
        agents_layout.addWidget(agents_header)
        agents_layout.addWidget(self.agents_count)
        
        status_row.addWidget(agents_card)
        
        status_row.addStretch()
        layout.addLayout(status_row)
        
        # Resources section
        resources_label = QLabel("📈 RECURSOS DEL SISTEMA")
        resources_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(resources_label)
        
        resources_row = QHBoxLayout()
        
        self.cpu_gauge = ResourceGauge("CPU", "#0078D4")
        self.ram_gauge = ResourceGauge("RAM", "#6CCB5F")
        self.disk_gauge = ResourceGauge("DISCO", "#FCE100")
        
        resources_row.addWidget(self.cpu_gauge)
        resources_row.addWidget(self.ram_gauge)
        resources_row.addWidget(self.disk_gauge)
        resources_row.addStretch()
        
        layout.addLayout(resources_row)
        
        # Agent status section
        agents_section = QLabel("🤖 ESTADO DE AGENTES")
        agents_section.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(agents_section)
        
        # Agent cards row
        agents_row = QHBoxLayout()
        
        self.guillcoder_card = AgentStatusCard("GUILLECODER", "👨‍💻")
        self.athenea_card = AgentStatusCard("ATHENEA", "🧠")
        self.virgilio_card = AgentStatusCard("VIRGILIO", "🌉")
        
        agents_row.addWidget(self.guillcoder_card)
        agents_row.addWidget(self.athenea_card)
        agents_row.addWidget(self.virgilio_card)
        
        layout.addLayout(agents_row)
        
        # Recent events
        events_label = QLabel("📋 EVENTOS RECIENTES")
        events_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(events_label)
        
        self.events_list = QTextEdit()
        self.events_list.setObjectName("log_viewer")
        self.events_list.setMaximumHeight(150)
        self.events_list.setReadOnly(True)
        self.events_list.append("[INFO] Sistema iniciado")
        self.events_list.append("[INFO] Interfaz conectada al PUERTO")
        
        layout.addWidget(self.events_list)
        
        # Add stretch at bottom
        layout.addStretch()
        
    def add_event(self, message: str):
        """Add event to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.events_list.append(f"[{timestamp}] {message}")
        
        # Scroll to bottom
        cursor = self.events_list.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.events_list.setTextCursor(cursor)


# =============================================================================
# AGENTS WIDGET
# =============================================================================

class AgentsWidget(QWidget):
    """Agents management and monitoring"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Left panel - Agent list
        left_panel = QFrame()
        left_panel.setObjectName("card")
        left_panel.setFixedWidth(300)
        
        left_layout = QVBoxLayout(left_panel)
        
        title = QLabel("🤖 AGENTES")
        title.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 16px;")
        left_layout.addWidget(title)
        
        self.agents_list = QListWidget()
        self.agents_list.addItems(["GUILLECODER", "ATHENEA", "VIRGILIO"])
        left_layout.addWidget(self.agents_list)
        
        # Add agent button
        add_btn = QPushButton("+ Añadir Agente")
        add_btn.setObjectName("primary_button")
        left_layout.addWidget(add_btn)
        
        layout.addWidget(left_panel)
        
        # Right panel - Agent details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(16)
        
        # Agent detail header
        header = QHBoxLayout()
        
        self.agent_name_label = QLabel("GUILLECODER")
        self.agent_name_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        
        self.agent_status = QLabel("EN LÍNEA")
        self.agent_status.setStyleSheet("""
            background-color: #6CCB5F;
            color: white;
            padding: 6px 16px;
            border-radius: 4px;
            font-weight: 600;
        """)
        
        header.addWidget(self.agent_name_label)
        header.addStretch()
        header.addWidget(self.agent_status)
        
        right_layout.addLayout(header)
        
        # Tabs for agent info
        tabs = QTabWidget()
        
        # Info tab
        info_tab = QWidget()
        info_layout = QFormLayout(info_tab)
        info_layout.setSpacing(12)
        
        info_layout.addRow("Estado:", QLabel("Activo"))
        info_layout.addRow("Tareas pendientes:", QLabel("2"))
        info_layout.addRow("Última actividad:", QLabel("Hace 5 minutos"))
        info_layout.addRow("Memoria usada:", QLabel("128 MB"))
        info_layout.addRow("Tiempo ejecución:", QLabel("2h 34m"))
        
        tabs.addTab(info_tab, "ℹ️ Información")
        
        # Logs tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        
        self.log_viewer = QTextEdit()
        self.log_viewer.setObjectName("log_viewer")
        self.log_viewer.setReadOnly(True)
        self.log_viewer.append("[2024-01-15 10:30:15] INFO: Agente iniciado")
        self.log_viewer.append("[2024-01-15 10:30:16] INFO: Conectando a PUERTO...")
        self.log_viewer.append("[2024-01-15 10:30:17] INFO: Conexión establecida")
        self.log_viewer.append("[2024-01-15 10:31:00] INFO: Procesando tarea #123")
        self.log_viewer.append("[2024-01-15 10:31:05] INFO: Tarea #123 completada")
        
        logs_layout.addWidget(self.log_viewer)
        
        logs_controls = QHBoxLayout()
        
        clear_logs_btn = QPushButton("🗑️ Limpiar")
        clear_logs_btn.setObjectName("secondary_button")
        
        export_logs_btn = QPushButton("📥 Exportar")
        export_logs_btn.setObjectName("secondary_button")
        
        refresh_logs_btn = QPushButton("🔄 Actualizar")
        refresh_logs_btn.setObjectName("primary_button")
        
        logs_controls.addWidget(clear_logs_btn)
        logs_controls.addWidget(export_logs_btn)
        logs_controls.addStretch()
        logs_controls.addWidget(refresh_logs_btn)
        
        logs_layout.addLayout(logs_controls)
        
        tabs.addTab(logs_tab, "📜 Logs")
        
        # Config tab
        config_tab = QWidget()
        config_layout = QFormLayout(config_tab)
        config_layout.setSpacing(12)
        
        config_layout.addRow("Puerto:", QLabel("5001"))
        config_layout.addRow("Timeout:", QLineEdit("30"))
        config_layout.addRow("Max reintentos:", QLineEdit("3"))
        config_layout.addRow("Auto-reinicio:", QComboBox())
        
        tabs.addTab(config_tab, "⚙️ Configuración")
        
        right_layout.addWidget(tabs)
        
        # Action buttons
        actions = QHBoxLayout()
        
        start_btn = QPushButton("▶ Iniciar")
        start_btn.setObjectName("primary_button")
        
        stop_btn = QPushButton("■ Detener")
        stop_btn.setObjectName("danger_button")
        
        restart_btn = QPushButton("↻ Reiniciar")
        restart_btn.setObjectName("secondary_button")
        
        config_btn = QPushButton("⚙️ Configurar")
        config_btn.setObjectName("secondary_button")
        
        actions.addWidget(start_btn)
        actions.addWidget(stop_btn)
        actions.addWidget(restart_btn)
        actions.addStretch()
        actions.addWidget(config_btn)
        
        right_layout.addLayout(actions)
        
        layout.addWidget(right_panel)


# =============================================================================
# BRIDGE WIDGET
# =============================================================================

class BridgeWidget(QWidget):
    """Bridge/Puente status and monitoring"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("🌉 ESTADO DEL PUERTO")
        title.setStyleSheet("font-size: 20px; font-weight: 600; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Service status row
        services_row = QHBoxLayout()
        
        # WebSocket status
        ws_card = QFrame()
        ws_card.setObjectName("card")
        ws_layout = QVBoxLayout(ws_card)
        ws_layout.setSpacing(12)
        
        ws_header = QLabel("🔌 WebSocket (8765)")
        ws_header.setStyleSheet("font-weight: 600; font-size: 14px;")
        
        self.ws_status = QLabel("🟢 CONECTADO")
        self.ws_status.setStyleSheet("color: #6CCB5F; font-weight: 600; font-size: 13px;")
        
        ws_info = QLabel("Clientes: 3\nMensajes/s: 12")
        ws_info.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        
        ws_layout.addWidget(ws_header)
        ws_layout.addWidget(self.ws_status)
        ws_layout.addWidget(ws_info)
        
        services_row.addWidget(ws_card)
        
        # REST API status
        rest_card = QFrame()
        rest_card.setObjectName("card")
        rest_layout = QVBoxLayout(rest_card)
        rest_layout.setSpacing(12)
        
        rest_header = QLabel("🌐 API REST (8080)")
        rest_header.setStyleSheet("font-weight: 600; font-size: 14px;")
        
        self.rest_status = QLabel("🟢 OPERATIVO")
        self.rest_status.setStyleSheet("color: #6CCB5F; font-weight: 600; font-size: 13px;")
        
        rest_info = QLabel("Endpoints: 15\nPeticiones/min: 45")
        rest_info.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        
        rest_layout.addWidget(rest_header)
        rest_layout.addWidget(self.rest_status)
        rest_layout.addWidget(rest_info)
        
        services_row.addWidget(rest_card)
        
        # Network status
        net_card = QFrame()
        net_card.setObjectName("card")
        net_layout = QVBoxLayout(net_card)
        net_layout.setSpacing(12)
        
        net_header = QLabel("📡 Conectividad")
        net_header.setStyleSheet("font-weight: 600; font-size: 14px;")
        
        self.net_status = QLabel("🟢 ONLINE")
        self.net_status.setStyleSheet("color: #6CCB5F; font-weight: 600; font-size: 13px;")
        
        net_info = QLabel("Latencia: 2ms\nPaquetes: 1.2K")
        net_info.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        
        net_layout.addWidget(net_header)
        net_layout.addWidget(self.net_status)
        net_layout.addWidget(net_info)
        
        services_row.addWidget(net_card)
        
        services_row.addStretch()
        layout.addLayout(services_row)
        
        # Connected agents section
        agents_section = QLabel("🔗 AGENTES CONECTADOS")
        agents_section.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(agents_section)
        
        # Connected agents table
        self.agents_table = QTableWidget()
        self.agents_table.setColumnCount(4)
        self.agents_table.setHorizontalHeaderLabels(["Agente", "Estado", "IP", "Último ping"])
        self.agents_table.setRowCount(3)
        
        agents_data = [
            ["GUILLECODER", "🟢 Activo", "192.168.1.100", "Hace 1s"],
            ["ATHENEA", "🟡 Trabajando", "192.168.1.101", "Hace 3s"],
            ["VIRGILIO", "🟢 Activo", "192.168.1.102", "Hace 2s"]
        ]
        
        for i, row_data in enumerate(agents_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                self.agents_table.setItem(i, j, item)
        
        layout.addWidget(self.agents_table)
        
        # Message queue section
        queue_section = QLabel("📬 COLA DE MENSAJES")
        queue_section.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(queue_section)
        
        queue_layout = QHBoxLayout()
        
        queue_card = QFrame()
        queue_card.setObjectName("card")
        queue_card_layout = QVBoxLayout(queue_card)
        
        self.queue_count = QLabel("5")
        self.queue_count.setStyleSheet("font-size: 32px; font-weight: 700; color: #FCE100;")
        
        queue_label = QLabel("mensajes pendientes")
        queue_label.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        
        queue_card_layout.addWidget(self.queue_count)
        queue_card_layout.addWidget(queue_label)
        
        queue_layout.addWidget(queue_card)
        
        # Queue actions
        clear_queue_btn = QPushButton("🗑️ Limpiar cola")
        clear_queue_btn.setObjectName("secondary_button")
        
        process_queue_btn = QPushButton("⚡ Procesar ahora")
        process_queue_btn.setObjectName("primary_button")
        
        queue_layout.addWidget(clear_queue_btn)
        queue_layout.addWidget(process_queue_btn)
        queue_layout.addStretch()
        
        layout.addLayout(queue_layout)
        
        # Bridge logs
        logs_section = QLabel("📜 LOGS DEL PUERTO")
        logs_section.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(logs_section)
        
        self.bridge_logs = QTextEdit()
        self.bridge_logs.setObjectName("log_viewer")
        self.bridge_logs.setMaximumHeight(200)
        self.bridge_logs.setReadOnly(True)
        self.bridge_logs.append("[10:30:15] INFO: Bridge iniciado en puerto 8765")
        self.bridge_logs.append("[10:30:16] INFO: API REST iniciada en puerto 8080")
        self.bridge_logs.append("[10:30:17] INFO: GUILLECODER conectado")
        self.bridge_logs.append("[10:30:18] INFO: ATHENEA conectada")
        self.bridge_logs.append("[10:30:19] INFO: VIRGILIO conectado")
        
        layout.addWidget(self.bridge_logs)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        clear_logs_btn = QPushButton("🗑️ Limpiar")
        clear_logs_btn.setObjectName("secondary_button")
        
        export_logs_btn = QPushButton("📥 Exportar")
        export_logs_btn.setObjectName("secondary_button")
        
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.setObjectName("primary_button")
        
        log_controls.addWidget(clear_logs_btn)
        log_controls.addWidget(export_logs_btn)
        log_controls.addStretch()
        log_controls.addWidget(refresh_btn)
        
        layout.addLayout(log_controls)


# =============================================================================
# API VAULT WIDGET
# =============================================================================

class APIVaultWidget(QWidget):
    """Secure API management - vault style"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title with lock icon
        title = QLabel("🔐 CAJA FUERTE DE APIs")
        title.setStyleSheet("font-size: 20px; font-weight: 600; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Security notice
        notice = QLabel("⚠️ Los valores de los tokens nunca se muestran en pantalla por seguridad")
        notice.setStyleSheet("color: #FCE100; font-size: 12px; padding: 8px; background-color: #2D2D2D; border-radius: 4px;")
        layout.addWidget(notice)
        
        # API list header
        header = QHBoxLayout()
        
        apis_label = QLabel("📋 APIs CONFIGURADAS")
        apis_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        
        add_api_btn = QPushButton("+ Añadir nueva API")
        add_api_btn.setObjectName("primary_button")
        
        header.addWidget(apis_label)
        header.addStretch()
        header.addWidget(add_api_btn)
        
        layout.addLayout(header)
        
        # API list (names only, no values)
        self.api_table = QTableWidget()
        self.api_table.setColumnCount(4)
        self.api_table.setHorizontalHeaderLabels(["Nombre", "Proveedor", "Estado", "Última verificación"])
        
        # Sample APIs - NO token values shown
        apis_data = [
            ["OpenAI", "OpenAI GPT-4", "🟢 Activo", "Hace 5 minutos"],
            ["Anthropic", "Claude API", "🟢 Activo", "Hace 3 minutos"],
            ["GitHub", "GitHub API", "🟡 Renovando", "Hace 1 hora"],
            ["Telegram", "Telegram Bot", "🟢 Activo", "Hace 1 minuto"],
            ["Discord", "Discord Bot", "🔴 Error", "Hace 10 minutos"]
        ]
        
        self.api_table.setRowCount(len(apis_data))
        for i, row_data in enumerate(apis_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                self.api_table.setItem(i, j, item)
        
        layout.addWidget(self.api_table)
        
        # API actions
        actions = QHBoxLayout()
        
        verify_all_btn = QPushButton("🔍 Verificar todas")
        verify_all_btn.setObjectName("primary_button")
        
        export_keys_btn = QPushButton("📤 Exportar claves (encriptado)")
        export_keys_btn.setObjectName("secondary_button")
        
        import_keys_btn = QPushButton("📥 Importar claves")
        import_keys_btn.setObjectName("secondary_button")
        
        actions.addWidget(verify_all_btn)
        actions.addWidget(export_keys_btn)
        actions.addWidget(import_keys_btn)
        actions.addStretch()
        
        layout.addLayout(actions)
        
        # Selected API details
        details_label = QLabel("ℹ️ DETALLES DE API SELECCIONADA")
        details_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(details_label)
        
        details_card = QFrame()
        details_card.setObjectName("card")
        details_layout = QFormLayout(details_card)
        details_layout.setSpacing(12)
        
        details_layout.addRow("Nombre:", QLabel("OpenAI"))
        details_layout.addRow("Proveedor:", QLabel("OpenAI"))
        details_layout.addRow("Tipo:", QLabel("GPT-4"))
        details_layout.addRow("Estado:", QLabel("🟢 Activo"))
        
        # Token field - masked
        token_field = QLineEdit()
        token_field.setText("sk-••••••••••••••••••••••••••••••")
        token_field.setEchoMode(QLineEdit.EchoMode.Password)
        token_field.setEnabled(False)
        details_layout.addRow("Token:", token_field)
        
        details_layout.addRow("Última verificación:", QLabel("Hace 5 minutos"))
        details_layout.addRow("Límite mensual:", QLabel("$100.00 / $100.00"))
        
        layout.addWidget(details_card)
        
        # API management buttons
        api_actions = QHBoxLayout()
        
        test_btn = QPushButton("🧪 Probar conexión")
        test_btn.setObjectName("primary_button")
        
        renew_btn = QPushButton("🔄 Renovar token")
        renew_btn.setObjectName("secondary_button")
        
        delete_btn = QPushButton("🗑️ Eliminar")
        delete_btn.setObjectName("danger_button")
        
        api_actions.addWidget(test_btn)
        api_actions.addWidget(renew_btn)
        api_actions.addWidget(delete_btn)
        api_actions.addStretch()
        
        layout.addLayout(api_actions)
        
        layout.addStretch()


# =============================================================================
# LABORATORY WIDGET
# =============================================================================

class LaboratoryWidget(QWidget):
    """LABORATORIO - CAT1-CAT12 browser"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Left panel - Categories tree
        left_panel = QFrame()
        left_panel.setObjectName("card")
        left_panel.setFixedWidth(280)
        
        left_layout = QVBoxLayout(left_panel)
        
        title = QLabel("🧪 LABORATORIO")
        title.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 16px;")
        left_layout.addWidget(title)
        
        # Category tree
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("Categorías")
        
        # Categories
        categories = [
            ("CAT1_ELECTRONICA", "📱"),
            ("CAT2_DMX", "🎛️"),
            ("CAT3_LASERMASTER", "🔴"),
            ("CAT4_QLC+", "💡"),
            ("CAT5_SISTEMA", "⚙️"),
            ("CAT6_HARDWARE", "🔧"),
            ("CAT7_WINDOWS", "🪟"),
            ("CAT8_AGENTES", "🤖"),
            ("CAT9_BRIDGE", "🌉"),
            ("CAT10_DESARROLLO", "💻"),
            ("CAT11_AIGEN", "🧠"),
            ("CAT12_DIY", "🔨")
        ]
        
        for cat_name, cat_icon in categories:
            item = QTreeWidgetItem([f"{cat_icon} {cat_name}"])
            self.category_tree.addTopLevelItem(item)
        
        left_layout.addWidget(self.category_tree)
        
        # Bench and Review sections
        sections_label = QLabel("📁 SECCIONES")
        sections_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #A0A0A0; margin-top: 16px;")
        left_layout.addWidget(sections_label)
        
        bench_btn = QPushButton("📋 BENCH (Trabajo actual)")
        bench_btn.setObjectName("secondary_button")
        bench_btn.setCheckable(True)
        bench_btn.setChecked(True)
        
        review_btn = QPushButton("📝 REVISAR (Pendientes)")
        review_btn.setObjectName("secondary_button")
        review_btn.setCheckable(True)
        
        archive_btn = QPushButton("📦 ARCHIVO")
        archive_btn.setObjectName("secondary_button")
        archive_btn.setCheckable(True)
        
        left_layout.addWidget(bench_btn)
        left_layout.addWidget(review_btn)
        left_layout.addWidget(archive_btn)
        
        left_layout.addStretch()
        
        layout.addWidget(left_panel)
        
        # Right panel - Projects
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(16)
        
        # Header
        header = QHBoxLayout()
        
        section_title = QLabel("📋 BENCH")
        section_title.setStyleSheet("font-size: 18px; font-weight: 600;")
        
        new_project_btn = QPushButton("+ Nuevo Proyecto")
        new_project_btn.setObjectName("primary_button")
        
        header.addWidget(section_title)
        header.addStretch()
        header.addWidget(new_project_btn)
        
        right_layout.addLayout(header)
        
        # Projects table
        projects_label = QLabel("PROYECTOS")
        projects_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #A0A0A0;")
        right_layout.addWidget(projects_label)
        
        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(4)
        self.projects_table.setHorizontalHeaderLabels(["Nombre", "Categoría", "Estado", "Última modificación"])
        
        projects_data = [
            ["lecciones_cajon", "CAT1_ELECTRONICA", "🟡 En desarrollo", "Hace 2 horas"],
            ["virgilio_v3", "CAT8_AGENTES", "🟢 Activo", "Ayer"],
            ["athenea_engine", "CAT8_AGENTES", "🟢 Activo", "Hace 3 días"]
        ]
        
        self.projects_table.setRowCount(len(projects_data))
        for i, row_data in enumerate(projects_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                self.projects_table.setItem(i, j, item)
        
        right_layout.addWidget(self.projects_table)
        
        # Project actions
        actions = QHBoxLayout()
        
        clone_btn = QPushButton("📋 Clonar a BENCH")
        clone_btn.setObjectName("primary_button")
        
        validate_btn = QPushButton("✓ Validar")
        validate_btn.setObjectName("secondary_button")
        
        archive_btn = QPushButton("📦 Archivar")
        archive_btn.setObjectName("secondary_button")
        
        delete_btn = QPushButton("🗑️ Eliminar")
        delete_btn.setObjectName("danger_button")
        
        actions.addWidget(clone_btn)
        actions.addWidget(validate_btn)
        actions.addWidget(archive_btn)
        actions.addWidget(delete_btn)
        actions.addStretch()
        
        right_layout.addLayout(actions)
        
        # File viewer section
        viewer_label = QLabel("📄 ARCHIVOS DEL PROYECTO")
        viewer_label.setStyleSheet("font-weight: 600; font-size: 13px; color: #A0A0A0;")
        right_layout.addWidget(viewer_label)
        
        # File tree
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Archivos")
        
        # Sample files
        root = QTreeWidgetItem(["📁 lecciones_cajon"])
        child1 = QTreeWidgetItem(["📄 lecciones_cajon.md"])
        child2 = QTreeWidgetItem(["📁 media"])
        child2.addChild(QTreeWidgetItem(["🖼️ imagen1.png"]))
        child2.addChild(QTreeWidgetItem(["🖼️ diagrama.jpg"]))
        root.addChild(child1)
        root.addChild(child2)
        
        self.file_tree.addTopLevelItem(root)
        self.file_tree.expandAll()
        
        right_layout.addWidget(self.file_tree)
        
        # File viewer
        self.file_viewer = QTextEdit()
        self.file_viewer.setMaximumHeight(150)
        self.file_viewer.setReadOnly(True)
        self.file_viewer.setPlainText("# Lecciones del Cajón\n\nContenido del archivo...")
        
        right_layout.addWidget(self.file_viewer)
        
        layout.addWidget(right_panel)


# =============================================================================
# CAJON WIDGET
# =============================================================================

class CajonWidget(QWidget):
    """CAJON - File inbox for processing"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("📦 CAJÓN - Entrada de Archivos")
        title.setStyleSheet("font-size: 20px; font-weight: 600; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Info card
        info_card = QFrame()
        info_card.setObjectName("card")
        info_layout = QHBoxLayout(info_card)
        
        info_layout.addWidget(QLabel("📁 Ruta:"))
        
        path_label = QLabel("C:/a2/CAMASOTS/CAJON/")
        path_label.setStyleSheet("color: #0078D4;")
        
        info_layout.addWidget(path_label)
        info_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.setObjectName("secondary_button")
        
        open_folder_btn = QPushButton("📂 Abrir carpeta")
        open_folder_btn.setObjectName("secondary_button")
        
        info_layout.addWidget(refresh_btn)
        info_layout.addWidget(open_folder_btn)
        
        layout.addWidget(info_card)
        
        # Files table
        files_label = QLabel("📋 ARCHIVOS ESPERANDO PROCESAMIENTO")
        files_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(files_label)
        
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(5)
        self.files_table.setHorizontalHeaderLabels(["Nombre", "Tipo", "Tamaño", "Fecha entrada", "Estado"])
        
        files_data = [
            ["input_dmx.json", "JSON", "2.4 KB", "Hace 10 min", "⏳ Pendiente"],
            ["config.yaml", "YAML", "1.1 KB", "Hace 1 hora", "⏳ Pendiente"],
            ["data.csv", "CSV", "156 KB", "Ayer", "🔄 Procesando"],
            ["script.py", "Python", "8.7 KB", "Ayer", "✅ Completado"]
        ]
        
        self.files_table.setRowCount(len(files_data))
        for i, row_data in enumerate(files_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                self.files_table.setItem(i, j, item)
        
        layout.addWidget(self.files_table)
        
        # Actions row
        actions = QHBoxLayout()
        
        process_btn = QPushButton("⚙️ Procesar con...")
        process_btn.setObjectName("primary_button")
        
        select_agent_combo = QComboBox()
        select_agent_combo.addItems(["GUILLECODER", "ATHENEA", "VIRGILIO"])
        
        chimney_btn = QPushButton("🔥 Enviar a CHIMENEA")
        chimney_btn.setObjectName("danger_button")
        
        delete_btn = QPushButton("🗑️ Eliminar")
        delete_btn.setObjectName("secondary_button")
        
        actions.addWidget(process_btn)
        actions.addWidget(select_agent_combo)
        actions.addWidget(chimney_btn)
        actions.addWidget(delete_btn)
        actions.addStretch()
        
        layout.addLayout(actions)
        
        # Processing result section
        result_label = QLabel("📤 RESULTADO DEL PROCESAMIENTO")
        result_label.setStyleSheet("font-weight: 600; font-size: 14px; color: #A0A0A0;")
        layout.addWidget(result_label)
        
        self.result_viewer = QTextEdit()
        self.result_viewer.setMaximumHeight(150)
        self.result_viewer.setObjectName("log_viewer")
        self.result_viewer.setReadOnly(True)
        self.result_viewer.append(">>> Seleccione un archivo y haga clic en 'Procesar con...'")
        
        layout.addWidget(self.result_viewer)
        
        # Export results
        export_layout = QHBoxLayout()
        
        export_btn = QPushButton("📥 Exportar resultado")
        export_btn.setObjectName("secondary_button")
        
        copy_btn = QPushButton("📋 Copiar al portapapeles")
        copy_btn.setObjectName("secondary_button")
        
        export_layout.addWidget(export_btn)
        export_layout.addWidget(copy_btn)
        export_layout.addStretch()
        
        layout.addLayout(export_layout)
        
        layout.addStretch()


# =============================================================================
# SETTINGS WIDGET
# =============================================================================

class SettingsWidget(QWidget):
    """Settings and configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("⚙️ CONFIGURACIÓN")
        title.setStyleSheet("font-size: 20px; font-weight: 600; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # General settings
        general_group = QGroupBox("📁 Configuración General")
        general_layout = QFormLayout(general_group)
        general_layout.setSpacing(16)
        
        base_path = QLineEdit("C:/a2/CAMASOTS")
        base_path.setReadOnly(True)
        
        general_layout.addRow("Ruta base de CAMASOTS:", base_path)
        general_layout.addRow("Directorio de datos:", QLineEdit("C:/a2/CAMASOTS/DATABASE"))
        general_layout.addRow("Directorio de logs:", QLineEdit("C:/a2/CAMASOTS/LOGS"))
        
        browse_btn = QPushButton("📂 Examinar...")
        general_layout.addRow("", browse_btn)
        
        layout.addWidget(general_group)
        
        # Network settings
        network_group = QGroupBox("🌐 Configuración de Red")
        network_layout = QFormLayout(network_group)
        network_layout.setSpacing(16)
        
        network_layout.addRow("Router:", QLineEdit("192.168.1.1"))
        network_layout.addRow("Canal WiFi principal:", QComboBox())
        network_layout.addRow("Canal WiFi secundario:", QComboBox())
        network_layout.addRow("DNS primario:", QLineEdit("8.8.8.8"))
        network_layout.addRow("DNS secundario:", QLineEdit("1.1.1.1"))
        
        layout.addWidget(network_group)
        
        # Resources settings
        resources_group = QGroupBox("💾 Límites de Recursos")
        resources_layout = QFormLayout(resources_group)
        resources_layout.setSpacing(16)
        
        resources_layout.addRow("RAM máxima para agentes:", QComboBox())
        resources_layout.addRow("Limpiar TEMP cada:", QComboBox())
        resources_layout.addRow("Máximo tamaño de logs:", QComboBox())
        resources_layout.addRow("Rotación de logs:", QComboBox())
        
        layout.addWidget(resources_group)
        
        # Interface settings
        interface_group = QGroupBox("🎨 Interfaz")
        interface_layout = QFormLayout(interface_group)
        interface_layout.setSpacing(16)
        
        theme_combo = QComboBox()
        theme_combo.addItems(["Oscuro (Windows 11)", "Claro", "Alto contraste"])
        
        interface_layout.addRow("Tema:", theme_combo)
        interface_layout.addRow("Animaciones:", QComboBox())
        interface_layout.addRow("Notificaciones:", QComboBox())
        interface_layout.addRow("Actualización automática:", QComboBox())
        
        layout.addWidget(interface_group)
        
        # Backup settings
        backup_group = QGroupBox("💼 Backup y Restauración")
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setSpacing(12)
        
        backup_info = QLabel("Crear copias de seguridad de la configuración y datos del sistema.")
        backup_info.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        backup_layout.addWidget(backup_info)
        
        backup_buttons = QHBoxLayout()
        
        create_backup_btn = QPushButton("💾 Crear Backup")
        create_backup_btn.setObjectName("primary_button")
        
        restore_btn = QPushButton("📥 Restaurar")
        restore_btn.setObjectName("secondary_button")
        
        auto_backup_combo = QComboBox()
        auto_backup_combo.addItems(["Automático: Diario", "Automático: Semanal", "Manual"])
        
        backup_buttons.addWidget(create_backup_btn)
        backup_buttons.addWidget(restore_btn)
        backup_buttons.addStretch()
        
        backup_layout.addLayout(backup_buttons)
        backup_layout.addWidget(auto_backup_combo)
        
        layout.addWidget(backup_group)
        
        # Save button
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        save_btn = QPushButton("💾 Guardar configuración")
        save_btn.setObjectName("primary_button")
        save_btn.setFixedWidth(200)
        
        reset_btn = QPushButton("↺ Restaurar valores por defecto")
        reset_btn.setObjectName("secondary_button")
        
        save_layout.addWidget(reset_btn)
        save_layout.addWidget(save_btn)
        
        layout.addLayout(save_layout)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)


# =============================================================================
# SIDEBAR WIDGET
# =============================================================================

class SidebarWidget(QWidget):
    """Left sidebar navigation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.selected_button = None
        
    def _setup_ui(self):
        self.setObjectName("sidebar")
        self.setFixedWidth(220)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 16, 8, 16)
        
        # Logo/Title
        logo = QLabel("CAMASOTS")
        logo.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #0078D4;
            padding: 8px 12px;
            margin-bottom: 16px;
        """)
        
        layout.addWidget(logo)
        
        # Navigation buttons
        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("🤖", "Agentes", "agents"),
            ("🌉", "Puente", "bridge"),
            ("🔐", "APIs", "apis"),
            ("🧪", "Laboratorio", "laboratory"),
            ("📦", "Cajón", "cajon"),
            ("⚙️", "Configuración", "settings")
        ]
        
        self.nav_buttons = {}
        
        for icon, text, page_id in nav_items:
            btn = QPushButton(f"  {icon}  {text}")
            btn.setObjectName("nav_button")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setProperty("page_id", page_id)
            
            self.nav_buttons[page_id] = btn
            layout.addWidget(btn)
            
        layout.addStretch()
        
        # Version info
        version = QLabel("v1.0.0")
        version.setStyleSheet("color: #666666; font-size: 11px; padding: 8px;")
        layout.addWidget(version)
        
    def select_button(self, page_id: str):
        """Select a navigation button"""
        if self.selected_button:
            self.selected_button.setChecked(False)
        
        if page_id in self.nav_buttons:
            self.nav_buttons[page_id].setChecked(True)
            self.selected_button = self.nav_buttons[page_id]


# =============================================================================
# MAIN WINDOW
# =============================================================================

class MainWindow(QMainWindow):
    """CAMASOTS Command Center - Main Window"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("CAMASOTS COMMAND CENTER")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 900)
        
        # Apply Windows 11 dark theme
        self.setStyleSheet(WINDOWS11_STYLESHEET)
        
        # Setup UI
        self._setup_ui()
        
        # WebSocket client
        self.ws_client = WebSocketClient("ws://localhost:8765")
        self.ws_client.message_received.connect(self._on_websocket_message)
        self.ws_client.connection_status.connect(self._on_connection_status)
        self.ws_client.start()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(2000)
        
        # Status bar
        self.statusBar().showMessage("Iniciando...")
        
    def _setup_ui(self):
        """Setup the main UI"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.sidebar = SidebarWidget()
        main_layout.addWidget(self.sidebar)
        
        # Connect sidebar buttons
        for page_id, btn in self.sidebar.nav_buttons.items():
            btn.clicked.connect(lambda checked, pid=page_id: self._on_nav_click(pid))
        
        # Content area
        self.content_stack = QStackedWidget()
        
        # Create all section widgets
        self.dashboard = DashboardWidget()
        self.agents = AgentsWidget()
        self.bridge = BridgeWidget()
        self.apis = APIVaultWidget()
        self.laboratory = LaboratoryWidget()
        self.cajon = CajonWidget()
        self.settings = SettingsWidget()
        
        # Add to stack
        self.content_stack.addWidget(self.dashboard)      # 0
        self.content_stack.addWidget(self.agents)          # 1
        self.content_stack.addWidget(self.bridge)          # 2
        self.content_stack.addWidget(self.apis)            # 3
        self.content_stack.addWidget(self.laboratory)      # 4
        self.content_stack.addWidget(self.cajon)          # 5
        self.content_stack.addWidget(self.settings)       # 6
        
        main_layout.addWidget(self.content_stack)
        
        # Select dashboard by default
        self.sidebar.select_button("dashboard")
        self.content_stack.setCurrentIndex(0)
        
    def _on_nav_click(self, page_id: str):
        """Handle navigation click"""
        self.sidebar.select_button(page_id)
        
        page_index = {
            "dashboard": 0,
            "agents": 1,
            "bridge": 2,
            "apis": 3,
            "laboratory": 4,
            "cajon": 5,
            "settings": 6
        }
        
        if page_id in page_index:
            self.content_stack.setCurrentIndex(page_index[page_id])
            self.statusBar().showMessage(f"Navegando a {page_id.capitalize()}...")
            
    def _on_websocket_message(self, message: dict):
        """Handle incoming WebSocket messages"""
        msg_type = message.get("type", "")
        
        if msg_type == "heartbeat":
            self._update_from_heartbeat(message)
        elif msg_type == "agent_status":
            self._update_agent_status(message)
        elif msg_type == "event":
            self.dashboard.add_event(message.get("message", ""))
            
    def _on_connection_status(self, connected: bool):
        """Handle connection status changes"""
        if connected:
            self.dashboard.connection_card.findChild(QLabel, "conn_status").setText("● CONECTADO")
            self.dashboard.connection_card.findChild(QLabel, "conn_status").setStyleSheet(
                "color: #6CCB5F; font-weight: 600;"
            )
            self.statusBar().showMessage("Conectado al PUERTO", 3000)
            self.dashboard.add_event("Conectado al PUERTO bridge")
        else:
            self.dashboard.connection_card.findChild(QLabel, "conn_status").setText("● DESCONECTADO")
            self.dashboard.connection_card.findChild(QLabel, "conn_status").setStyleSheet(
                "color: #D13438; font-weight: 600;"
            )
            self.statusBar().showMessage("Desconectado del PUERTO", 3000)
            
    def _update_from_heartbeat(self, message: dict):
        """Update UI from heartbeat message"""
        agents = message.get("agents", {})
        
        # Update agent cards
        if "GUILLECODER" in agents:
            data = agents["GUILLECODER"]
            self.dashboard.guillcoder_card.update_status(
                data.get("status", "offline"),
                data.get("tasks", 0)
            )
            
        if "ATHENEA" in agents:
            data = agents["ATHENEA"]
            self.dashboard.athenea_card.update_status(
                data.get("status", "offline"),
                data.get("tasks", 0)
            )
            
        if "VIRGILIO" in agents:
            data = agents["VIRGILIO"]
            self.dashboard.virgilio_card.update_status(
                data.get("status", "offline"),
                data.get("tasks", 0)
            )
            
        # Update agent count
        online_count = sum(1 for a in agents.values() if a.get("status") != "offline")
        self.dashboard.agents_count.setText(f"{online_count} / 3")
        
    def _update_time(self):
        """Update system time display"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.dashboard.time_label.setText(current_time)
        
    def _auto_refresh(self):
        """Auto refresh data"""
        # Simulate resource updates
        import random
        cpu = random.randint(20, 60)
        ram = random.randint(30, 70)
        disk = random.randint(40, 55)
        
        self.dashboard.cpu_gauge.set_value(cpu)
        self.dashboard.ram_gauge.set_value(ram)
        self.dashboard.disk_gauge.set_value(disk)
        
    def closeEvent(self, event):
        """Handle window close"""
        self.ws_client.stop()
        self.ws_client.wait()
        event.accept()


# =============================================================================
# ENTRY POINT
# =============================================================================

def main():
    """Main entry point"""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("CAMASOTS")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("CAMASOTS")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
