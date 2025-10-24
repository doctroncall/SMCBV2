#!/bin/bash
# ========================================
# MT5 Sentiment Analysis Bot Launcher
# Anaconda/Conda Version
# For Linux/Mac users
# ========================================
# This script uses Anaconda for better stability with ML dependencies

echo ""
echo "========================================"
echo "MT5 Sentiment Analysis Bot (Anaconda)"
echo "========================================"
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "[ERROR] Anaconda/Miniconda is not installed or not in PATH"
    echo ""
    echo "Please install Anaconda or Miniconda:"
    echo "  - Anaconda (full): https://www.anaconda.com/download"
    echo "  - Miniconda (minimal): https://docs.conda.io/en/latest/miniconda.html"
    echo ""
    echo "On macOS:"
    echo "  brew install --cask anaconda"
    echo "  OR: brew install --cask miniconda"
    echo ""
    echo "On Linux:"
    echo "  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    echo "  bash Miniconda3-latest-Linux-x86_64.sh"
    echo ""
    echo "After installation:"
    echo "  1. Restart your terminal"
    echo "  2. Run this script again"
    echo ""
    exit 1
fi

# Get conda version
CONDA_VERSION=$(conda --version 2>&1 | awk '{print $2}')
echo "[OK] Conda found - Version $CONDA_VERSION"
echo ""

# Initialize conda for bash if needed
if [ ! -f "$HOME/.bashrc" ] || ! grep -q "conda initialize" "$HOME/.bashrc" 2>/dev/null; then
    echo "[SETUP] Initializing conda for bash..."
    conda init bash
    echo "[INFO] Please restart your terminal and run this script again"
    exit 0
fi

# Source conda
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

# Check if conda environment exists
if ! conda env list | grep -q "^mt5-sentiment-bot "; then
    echo "[SETUP] Creating conda environment from environment.yml..."
    echo "This will take 5-15 minutes - please be patient"
    echo ""
    
    # Check if environment.yml exists
    if [ ! -f "environment.yml" ]; then
        echo "[ERROR] environment.yml not found"
        echo "Please ensure environment.yml is in the project directory"
        exit 1
    fi
    
    echo "[SETUP] Installing packages with conda..."
    echo "Progress: This includes TA-Lib and all ML libraries"
    echo ""
    
    conda env create -f environment.yml
    if [ $? -ne 0 ]; then
        echo ""
        echo "[ERROR] Failed to create conda environment"
        echo ""
        echo "Troubleshooting:"
        echo "1. Check your internet connection"
        echo "2. Try: conda clean --all"
        echo "3. Try: conda update conda"
        echo "4. Check the error messages above"
        echo ""
        exit 1
    fi
    
    echo ""
    echo "[OK] Conda environment created successfully"
    echo ""
else
    echo "[OK] Conda environment 'mt5-sentiment-bot' already exists"
    echo "[INFO] To update environment: conda env update -f environment.yml"
fi

echo ""
echo "[SETUP] Activating conda environment..."

# Activate the conda environment
conda activate mt5-sentiment-bot
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate conda environment"
    echo ""
    echo "Try these solutions:"
    echo "1. Restart your terminal"
    echo "2. Run: conda init bash (or conda init zsh for macOS)"
    echo "3. Delete and recreate: conda env remove -n mt5-sentiment-bot"
    echo ""
    exit 1
fi

echo "[OK] Conda environment activated"
echo "Environment: mt5-sentiment-bot"
echo ""

# Verify key packages are installed
echo "[SETUP] Verifying installation..."
python -c "import streamlit" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] Streamlit not found, attempting to install missing packages..."
    conda env update -f environment.yml
fi

python -c "import talib" &> /dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] TA-Lib not properly installed"
    echo "Attempting to install from conda-forge..."
    conda install -c conda-forge ta-lib -y
    if [ $? -ne 0 ]; then
        echo "[ERROR] TA-Lib installation failed"
        echo "Try manually: conda install -c conda-forge ta-lib"
        exit 1
    fi
fi

echo "[OK] All packages verified"
echo ""

# Create necessary directories
echo "[SETUP] Checking directory structure..."
mkdir -p data logs models reports
echo "[OK] Directory structure ready"
echo ""

# Check if database needs initialization
if [ ! -f "data/mt5_sentiment.db" ]; then
    echo "[SETUP] Initializing database..."
    python -c "from src.database.models import init_database; init_database(); print('[OK] Database initialized')" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "[WARNING] Database initialization failed - will retry on first run"
        echo "This is normal for first-time setup"
    else
        echo "[OK] Database initialized successfully"
    fi
else
    echo "[OK] Database already initialized"
fi

echo ""
echo "========================================"
echo "Starting MT5 Sentiment Analysis Bot..."
echo "========================================"
echo ""
echo "[INFO] Using Anaconda environment: mt5-sentiment-bot"
echo "[INFO] Dashboard will open in your browser automatically"
echo "[INFO] Press Ctrl+C to stop the bot"
echo ""
echo "Launching Streamlit..."
echo ""

# Start Streamlit with the app
streamlit run app.py --server.headless=true --server.port=8501
STREAMLIT_EXIT_CODE=$?

# If Streamlit exits, show message
echo ""
echo "========================================"
echo "Bot stopped"
echo "========================================"

if [ $STREAMLIT_EXIT_CODE -ne 0 ]; then
    echo ""
    echo "[WARNING] Application exited with error code: $STREAMLIT_EXIT_CODE"
    echo "Check the logs folder for error details"
    echo ""
fi

echo ""
echo "To restart the bot, run this script again: ./start_bot.sh"
echo "To deactivate conda: conda deactivate"
echo ""
