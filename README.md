# 🛡️ Argus v1.0

Professional Network Security Tool for Learning Red Team Skills and Network Analysis

**Educational Use Only** | **For Computer Science & Cybersecurity Students** | **Penetration Testing Learning**

---

## 📋 Overview

Argus is a **comprehensive educational application** that teaches fundamental network security concepts through practical implementation:

- **Network Discovery** via ARP scanning
- **Man-in-the-Middle (MITM) Attacks** using ARP spoofing
- **Packet Analysis** and network sniffing with filtering
- **Network Visualization** with interactive topology mapping
- **Real-time Monitoring** with color-coded logging

### Key Features

✅ **Network Scanner** - Discover all active hosts on your network
✅ **ARP Spoofer** - Perform MITM attacks using ARP spoofing
✅ **Packet Sniffer** - Capture and analyze TCP, HTTP, DNS traffic
✅ **Smart Filters** - Detect specific packet types (TCP/HTTP/DNS/IP)
✅ **Network Map** - Visual topology of discovered hosts
✅ **Color Logging** - Magenta alerts, red errors, green success
✅ **Professional GUI** - Built with PySide6 (Qt6)

---

## 🎓 Perfect For

- 👨‍🎓 **Computer Science Students** learning network fundamentals
- 🔐 **Cybersecurity Learners** studying MITM attacks
- 🎯 **Red Team Training** and penetration testing education
- 📚 **Network Administration** education
- 🛡️ **Security Awareness** demonstrations

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.7+
python --version

# Administrator/Root privileges required!
```

### Installation

```bash
# Clone your published repository
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
# Must run as Administrator!
python mitm_gui.py
```

**Windows**: Right-click PowerShell → Run as Administrator  
**Linux/Mac**: Use `sudo python mitm_gui.py`

---

## ✅ Before Publishing to GitHub

- Use a private repository if this is meant only for a lab or class exercise.
- Remove any real capture files, logs, host lists, passwords, or other generated network data.
- Keep only demo-safe sample files in the repository.
- Review the README, screenshots, and comments for any local machine names, paths, or personal details.
- Add or update `.gitignore` entries for any new output folders you create later.

---

## 📖 How It Works

### 1. Network Discovery (Scanner)

```
Interface → Scan Network → Find All Hosts → Display Results
         (ARP Requests)   (Parse Replies)
```

Discovers all active devices on your network using ARP protocol:
- Sends ARP broadcasts to all IPs in your network range
- Collects MAC addresses from replies
- Shows results in real-time with color coding

**Example Output:**
```
[10:30:15] [*] Using interface: Ethernet
[10:30:15] [*] Network: 192.168.1.0/24
[10:30:18] [+] HOST FOUND: 192.168.1.50 → 3c:97:0e:a5:2d:11
[10:30:18] [+] HOST FOUND: 192.168.1.100 → b2:4f:1a:c8:7e:44
[10:30:21] [✓] Scan complete: 5 hosts discovered
```

### 2. ARP Spoofing (MITM Attack)

```
┌─────────────┐
│    Victim   │
└─────────────┘
      ↑ Thinks I'm Gateway
      │
┌─────────────┐         ┌─────────────┐
│  Attacker   │←────────│   Gateway   │
└─────────────┘         └─────────────┘
  Thinks victim's MAC    Thinks I'm Victim
```

Positions attacker between victim and gateway:
1. Get MAC addresses of victim and gateway
2. Send forged ARP packets every second
3. Victim thinks attacker is gateway
4. Gateway thinks attacker is victim
5. All traffic flows through attacker
6. Restore ARP tables when done

**Example Output:**
```
[10:35:04] [+] Target: 192.168.1.100 (3c:97:0e:a5:2d:11)
[10:35:04] [+] Gateway: 192.168.1.1 (a4:9e:3d:2b:15:cc)
[10:35:04] [*] Starting ARP spoof...
[10:35:34] [*] Packets sent: 30
[10:36:00] [✓] ARP spoof stopped and tables restored
```

### 3. Packet Sniffing (Traffic Analysis)

```
Configure Filters → Sniff Packets → Detect Types → Log Details
   (TCP/HTTP/DNS)   (Live capture)  (Parse data)
```

Captures and analyzes network traffic in real-time:

**TCP Detection:**
```
[TCP] 192.168.1.100:54321 → 8.8.8.8:53
PAYLOAD: DNS request data...
```

**HTTP Detection:**
```
[HTTP REQUEST] DETECTED!
Host: www.google.com
Path: /search?q=network+security
Method: GET
```

**DNS Detection:**
```
[DNS] QUERY DETECTED!
Domain: facebook.com
```

---

## 📊 Application Architecture

### Core Components

```python
NetworkScanner      → Discovers hosts via ARP
  ├─ scan()              Initiate scan
  ├─ _scan_thread()      Background scanning
  └─ Signal: finished()  Results ready

