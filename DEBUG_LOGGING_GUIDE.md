# 🔍 Comprehensive Debug Logging Guide

**Date:** 2025-10-21  
**Purpose:** Track every step of execution to identify failures  
**Status:** ✅ ENABLED

---

## 📋 **Log Files Created:**

### **1. `logs/mt5_bot_debug_trace.log`** 🔥 **PRIMARY DEBUG LOG**
**Purpose:** Comprehensive trace of EVERY step  
**Level:** DEBUG (most detailed)  
**Format:**
```
2025-10-21 03:45:23.456 | DEBUG    | mt5_connection      | mt5_connector.py:connect:45 | [DEBUG] MT5Connector.connect() called
2025-10-21 03:45:23.457 | DEBUG    | mt5_connection      | mt5_connector.py:connect:46 |   Login: 211744072
2025-10-21 03:45:23.458 | DEBUG    | data_fetcher        | data_fetcher.py:get_ohlcv:195 | [DEBUG] Calling mt5.copy_rates_from_pos(EURUSD, 16385, 0, 1000)...
```

**Features:**
- ✅ Millisecond precision timestamps
- ✅ Shows exact file:function:line
- ✅ Includes stack traces
- ✅ 50MB rotation
- ✅ 7 day retention

---

### **2. `logs/mt5_bot.log`** 📝 **GENERAL LOG**
**Purpose:** All operations (INFO level and above)  
**Level:** INFO  
**Format:**
```
2025-10-21 03:45:23 | INFO     | general - Starting analysis
2025-10-21 03:45:24 | INFO     | mt5 - Connected to MT5: 211744072
2025-10-21 03:45:25 | INFO     | data_fetcher - Fetched 1000 bars for EURUSD H1
```

---

### **3. `logs/mt5_bot_errors.log`** ❌ **ERRORS ONLY**
**Purpose:** Only errors and critical issues  
**Level:** ERROR  
**Format:**
```
2025-10-21 03:45:30 | ERROR    | mt5 - Failed to fetch data: Symbol not found
2025-10-21 03:45:31 | ERROR    | health - Health check failed: MT5 not connected
```

---

### **4. `logs/mt5_bot_json.log`** 🔧 **MACHINE-READABLE**
**Purpose:** JSON format for automated processing  
**Level:** DEBUG  
**Format:**
```json
{"text": "Connected to MT5", "record": {"time": "2025-10-21T03:45:23.456", "level": "INFO", "message": "Connected to MT5: 211744072"}}
```

---

## 🔍 **What's Being Logged:**

### **MT5 Connector (`mt5_connector.py`):**

#### **On Initialization:**
```
[DEBUG] MT5Connector.__init__() - Created new connector instance
[DEBUG]   Login: 211744072
[DEBUG]   Server: ExnessKE-MT5Trial9
[DEBUG]   Path: C:\Program Files\MetaTrader 5\terminal64.exe
```

#### **On is_connected() Check:**
```
[DEBUG] MT5Connector.is_connected() called
[DEBUG]   self.connected = True
[DEBUG]   terminal_info = True
[DEBUG]   Result = True
```

