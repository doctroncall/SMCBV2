@echo off
setlocal enabledelayedexpansion
REM =============================================
REM SMC Bot - Main Orchestrator
REM Simple and Direct - Anaconda Environment
REM =============================================

echo.
echo =============================================
echo      SMC BOT - ANACONDA LAUNCHER
echo =============================================
echo.

REM Step 1: Check if conda is installed and initialized
echo [1/5] Checking Conda installation...

REM Try basic check first
where conda >nul 2>&1
if not errorlevel 1 (
    echo [OK] Conda is installed
    goto :conda_found
)

REM If 'where' fails, try to find conda in standard locations and add to PATH
set "CONDA_FOUND="
set "CONDA_PATH="

REM Check common installation locations
if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
    set "CONDA_FOUND=1"
    set "CONDA_PATH=%USERPROFILE%\anaconda3"
)
if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
    set "CONDA_FOUND=1"
    set "CONDA_PATH=%USERPROFILE%\miniconda3"
)
if exist "%ProgramData%\anaconda3\Scripts\conda.exe" (
    set "CONDA_FOUND=1"
    set "CONDA_PATH=%ProgramData%\anaconda3"
)
if exist "%ProgramData%\miniconda3\Scripts\conda.exe" (
    set "CONDA_FOUND=1"
    set "CONDA_PATH=%ProgramData%\miniconda3"
)
if exist "C:\ProgramData\Anaconda3\Scripts\conda.exe" (
    set "CONDA_FOUND=1"
    set "CONDA_PATH=C:\ProgramData\Anaconda3"
)
if exist "C:\ProgramData\Miniconda3\Scripts\conda.exe" (
    set "CONDA_FOUND=1"
    set "CONDA_PATH=C:\ProgramData\Miniconda3"
)

if defined CONDA_FOUND (
    echo [OK] Conda is installed but not in PATH
    echo [INFO] Adding conda to PATH temporarily...
    
    REM Add conda to PATH for this session
    if defined CONDA_PATH (
        set "PATH=!CONDA_PATH!\Scripts;!CONDA_PATH!\Library\bin;!CONDA_PATH!;!PATH!"
        echo [OK] Using conda from: !CONDA_PATH!
    )
    goto :conda_found
)

REM Last resort: Try user's specific Anaconda installation
if exist "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Anaconda (anaconda3)" (
    REM This is likely a shortcut location, try to find actual installation
    if exist "%PROGRAMDATA%\anaconda3\Scripts\conda.exe" (
        set "CONDA_FOUND=1"
        set "CONDA_PATH=%PROGRAMDATA%\anaconda3"
        set "PATH=!CONDA_PATH!\Scripts;!CONDA_PATH!\Library\bin;!CONDA_PATH!;!PATH!"
        echo [OK] Found Anaconda installation
        goto :conda_found
    )
)

REM If still not found, show error
echo [ERROR] Conda not found!
echo.
echo Please install Anaconda or Miniconda from:
echo   https://www.anaconda.com/download
echo.
echo After installation:
echo   1. Restart your command prompt
echo   2. Run: conda init cmd.exe
echo   3. Run this script again
echo.
pause
exit /b 1

:conda_found
echo.

REM Step 2: Check if environment exists, create if needed
echo [2/5] Checking conda environment smc_bot...

REM Use consistent environment name (no spaces)
set "ENV_NAME=smc_bot"

REM Improved environment detection - check if we can activate it
call conda activate %ENV_NAME% >nul 2>&1
if not errorlevel 1 (
    echo [OK] Environment %ENV_NAME% exists and can be activated
    goto :env_ready
)

REM Alternative detection method - look for environment in list
echo [INFO] Checking environment list...
conda env list > temp_env_list.txt 2>&1
findstr /r /c:"%ENV_NAME%" temp_env_list.txt >nul 2>&1
if not errorlevel 1 (
    echo [OK] Environment %ENV_NAME% found in environment list
    del temp_env_list.txt
    goto :env_exists_but_not_initialized
)
del temp_env_list.txt

REM If we get here, environment doesn't exist
echo [INFO] Environment "%ENV_NAME%" not found - creating now...
echo [INFO] This will take a few minutes...
echo.

if not exist "environment.yml" (
    echo [ERROR] environment.yml not found!
    echo Please ensure you're in the bot directory
    pause
    exit /b 1
)

