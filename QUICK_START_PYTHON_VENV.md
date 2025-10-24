# 🚀 Quick Start - Python venv (No Conda)

## ⚡ 3-Step Setup

### Windows:

```batch
# Step 1: Setup (one time only)
setup_venv.bat

# Step 2: Run the bot
run_bot.bat

# That's it!
```

### Linux/Mac:

```bash
# Step 1: Setup (one time only)
chmod +x setup_venv.sh run_bot.sh
./setup_venv.sh

# Step 2: Run the bot
./run_bot.sh

# That's it!
```

## 📋 Prerequisites

- **Python 3.11+** installed
- **Download**: https://www.python.org/downloads/
- **Windows**: Check "Add Python to PATH" during install

## ⚙️ What Happens During Setup

1. ✅ Creates Python virtual environment in `venv/` folder
2. ✅ Installs all dependencies from `requirements.txt`
3. ✅ Verifies critical packages (MT5, Streamlit, etc.)
4. ✅ Creates necessary folders (data, logs, models, reports)

**Time**: 5-10 minutes (downloads packages)

## 🎯 Daily Usage

Just run:
```batch
run_bot.bat    # Windows
./run_bot.sh   # Linux/Mac
```

The script automatically:
- Activates the virtual environment
- Checks dependencies
- Launches the Streamlit dashboard
- Opens browser to http://localhost:8501

## 🔍 Verify Installation

```batch
python verify_dependencies.py
```

Should show:
- ✅ All packages installed
- ✅ Running in Python venv

## 🆘 Troubleshooting

### TA-Lib fails to install (Windows):

1. Download wheel: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Install: `pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl`
3. Run `setup_venv.bat` again

### TensorFlow fails (Windows):

1. Install VC++ redistributables: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Run `setup_venv.bat` again

### Python not found:

- Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Python311\python.exe -m venv venv`

### Setup fails completely:

```batch
# Clean start
rmdir /s /q venv      # Windows
rm -rf venv           # Linux/Mac

# Try again
setup_venv.bat        # Windows
./setup_venv.sh       # Linux/Mac
```

## 📦 What Gets Installed

All packages from `requirements.txt`:

- **Core**: Streamlit, MetaTrader5
- **Data**: Pandas, NumPy, TA-Lib
- **ML**: Scikit-learn, XGBoost, LightGBM, CatBoost, TensorFlow
- **Viz**: Plotly, Matplotlib, Seaborn
- **Database**: SQLAlchemy
- **Logging**: Loguru
- **30+ packages total**

## 🔄 Migrating from Conda?

See: `PYTHON_VENV_MIGRATION.md`

Your data, models, and configs are safe - nothing changes in the bot code!

## 📁 Folder Structure After Setup

```
workspace/
├── venv/              # Virtual environment (auto-created)
├── data/              # Trading data & database
├── logs/              # Application logs
├── models/            # ML models
├── reports/           # Generated reports
├── src/               # Bot source code
├── gui/               # Streamlit interface
├── run_bot.bat        # START HERE (Windows)
├── run_bot.sh         # START HERE (Linux/Mac)
└── requirements.txt   # Dependencies list
```

## 🎉 Success Indicators

When everything works:

1. ✅ `setup_venv.bat` completes without errors
2. ✅ `verify_dependencies.py` shows all green checkmarks
3. ✅ `run_bot.bat` launches Streamlit dashboard
4. ✅ Browser opens to http://localhost:8501
5. ✅ You see the SMC Bot interface

## 💡 Tips

- **First run takes longer**: Downloads ~2GB of packages
- **Subsequent runs**: Start in seconds
- **Update packages**: Delete `venv/` and run `setup_venv` again
- **Multiple bots**: Each bot folder has its own `venv/`

## 🔗 Next Steps After Setup

1. Configure MT5 credentials in `credentials.toml`
2. Connect to MetaTrader 5
3. Select your trading symbol
4. Run sentiment analysis
5. View results in dashboard

Happy Trading! 🚀
