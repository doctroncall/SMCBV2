# 🚀 START HERE - SMC Trading Bot Setup

## Choose Your Setup Method

### ⭐ **RECOMMENDED: Python venv (Simple & Fast)**

**Best for**: Most users, simpler setup, no Anaconda needed

```batch
# Windows
setup_venv.bat
run_bot.bat

# Linux/Mac
./setup_venv.sh
./run_bot.sh
```

📖 **Full Guide**: [QUICK_START_PYTHON_VENV.md](QUICK_START_PYTHON_VENV.md)

---

### 📦 **Alternative: Anaconda/Conda (If you prefer)**

**Best for**: Users who already have Anaconda installed

```batch
# Windows
conda smc.bat

# Linux/Mac
./start_bot.sh
```

📖 **Full Guide**: [START_HERE_ANACONDA.md](START_HERE_ANACONDA.md)

---

## 🔄 Migrating from Conda to Python venv?

If you're currently using Anaconda and want to switch to pure Python:

📖 **Migration Guide**: [PYTHON_VENV_MIGRATION.md](PYTHON_VENV_MIGRATION.md)

**TL;DR**: Run `setup_venv.bat`, then use `run_bot.bat`. Your data is safe!

---

## ⚡ Super Quick Start

1. **Install Python 3.11+**: https://www.python.org/downloads/
2. **Run setup**:
   - Windows: Double-click `setup_venv.bat`
   - Linux/Mac: `./setup_venv.sh`
3. **Run bot**:
   - Windows: Double-click `run_bot.bat`
   - Linux/Mac: `./run_bot.sh`
4. **Configure MT5** in the dashboard
5. **Start trading!**

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **QUICK_START_PYTHON_VENV.md** | Python venv setup (recommended) |
| **PYTHON_VENV_MIGRATION.md** | Migrate from Conda to Python |
| **START_HERE_ANACONDA.md** | Anaconda/Conda setup |
| **QUICK_START.md** | Original quick start guide |
| **README.md** | Full project documentation |
| **TROUBLESHOOTING.md** | Common issues & solutions |

---

## 🆘 Need Help?

1. **Verify dependencies**: `python verify_dependencies.py`
2. **Check logs**: Look in `logs/` folder
3. **Common issues**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 🎯 What's Different Between Methods?

| Aspect | Python venv | Anaconda |
|--------|------------|----------|
| Setup Complexity | ⭐ Simple | ⭐⭐ Medium |
| Download Size | ~2GB packages | ~2GB packages + 400MB Anaconda |
| Installation Time | 5-10 min | 10-20 min |
| Bot Features | ✅ All | ✅ All |
| Performance | ✅ Same | ✅ Same |
| Updates | `pip` | `conda` |

**Both work identically!** Choose what's easier for you.

---

## ✅ Success Checklist

- [ ] Python 3.11+ installed (check: `python --version`)
- [ ] Setup script completed successfully
- [ ] All dependencies verified (green checkmarks)
- [ ] Bot dashboard opens in browser
- [ ] MT5 connection configured

---

## 🚀 Ready to Trade!

After setup, see:
- **Quick Start Guide**: [QUICK_START.md](QUICK_START.md)
- **Full Documentation**: [README.md](README.md)

Happy Trading! 📈
