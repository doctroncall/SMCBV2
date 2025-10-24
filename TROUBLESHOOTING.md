# 🔧 Troubleshooting Guide

## Common Issues and Solutions

---

## 🚫 MT5 Connection Issues

### **Issue: "MT5 Connection (CRITICAL): Not connected"**

#### **Symptoms:**
- Health check shows MT5 connection failure
- Log shows: `MT5 initialization failed`
- Error: "Failed to collect data, check MT5 connection"

#### **Solutions:**

**1. Verify MT5 is Installed**
```bash
# Windows
dir "C:\Program Files\MetaTrader 5\terminal64.exe"

# If not found, download from:
# https://www.metatrader5.com/en/download
```

**2. Check Credentials**
The bot uses hardcoded testing credentials by default:
```
Login: 211744072
Password: dFbKaNLWQ53@9@Z
Server: ExnessKE-MT5Trial9
```

To verify:
```python
from config.settings import MT5Config
print(f"Login: {MT5Config.LOGIN}")
print(f"Server: {MT5Config.SERVER}")
```

**3. Check MT5 Path**
```python
# Verify path in config/settings.py
PATH: str = os.getenv("MT5_PATH", r"C:\Program Files\MetaTrader 5\terminal64.exe")

# Common paths:
# Windows: C:\Program Files\MetaTrader 5\terminal64.exe
# Windows (32-bit): C:\Program Files (x86)\MetaTrader 5\terminal.exe
```

**4. Test Connection Manually**
```python
from src.mt5.connection import MT5Connection

conn = MT5Connection()
try:
    if conn.connect():
        print("✅ Connected!")
        print(f"Account: {conn.get_account_info()}")
    else:
        print(f"❌ Failed: {conn._last_error}")
except Exception as e:
    print(f"❌ Error: {e}")
```

**5. Check Firewall**
- Allow `terminal64.exe` through Windows Firewall
- Check antivirus isn't blocking MT5

**6. Server Accessibility**
```python
# Try pinging the server
import socket
try:
    socket.gethostbyname('mt5.exness.com')
    print("✅ Server reachable")
except:
    print("❌ Server not reachable - check internet")
```

---

## 📊 Health Check Issues

### **Issue: "Health Check shows WARNING or CRITICAL"**

#### **Understanding Health Statuses:**

**Components Checked:**
1. **System Resources** (CPU, Memory, Disk)
2. **MT5 Connection** (Connected, Ping)
3. **Data Pipeline** (Database, Data freshness)
4. **ML Model** (Loaded, Accuracy)

#### **Reading Health Logs:**

**Before (Just counts):**
```
Health Check: Overall System - WARNING - Metrics: {"issues": 3}
```

**Now (Detailed):**
```
Health Check: Overall System - WARNING - Metrics: {"issue_count": 3, "details": "MT5 Connection (CRITICAL): Not connected - Missing credentials | Data Pipeline (WARNING): Low data freshness - 5 bars | ML Model (WARNING): No active model loaded"}

Health Issue 1/3: MT5 Connection (CRITICAL): Not connected - Missing credentials
Health Issue 2/3: Data Pipeline (WARNING): Low data freshness - 5 bars in last 24h
Health Issue 3/3: ML Model (WARNING): No active model loaded
```

#### **Solving Specific Issues:**

**1. System Resources (High CPU/Memory/Disk)**
```
Issue: "System resources (WARNING): CPU: 85.2%, Memory: 78.5%"

Solutions:
- Close unnecessary programs
- Increase RAM if consistently high
- Clean disk space
```

**2. MT5 Connection**
```
Issue: "MT5 Connection (CRITICAL): Not connected - Code 1, Init failed"

Solutions:
- See "MT5 Connection Issues" section above
- Check credentials
- Verify MT5 is running
- Check server status
```

**3. Data Pipeline**
```
Issue: "Data Pipeline (WARNING): Low data freshness - 5 bars in last 24h"

Solutions:
- Run analysis to fetch fresh data
- Check MT5 connection
- Verify database is writable
- Check data/ folder permissions
```

**4. ML Model**
```
Issue: "ML Model (WARNING): No active model loaded"

Solutions:
- Train a model first (will be added in future updates)
- Model loads after first training
- Check models/ folder exists
```

---

## 📈 GUI Issues

### **Issue: "Duplicate Metrics Displayed"**

**Status:** ✅ FIXED in latest version

**If still seeing:**
1. Pull latest code: `git pull origin main`
2. Restart bot: `start_bot.bat`

---

### **Issue: "Says connected but can't fetch data"**

#### **Diagnosis:**
```python
# Check connection status
from src.mt5.connection import get_mt5_connection
conn = get_mt5_connection()

print(f"Connected: {conn.is_connected()}")
print(f"Account Info: {conn.get_account_info()}")

# Try to fetch data
from src.mt5.data_fetcher import MT5DataFetcher
fetcher = MT5DataFetcher(conn)
df = fetcher.get_ohlcv("EURUSD", "H1", count=10)
print(f"Data fetched: {len(df) if df is not None else 0} bars")
```

#### **Solutions:**

**1. Connection is Stale**
```python
# Force reconnect
conn.disconnect()
conn.connect()
```

**2. Symbol Not Available**
```python
# Check available symbols
symbols = conn.get_symbols()
print(f"Available: {symbols[:10]}")  # First 10
```

**3. Market Closed**
```python
# Check trading hours
# Forex: Mon-Fri 24h (but feeds may have gaps)
# Check current time vs market hours
```

---

## 🗄️ Database Issues

### **Issue: "Database errors in logs"**

#### **Common Errors:**

