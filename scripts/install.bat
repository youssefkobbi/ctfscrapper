@echo off
REM Install script for ctfscrapper (Windows)

echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║                     ctfscrapper Installation Script                          ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Check Python version
python --version 2>nul | findstr /r "3\.[8-9] 3\.[1-9][0-9]" >nul
if errorlevel 1 (
    echo ❌ Error: Python 3.8+ required
    exit /b 1
)
echo ✅ Python version OK

REM Create virtual environment
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate and install
echo 📥 Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -e .

echo.
echo ✅ Installation complete!
echo.
echo Usage:
echo   call venv\Scripts\activate.bat
echo   ctfscrapper -u https://ctf.example.com -U user -P pass
echo.
echo Or run directly:
echo   venv\Scripts\ctfscrapper.exe -u https://ctf.example.com -U user -P pass
pause
