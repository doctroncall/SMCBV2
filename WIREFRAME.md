# MT5 Sentiment Bot - Visual Wireframe

## 🎨 Main Dashboard - Detailed Wireframe

### Full Layout View

```
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║  🎯 MT5 SENTIMENT ANALYSIS BOT v1.0                     [🏥 Health: ● Healthy] [⚙️]      ║
╠═══════════════════════════════════════════════════════════════════════════════════════════╣
║ ┌─────────────────────────────────────────────────────────────────────────────────────┐  ║
║ │  CONTROL PANEL                                                                      │  ║
║ │  ┌──────────┐ ┌───────────┐ ┌────────────┐ ┌──────────────┐  Last Update: 14:32:15│  ║
║ │  │Symbol    │ │Timeframe  │ │Auto-Refresh│ │MT5 Status    │  Next Update: 14:35:00│  ║
║ │  │EURUSD  ▼ │ │H1       ▼ │ │[●] ON      │ │[●] Connected │                       │  ║
║ │  └──────────┘ └───────────┘ └────────────┘ └──────────────┘                       │  ║
║ └─────────────────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                           ║
║ ┌─────────────────────┐  ┌────────────────────────────────────────────────────────────┐ ║
║ │  CURRENT SENTIMENT  │  │  CONFIDENCE & FACTORS                                      │ ║
║ │                     │  │                                                            │ ║
║ │       ⬆️             │  │  Overall Confidence: 82%                                   │ ║
║ │    BULLISH          │  │  ████████████████████░░░░░                                │ ║
║ │                     │  │                                                            │ ║
║ │   Confidence        │  │  Contributing Factors:                                     │ ║
║ │      82%            │  │  ✓ Trend Direction (95%)      Weight: 25%                 │ ║
║ │                     │  │  ✓ SMC Structure (88%)        Weight: 30%                 │ ║
║ │   Risk Level        │  │  ✓ Momentum (76%)             Weight: 20%                 │ ║
║ │    🟡 MEDIUM        │  │  ✓ Volume Profile (79%)       Weight: 15%                 │ ║
║ │                     │  │  ⚠ Volatility (54%)           Weight: 10%                 │ ║
║ │  [Since: 09:15]     │  │                                                            │ ║
║ │  [Duration: 5h 17m] │  │  📊 Timeframe Confluence:                                  │ ║
║ │                     │  │  M15: BULLISH (78%)  H1: BULLISH (82%)                    │ ║
║ │  Previous:          │  │  H4:  BULLISH (75%)  D1: BULLISH (71%)                    │ ║
║ │  NEUTRAL (68%)      │  │                                                            │ ║
║ └─────────────────────┘  └────────────────────────────────────────────────────────────┘ ║
║                                                                                           ║
║ ┌─────────────────────────────────────────────────────────────────────────────────────┐  ║
║ │  📊 LIVE PRICE CHART                                         [📷] [↗️] [⬇️ Export]   │  ║
║ │ ╔═══════════════════════════════════════════════════════════════════════════════╗  │  ║
║ │ ║  1.0890 ┤                                    ┌──┐                            ║  │  ║
║ │ ║         ┤                               ┌────┘  └───┐                        ║  │  ║
║ │ ║  1.0880 ┤                          ┌────┘           │    ⬆️ CURRENT          ║  │  ║
║ │ ║         ┤                     ┌────┘                └──┐                     ║  │  ║
║ │ ║  1.0870 ┤  [Order Block] ▓▓▓▓│                        └──┐                  ║  │  ║
║ │ ║         ┤                └────┘                          └─────┐             ║  │  ║
║ │ ║  1.0860 ┤              [FVG] ░░░░░                            │             ║  │  ║
║ │ ║         ┤         ┌────┘                                      └──           ║  │  ║
║ │ ║  1.0850 ┤    ─────┘  [Liquidity Zone] ▼▼▼                                  ║  │  ║
║ │ ║         └─────┬────────┬────────┬────────┬────────┬────────┬───────┬───     ║  │  ║
║ │ ║              09:00   10:00   11:00   12:00   13:00   14:00   15:00        ║  │  ║
║ │ ╚═══════════════════════════════════════════════════════════════════════════════╝  │  ║
║ │  Legend: [▓] Order Blocks  [░] Fair Value Gap  [▼] Liquidity  [─] Support/Resist │  ║
║ └─────────────────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                           ║
║ ╔═══════════════════════════════════════════════════════════════════════════════════╗   ║
║ ║ TABS: [📈 Indicators] [🧠 Smart Money] [📊 ML Analysis] [📜 History] [🔍 Logs]  ║   ║
║ ╠═══════════════════════════════════════════════════════════════════════════════════╣   ║
║ ║ 📈 TECHNICAL INDICATORS                                                           ║   ║
║ ║ ┌────────────────┬──────────┬──────────────┬──────────┬────────────────────────┐ ║   ║
║ ║ │ Indicator      │ Value    │ Signal       │ Strength │ Contribution           │ ║   ║
║ ║ ├────────────────┼──────────┼──────────────┼──────────┼────────────────────────┤ ║   ║
║ ║ │ RSI (14)       │ 67.3     │ 🟢 BULLISH   │ ████████ │ 8/10                   │ ║   ║
║ ║ │ MACD           │ +0.0023↑ │ 🟢 BULLISH   │ █████████│ 9/10                   │ ║   ║
║ ║ │ ADX (14)       │ 28.5     │ 🟡 TRENDING  │ ███████  │ 7/10                   │ ║   ║
║ ║ │ Stochastic     │ 71.2/68.9│ 🟢 BULLISH   │ ███████  │ 7/10                   │ ║   ║
║ ║ │ Bollinger B.   │ Upper 25%│ 🟡 NEUTRAL   │ █████    │ 5/10                   │ ║   ║
║ ║ │ ATR (14)       │ 0.0015   │ 🟡 NORMAL    │ ██████   │ 6/10                   │ ║   ║
║ ║ │ EMA 20/50      │ +0.0034  │ 🟢 BULLISH   │ ████████ │ 8/10                   │ ║   ║
║ ║ │ VWAP           │ 1.0862   │ 🟢 ABOVE     │ ███████  │ 7/10                   │ ║   ║
║ ║ │ Volume Profile │ POC:1.086│ 🟢 BULLISH   │ ███████  │ 7/10                   │ ║   ║
║ ║ │ OBV            │ +125.4M↑ │ 🟢 BULLISH   │ ████████ │ 8/10                   │ ║   ║
║ ║ └────────────────┴──────────┴──────────────┴──────────┴────────────────────────┘ ║   ║
║ ║                                                                                   ║   ║
║ ║ [📊 Show Indicator Details] [⚙️ Configure Weights] [📈 View Indicator Charts]    ║   ║
║ ╚═══════════════════════════════════════════════════════════════════════════════════╝   ║
║                                                                                           ║
║ ╔═══════════════════════════════════════════════════════════════════════════════════╗   ║
║ ║ 🧠 SMART MONEY CONCEPTS (SMC) ANALYSIS                                            ║   ║
║ ║                                                                                   ║   ║
║ ║ 📈 Market Structure: BULLISH (Higher Highs, Higher Lows Pattern)                 ║   ║
║ ║    ┌────────────────────────────────────────────────────────────────┐            ║   ║
║ ║    │ Last BOS (Break of Structure): 1.0856 @ 15:20                 │            ║   ║
║ ║    │ Previous ChOCh: 1.0841 @ 14:05                                │            ║   ║
║ ║    │ Swing High: 1.0891 | Swing Low: 1.0834                        │            ║   ║
║ ║    └────────────────────────────────────────────────────────────────┘            ║   ║
║ ║                                                                                   ║   ║
║ ║ 📦 Active Order Blocks (3):                                                      ║   ║
║ ║    ┌─────────────────────────────────────────────────────────────────────────┐   ║   ║
║ ║    │ 1. 🟢 Bullish OB: 1.0842-1.0847 | Strength: ████████ 8/10 | ACTIVE      │   ║   ║
║ ║    │    - Created: 13:45 | Tested: 0 times | Volume: High                    │   ║
║ ║    │ 2. 🟢 Bullish OB: 1.0835-1.0839 | Strength: ██████ 6/10 | ACTIVE        │   ║
║ ║    │    - Created: 12:30 | Tested: 1 time | Volume: Medium                   │   ║
║ ║    │ 3. 🔴 Bearish OB: 1.0893-1.0897 | Strength: █████ 5/10 | RESISTANCE     │   ║
║ ║    └─────────────────────────────────────────────────────────────────────────┘   ║   ║
║ ║                                                                                   ║   ║
║ ║ 📊 Fair Value Gaps (FVGs):                                                       ║   ║
║ ║    ┌─────────────────────────────────────────────────────────────────────────┐   ║   ║
║ ║    │ • FVG #1: 1.0838-1.0841 | Status: UNFILLED (50%) | Priority: HIGH      │   ║   ║
║ ║    │ • FVG #2: 1.0851-1.0854 | Status: FILLED | Created: 11:20              │   ║   ║
║ ║    └─────────────────────────────────────────────────────────────────────────┘   ║   ║
║ ║                                                                                   ║   ║
║ ║ 💧 Liquidity Analysis:                                                           ║   ║
║ ║    ┌─────────────────────────────────────────────────────────────────────────┐   ║   ║
║ ║    │ • Liquidity Pool: 1.0835 (Weak - Likely Target)                        │   ║   ║
║ ║    │ • Equal Lows: 1.0832, 1.0834 (3 touches - High Priority Target)        │   ║   ║
║ ║    │ • Stop Hunt Detected: 1.0836 @ 10:15 (Wicked down)                     │   ║
║ ║    └─────────────────────────────────────────────────────────────────────────┘   ║   ║
║ ║                                                                                   ║   ║
║ ║ 🎯 Supply & Demand Zones:                                                        ║   ║
║ ║    ┌─────────────────────────────────────────────────────────────────────────┐   ║   ║
║ ║    │ Demand Zone: 1.0840-1.0848 | Strength: ████████ 8/10 | Fresh          │   ║   ║
║ ║    │ Supply Zone: 1.0890-1.0898 | Strength: ██████ 6/10 | Tested Once      │   ║   ║
║ ║    └─────────────────────────────────────────────────────────────────────────┘   ║   ║
║ ║                                                                                   ║   ║
║ ║ 📏 Premium/Discount Analysis:                                                    ║   ║
║ ║    Current Price: 1.0877 → 🟢 DISCOUNT ZONE (38.2% Fib)                         ║   ║
║ ║    ┌─────────────────────────────────────────────────────────┐                  ║   ║
║ ║    │ Premium:  1.0885-1.0900 (Sell Zone)                     │                  ║
║ ║    │ Equilibrium: 1.0870 (50%)                               │                  ║
║ ║    │ Discount: 1.0850-1.0835 (Buy Zone) ← CURRENT            │                  ║
║ ║    └─────────────────────────────────────────────────────────┘                  ║   ║
║ ║                                                                                   ║   ║
║ ║ 💡 SMC Insights:                                                                 ║   ║
║ ║    • Market is creating higher highs and higher lows (Bullish structure)        ║   ║
║ ║    • Price is currently in discount zone - favorable for long entries           ║   ║
║ ║    • Strong bullish order block below acting as support                         ║   ║
║ ║    • Unfilled FVG may act as magnet for price                                   ║   ║
║ ║                                                                                   ║   ║
║ ╚═══════════════════════════════════════════════════════════════════════════════════╝   ║
║                                                                                           ║
║ ╔═══════════════════════════════════════════════════════════════════════════════════╗   ║
║ ║ 🤖 MACHINE LEARNING ANALYSIS                                                      ║   ║
║ ║                                                                                   ║   ║
║ ║ 📊 Active Model: Ensemble_v2.3.1 (XGBoost + RandomForest + LSTM)                ║   ║
║ ║ Last Training: 2 hours ago | Samples: 10,247 | Accuracy: 73.2%                  ║   ║
║ ║                                                                                   ║   ║
║ ║ 🎯 Current Prediction:                                                           ║   ║
║ ║    ┌────────────────────────────────────────────────────────────────────────┐    ║   ║
║ ║    │ Direction: BULLISH                                                     │    ║   ║
║ ║    │ Confidence: 82% ████████████████████░░░░░                             │    ║   ║
║ ║    │ Expected Move: +45 pips (1h horizon)                                   │    ║   ║
║ ║    │ Probability Distribution:                                              │    ║   ║
║ ║    │   Bullish: 82% ████████████████████████████████████                   │    ║   ║
║ ║    │   Neutral: 12% ████                                                    │    ║   ║
║ ║    │   Bearish:  6% ██                                                      │    ║   ║
║ ║    └────────────────────────────────────────────────────────────────────────┘    ║   ║
║ ║                                                                                   ║   ║
║ ║ 🔑 Top Feature Importance:                                                       ║   ║
║ ║    ┌──────────────────────────────────────────────────────────────────┐          ║   ║
║ ║    │ 1. Market Structure (SMC):     ████████████████ 23.4%           │          ║   ║
║ ║    │ 2. MACD Signal:                ███████████████ 18.7%            │          ║
║ ║    │ 3. Order Block Proximity:      ████████████ 15.2%               │          ║
║ ║    │ 4. Multi-TF Confluence:        ███████████ 13.8%                │          ║
║ ║    │ 5. Volume Profile:             █████████ 11.4%                  │          ║
║ ║    │ 6. RSI Divergence:             ████████ 9.3%                    │          ║
║ ║    │ 7. ATR Normalized:             ██████ 8.2%                      │          ║
║ ║    └──────────────────────────────────────────────────────────────────┘          ║   ║
║ ║                                                                                   ║   ║
║ ║ 📈 Model Performance Trends:                                                     ║   ║
║ ║    ┌─────────────────────────────────────────────────────────────────────────┐   ║   ║
║ ║    │ Accuracy:  Last 24h: 78% | Last 7d: 73% | Last 30d: 71%               │   ║   ║
║ ║    │ Win Rate:  Last 24h: 14/18 | Last 7d: 52/71 | Last 30d: 215/303       │   ║   ║
║ ║    │                                                                         │   ║   ║
║ ║    │ [Accuracy Trend Chart - Line graph showing improvement over time]      │   ║   ║
║ ║    │  80% ┤              ┌──────────────                                    │   ║   ║
║ ║    │      ┤         ┌────┘                                                  │   ║   ║
║ ║    │  70% ┤    ─────┘                                                       │   ║   ║
║ ║    │  60% ┤────                                                             │   ║   ║
║ ║    │      └────┬────┬────┬────┬────┬────                                   │   ║   ║
║ ║    │         30d   21d   14d   7d    1d                                     │   ║   ║
║ ║    └─────────────────────────────────────────────────────────────────────────┘   ║   ║
║ ║                                                                                   ║   ║
║ ║ 🔄 Next Training: In 22 hours (@ 2025-10-21 12:00 UTC)                          ║   ║
║ ║ 📊 Training Data: Growing (10,247 → 10,300 samples expected)                    ║   ║
║ ║                                                                                   ║   ║
║ ║ [🔄 Force Retrain Now] [📊 View Training History] [⚙️ Model Settings]            ║   ║
║ ╚═══════════════════════════════════════════════════════════════════════════════════╝   ║
║                                                                                           ║
║ ╔═══════════════════════════════════════════════════════════════════════════════════╗   ║
║ ║ 📜 PREDICTION HISTORY (Last 24 Hours)                                             ║   ║
║ ║ ┌────────┬──────────┬──────────┬────────────┬─────────┬──────────────────────┐   ║   ║
║ ║ │ Time   │ Symbol   │ Sentiment│ Confidence │ Result  │ Price Change         │   ║   ║
║ ║ ├────────┼──────────┼──────────┼────────────┼─────────┼──────────────────────┤   ║   ║
║ ║ │ 14:00  │ EURUSD   │ BULLISH  │ 82%        │ ⏳ Live │ -                    │   ║   ║
║ ║ │ 09:15  │ EURUSD   │ NEUTRAL  │ 68%        │ ✓ RIGHT │ +12 pips             │   ║   ║
║ ║ │ 04:30  │ EURUSD   │ BEARISH  │ 71%        │ ✗ WRONG │ +25 pips (Reversed)  │   ║   ║
║ ║ │ 23:45  │ EURUSD   │ BULLISH  │ 79%        │ ✓ RIGHT │ +38 pips             │   ║   ║
║ ║ │ 19:00  │ EURUSD   │ BULLISH  │ 85%        │ ✓ RIGHT │ +52 pips             │   ║   ║
║ ║ │ 14:15  │ EURUSD   │ NEUTRAL  │ 65%        │ ✓ RIGHT │ -3 pips (Ranging)    │   ║   ║
║ ║ └────────┴──────────┴──────────┴────────────┴─────────┴──────────────────────┘   ║   ║
║ ║                                                                                   ║   ║
║ ║ 📊 Statistics:                                                                   ║   ║
║ ║    • Today: 78% Accuracy (14/18 predictions)                                    ║   ║
║ ║    • Average Confidence: 74%                                                    ║   ║
║ ║    • Best Streak: 7 correct in a row                                            ║   ║
║ ║                                                                                   ║   ║
║ ║ [📥 Export History CSV] [📊 Detailed Analytics] [🔍 Filter]                      ║   ║
║ ╚═══════════════════════════════════════════════════════════════════════════════════╝   ║
║                                                                                           ║
║ ╔═══════════════════════════════════════════════════════════════════════════════════╗   ║
║ ║ 🏥 SYSTEM HEALTH DASHBOARD                                                        ║   ║
║ ║                                                                                   ║   ║
║ ║ 🌐 MT5 Connection:                                                               ║   ║
║ ║    ┌───────────────────────────────────────────────────────────────────────┐     ║   ║
║ ║    │ Status: ● CONNECTED (Healthy)                                        │     ║   ║
║ ║    │ Server: ICMarkets-Demo                                               │     ║   ║
║ ║    │ Account: ****5678                                                    │     ║   ║
║ ║    │ Ping: 23ms (Excellent)                                               │     ║   ║
║ ║    │ Last Successful Fetch: 3 seconds ago                                 │     ║   ║
║ ║    │ Uptime: 8h 42m (99.8%)                                              │     ║   ║
║ ║    │ Failed Requests: 2/1,247 (0.16%)                                    │     ║   ║
║ ║    └───────────────────────────────────────────────────────────────────────┘     ║   ║
║ ║                                                                                   ║   ║
║ ║ 💾 Data Pipeline:                                                                ║   ║
║ ║    ┌───────────────────────────────────────────────────────────────────────┐     ║   ║
║ ║    │ Status: ● OPERATIONAL                                                │     ║   ║
║ ║    │ Database: Connected (SQLite)                                         │     ║   ║
║ ║    │ Records: 127,845 candles                                             │     ║   ║
║ ║    │ Data Quality: 99.2% (12 gaps detected, auto-filled)                  │     ║   ║
║ ║    │ Storage: 234 MB / 10 GB (2.3%)                                       │     ║   ║
║ ║    │ Last Backup: 4 hours ago                                             │     ║   ║
║ ║    └───────────────────────────────────────────────────────────────────────┘     ║   ║
║ ║                                                                                   ║   ║
║ ║ 🤖 ML Model:                                                                     ║   ║
║ ║    ┌───────────────────────────────────────────────────────────────────────┐     ║   ║
║ ║    │ Status: ● ACTIVE (Ensemble_v2.3.1)                                   │     ║   ║
║ ║    │ Loaded: Successfully                                                 │     ║   ║
║ ║    │ Last Prediction: 14:32:15 (0s ago)                                   │     ║   ║
║ ║    │ Inference Time: 142ms (Good)                                         │     ║   ║
║ ║    │ Last Training: 2 hours ago                                           │     ║   ║
║ ║    │ Next Training: In 22 hours                                           │     ║   ║
║ ║    │ Model Drift: ⚠️ Low (2.3% - within threshold)                        │     ║   ║
║ ║    └───────────────────────────────────────────────────────────────────────┘     ║   ║
║ ║                                                                                   ║   ║
║ ║ 💻 System Resources:                                                             ║   ║
║ ║    ┌───────────────────────────────────────────────────────────────────────┐     ║   ║
║ ║    │ CPU: 12% ███░░░░░░░░░░░░░░░░░░░░░░░░                                │     ║   ║
║ ║    │ RAM: 847 MB / 2.4 GB (34%) ████████░░░░░░░░░░░░░░░░░░░              │     ║   ║
║ ║    │ Disk: 6.7 GB / 10 GB (67%) ████████████████░░░░░░░░░░░              │     ║   ║
║ ║    │ Network: ↓ 2.3 KB/s  ↑ 0.8 KB/s                                      │     ║   ║
║ ║    │ Threads: 12 active                                                   │     ║   ║
║ ║    │ Temperature: Normal                                                  │     ║   ║
║ ║    └───────────────────────────────────────────────────────────────────────┘     ║   ║
║ ║                                                                                   ║   ║
║ ║ 🔍 Recent Issues & Alerts:                                                       ║   ║
║ ║    ┌───────────────────────────────────────────────────────────────────────┐     ║   ║
║ ║    │ ⚠️ 10:23 - Minor data gap detected (5 candles) - AUTO-RECOVERED     │     ║   ║
║ ║    │ ✓ 09:15 - MT5 connection restored after 2s timeout                  │     ║   ║
║ ║    │ ℹ️ 08:00 - Scheduled backup completed successfully                   │     ║   ║
║ ║    └───────────────────────────────────────────────────────────────────────┘     ║   ║
║ ║                                                                                   ║   ║
║ ║ 🔧 Self-Diagnostics:                                                             ║   ║
║ ║    [▶️ Run Full Diagnostic] [🔄 Test MT5 Connection] [💾 Verify Database]        ║   ║
║ ║    [🤖 Validate Model] [📊 Check Data Quality]                                   ║   ║
║ ║                                                                                   ║   ║
║ ║ Last Full Diagnostic: 1 hour ago - All systems passed ✓                         ║   ║
║ ╚═══════════════════════════════════════════════════════════════════════════════════╝   ║
║                                                                                           ║
║ ┌─────────────────────────────────────────────────────────────────────────────────────┐ ║
║ │  📥 ACTIONS & REPORTS                                                               │ ║
║ │  ┌──────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌──────────────────┐  │ ║
║ │  │ 📊 Generate      │ │ 🔄 Force       │ │ 📋 View Full   │ │ 💾 Export        │  │ ║
║ │  │    PDF Report    │ │    Retrain     │ │    Logs        │ │    Data          │  │ ║
║ │  └──────────────────┘ └────────────────┘ └────────────────┘ └──────────────────┘  │ ║
║ │                                                                                     │ ║
║ │  📄 Available Reports:                                                              │ ║
║ │  • Daily Summary Report (PDF)         [Generate] [Download Last]                   │ ║
║ │  • Weekly Performance Report (PDF)    [Generate] [Download Last]                   │ ║
║ │  • Monthly Analytics Report (PDF)     [Generate] [Download Last]                   │ ║
║ │  • Custom Date Range Report           [Configure & Generate]                       │ ║
║ └─────────────────────────────────────────────────────────────────────────────────────┘ ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
```