ARPSpoofer          → MITM attack via ARP spoofing
  ├─ start_spoof()       Start spoofing
  ├─ stop_spoof()        Stop spoofing
  ├─ _get_mac()          Resolve MAC addresses
  └─ _spoof()            Send forged ARP packet

PacketSniffer       → Capture and analyze traffic
  ├─ start_sniff()       Start capturing
  ├─ stop_sniff()        Stop capturing
  └─ set_detection_filters()  Configure detection

ColoredLogWidget     → Display colored messages
  └─ log()           Add timestamped message

NetworkMapCanvas    → Visualize network topology
  └─ update_network()    Draw network graph
```

### Threading Model

```
Main GUI Thread
  ├─ Scanner Thread (daemon)
  ├─ Spoofer Thread (daemon)
  └─ Sniffer Thread (daemon)

Signals: Thread-safe communication
```

### Color Scheme

| Color  | Hex     | Use Case          |
|--------|---------|-------------------|
| 🔴 Red | #ff4444 | Errors            |
| 🟡 Yellow | #ffaa00 | Warnings         |
| 🟢 Green | #44ff44 | Success          |
| 🟣 Magenta | #ff0088 | **Detections!** |
| 🔵 Cyan | #00ffff | Information      |

---

## 🔧 Requirements

### Python Packages

```
PySide6==6.x.x          # GUI framework
scapy==2.x.x            # Packet manipulation
psutil==5.x.x           # System/network info
matplotlib==3.x.x       # Visualization
networkx==2.x.x         # Graph visualization
```

### System Requirements

- **Windows**: Administrator privileges
- **Linux**: Root (sudo) privileges
- **macOS**: Admin access
- Python 3.7 or higher
- Network interface with proper drivers

---

## 📚 Educational Concepts Covered

### Network Protocols

- **ARP (Address Resolution Protocol)** - Layer 2 discovery
- **Ethernet Frames** - Link layer communication
- **IP Headers** - Network layer routing
- **TCP/UDP** - Transport layer protocols
- **HTTP** - Application layer protocol
- **DNS** - Domain name resolution

### Security Concepts

- **MITM Attacks** - How to position between two hosts
- **ARP Spoofing** - Exploiting protocol weaknesses
- **Traffic Interception** - Capturing unencrypted data
- **Network Reconnaissance** - Discovery techniques
- **Packet Analysis** - Understanding traffic patterns
- **Defense Mechanisms** - How to detect/prevent attacks

### Programming Concepts

- **Multi-threading** - Async operations
- **Qt Signals/Slots** - Thread-safe communication
- **GUI Development** - Professional interfaces
- **Network Programming** - Socket operations
- **Data Structures** - Organizing network data
- **Error Handling** - Graceful failure recovery

---

## 📖 Complete Documentation

| Document | Purpose |
|----------|---------|
| `APP_LOGIC.txt` | **Complete function documentation** |
| `README.md` | This file |
| `PROFESSIONAL_FEATURES.txt` | Feature guide |
| `COLOR_FEATURE_GUIDE.txt` | Color meaning reference |
| `EXAMPLE_LOG_OUTPUT.txt` | Sample execution output |

---

## ⚙️ Usage Workflow

### Step 1: Network Scan

```
1. Select network interface from dropdown
2. Click "🔍 Scan Network"
3. Wait for results (usually 5-10 seconds)
4. See discovered hosts in table
5. Network map updates automatically
```

### Step 2: Setup Attack

```
1. Click on a host in the table
2. Enter Target IP (the victim)
3. Enter Gateway IP (usually 192.168.1.1)
4. Click "⚡ Start ARP Spoof"
```

### Step 3: Sniff Traffic

```
1. Enable detection filters (TCP, HTTP, DNS)
2. Enter Victim IP
3. Click "📡 Start Sniffing"
4. Watch for 🟣 MAGENTA detections in log
5. See detailed packet information
```

### Step 4: Stop & Cleanup

```
1. Click "⏹️ Stop ARP Spoof"
2. Click "⏹️ Stop Sniffing"
3. Network restored to normal
```

---

## 🛡️ Legal & Ethical Guidelines

### ⚠️ Important

This tool is **for educational purposes only**:

```
✓ Use on networks you own
✓ Use in controlled lab environments
✓ Use to learn security concepts
✗ Never use without permission
✗ Never use for malicious purposes
✗ Unauthorized access is ILLEGAL
```

### Recommended Setup

- Virtual machines (VirtualBox, VMware)
- Isolated test network
- No real victim data
- Proper lab documentation

### Legal Consequences

Unauthorized network access or interception can result in:
- Criminal charges
- Civil lawsuits
- Imprisonment
- Fines
- Professional consequences

---

## 🔍 Detection & Defense

### How Admins Detect MITM

- ARP monitoring tools detect spoofing
- IDS/IPS systems alert on suspicious traffic
- Network baseline monitoring
- Certificate validation failures
- Encrypted traffic inspection

### Defenses Against MITM

- HTTPS/TLS encryption
- VPN usage
- Static ARP bindings
- 802.1X network authentication
- Network segmentation
- Defense in depth strategies

---

## 📝 Example Scenarios

### Scenario 1: Educational Lab

```
Learning Objective: Understand ARP spoofing
Setup: Virtual machines, isolated network
Steps:
  1. Scan network (find victim VM)
  2. Perform ARP spoof (become MITM)
  3. Sniff HTTP traffic (unencrypted)
  4. Observe packet details
  5. Restore network
