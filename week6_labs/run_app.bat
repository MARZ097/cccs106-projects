@echo off
REM Windows batch script to run the weather application
REM Make sure you have activated your virtual environment first!

echo Starting Weather Application...
echo.
echo Make sure you have:
echo   1. Created a .env file with your OPENWEATHER_API_KEY
echo   2. Activated your virtual environment
echo   3. Installed requirements: pip install -r requirements.txt
echo.

cd /d %~dp0
REM Change to weather_app directory to allow direct script execution
cd weather_app
python main.py
cd ..

pause