**1. "Database locked"**
```
Solution: Only one instance should run at a time
- Close other bot instances
- Check for zombie processes
- Delete data/mt5_sentiment.db-journal if exists
```

**2. "Table doesn't exist"**
```python
Solution: Initialize database
from src.database.repository import DatabaseRepository
from src.database.models import Base
from sqlalchemy import create_engine

engine = create_engine("sqlite:///data/mt5_sentiment.db")
Base.metadata.create_all(engine)
print("✅ Database initialized")
```

**3. "Permission denied"**
```bash
# Check folder permissions
ls -la data/

# Fix permissions (Linux/Mac)
chmod 755 data/
chmod 644 data/mt5_sentiment.db

# Windows: Check folder isn't read-only
```

---

## 📊 Data Collection Issues

### **Issue: "Failed to collect data"**

#### **Error Variations:**
- "Error during analysis: Failed to fetch data"
- "No data available for analysis"
- "Empty dataframe returned"

#### **Solutions:**

**1. Check MT5 Connection**
```python
from src.mt5.connection import get_mt5_connection
conn = get_mt5_connection()
if not conn.is_connected():
    conn.connect()
```

**2. Verify Symbol Name**
```python
# Correct format
"EURUSD"  # ✅ Correct
"EUR/USD" # ❌ Wrong

# Check available symbols
import MetaTrader5 as mt5
symbols = mt5.symbols_get()
print([s.name for s in symbols[:20]])
```

**3. Check Timeframe**
```python
# Valid timeframes
valid_tfs = ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"]
```

**4. Increase Timeout**
```python
# In config/settings.py
TIMEOUT: int = 120000  # Increase to 2 minutes
```

---

## 🤖 ML Model Issues

### **Issue: "No active model loaded"**

**Status:** Expected on first run

**Solutions:**
1. Model training will be added in future updates
2. Bot works without ML (uses technical + SMC analysis)
3. ML features are optional enhancements

---

## 🔄 Auto-Refresh Issues

### **Issue: "Metrics not updating"**

#### **Solutions:**

**1. Check Update Frequency**
```python
# In config/settings.py
UPDATE_FREQUENCY: int = 5  # Minutes between updates
```

**2. Manual Refresh**
- Click "🔄 Refresh Now" in Metrics tab
- Click "Analyze" button to force update

**3. Session State**
```python
# In Streamlit, metrics track last update time
# Restart app to reset: Ctrl+C, then start_bot.bat
```

---

## 🎨 UI/Display Issues

### **Issue: "Charts not displaying"**

#### **Solutions:**

**1. Run Analysis First**
- Click "Analyze" button
- Wait for completion
- Charts appear in respective tabs

**2. Check Data Availability**
```python
# Need data to display charts
# Run at least one successful analysis
```

**3. Browser Cache**
- Hard refresh: Ctrl+Shift+R
- Clear browser cache
- Try different browser

---

## 📝 Log Analysis

### **Understanding Log Levels:**

```
INFO     - Normal operations
WARNING  - Potential issues, bot continues
ERROR    - Errors occurred, functionality impaired
CRITICAL - Severe errors, component failed
```

### **Key Log Files:**

```
logs/
  ├── mt5_bot.log           # Main log file
  ├── mt5_bot_errors.log    # Errors only
  ├── mt5_bot_json.log      # JSON format logs
  └── health/               # Health check logs
```

### **Searching Logs:**

```bash
# Find connection errors
grep "MT5 Connection" logs/mt5_bot.log

# Find today's errors
grep "ERROR" logs/mt5_bot.log | grep "2025-10-21"

# Last 20 lines
tail -n 20 logs/mt5_bot.log

# Follow live
tail -f logs/mt5_bot.log
```

---

## 🆘 Getting More Help

### **1. Enable Debug Mode**
```python
# In config/settings.py
DEBUG: bool = True
LOG_LEVEL: str = "DEBUG"
```

### **2. Run Diagnostics**
```python
from src.health.diagnostics import SystemDiagnostics

diag = SystemDiagnostics()
results = diag.run_full_diagnostics()

for test_name, result in results.items():
    print(f"{test_name}: {'✅' if result['passed'] else '❌'}")
    if not result['passed']:
        print(f"  Error: {result.get('error')}")
```

### **3. Check GitHub Issues**
https://github.com/doctroncall/CURSOR-SMC-MAIN/issues

### **4. Review Documentation**
- `SETUP_GUIDE.md` - Installation steps
- `ARCHITECTURE_REVIEW.md` - Technical details
- `METRICS_DOCUMENTATION.md` - Metrics info
- `TEST_CREDENTIALS.md` - Credentials info

---

## 🔍 Quick Diagnostic Checklist

```
□ MT5 installed and accessible
□ Credentials hardcoded in config/settings.py
□ Python 3.10+ installed
□ All dependencies installed (requirements.txt)
□ TA-Lib installed correctly
□ Firewall allows MT5
□ Internet connection active
□ Server (ExnessKE-MT5Trial9) accessible
□ data/ folder exists and writable
□ logs/ folder exists and writable
□ No other bot instances running
□ Latest code pulled from GitHub
```

---

## 📞 Still Having Issues?

If none of the above solutions work:

1. **Capture full error output:**
```bash
# Run with full logging
python app.py > debug.log 2>&1
```

2. **Check all logs:**
```bash
cat logs/mt5_bot.log
cat logs/mt5_bot_errors.log
```

3. **Provide details:**
- Operating system
- Python version
- MT5 version
- Error messages
- Steps to reproduce

4. **Open GitHub issue:**
- Include log excerpts
- Describe what you tried
- Mention this guide

---

**Last Updated:** 2025-10-21  
**Status:** ✅ Active Support
