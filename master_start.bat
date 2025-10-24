@echo off
setlocal enabledelayedexpansion
REM ================================================================================
REM  SMC TRADING BOT - MASTER STARTUP
REM  Complete automated setup, verification, and launch
REM ================================================================================

echo.
echo ================================================================================
echo   SMC TRADING BOT - MASTER STARTUP v2.0
echo ================================================================================
echo.
echo [INFO] Starting comprehensive bot initialization...
echo.

REM ================================================================================
REM STEP 1: Environment Detection
REM ================================================================================
echo [1/7] Detecting Python environment...
echo.

set "PYTHON_CMD="
set "VENV_ACTIVE=0"
set "CONDA_ACTIVE=0"

REM Check if we're in a venv
if exist "venv\Scripts\python.exe" (
    echo [OK] Python venv detected at: venv\
    set "PYTHON_CMD=venv\Scripts\python.exe"
    set "VENV_ACTIVE=1"
    goto :python_found
)

REM Check if we're in conda
where conda >nul 2>&1
if not errorlevel 1 (
    echo [OK] Conda detected in PATH
    set "CONDA_ACTIVE=1"
    goto :check_conda_env
)

REM Check standard Python
where python >nul 2>&1
if not errorlevel 1 (
    echo [OK] Python found in PATH
    set "PYTHON_CMD=python"
    goto :python_found
)

echo [ERROR] No Python installation found!
echo.
echo Please install Python 3.11+ or run one of these:
echo   - setup_venv.bat  (recommended - pure Python)
echo   - conda smc.bat   (if you have Anaconda)
echo.
pause
exit /b 1

:check_conda_env
REM Check if conda environment exists
conda env list | findstr "smc_bot" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Conda environment 'smc_bot' found
    call conda activate smc_bot
    set "PYTHON_CMD=python"
    goto :python_found
)
echo [WARNING] Conda found but 'smc_bot' environment not created
echo [INFO] Will try to use system Python or create venv
goto :create_venv

:create_venv
echo.
echo [SETUP] No environment found. Creating Python venv...
echo.

REM Check if we have Python available
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Running automated setup...
call setup_venv.bat
if errorlevel 1 (
    echo [ERROR] Setup failed. Please check errors above.
    pause
    exit /b 1
)

echo [OK] Setup completed successfully
set "PYTHON_CMD=venv\Scripts\python.exe"
set "VENV_ACTIVE=1"
goto :python_found

:python_found
echo [OK] Python ready: %PYTHON_CMD%
echo.

REM ================================================================================
REM STEP 2: Verify Python Version
REM ================================================================================
echo [2/7] Verifying Python version...
echo.

%PYTHON_CMD% -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python 3.11+ recommended
    %PYTHON_CMD% --version
) else (
    for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do echo [OK] Python %%v
)
echo.

REM ================================================================================
REM STEP 3: Activate Environment
REM ================================================================================
echo [3/7] Activating environment...
echo.

if %VENV_ACTIVE%==1 (
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        echo [OK] Virtual environment activated
    )
) else if %CONDA_ACTIVE%==1 (
    call conda activate smc_bot >nul 2>&1
    echo [OK] Conda environment activated
) else (
    echo [OK] Using system Python
)
echo.

REM ================================================================================
REM STEP 4: Verify Critical Dependencies
REM ================================================================================
echo [4/7] Verifying critical dependencies...
echo.

set "DEPS_OK=1"
set "MISSING_DEPS="

REM Check Streamlit
%PYTHON_CMD% -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [X] Streamlit - MISSING
    set "DEPS_OK=0"
    set "MISSING_DEPS=!MISSING_DEPS! streamlit"
) else (
    echo [OK] Streamlit
)

REM Check MetaTrader5
%PYTHON_CMD% -c "import MetaTrader5" >nul 2>&1
if errorlevel 1 (
    echo [X] MetaTrader5 - MISSING
    set "DEPS_OK=0"
    set "MISSING_DEPS=!MISSING_DEPS! MetaTrader5"
) else (
    echo [OK] MetaTrader5
)