**Why This Matters:**
- Shows if connector thinks it's connected
- Shows if MT5 terminal is actually running
- Reveals mismatches (thinks connected but terminal isn't)

---

### **Data Fetcher (`src/mt5/data_fetcher.py`):**

#### **On Initialization:**
```
[DEBUG] MT5DataFetcher.__init__() called
[DEBUG]   connection parameter = None
[DEBUG]   Will use: Global MT5 API
[DEBUG]   Global MT5 terminal_info = <TerminalInfo object>
[DEBUG]   ✓ MT5 globally initialized
[DEBUG]   Terminal: MetaTrader 5
[DEBUG]   Company: Exness (KE) Limited
```

**Why This Matters:**
- Shows if connection=None was passed correctly
- Confirms global MT5 is initialized
- Shows which terminal is connected

#### **On Data Fetch (get_ohlcv):**
```
[DEBUG] MT5DataFetcher.get_ohlcv() called
[DEBUG]   Symbol: EURUSD
[DEBUG]   Timeframe: H1
[DEBUG]   Count: 1000
[DEBUG]   Start pos: 0
[DEBUG]   Total requests so far: 1
[DEBUG]   Converting timeframe string to enum...
[DEBUG]   ✓ Timeframe enum: Timeframe.H1
[DEBUG]   ✓ Timeframe value: 16385
[DEBUG]   Checking MT5 state before fetching...
[DEBUG]   ✓ MT5 terminal connected
[DEBUG]   Terminal: MetaTrader 5
[DEBUG]   Calling mt5.copy_rates_from_pos(EURUSD, 16385, 0, 1000)...
[DEBUG]   mt5.copy_rates_from_pos() returned: <class 'numpy.ndarray'>
[DEBUG]   ✓ Successfully fetched 1000 rates
[DEBUG]   First rate time: 2025-10-15 10:00:00
[DEBUG]   Last rate time: 2025-10-21 03:45:00
```

**Why This Matters:**
- Tracks exact parameters passed
- Shows timeframe conversion (H1 → 16385)
- Verifies MT5 connection before fetching
- Shows actual MT5 API call
- Shows return type (should be numpy array)
- Shows number of rates fetched
- Shows data time range

#### **On Failure:**
```
[DEBUG]   ✗ FAILED to fetch data!
[DEBUG]   rates = None
[DEBUG]   MT5 Error: (1, 'Unknown symbol')
[DEBUG]   Error code: 1
[DEBUG]   Error message: Unknown symbol
```

**Common Error Codes:**
- `1` - Unknown symbol
- `2` - Invalid arguments
- `64` - No connection
- `4754` - Symbol not selected in Market Watch

---

## 🎯 **How to Use the Logs:**

### **Scenario 1: Data Fetching Fails**

**What to check in `mt5_bot_debug_trace.log`:**

```bash
# Search for the fetch attempt
grep "get_ohlcv" logs/mt5_bot_debug_trace.log | tail -50

# Look for:
1. Was get_ohlcv() called?
   → [DEBUG] MT5DataFetcher.get_ohlcv() called

2. What parameters were passed?
   → Symbol: EURUSD, Timeframe: H1, Count: 1000

3. Did timeframe convert?
   → ✓ Timeframe enum: Timeframe.H1

4. Was MT5 connected?
   → ✓ MT5 terminal connected
   OR
   → ✗ MT5 terminal NOT connected!

5. What did copy_rates_from_pos return?
   → mt5.copy_rates_from_pos() returned: <class 'numpy.ndarray'>
   OR
   → ✗ FAILED to fetch data!

6. If failed, what was the error?
   → MT5 Error: (64, 'No connection')
```

---

### **Scenario 2: Health Check Shows CRITICAL**

**What to check in `mt5_bot_debug_trace.log`:**

```bash
# Search for health check
grep "is_connected" logs/mt5_bot_debug_trace.log | tail -20

# Look for:
1. Was is_connected() called?
   → [DEBUG] MT5Connector.is_connected() called

2. What did self.connected say?
   → self.connected = True  (connector thinks it's connected)
   OR
   → self.connected = False (connector knows it's not)

3. What did terminal_info say?
   → terminal_info = True  (MT5 actually running)
   OR
   → terminal_info = False (MT5 not running!)

4. What was the final result?
   → Result = True  (should show HEALTHY)
   OR
   → Result = False (will show CRITICAL)
```

---

### **Scenario 3: Connection Issues**

**What to check in `mt5_bot_debug_trace.log`:**

```bash
# Search for connector initialization
grep "MT5Connector.__init__" logs/mt5_bot_debug_trace.log

# Look for:
1. How many times was connector created?
   → Should see 1 time (single instance)
   → If you see 2+ times, multiple instances created! ❌

2. What credentials were used?
   → Login: 211744072
   → Server: ExnessKE-MT5Trial9

3. Then search for connection attempts
grep "MT5 CONNECTION ATTEMPT" logs/mt5_bot_debug_trace.log

4. Look for connection success
grep "CONNECTION SUCCESSFUL" logs/mt5_bot_debug_trace.log
```

---

## 📊 **Debug Console Prints:**

In addition to log files, debug info is printed to **console in real-time**:

```bash
# When bot starts:
[DEBUG] MT5Connector.__init__() - Created new connector instance
[DEBUG]   Login: 211744072
[DEBUG]   Server: ExnessKE-MT5Trial9

# When connecting:
============================================================
MT5 CONNECTION ATTEMPT
============================================================
[1/4] Validating credentials...
   ✓ Credentials validated
...

# When fetching data:
[DEBUG] MT5DataFetcher.__init__() called
[DEBUG]   connection parameter = None
[DEBUG]   Will use: Global MT5 API
[DEBUG]   ✓ MT5 globally initialized

[DEBUG] MT5DataFetcher.get_ohlcv() called
[DEBUG]   Symbol: EURUSD
[DEBUG]   ✓ Successfully fetched 1000 rates
```

---

## 🔧 **Analyzing Logs:**

### **Method 1: Tail in Real-Time**
```bash
# Watch debug log live
tail -f logs/mt5_bot_debug_trace.log

# Watch errors only
tail -f logs/mt5_bot_errors.log
```

### **Method 2: Search Specific Issues**
```bash
# Find all failures
grep "✗" logs/mt5_bot_debug_trace.log

# Find MT5 errors
grep "MT5 Error" logs/mt5_bot_debug_trace.log

# Find connection checks
grep "is_connected" logs/mt5_bot_debug_trace.log

# Find data fetches
grep "get_ohlcv" logs/mt5_bot_debug_trace.log
```

### **Method 3: Extract Specific Timeframe**
```bash
# Get logs from last 5 minutes
grep "2025-10-21 03:4[0-5]" logs/mt5_bot_debug_trace.log

# Get logs for specific operation
grep -A 20 "get_ohlcv() called" logs/mt5_bot_debug_trace.log
```

---

## 🎯 **What Each Check Tells You:**

| Check | Success | Failure | Meaning |
|-------|---------|---------|---------|
| `MT5Connector.__init__` | 1 instance | Multiple instances | Single vs multiple connectors |
| `is_connected()` | `Result = True` | `Result = False` | Actual connection state |
| `self.connected` | `True` | `False` | Connector thinks it's connected |
| `terminal_info` | `True` | `False` | MT5 terminal actually running |
| `Global MT5 initialized` | ✓ | ✗ | MT5 API initialized globally |
| `copy_rates_from_pos()` | `<class 'numpy.ndarray'>` | `None` | Data fetch success |
| `Successfully fetched X rates` | ✓ | ✗ | Got data from MT5 |

---

## 🚀 **Testing The Debug Logging:**

### **Test 1: Check Log Files Created**
```bash
# After starting bot, check logs directory
ls -lh logs/

# Should see:
mt5_bot.log
mt5_bot_errors.log
mt5_bot_json.log
mt5_bot_debug_trace.log  ← NEW!
```

### **Test 2: Check Debug Output**
```bash
# Look at last 50 lines
tail -50 logs/mt5_bot_debug_trace.log

# Should see:
[DEBUG] entries with millisecond timestamps
[DEBUG] file:function:line information
[DEBUG] Detailed step-by-step traces
```

### **Test 3: Trace a Connection**
1. Start bot: `start_bot.bat`
2. Connect to MT5 (Settings tab)
3. Check log:
```bash
grep "MT5Connector" logs/mt5_bot_debug_trace.log | tail -20
```

### **Test 4: Trace a Data Fetch**
1. Connect to MT5
2. Run Analysis (EURUSD H1)
3. Check log:
```bash
grep "get_ohlcv" logs/mt5_bot_debug_trace.log | tail -50
```

---

## 📋 **Debugging Checklist:**

When something fails:

1. ✅ Check console output first (real-time)
2. ✅ Check `mt5_bot_debug_trace.log` (comprehensive)
3. ✅ Search for `✗` (failures)
4. ✅ Search for the failing operation
5. ✅ Check preceding steps
6. ✅ Look for MT5 Error codes
7. ✅ Verify connection state
8. ✅ Check for multiple connector instances

---

## 🎉 **What This Gives You:**

### **Before (Limited Logging):**
```
Failed to fetch data
```
❌ No idea why!

### **After (Comprehensive Logging):**
```
[DEBUG] MT5DataFetcher.get_ohlcv() called
[DEBUG]   Symbol: EURUSD
[DEBUG]   ✓ Timeframe enum: Timeframe.H1
[DEBUG]   Checking MT5 state before fetching...
[DEBUG]   ✗ MT5 terminal NOT connected!
[DEBUG]   MT5 Error: (64, 'No connection')
[DEBUG]   ✗ FAILED to fetch data!
```
✅ **Exact cause:** MT5 not connected, error code 64!

---

## 📞 **Next Steps:**

1. **Restart bot:**
   ```bash
   start_bot.bat
   ```

2. **Reproduce the issue**

3. **Send me the last 100 lines of debug log:**
   ```bash
   tail -100 logs/mt5_bot_debug_trace.log
   ```

4. **I'll tell you exactly what's failing!** 🎯

---

**Status:** ✅ Comprehensive logging enabled  
**Result:** Every step traced, failures identified easily!