## 📱 Sidebar (Settings Panel)

```
╔═══════════════════════════╗
║ ⚙️ CONFIGURATION          ║
╠═══════════════════════════╣
║                           ║
║ 🔌 MT5 CONNECTION         ║
║ ┌───────────────────────┐ ║
║ │ Account: ****5678     │ ║
║ │ Server: ICMarkets     │ ║
║ │ Status: ● Connected   │ ║
║ │ [Edit Credentials]    │ ║
║ │ [Test Connection]     │ ║
║ └───────────────────────┘ ║
║                           ║
║ 📊 ANALYSIS SETTINGS      ║
║ ┌───────────────────────┐ ║
║ │ Tracked Symbols:      │ ║
║ │ • EURUSD [Active]     │ ║
║ │ • GBPUSD [Paused]     │ ║
║ │ • XAUUSD [Paused]     │ ║
║ │ [+ Add Symbol]        │ ║
║ │                       │ ║
║ │ Active Timeframes:    │ ║
║ │ [✓] M15               │ ║
║ │ [✓] H1                │ ║
║ │ [✓] H4                │ ║
║ │ [✓] D1                │ ║
║ │                       │ ║
║ │ Update Frequency:     │ ║
║ │ [ 5 minutes ▼]        │ ║
║ │                       │ ║
║ │ Lookback Period:      │ ║
║ │ [1000] candles        │ ║
║ └───────────────────────┘ ║
║                           ║
║ 🤖 MODEL SETTINGS         ║
║ ┌───────────────────────┐ ║
║ │ Auto-Retrain: [✓]     │ ║
║ │ Schedule: Daily 12:00 │ ║
║ │                       │ ║
║ │ Min Confidence: 70%   │ ║
║ │ [─────●─────] 70%     │ ║
║ │                       │ ║
║ │ Active Model:         │ ║
║ │ Ensemble_v2.3.1 ▼     │ ║
║ │                       │ ║
║ │ [Model History]       │ ║
║ │ [Rollback to v2.2.8]  │ ║
║ └───────────────────────┘ ║
║                           ║
║ 🔔 ALERTS & NOTIFICATIONS ║
║ ┌───────────────────────┐ ║
║ │ Sentiment Change: [✓] │ ║
║ │ High Confidence:  [✓] │ ║
║ │   (> 85%)             │ ║
║ │ System Errors:    [✓] │ ║
║ │ Connection Issues:[✓] │ ║
║ │ Daily Report:     [✓] │ ║
║ │                       │ ║
║ │ Notification Method:  │ ║
║ │ [✓] In-App            │ ║
║ │ [✓] Email             │ ║
║ │ [ ] Telegram          │ ║
║ │ [ ] Webhook           │ ║
║ │                       │ ║
║ │ [Configure Channels]  │ ║
║ └───────────────────────┘ ║
║                           ║
║ 🎨 DISPLAY SETTINGS       ║
║ ┌───────────────────────┐ ║
║ │ Theme: [Dark ▼]       │ ║
║ │ Chart Type: [Candles] │ ║
║ │ Show Grid: [✓]        │ ║
║ │ Show Tooltips: [✓]    │ ║
║ │ Animations: [✓]       │ ║
║ └───────────────────────┘ ║
║                           ║
║ 📊 DATA MANAGEMENT        ║
║ ┌───────────────────────┐ ║
║ │ Database Size: 234 MB │ ║
║ │ Records: 127,845      │ ║
║ │                       │ ║
║ │ [Backup Now]          │ ║
║ │ [Restore Backup]      │ ║
║ │ [Clean Old Data]      │ ║
║ │ [Export Database]     │ ║
║ └───────────────────────┘ ║
║                           ║
║ 🔒 SECURITY               ║
║ ┌───────────────────────┐ ║
║ │ [Change Password]     │ ║
║ │ [View Audit Log]      │ ║
║ │ [Session Management]  │ ║
║ └───────────────────────┘ ║
║                           ║
║ ℹ️ ABOUT                  ║
║ ┌───────────────────────┐ ║
║ │ Version: 1.0.0        │ ║
║ │ Build: 20251020       │ ║
║ │ [Documentation]       │ ║
║ │ [Check Updates]       │ ║
║ │ [Report Issue]        │ ║
║ └───────────────────────┘ ║
╚═══════════════════════════╝
```

