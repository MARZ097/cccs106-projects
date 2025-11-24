@echo off
REM Setup script for Weather Application
echo ========================================
echo Weather Application Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [3/4] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo.

echo [4/4] Setting up environment file...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo Created .env file from .env.example
        echo.
        echo IMPORTANT: Please edit .env and add your OpenWeatherMap API key!
        echo Get your free key from: https://openweathermap.org/api
    ) else (
        echo OPENWEATHER_API_KEY=your_api_key_here > .env
        echo Created .env file. Please add your API key!
    )
) else (
    echo .env file already exists.
)
echo.

echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env and add your OPENWEATHER_API_KEY
echo   2. Run: run_app.bat
echo   3. Or manually: venv\Scripts\activate ^&^& python weather_app/main.py
echo.
pause

