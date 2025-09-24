@echo off
echo Starting Enhanced Contact Book Application...
echo.

REM Try different methods to run the app
echo Attempting to run with virtual environment Python...
..\..\..\cccs106_env_villaruel\Scripts\python.exe main.py

REM If the above fails, try with system Python
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Virtual environment Python failed, trying system Python...
    python main.py
)

REM If that also fails, try with python3
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo System Python failed, trying python3...
    python3 main.py
)

REM If all methods fail
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to run the application with all methods.
    echo Please check:
    echo 1. Python is installed and in PATH
    echo 2. Flet is installed: pip install flet
    echo 3. You're in the correct directory
    echo.
    echo You can also try running manually:
    echo python main.py
)

echo.
echo Press any key to close...
pause >nul
