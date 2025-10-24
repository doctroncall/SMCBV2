# 🚀 Quick Start Guide - Anaconda Edition

Get your MT5 Sentiment Analysis Bot running in 2 easy steps!

## ⚡ Fast Track Installation

Your bot now uses **Anaconda** for maximum stability and automatic dependency management!

### Windows Users:

1. **Install Anaconda/Miniconda**
   - Anaconda: https://www.anaconda.com/download
   - Miniconda: https://docs.conda.io/en/latest/miniconda.html

2. **Double-click `start_bot.bat`**
3. **Wait 5-15 minutes (first time only)**
4. **Dashboard opens automatically!**

### Linux/Mac Users:

1. **Install Anaconda/Miniconda**
   - Anaconda: https://www.anaconda.com/download
   - Miniconda: https://docs.conda.io/en/latest/miniconda.html

2. **Run in terminal:**
   ```bash
   ./start_bot.sh
   ```
3. **Wait 5-15 minutes (first time only)**
4. **Dashboard opens automatically!**

---

## 📋 What the Anaconda Launcher Does:

✅ Checks if Anaconda/Miniconda is installed  
✅ Creates isolated conda environment (`mt5-sentiment-bot`)  
✅ **Installs TA-Lib automatically** (no manual steps!)  
✅ Installs all ML libraries (TensorFlow, XGBoost, etc.)  
✅ Installs Streamlit and all dependencies  
✅ Creates required directories (data, logs, models, reports)  
✅ Initializes SQLite database  
✅ Launches Streamlit dashboard  
✅ Opens browser at http://localhost:8501  

---

## 🌟 Why Anaconda is Better

### The Old Way (Standard Python):
❌ Manual TA-Lib installation (complicated!)  
❌ Download wheel files  
❌ Match Python version  
❌ Compilation errors  
❌ Dependency conflicts  

### The New Way (Anaconda):
✅ **TA-Lib installs automatically!**  
✅ **No manual downloads**  
✅ **No compilation needed**  
✅ **No dependency conflicts**  
✅ **Works first time**  
✅ **Cross-platform consistency**  

---

## ⚙️ What You Need:

### Prerequisites:
- [ ] **Anaconda or Miniconda installed**
- [ ] Internet connection (first-time setup only)
- [ ] ~2GB free disk space
- [ ] 5-15 minutes (first run only)
- [ ] MT5 credentials (for later)

### First-Time Setup:

**1. Install Anaconda/Miniconda**

Choose your preference:

**Anaconda (Full Package - Recommended for Beginners)**
- Download: https://www.anaconda.com/download
- Size: ~3GB
- Includes: Anaconda Navigator GUI + 250+ packages
- Best for: Users who want everything ready

**Miniconda (Minimal - Recommended for Advanced Users)**
- Download: https://docs.conda.io/en/latest/miniconda.html
- Size: ~400MB
- Includes: Just conda + Python
- Best for: Users who want minimal install

**Installation Tips:**
- **Windows:** Check "Add Anaconda to PATH" (optional but helpful)
- **Mac:** Use installer or `brew install --cask anaconda`
- **Linux:** Download shell script and run: `bash Miniconda3-latest-Linux-x86_64.sh`

**2. Run the Bot**

**Windows:** Open Anaconda Prompt (or regular cmd if conda is in PATH)
```batch
cd path\to\mt5-sentiment-bot
start_bot.bat
```

**Linux/Mac:** Open terminal
```bash
cd /path/to/mt5-sentiment-bot
./start_bot.sh
```

**3. Wait for Setup**

First run only (5-15 minutes):
- Creating conda environment...
- Installing TA-Lib from conda-forge... ✓
- Installing machine learning libraries...
- Installing visualization tools...
- Setting up database...
- Starting dashboard...

**4. Configure MT5**

Once dashboard opens:
1. Go to **Settings** tab
2. Click **MT5 Connection**
3. Enter your credentials
4. Click **Connect**

---

## 🎯 Using the Bot:

1. **Dashboard opens automatically** in your browser
2. **Select symbol** (e.g., EURUSD) from sidebar
3. **Choose timeframe** (e.g., H1)
4. **Click "Analyze"** button
5. **View results** in real-time!

---

## 🔧 Troubleshooting:

### "conda: command not found"

**Windows:**
- Use **Anaconda Prompt** instead of regular cmd
- Or add Anaconda to PATH during installation

**Linux/Mac:**
```bash
# Initialize conda for your shell
conda init bash  # or: conda init zsh for Mac
# Restart terminal
```

### "Failed to create conda environment"

```bash
# Update conda
conda update conda

# Clean cache
conda clean --all

# Try again
./start_bot.sh  # or start_bot.bat
```

### "TA-Lib import error"

```bash
# Activate environment
conda activate mt5-sentiment-bot

# Install TA-Lib manually
conda install -c conda-forge ta-lib -y

# Verify
python -c "import talib; print('TA-Lib works!')"
```

### "Environment activation failed"

```bash
# Initialize conda
conda init bash  # Linux
conda init zsh   # Mac  
conda init cmd.exe  # Windows

# Restart terminal and try again
```

### "Streamlit won't start"

```bash
# Check environment is activated
conda activate mt5-sentiment-bot

# Verify streamlit installed
conda list streamlit

# Check port 8501 is available
# Windows: netstat -an | findstr 8501
# Linux/Mac: lsof -i :8501

# Try manually
streamlit run app.py
```

### "MT5 connection failed"

This is normal! You need to configure MT5 first:
1. Dashboard → Settings tab
2. MT5 Connection section
3. Enter your MT5 credentials
4. Click Connect

---

## 💡 Useful Commands:

```bash
# Check conda is installed
conda --version

# List all conda environments
conda env list

# Activate environment manually
conda activate mt5-sentiment-bot

# Deactivate when done
conda deactivate

# Update all packages in environment
conda env update -f environment.yml

# Remove environment (to start fresh)
conda env remove -n mt5-sentiment-bot

# Clean conda cache (free up space)
conda clean --all
```

---

## 📚 Need More Help?

- **Quick reference:** `START_HERE_ANACONDA.md`
- **Full documentation:** `ANACONDA_MIGRATION_COMPLETE.md`
- **Detailed setup:** `SETUP_GUIDE.md`
- **Troubleshooting:** Check the `logs/` folder

---

## 🎊 You're Ready!

Your professional MT5 trading bot is ready with Anaconda! 

**Benefits you now have:**
✅ **Stable environment** - No more dependency issues  
✅ **Automatic TA-Lib** - No manual installation  
✅ **Optimized ML** - Faster computations  
✅ **Professional setup** - Industry standard  
✅ **Easy updates** - Just `conda env update`  

---

**Pro Tips:**
- Use **Anaconda Prompt** on Windows for best experience
- Enable **Multi-Timeframe Analysis** for better signals
- Check **Health** tab to monitor system status
- Generate **PDF reports** from the dashboard
- Configure **alerts** in Settings tab

---

**Built with Anaconda - The Data Science Standard** 🐍📊

*Happy Trading!* 📈
