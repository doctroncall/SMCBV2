# 🔄 Migration from Anaconda to Pure Python (venv)

## 📋 Overview

This guide helps you migrate from Anaconda/Conda to pure Python virtual environments (venv). The bot code **remains unchanged** - only the environment setup is different.

## ✅ Why Migrate?

- **Simpler**: No need to install/manage Anaconda (400MB+ download)
- **Faster**: pip is generally faster than conda for package installation
- **Standard**: Uses Python's built-in `venv` module (no external dependencies)
- **Lighter**: Virtual environment is smaller and more portable
- **Compatible**: All bot features work identically in both environments

## ⚠️ Important: Nothing Changes in the Bot Code!

The migration is **100% safe** because:
- ✅ The bot Python code is **identical** in both environments
- ✅ All dependencies are the same (just installed via pip instead of conda)
- ✅ Your existing data, models, and configurations are **preserved**
- ✅ You can switch back to conda anytime if needed

## 🚀 Quick Start: Migration Steps

### Option A: Clean Migration (Recommended)

1. **Backup your data** (optional but recommended):
   ```bash
   # Your data/models/logs are safe, but good practice:
   # Copy the entire project folder as backup
   ```

2. **Run the Python venv setup**:
   
   **Windows:**
   ```batch
   setup_venv.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x setup_venv.sh
   ./setup_venv.sh
   ```

3. **Start the bot with new launcher**:
   
   **Windows:**
   ```batch
   run_bot.bat
   ```
   
   **Linux/Mac:**
   ```bash
   ./run_bot.sh
   ```

That's it! You're now running on pure Python.

### Option B: Side-by-Side Testing

Keep both environments and test before fully migrating:

1. **Create venv** (without removing conda):
   ```batch
   setup_venv.bat    # Windows
   ./setup_venv.sh   # Linux/Mac
   ```

2. **Test with venv**:
   ```batch
   run_bot.bat       # Uses venv
   ```

3. **Compare with conda** (if you want):
   ```batch
   conda smc.bat     # Still works!
   ```

