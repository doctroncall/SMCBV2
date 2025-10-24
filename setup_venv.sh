#!/bin/bash
# =============================================
# SMC Bot - Python Virtual Environment Setup
# Pure Python (No Conda Required)
# =============================================

echo ""
echo "============================================="
echo "   SMC BOT - PYTHON VENV SETUP"
echo "============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check if Python is installed
echo "[1/5] Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 not found!${NC}"
    echo ""
    echo "Please install Python 3.11 or later:"
    echo ""
    echo "On Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install python3.11 python3.11-venv python3-pip"
    echo ""
    echo "On macOS:"
    echo "  brew install python@3.11"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}[OK] Python version: $PYTHON_VERSION${NC}"

# Verify Python version is 3.11 or higher
python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] Python 3.11+ recommended. Current: $PYTHON_VERSION${NC}"
    echo -e "${YELLOW}[INFO] Continuing anyway... but some features may not work optimally${NC}"
fi
echo ""

# Step 2: Create virtual environment if it doesn't exist
echo "[2/5] Setting up virtual environment..."

if [ -d "venv" ]; then
    echo -e "${GREEN}[OK] Virtual environment already exists${NC}"
else
    echo -e "${BLUE}[INFO] Creating virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment!${NC}"
        echo ""
        echo "Try installing venv:"
        echo "  Ubuntu/Debian: sudo apt install python3.11-venv"
        echo "  macOS: Should be included with Python"
        echo ""
        exit 1
    fi
    echo -e "${GREEN}[OK] Virtual environment created${NC}"
fi
echo ""

# Step 3: Activate virtual environment
echo "[3/5] Activating virtual environment..."

if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}[ERROR] Virtual environment is corrupted!${NC}"
    echo "Delete the 'venv' folder and run this script again"
    exit 1
fi

source venv/bin/activate
echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo ""

# Step 4: Upgrade pip and install dependencies
echo "[4/5] Installing dependencies..."
echo -e "${BLUE}[INFO] This may take 5-10 minutes on first run...${NC}"
echo ""

# Upgrade pip first
python -m pip install --upgrade pip setuptools wheel --quiet
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] Failed to upgrade pip, continuing anyway...${NC}"
fi

# Install requirements
echo -e "${BLUE}[INFO] Installing packages from requirements.txt...${NC}"
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}[ERROR] Failed to install some dependencies!${NC}"
    echo ""
    echo "Common issues and solutions:"
    echo ""
    echo "1. TA-Lib installation failed?"
    echo "   Ubuntu/Debian:"
    echo "     sudo apt install build-essential wget"
    echo "     wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz"
    echo "     tar -xzf ta-lib-0.4.0-src.tar.gz"
    echo "     cd ta-lib/ && ./configure --prefix=/usr && make && sudo make install"
    echo "     pip install TA-Lib"
    echo ""
    echo "   macOS:"
    echo "     brew install ta-lib"
    echo "     pip install TA-Lib"
    echo ""
    echo "2. Other packages failing?"
    echo "   - Try: pip install --upgrade pip"
    echo "   - Run this script again"
    echo ""
    exit 1
fi

echo -e "${GREEN}[OK] All dependencies installed${NC}"
echo ""

# Step 5: Verify installation
echo "[5/5] Verifying installation..."

python -c "import streamlit; print('[OK] Streamlit ' + streamlit.__version__)" 2>/dev/null || echo -e "${YELLOW}[WARNING] Streamlit not found${NC}"
python -c "import MetaTrader5; print('[OK] MetaTrader5 installed')" 2>/dev/null || echo -e "${YELLOW}[WARNING] MetaTrader5 not found${NC}"
python -c "import pandas; print('[OK] Pandas ' + pandas.__version__)" 2>/dev/null || echo -e "${YELLOW}[WARNING] Pandas not found${NC}"
python -c "import numpy; print('[OK] NumPy installed')" 2>/dev/null || echo -e "${YELLOW}[WARNING] NumPy not found${NC}"
python -c "import sklearn; print('[OK] Scikit-learn installed')" 2>/dev/null || echo -e "${YELLOW}[WARNING] Scikit-learn not found${NC}"

# Try TA-Lib with better error message
python -c "import talib; print('[OK] TA-Lib installed')" 2>/dev/null || (
    echo -e "${YELLOW}[WARNING] TA-Lib not found - this is a critical dependency${NC}"
    echo -e "${YELLOW}[INFO] See installation instructions above${NC}"
)

# Create necessary directories
echo ""
echo "[INFO] Creating necessary directories..."
mkdir -p data logs models reports
echo -e "${GREEN}[OK] Directory structure ready${NC}"

echo ""
echo "============================================="
echo "   SETUP COMPLETE!"
echo "============================================="
echo ""
echo "Next steps:"
echo "  1. To start the bot: ./run_bot.sh"
echo "  2. To activate venv manually: source venv/bin/activate"
echo "  3. To deactivate: deactivate"
echo ""
echo "Virtual environment location: $(pwd)/venv"
echo ""