REM Check Pandas
%PYTHON_CMD% -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo [X] Pandas - MISSING
    set "DEPS_OK=0"
    set "MISSING_DEPS=!MISSING_DEPS! pandas"
) else (
    echo [OK] Pandas
)

REM Check NumPy
%PYTHON_CMD% -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo [X] NumPy - MISSING
    set "DEPS_OK=0"
    set "MISSING_DEPS=!MISSING_DEPS! numpy"
) else (
    echo [OK] NumPy
)

REM Check TA-Lib
%PYTHON_CMD% -c "import talib" >nul 2>&1
if errorlevel 1 (
    echo [X] TA-Lib - MISSING
    set "DEPS_OK=0"
    set "MISSING_DEPS=!MISSING_DEPS! TA-Lib"
) else (
    echo [OK] TA-Lib
)

REM Check Loguru
%PYTHON_CMD% -c "import loguru" >nul 2>&1
if errorlevel 1 (
    echo [X] Loguru - MISSING
    set "DEPS_OK=0"
    set "MISSING_DEPS=!MISSING_DEPS! loguru"
) else (
    echo [OK] Loguru
)

echo.

if %DEPS_OK%==0 (
    echo [ERROR] Missing dependencies:%MISSING_DEPS%
    echo.
    echo [ATTEMPTING AUTO-FIX]
    echo Installing missing packages...
    echo.
    
    if %VENV_ACTIVE%==1 (
        pip install -r requirements.txt
    ) else if %CONDA_ACTIVE%==1 (
        conda env update -f environment.yml
    ) else (
        pip install -r requirements.txt
    )
    
    echo.
    echo [INFO] Packages installed. Re-verifying...
    echo.
    
    REM Re-verify
    %PYTHON_CMD% -c "import streamlit, MetaTrader5, pandas, numpy, talib, loguru" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Auto-fix failed. Please run:
        if %VENV_ACTIVE%==1 (
            echo   pip install -r requirements.txt
        ) else if %CONDA_ACTIVE%==1 (
            echo   conda env update -f environment.yml
        ) else (
            echo   setup_venv.bat
        )
        pause
        exit /b 1
    ) else (
        echo [OK] All dependencies now available!
    )
)

echo [OK] All critical dependencies verified
echo.

REM ================================================================================
REM STEP 5: Create Necessary Directories
REM ================================================================================
echo [5/7] Setting up directory structure...
echo.

if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "models" mkdir models
if not exist "reports" mkdir reports

echo [OK] Directories ready
echo     - data\
echo     - logs\
echo     - models\
echo     - reports\
echo.

REM ================================================================================
REM STEP 6: Initialize Database
REM ================================================================================
echo [6/7] Checking database...
echo.

if exist "data\mt5_sentiment.db" (
    echo [OK] Database exists
) else (
    echo [INFO] Initializing database...
    %PYTHON_CMD% -c "from src.database.models import init_database; init_database(); print('[OK] Database created')" 2>nul
    if errorlevel 1 (
        echo [WARNING] Database initialization failed - will retry on first run
    ) else (
        echo [OK] Database initialized
    )
)
echo.

REM ================================================================================
REM STEP 7: Launch Bot
REM ================================================================================
echo [7/7] Launching SMC Trading Bot...
echo.
echo ================================================================================
echo   STARTUP COMPLETE - LAUNCHING DASHBOARD
echo ================================================================================
echo.
echo [INFO] The bot dashboard will open in your browser
echo [INFO] Default URL: http://localhost:8501
echo.
echo [v2.0 FEATURES ACTIVE]
echo   - Multi-timeframe analysis
echo   - Smart Money Concepts (SMC)
echo   - Market Regime Detection
echo   - ML Model Training
echo   - Advanced sentiment engine
echo.
echo Press Ctrl+C to stop the bot
echo.
echo ================================================================================
echo.

REM Start Streamlit
streamlit run app.py --server.headless=true --server.port=8501

REM If Streamlit exits
echo.
echo ================================================================================
echo   BOT STOPPED
echo ================================================================================
echo.
echo To restart: master_start.bat
echo.
pause

endlocal
