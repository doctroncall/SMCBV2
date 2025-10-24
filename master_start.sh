#!/bin/bash
# ================================================================================
#  SMC TRADING BOT - MASTER STARTUP
#  Complete automated setup, verification, and launch
# ================================================================================

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "================================================================================"
echo "  SMC TRADING BOT - MASTER STARTUP v2.0"
echo "================================================================================"
echo ""
echo -e "${BLUE}[INFO]${NC} Starting comprehensive bot initialization..."
echo ""

# ================================================================================
# STEP 1: Environment Detection
# ================================================================================
echo -e "${BLUE}[1/7]${NC} Detecting Python environment..."
echo ""

PYTHON_CMD=""
VENV_ACTIVE=0
CONDA_ACTIVE=0

# Check if we're in a venv
if [ -f "venv/bin/python" ]; then
    echo -e "${GREEN}[OK]${NC} Python venv detected at: venv/"
    PYTHON_CMD="venv/bin/python"
    VENV_ACTIVE=1
elif command -v conda &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Conda detected in PATH"
    CONDA_ACTIVE=1
    
    # Check if conda environment exists
    if conda env list | grep -q "smc_bot"; then
        echo -e "${GREEN}[OK]${NC} Conda environment 'smc_bot' found"
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate smc_bot
        PYTHON_CMD="python"
    else
        echo -e "${YELLOW}[WARNING]${NC} Conda found but 'smc_bot' environment not created"
        echo -e "${BLUE}[INFO]${NC} Creating environment..."
        conda env create -f environment.yml
        conda activate smc_bot
        PYTHON_CMD="python"
    fi
elif command -v python3 &> /dev/null; then
    echo -e "${GREEN}[OK]${NC} Python3 found in PATH"
    PYTHON_CMD="python3"
else
    echo -e "${RED}[ERROR]${NC} No Python installation found!"
    echo ""
    echo "Please install Python 3.11+ or run:"
    echo "  - ./setup_venv.sh  (recommended)"
    echo "  - conda env create -f environment.yml"
    echo ""
    exit 1
fi

# If no venv and no conda, create venv
if [ $VENV_ACTIVE -eq 0 ] && [ $CONDA_ACTIVE -eq 0 ]; then
    if [ ! -d "venv" ]; then
        echo ""
        echo -e "${BLUE}[SETUP]${NC} No environment found. Creating Python venv..."
        echo ""
        chmod +x setup_venv.sh
        ./setup_venv.sh
        PYTHON_CMD="venv/bin/python"
        VENV_ACTIVE=1
    fi
fi

echo -e "${GREEN}[OK]${NC} Python ready: $PYTHON_CMD"
echo ""

# ================================================================================
# STEP 2: Verify Python Version
# ================================================================================
echo -e "${BLUE}[2/7]${NC} Verifying Python version..."
echo ""

$PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} Python 3.11+ recommended"
    $PYTHON_CMD --version
else
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo -e "${GREEN}[OK]${NC} $PYTHON_VERSION"
fi
echo ""

# ================================================================================
# STEP 3: Activate Environment
# ================================================================================
echo -e "${BLUE}[3/7]${NC} Activating environment..."
echo ""

if [ $VENV_ACTIVE -eq 1 ]; then
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo -e "${GREEN}[OK]${NC} Virtual environment activated"
    fi
elif [ $CONDA_ACTIVE -eq 1 ]; then
    echo -e "${GREEN}[OK]${NC} Conda environment activated"
else
    echo -e "${GREEN}[OK]${NC} Using system Python"
fi
echo ""

# ================================================================================
# STEP 4: Verify Critical Dependencies
# ================================================================================
echo -e "${BLUE}[4/7]${NC} Verifying critical dependencies..."
echo ""

DEPS_OK=1
MISSING_DEPS=""

# Check each dependency
check_dep() {
    $PYTHON_CMD -c "import $1" &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} $2"
    else
        echo -e "${RED}[X]${NC} $2 - MISSING"
        DEPS_OK=0
        MISSING_DEPS="$MISSING_DEPS $2"
    fi
}

check_dep "streamlit" "Streamlit"
check_dep "MetaTrader5" "MetaTrader5"
check_dep "pandas" "Pandas"
check_dep "numpy" "NumPy"
check_dep "talib" "TA-Lib"
check_dep "loguru" "Loguru"

echo ""

if [ $DEPS_OK -eq 0 ]; then
    echo -e "${RED}[ERROR]${NC} Missing dependencies:$MISSING_DEPS"
    echo ""
    echo -e "${BLUE}[ATTEMPTING AUTO-FIX]${NC}"
    echo "Installing missing packages..."
    echo ""
    
    if [ $VENV_ACTIVE -eq 1 ]; then
        pip install -r requirements.txt
    elif [ $CONDA_ACTIVE -eq 1 ]; then
        conda env update -f environment.yml
    else
        pip install -r requirements.txt
    fi
    
    echo ""
    echo -e "${BLUE}[INFO]${NC} Packages installed. Re-verifying..."
    echo ""
    
    # Re-verify
    $PYTHON_CMD -c "import streamlit, MetaTrader5, pandas, numpy, talib, loguru" &> /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Auto-fix failed. Please run:"
        echo "  ./setup_venv.sh"
        exit 1
    else
        echo -e "${GREEN}[OK]${NC} All dependencies now available!"
    fi
fi

echo -e "${GREEN}[OK]${NC} All critical dependencies verified"
echo ""

# ================================================================================
# STEP 5: Create Necessary Directories
# ================================================================================
echo -e "${BLUE}[5/7]${NC} Setting up directory structure..."
echo ""

mkdir -p data logs models reports

echo -e "${GREEN}[OK]${NC} Directories ready"
echo "    - data/"
echo "    - logs/"
echo "    - models/"
echo "    - reports/"
echo ""

# ================================================================================
# STEP 6: Initialize Database
# ================================================================================
echo -e "${BLUE}[6/7]${NC} Checking database..."
echo ""

if [ -f "data/mt5_sentiment.db" ]; then
    echo -e "${GREEN}[OK]${NC} Database exists"
else
    echo -e "${BLUE}[INFO]${NC} Initializing database..."
    $PYTHON_CMD -c "from src.database.models import init_database; init_database(); print('[OK] Database created')" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[WARNING]${NC} Database initialization failed - will retry on first run"
    else
        echo -e "${GREEN}[OK]${NC} Database initialized"
    fi
fi
echo ""

# ================================================================================
# STEP 7: Launch Bot
# ================================================================================
echo -e "${BLUE}[7/7]${NC} Launching SMC Trading Bot..."
echo ""
echo "================================================================================"
echo "  STARTUP COMPLETE - LAUNCHING DASHBOARD"
echo "================================================================================"
echo ""
echo -e "${BLUE}[INFO]${NC} The bot dashboard will open in your browser"
echo -e "${BLUE}[INFO]${NC} Default URL: http://localhost:8501"
echo ""
echo -e "${GREEN}[v2.0 FEATURES ACTIVE]${NC}"
echo "  - Multi-timeframe analysis"
echo "  - Smart Money Concepts (SMC)"
echo "  - Market Regime Detection"
echo "  - ML Model Training"
echo "  - Advanced sentiment engine"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""
echo "================================================================================"
echo ""

# Start Streamlit
streamlit run app.py --server.headless=true --server.port=8501

# If Streamlit exits
echo ""
echo "================================================================================"
echo "  BOT STOPPED"
echo "================================================================================"
echo ""
echo "To restart: ./master_start.sh"
echo ""
