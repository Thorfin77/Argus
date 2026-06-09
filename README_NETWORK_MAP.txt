MITM ATTACK TOOL WITH NETWORK MAP VISUALIZATION
=================================================

VERSION: 2.0 - Network Map Edition
NEW FEATURES: Interactive network visualization with networkx and matplotlib

REQUIREMENTS:
=============
- Python 3.7+
- Administrator privileges (Windows)
- Required packages: PySide6, scapy, psutil, matplotlib, networkx

INSTALLATION:
==============
1. Open PowerShell as Administrator
2. Navigate to MITM folder:
   cd "C:\Users\Imen\Documents\learn_python\Python_security\MITM"

3. Install packages:
   pip install PySide6 scapy psutil matplotlib networkx
   
   OR run the batch file:
   .\install_packages.bat

RUNNING THE APP:
================
1. Open PowerShell as Administrator
2. Run:
   python mitm_gui.py

LAYOUT:
=======
The GUI has 3 main sections:

LEFT SECTION:
- Network Interface Selector (dropdown)
- Network Scanner with results table
- ARP Spoof Controls (Target IP, Gateway IP, Start button)
- Packet Sniffer Controls (Victim IP, Start button)

CENTER SECTION:
- Interactive Network Map Visualization
- Shows gateway (red node) and hosts (blue nodes)
- Displays network topology
- Updates after each scan

RIGHT SECTION:
- Real-time Log Output
- Shows all operations and errors
- Scrollable text display

USAGE WORKFLOW:
===============
1. Select your network interface from the dropdown
2. Click "Scan Network" to discover hosts
3. View the network map showing discovered devices
4. Enter Target IP and Gateway IP
5. Click "Start ARP Spoof" to begin MITM attack
6. (Optional) Enter Victim IP and click "Start Sniffing"
7. Monitor the log for packets and information

FEATURES:
=========
✓ Interactive network map with networkx
✓ Network visualization with matplotlib
✓ Real-time host discovery via ARP scan
✓ ARP spoofing (MITM attack)
✓ Packet sniffing for HTTP and Chat traffic
✓ Dark theme UI
✓ Interface selection dropdown
✓ Comprehensive error logging

TROUBLESHOOTING:
================
If the network map doesn't appear:
- Make sure matplotlib is installed: pip install matplotlib
- Check that networkx is installed: pip install networkx

If ARP spoof doesn't work:
- Run as Administrator
- Use correct Target and Gateway IPs
- Select the correct network interface
- Ensure target is on your network

If packet sniffing doesn't work:
- Run as Administrator
- Enter valid victim IP
- Make sure ARP spoof is running first

NOTES:
======
- Always run as Administrator on Windows
- This tool is for educational purposes only
- Only use on networks you own or have permission to test
- Legal disclaimer: Unauthorized network access is illegal

LICENSE: Educational Use Only