REM Create environment with consistent name
conda env create -f environment.yml -n %ENV_NAME%
if errorlevel 1 (
    echo [ERROR] Failed to create environment!
    echo [INFO] This might be because the environment already exists with a different name
    echo [INFO] Checking for existing environments...
    conda env list
    echo.
    echo [INFO] Try: conda env remove -n %ENV_NAME%
    echo Then run this script again
    pause
    exit /b 1
)
echo [OK] Environment created successfully
goto :env_ready

:env_exists_but_not_initialized
echo [OK] Environment %ENV_NAME% exists but conda not initialized
echo [INFO] Attempting to activate using full path...

REM Find the actual path to the environment
for /f "tokens=1,2" %%i in ('conda env list ^| findstr "%ENV_NAME%"') do (
    if "%%i"=="%ENV_NAME%" (
        set "ENV_PATH=%%j"
        goto :activate_by_path
    )
)

REM If we can't find the path, try standard locations
echo [INFO] Trying standard environment locations...
if exist "C:\Users\bnria\.conda\envs\%ENV_NAME%" (
    set "ENV_PATH=C:\Users\bnria\.conda\envs\%ENV_NAME%"
    goto :activate_by_path
)
if exist "C:\ProgramData\Anaconda3\envs\%ENV_NAME%" (
    set "ENV_PATH=C:\ProgramData\Anaconda3\envs\%ENV_NAME%"
    goto :activate_by_path
)
if exist "C:\ProgramData\anaconda3\envs\%ENV_NAME%" (
    set "ENV_PATH=C:\ProgramData\anaconda3\envs\%ENV_NAME%"
    goto :activate_by_path
)

echo [ERROR] Could not determine environment path!
echo [INFO] Please run 'conda init cmd.exe' and restart your terminal
pause
exit /b 1

:activate_by_path
echo [INFO] Activating environment using path: !ENV_PATH!
set "PATH=!ENV_PATH!;!ENV_PATH!\Scripts;!ENV_PATH!\Library\bin;!PATH!"
set "CONDA_PREFIX=!ENV_PATH!"
set "CONDA_DEFAULT_ENV=!ENV_NAME!"
goto :env_ready

:env_ready
echo.

REM Step 3: Verify Python is working in the environment
echo [3/5] Verifying Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not accessible in environment!
    echo [INFO] Please run 'conda init cmd.exe' and restart your terminal
    pause
    exit /b 1
)
python -c "import sys; print('[OK] Python version: ' + sys.version.split()[0])" 2>nul
echo.

REM Step 4: Verify and install dependencies
echo [4/5] Verifying dependencies...

REM Ensure conda env matches expected name
echo [INFO] Ensuring environment packages are installed for %ENV_NAME%...
conda env update -f environment.yml -n %ENV_NAME% --prune >nul 2>&1

REM Check critical packages one-by-one and install fallbacks when needed
python -c "import streamlit" >nul 2>&1 || (
    echo [INFO] Installing Streamlit...
    conda install -n %ENV_NAME% -c conda-forge streamlit -y
)

python -c "import talib" >nul 2>&1 || (
    echo [INFO] Installing TA-Lib via conda-forge...
    conda install -n %ENV_NAME% -c conda-forge ta-lib -y
)

python -c "import loguru" >nul 2>&1 || (
    echo [INFO] Installing loguru via conda-forge...
    conda install -n %ENV_NAME% -c conda-forge loguru -y
)

python -c "import MetaTrader5" >nul 2>&1 || (
    echo [INFO] Installing MetaTrader5 via pip...
    pip install --upgrade pip
    pip install MetaTrader5
)

python -c "import plotly" >nul 2>&1 || (
    echo [INFO] Installing plotly via conda-forge...
    conda install -n %ENV_NAME% -c conda-forge plotly -y
)

python -c "import kaleido" >nul 2>&1 || (
    echo [INFO] Installing kaleido via pip (conda often unavailable on Windows)...
    pip install kaleido
)

python -c "import pandas_ta" >nul 2>&1 || (
    echo [INFO] Installing pandas-ta via pip...
    pip install pandas-ta
)

echo [OK] All dependencies ready
echo.

REM Create necessary directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "models" mkdir models
if not exist "reports" mkdir reports

REM Step 5: Launch the bot
echo [5/5] Launching SMC Bot...
echo.
echo =============================================
echo      BOT IS STARTING
echo =============================================
echo.
echo The dashboard will open in your browser
echo Press Ctrl+C to stop the bot
echo.

streamlit run app.py --server.headless=true --server.port=8501

REM When bot stops
echo.
echo =============================================
echo      BOT STOPPED
echo =============================================
echo.
echo To restart: Run "conda smc.bat" again
echo.
pause

endlocal
