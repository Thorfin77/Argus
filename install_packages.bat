@echo off
REM Install required packages for MITM GUI with Network Map
REM Run this as Administrator

echo Installing required packages...
echo.

pip install PySide6 scapy psutil matplotlib networkx

echo.
echo Installation complete!
echo You can now run: python mitm_gui.py
pause