## 📊 PDF Report Sample Layout

```
╔═══════════════════════════════════════════════════════════════════╗
║                    MT5 SENTIMENT ANALYSIS REPORT                  ║
║                         EURUSD - Daily Summary                    ║
║                         Date: 2025-10-20                          ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║ EXECUTIVE SUMMARY                                                 ║
║ ═══════════════════════════════════════════════════════════════  ║
║                                                                   ║
║ Overall Performance: 78% Accuracy (14/18 predictions)            ║
║ Primary Sentiment: BULLISH (82% confidence)                      ║
║ Total Signals Generated: 18                                      ║
║ Correct Predictions: 14                                          ║
║ Incorrect Predictions: 4                                         ║
║                                                                   ║
║ KEY STATISTICS                                                    ║
║ ═══════════════════════════════════════════════════════════════  ║
║                                                                   ║
║ • Average Confidence: 74%                                        ║
║ • Best Streak: 7 correct predictions                             ║
║ • Worst Streak: 2 incorrect predictions                          ║
║ • Average Price Movement: +32 pips per signal                    ║
║ • System Uptime: 99.8%                                           ║
║                                                                   ║
║ PRICE CHART & ANALYSIS                                           ║
║ ═══════════════════════════════════════════════════════════════  ║
║                                                                   ║
║ [Full-page chart showing:                                        ║
║  - Price action (OHLC candles)                                   ║
║  - Prediction markers (colored dots)                             ║
║  - Accuracy indicators (✓ or ✗)                                  ║
║  - Key support/resistance levels                                 ║
║  - Order blocks and FVGs]                                        ║
║                                                                   ║
║ PREDICTION BREAKDOWN                                             ║
║ ═══════════════════════════════════════════════════════════════  ║
║                                                                   ║
║ [Table with all predictions, times, confidence, and results]     ║
║                                                                   ║
║ INDICATOR PERFORMANCE                                            ║
║ ═══════════════════════════════════════════════════════════════  ║
║                                                                   ║
║ Top Performing Indicators:                                       ║
║ 1. MACD: 89% accuracy                                            ║
║ 2. Market Structure: 87% accuracy                                ║
║ 3. Order Blocks: 84% accuracy                                    ║
║                                                                   ║
║ [Charts showing individual indicator performance]                ║
║                                                                   ║
║ MACHINE LEARNING INSIGHTS                                        ║
║ ═══════════════════════════════════════════════════════════════  ║
║                                                                   ║
║ • Model Version: Ensemble_v2.3.1                                 ║
║ • Training Data: 10,247 samples                                  ║
║ • Feature Importance Chart                                       ║
║ • Model Performance Trend                                        ║
║                                                                   ║
║ RECOMMENDATIONS                                                   ║
║ ═══════════════════════════════════════════════════════════════  ║
║                                                                   ║
║ • Continue monitoring current bullish sentiment                  ║
║ • Key levels to watch: 1.0835 (support), 1.0895 (resistance)    ║
║ • Model performance improving - continue current strategy        ║
║                                                                   ║
║                                               Generated by        ║
║                                    MT5 Sentiment Analysis Bot     ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 🎯 Color Scheme & Design Guidelines

### Colors
- **Primary**: Deep Blue (#1E40AF) - Headers, buttons
- **Success/Bullish**: Green (#10B981) - Bullish signals
- **Warning/Neutral**: Amber (#F59E0B) - Neutral signals
- **Danger/Bearish**: Red (#EF4444) - Bearish signals
- **Info**: Cyan (#06B6D4) - Information
- **Background**: Dark (#0F172A) or Light (#F8FAFC)
- **Text**: High contrast for readability

### Typography
- **Headers**: Bold, 18-24px
- **Body**: Regular, 14-16px
- **Metrics**: Monospace for numbers
- **Icons**: Clear, consistent size

### Spacing
- Generous padding between sections
- Clear visual hierarchy
- Grouped related information
- Breathing room for data-dense areas

---

## 💡 Interactive Elements

1. **Hover Effects**: Show detailed tooltips
2. **Click Actions**: Drill down into details
3. **Real-time Updates**: Smooth transitions
4. **Loading States**: Clear progress indicators
5. **Responsiveness**: Works on various screen sizes

---

*This wireframe represents the complete vision for the application.*
*Ready for implementation once design is approved!*
