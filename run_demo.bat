@echo off
REM HoMM3 Bot - Demo Launcher for Windows

echo Starting HoMM3 Bot Demo...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then run: venv\Scripts\activate
    echo Then run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment and run
call venv\Scripts\activate.bat
python run.py --demo

pause
