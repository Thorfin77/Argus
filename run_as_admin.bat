@echo off
REM Run MITM GUI as Administrator
REM This batch file ensures the app has the required permissions

python -m pip install --upgrade PySide6 scapy psutil 2>nul
echo.
echo Starting MITM GUI as Administrator...
echo.
python "%~dp0mitm_gui.py"
pause
