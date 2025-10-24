#!/bin/bash
# =============================================
# SMC Bot - Main Launcher
# Pure Python Virtual Environment
# =============================================

echo ""
echo "============================================="
echo "   SMC BOT - LAUNCHER"
echo "============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}[ERROR] Virtual environment not found!${NC}"
    echo ""
    echo "Please run the setup first:"
    echo "  ./setup_venv.sh"
    echo ""
    exit 1
fi

echo "[1/4] Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}[OK] Virtual environment activated${NC}"
echo ""

# Verify Python is working
echo "[2/4] Verifying Python environment..."
if ! command -v python &> /dev/null; then
    echo -e "${RED}[ERROR] Python not accessible in virtual environment!${NC}"
    echo "Try deleting the 'venv' folder and running setup_venv.sh again"
    exit 1
fi
PYTHON_VERSION=$(python --version 2>&1)
echo -e "${GREEN}[OK] $PYTHON_VERSION${NC}"
echo ""

# Verify critical dependencies
echo "[3/4] Checking critical dependencies..."

DEPS_OK=1

python -c "import streamlit" &> /dev/null || {
    echo -e "${RED}[ERROR] Streamlit not found${NC}"
    DEPS_OK=0
}

python -c "import MetaTrader5" &> /dev/null || {
    echo -e "${YELLOW}[WARNING] MetaTrader5 not found - install will be attempted${NC}"
    pip install --quiet MetaTrader5
}

python -c "import pandas" &> /dev/null || {
    echo -e "${RED}[ERROR] Pandas not found${NC}"
    DEPS_OK=0
}

if [ $DEPS_OK -eq 0 ]; then
    echo ""
    echo -e "${RED}[ERROR] Critical dependencies missing!${NC}"
    echo "Please run: ./setup_venv.sh"
    echo ""
    exit 1
fi

echo -e "${GREEN}[OK] All critical dependencies present${NC}"
echo ""

# Create necessary directories
mkdir -p data logs models reports

# Initialize database if needed
if [ ! -f "data/mt5_sentiment.db" ]; then
    echo "[INFO] Initializing database..."
    python -c "from src.database.models import init_database; init_database(); print('[OK] Database initialized')" 2>/dev/null || {
        echo -e "${YELLOW}[WARNING] Database initialization failed - will retry on first run${NC}"
    }
fi

# Step 4: Launch the bot
echo "[4/4] Launching SMC Bot..."
echo ""
echo "============================================="
echo "   BOT IS STARTING"
echo "============================================="
echo ""
echo "The dashboard will open in your browser"
echo "Default URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the bot"
echo ""

# Start Streamlit
streamlit run app.py --server.headless=true --server.port=8501
STREAMLIT_EXIT_CODE=$?

# When bot stops
echo ""
echo "============================================="
echo "   BOT STOPPED"
echo "============================================="

if [ $STREAMLIT_EXIT_CODE -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}[WARNING] Application exited with error code: $STREAMLIT_EXIT_CODE${NC}"
    echo "Check the logs folder for error details"
fi

echo ""
echo "To restart: ./run_bot.sh"
echo ""