4. **Once satisfied, you can remove conda** (optional):
   - Uninstall Anaconda/Miniconda from your system
   - Or just keep both (they don't conflict)

## 📁 File Changes Overview

### New Files (venv-based):
```
✅ setup_venv.bat          # Windows: Create Python venv
✅ setup_venv.sh           # Linux/Mac: Create Python venv
✅ run_bot.bat             # Windows: Run bot with venv
✅ run_bot.sh              # Linux/Mac: Run bot with venv
✅ PYTHON_VENV_MIGRATION.md # This guide
```

### Old Files (conda-based) - Still Available:
```
📦 conda smc.bat           # Old Windows conda launcher
📦 start_bot.sh            # Old Linux/Mac conda launcher
📦 start_bot.bat           # Wrapper for conda smc.bat
📦 environment.yml         # Conda environment definition
📦 fix_loguru.bat          # Conda-specific fix
📦 verify_dependencies.bat # Now supports both!
```

### Updated Files:
```
✏️ verify_dependencies.py  # Now detects venv or conda automatically
✏️ requirements.txt        # Already existed, now primary source
```

### Unchanged (Your Data is Safe):
```
✅ data/                   # All your trading data
✅ logs/                   # All your logs
✅ models/                 # All your ML models
✅ reports/                # All your reports
✅ config.toml             # Your configuration
✅ credentials.toml        # Your MT5 credentials
✅ All source code         # Zero changes to bot logic!
```

## 🔧 Technical Details

### Python Requirements

- **Python Version**: 3.11 or later (same as conda requirement)
- **Installation**: Download from [python.org](https://www.python.org/downloads/)
- **Important**: Check "Add Python to PATH" during installation (Windows)

### Installation Process

#### Windows Setup

```batch
# 1. Check Python is installed
python --version

# 2. Create virtual environment
python -m venv venv

# 3. Activate (done automatically by scripts)
venv\Scripts\activate.bat

# 4. Install packages
pip install -r requirements.txt

# Use the automated script:
setup_venv.bat
```

#### Linux/Mac Setup

```bash
# 1. Check Python is installed
python3 --version

# 2. Install venv if needed (Ubuntu/Debian)
sudo apt install python3.11-venv

# 3. Create virtual environment
python3 -m venv venv

# 4. Activate (done automatically by scripts)
source venv/bin/activate

# 5. Install packages
pip install -r requirements.txt

# Use the automated script:
./setup_venv.sh
```

### Package Installation

All packages from `environment.yml` are in `requirements.txt`:

| Package | Conda | Pip (venv) | Notes |
|---------|-------|------------|-------|
| streamlit | ✓ | ✓ | Identical |
| pandas | ✓ | ✓ | Identical |
| numpy | ✓ | ✓ | Identical |
| MetaTrader5 | via pip | ✓ | Same source |
| TA-Lib | via conda-forge | ✓* | May need manual install (see below) |
| scikit-learn | ✓ | ✓ | Identical |
| xgboost | ✓ | ✓ | Identical |
| lightgbm | ✓ | ✓ | Identical |
| catboost | via pip | ✓ | Same source |
| tensorflow | ✓ | ✓ | Identical |
| plotly | ✓ | ✓ | Identical |
| loguru | ✓ | ✓ | Identical |
| All others | ✓ | ✓ | Identical |

**Note on TA-Lib**: This is the only package that may need special handling on some systems.

## 🔍 Troubleshooting

### TA-Lib Installation Issues

TA-Lib is the most common issue when moving from conda to pip.

#### Windows Solutions:

**Option 1 - Pre-compiled Wheel (Easiest):**
1. Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Choose correct version (e.g., `TA_Lib-0.4.28-cp311-cp311-win_amd64.whl` for Python 3.11)
3. Install: `pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl`

**Option 2 - Try pip directly:**
```batch
pip install TA-Lib
```

If it works, great! If not, use Option 1.

#### Linux Solutions:

**Ubuntu/Debian:**
```bash
# Install dependencies
sudo apt-get install build-essential wget

# Install TA-Lib C library
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Install Python wrapper
pip install TA-Lib
```

**macOS:**
```bash
# Install via Homebrew
brew install ta-lib

# Install Python wrapper
pip install TA-Lib
```

### TensorFlow Issues

If TensorFlow fails to install:

**Windows:**
1. Install Visual C++ Redistributables: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Retry: `pip install tensorflow`

**Linux:**
Usually works out of the box. If not:
```bash
pip install tensorflow-cpu  # CPU-only version
```

### Other Common Issues

#### "Python not found"
- Windows: Reinstall Python with "Add to PATH" checked
- Linux/Mac: Use `python3` instead of `python`

#### "venv not found"
- Ubuntu/Debian: `sudo apt install python3.11-venv`
- Should be built-in on Windows/Mac

#### "pip is outdated"
```bash
python -m pip install --upgrade pip
```

#### Packages failing to install
```bash
# Upgrade pip and retry
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 🔄 Switching Between Environments

You can keep both and switch as needed:

### Use venv:
```batch
run_bot.bat          # Windows
./run_bot.sh         # Linux/Mac
```

### Use conda:
```batch
conda smc.bat        # Windows
./start_bot.sh       # Linux/Mac
```

### Check current environment:
```batch
verify_dependencies.bat  # Windows
python verify_dependencies.py  # Linux/Mac
```

## 🗑️ Removing Conda (Optional)

If you want to completely remove Anaconda/Miniconda after migrating:

### Windows:
1. Settings → Apps → Uninstall "Anaconda3" or "Miniconda3"
2. Delete folder: `C:\Users\<username>\anaconda3` (if exists)
3. Remove from PATH (Settings → Environment Variables)

### Linux:
```bash
# Remove conda
rm -rf ~/anaconda3  # or ~/miniconda3
rm -rf ~/.conda

# Remove from shell config
# Edit ~/.bashrc and remove conda init section
nano ~/.bashrc
```

### macOS:
```bash
# If installed via Homebrew
brew uninstall anaconda  # or miniconda

# If installed manually
rm -rf ~/anaconda3  # or ~/miniconda3
rm -rf ~/.conda
```

**Note**: Only do this after confirming venv works perfectly!

## 📊 Verification

After migration, verify everything works:

1. **Check Python environment**:
   ```batch
   python verify_dependencies.py
   ```
   Should show: "✓ Running in Python venv"

2. **Test bot startup**:
   ```batch
   run_bot.bat  # or ./run_bot.sh
   ```
   Should launch without errors

3. **Test MT5 connection**:
   - Open the bot dashboard
   - Go to MT5 Connection panel
   - Connect to MT5
   - Should work identically

4. **Test analysis**:
   - Run a sentiment analysis
   - Check all panels work
   - Verify ML models load correctly

## 🎯 Summary

| Aspect | Before (Conda) | After (venv) | Changed? |
|--------|---------------|--------------|----------|
| Bot Code | ✓ Working | ✓ Working | ❌ No |
| Dependencies | ✓ Installed | ✓ Installed | ❌ No |
| Data/Models | ✓ Saved | ✓ Saved | ❌ No |
| Configuration | ✓ Set | ✓ Set | ❌ No |
| Startup Script | `conda smc.bat` | `run_bot.bat` | ✅ Yes |
| Environment | Anaconda | Python venv | ✅ Yes |
| Package Manager | conda | pip | ✅ Yes |

**Bottom Line**: Only the environment setup changes. The bot itself is untouched!

## 🆘 Need Help?

If you encounter issues:

1. **Check verify_dependencies.py output** - it will tell you what's missing
2. **Review setup script output** - look for error messages
3. **Common fixes**:
   - Delete `venv` folder and run `setup_venv` again
   - Update pip: `python -m pip install --upgrade pip`
   - Install packages one by one to find the problematic one

## 📚 Additional Resources

- Python venv docs: https://docs.python.org/3/library/venv.html
- pip documentation: https://pip.pypa.io/
- TA-Lib wheels (Windows): https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
- Python downloads: https://www.python.org/downloads/

---

**Migration Date**: 2025-10-23  
**Bot Version**: v2.0+  
**Status**: ✅ Tested and Production-Ready
