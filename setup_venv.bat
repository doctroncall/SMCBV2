@echo off
setlocal enabledelayedexpansion
REM =============================================
REM SMC Bot - Python Virtual Environment Setup
REM Pure Python (No Conda Required)
REM =============================================

echo.
echo =============================================
echo   SMC BOT - PYTHON VENV SETUP
echo =============================================
echo.

REM Step 1: Check if Python is installed
echo [1/5] Checking Python installation...

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH!
    echo.
    echo Please install Python 3.11 or later from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo [OK] Python version: %PYTHON_VERSION%

REM Verify Python version is 3.11 or higher
python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python 3.11+ recommended. Current: %PYTHON_VERSION%
    echo [INFO] Continuing anyway... but some features may not work optimally
)
echo.

REM Step 2: Create virtual environment if it doesn't exist
echo [2/5] Setting up virtual environment...

if exist "venv\" (
    echo [OK] Virtual environment already exists
) else (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        echo [INFO] Try: python -m pip install --upgrade pip virtualenv
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

REM Step 3: Activate virtual environment
echo [3/5] Activating virtual environment...

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment is corrupted!
    echo [INFO] Delete the 'venv' folder and run this script again
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Step 4: Upgrade pip and install dependencies
echo [4/5] Installing dependencies...
echo [INFO] This may take 5-10 minutes on first run...
echo.

REM Upgrade pip first
python -m pip install --upgrade pip setuptools wheel --quiet
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)

REM Install requirements
echo [INFO] Installing packages from requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install some dependencies!
    echo.
    echo Common issues and solutions:
    echo.
    echo 1. TA-Lib installation failed?
    echo    - Windows: Download wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
    echo    - Install with: pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl
    echo.
    echo 2. TensorFlow installation failed?
    echo    - You may need Visual C++ redistributables
    echo    - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    echo 3. Other packages failing?
    echo    - Try: pip install --upgrade pip
    echo    - Run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] All dependencies installed
echo.

REM Step 5: Verify installation
echo [5/5] Verifying installation...

python -c "import streamlit; print('[OK] Streamlit ' + streamlit.__version__)" 2>nul || echo [WARNING] Streamlit not found
python -c "import MetaTrader5; print('[OK] MetaTrader5 installed')" 2>nul || echo [WARNING] MetaTrader5 not found
python -c "import pandas; print('[OK] Pandas ' + pandas.__version__)" 2>nul || echo [WARNING] Pandas not found
python -c "import numpy; print('[OK] NumPy installed')" 2>nul || echo [WARNING] NumPy not found
python -c "import sklearn; print('[OK] Scikit-learn installed')" 2>nul || echo [WARNING] Scikit-learn not found

REM Try TA-Lib with better error message
python -c "import talib; print('[OK] TA-Lib installed')" 2>nul || (
    echo [WARNING] TA-Lib not found - this is a critical dependency
    echo [INFO] See installation instructions above
)

echo.
echo =============================================
echo   SETUP COMPLETE!
echo =============================================
echo.
echo Next steps:
echo   1. To start the bot: run_bot.bat
echo   2. To activate venv manually: venv\Scripts\activate.bat
echo   3. To deactivate: deactivate
echo.
echo Virtual environment location: %CD%\venv
echo.
pause

endlocal