Lesson: Why HTTPS and encryption matter!
```

### Scenario 2: Defensive Testing

```
Learning Objective: Detect MITM attacks
Setup: Monitoring tools + MITM tool
Steps:
  1. Run MITM attack
  2. Monitor network with Wireshark/tcpdump
  3. Identify ARP spoofing attempts
  4. Detect unusual traffic patterns
  5. Alert on detections
Lesson: How to detect and respond to attacks!
```

---

## 🐛 Troubleshooting

### "No interface found"

```
✓ Check network connection
✓ Run as Administrator
✓ Virtual machines may need bridge mode
✓ Check if network card drivers are installed
```

### "Hosts not found during scan"

```
✓ Make sure interface is selected
✓ Check gateway IP is correct
✓ Hosts must be on same network
✓ Some firewalls may block ARP
```

### "Permission Denied"

```
✓ Must run as Administrator (Windows)
✓ Must use sudo (Linux)
✓ Scapy needs raw socket access
```

### "ARP spoof not working"

```
✓ Run as Administrator
✓ Check IP addresses are correct
✓ Both target and gateway must be reachable
✓ Try pinging them first
```

---

## 📊 Performance

- **Network Scan**: 5-30 seconds (depends on network)
- **ARP Spoof**: Continuous (1 packet/second)
- **Packet Sniffer**: Real-time capture (depends on traffic)
- **GUI Response**: <100ms (threaded operations)

---

## 🤝 Contributing

This is an **educational project**. Contributions welcome!

- Bug reports
- Documentation improvements
- Educational enhancements
- Lab exercise suggestions
- Security improvements

---

## 📄 License

**Educational Use Only**

This software is provided for learning purposes in:
- University courses
- Cybersecurity training
- Penetration testing education
- Security research (authorized)

Not for commercial use or unauthorized testing.

---

## 👨‍💼 Author

**Argus** - Red Team & Security Educator

Created for computer science and cybersecurity students learning network security.

---

## 📞 Support & Questions

For questions about:

- **Networking concepts**: Check APP_LOGIC.txt
- **How to use the app**: Read PROFESSIONAL_FEATURES.txt
- **Color meanings**: See COLOR_FEATURE_GUIDE.txt
- **Example output**: View EXAMPLE_LOG_OUTPUT.txt

---

## 🔗 Resources

### Learning Materials

- [Scapy Documentation](https://scapy.readthedocs.io/)
- [ARP Protocol](https://en.wikipedia.org/wiki/Address_Resolution_Protocol)
- [MITM Attacks](https://en.wikipedia.org/wiki/Man-in-the-middle_attack)
- [Network Security Basics](https://www.coursera.org/learn/network-security)

### Related Tools

- **Wireshark** - Packet analysis
- **tcpdump** - Command-line packet capture
- **Ettercap** - MITM attack framework
- **Bettercap** - Reverse engineering framework

---

## ✨ Features at a Glance

```
┌─ Argus v1.0 ─┐
├─ 🔍 Network Scanner        │
│   └─ ARP scanning          │
│   └─ Host discovery        │
├─ ⚡ ARP Spoofer           │
│   └─ MITM positioning      │
│   └─ Traffic interception  │
├─ 📡 Packet Sniffer        │
│   └─ TCP detection         │
│   └─ HTTP capture          │
│   └─ DNS monitoring        │
├─ 🎨 Professional GUI      │
│   └─ Color-coded logging   │
│   └─ Network visualization │
└─ 🛡️ Educational Tool     │
    └─ Learn security        │
```

---

## 🎯 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Design upgrade, borderless inputs, Argus branding |
| 3.0 | Jan 2026 | Color logging, detection filters, professional design |
| 2.0 | 2024 | GUI, network scanning, visualization |
| 1.0 | 2024 | Basic ARP spoofing script |

---

**Remember**: Use ethically and legally! 🛡️

For educational purposes only. Unauthorized access is illegal.

---

Version: 1.0  
Author: Argus  
Date: January 16, 2026  
Category: Educational | Cybersecurity | Network Security
