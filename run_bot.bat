@echo off
setlocal enabledelayedexpansion
REM =============================================
REM SMC Bot - Main Launcher
REM Pure Python Virtual Environment
REM =============================================

echo.
echo =============================================
echo      SMC BOT - LAUNCHER
echo =============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run the setup first:
    echo   setup_venv.bat
    echo.
    pause
    exit /b 1
)

echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Verify Python is working
echo [2/4] Verifying Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not accessible in virtual environment!
    echo [INFO] Try deleting the 'venv' folder and running setup_venv.bat again
    pause
    exit /b 1
)
python -c "import sys; print('[OK] Python ' + sys.version.split()[0])"
echo.

REM Verify critical dependencies
echo [3/4] Checking critical dependencies...

set "DEPS_OK=1"

python -c "import streamlit" >nul 2>&1 || (
    echo [ERROR] Streamlit not found
    set "DEPS_OK=0"
)

python -c "import MetaTrader5" >nul 2>&1 || (
    echo [WARNING] MetaTrader5 not found - install will be attempted
    pip install --quiet MetaTrader5
)

python -c "import pandas" >nul 2>&1 || (
    echo [ERROR] Pandas not found
    set "DEPS_OK=0"
)

if "%DEPS_OK%"=="0" (
    echo.
    echo [ERROR] Critical dependencies missing!
    echo Please run: setup_venv.bat
    echo.
    pause
    exit /b 1
)

echo [OK] All critical dependencies present
echo.

REM Create necessary directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "models" mkdir models
if not exist "reports" mkdir reports

REM Step 4: Launch the bot
echo [4/4] Launching SMC Bot...
echo.
echo =============================================
echo      BOT IS STARTING
echo =============================================
echo.
echo The dashboard will open in your browser
echo Default URL: http://localhost:8501
echo.
echo Press Ctrl+C to stop the bot
echo.

REM Start Streamlit
streamlit run app.py --server.headless=true --server.port=8501

REM When bot stops
echo.
echo =============================================
echo      BOT STOPPED
echo =============================================
echo.
echo To restart: run_bot.bat
echo.
pause

endlocal
