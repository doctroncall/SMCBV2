# MT5 Sentiment Analysis Bot - Project Design Document

## 🎯 Project Overview
A professional, production-grade Python/Streamlit application that analyzes MT5 trading data using technical indicators and Smart Money Concepts (SMC) to provide real-time market sentiment analysis with self-learning capabilities.

---

## 📋 Core Requirements

### 1. MT5 Integration
- **Connection Management**
  - Secure credential storage
  - Auto-reconnection on failure
  - Connection health monitoring
  - Multiple account support (optional)
  - Rate limiting compliance

### 2. Data Collection
- **Real-time Data**
  - OHLCV (Open, High, Low, Close, Volume)
  - Tick data
  - Multiple timeframes (M1, M5, M15, H1, H4, D1)
  - Bid/Ask spreads
  
- **Historical Data**
  - Configurable lookback period
  - Data validation and cleaning
  - Gap detection and handling
  - Storage in local database (SQLite/PostgreSQL)

### 3. Analysis Engine

#### Technical Indicators
- **Trend Indicators**
  - Moving Averages (SMA, EMA, WMA)
  - MACD
  - ADX
  - Ichimoku Cloud
  
- **Momentum Indicators**
  - RSI
  - Stochastic
  - CCI
  - Williams %R
  
- **Volatility Indicators**
  - Bollinger Bands
  - ATR
  - Keltner Channels
  
- **Volume Indicators**
  - Volume Profile
  - OBV (On Balance Volume)
  - VWAP
  - Money Flow Index

#### Smart Money Concepts (SMC)
- **Market Structure**
  - Break of Structure (BOS)
  - Change of Character (ChOCh)
  - Higher Highs/Lower Lows tracking
  - Swing points identification
  
- **Liquidity Analysis**
  - Liquidity pools identification
  - Stop hunts detection
  - Equal highs/lows
  
- **Fair Value Gaps (FVG)**
  - Imbalance detection
  - Gap filling tracking
  
- **Order Blocks**
  - Bullish/Bearish order blocks
  - Breaker blocks
  
- **Supply & Demand Zones**
  - Zone identification
  - Zone strength scoring
  
- **Premium/Discount Zones**
  - Fibonacci retracement levels
  - 50% equilibrium

### 4. Sentiment Generation
- **Multi-Factor Scoring**
  - Weighted indicator signals
  - SMC pattern recognition
  - Timeframe confluence
  - Confidence score (0-100%)
  
- **Output**
  - Primary: BULLISH / BEARISH / FLAT
  - Confidence level
  - Key factors contributing to sentiment
  - Risk level assessment

### 5. Machine Learning Pipeline

#### Training Data
- Historical sentiment predictions
- Actual price movements
- Feature vectors from indicators
- Market context (session, volatility regime)

#### Model Architecture
- **Ensemble Approach**
  - Random Forest for feature importance
  - XGBoost for prediction
  - Neural Network for pattern recognition
  - Voting/Stacking ensemble
  
#### Self-Learning
- **Daily Retraining**
  - 24h sentiment verification
  - Accuracy calculation
  - Model parameter tuning
  - Feature importance re-evaluation
  
- **Continuous Improvement**
  - Online learning capability
  - A/B testing of models
  - Model versioning and rollback
  - Performance metric tracking

### 6. Logging & Monitoring

#### Detailed Logging
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Categories**:
  - MT5 connection events
  - Data retrieval operations
  - Indicator calculations
  - Sentiment generation
  - ML model operations
  - User interactions
  - System health checks
  
- **Storage**:
  - Rotating file logs
  - Database logging for critical events
  - Structured logging (JSON format)

#### Monitoring
- Performance metrics
- API call counts
- Prediction accuracy over time
- System resource usage

### 7. Health Check & Troubleshooting Module

#### Self-Diagnostics
- **Connection Health**
  - MT5 connection status
  - Internet connectivity
  - API response times
  
- **Data Quality**
  - Missing data detection
  - Anomaly detection
  - Data freshness checks
  
- **System Resources**
  - CPU usage
  - Memory usage
  - Disk space
  - Thread status
  
- **Model Health**
  - Prediction confidence trends
  - Accuracy degradation alerts
  - Feature distribution drift

#### Auto-Recovery
- Automatic reconnection
- Data backfill on gaps
- Fallback to cached predictions
- Alert notifications

### 8. Reporting System

#### Real-time Dashboard Metrics
- Current sentiment
- Confidence score
- Active signals
- Recent predictions vs actual

#### PDF Reports
- **Daily Report**
  - Summary of sentiments
  - Accuracy metrics
  - Top performing signals
  - Charts and visualizations
  
- **Weekly/Monthly Report**
  - Performance trends
  - Model improvements
  - Statistical analysis
  - Recommendation insights

---

## 🎨 Dashboard Design

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 MT5 Sentiment Analysis Bot        [Health: ●] [⚙️ Settings]│
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────┐  Symbol: [EURUSD ▼]  [●] Connected       │
│ │  SENTIMENT   │  Timeframe: [H1 ▼]   Last Update: 14:32  │
│ │              │                                            │
│ │   BULLISH    │  Confidence: ████████░░ 82%              │
│ │      ▲       │                                            │
│ │   [82%]      │  Risk Level: Medium                       │
│ └──────────────┘                                            │
├─────────────────────────────────────────────────────────────┤
│ 📊 LIVE PRICE CHART                                         │
│ ┌───────────────────────────────────────────────────────┐  │
│ │         [Interactive Plotly/Lightweight Chart]        │  │
│ │         • Price action                                │  │
│ │         • Order blocks                                │  │
│ │         • FVGs                                        │  │
│ │         • Support/Resistance                          │  │
│ └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ TABS: [📈 Indicators] [🧠 SMC] [📊 Analysis] [📜 History]  │
├─────────────────────────────────────────────────────────────┤
│ 📈 INDICATORS TAB                                           │
│ ┌─────────────┬─────────────┬──────────────┬──────────┐   │
│ │ Indicator   │ Value       │ Signal       │ Weight   │   │
│ ├─────────────┼─────────────┼──────────────┼──────────┤   │
│ │ RSI(14)     │ 67.3       │ BULLISH      │ 8/10     │   │
│ │ MACD        │ 0.0023 ▲   │ BULLISH      │ 9/10     │   │
│ │ ADX         │ 28.5       │ TRENDING     │ 7/10     │   │
│ │ Boll Bands  │ Upper      │ NEUTRAL      │ 5/10     │   │
│ └─────────────┴─────────────┴──────────────┴──────────┘   │
├─────────────────────────────────────────────────────────────┤
│ 🧠 SMC ANALYSIS                                             │
│ • Market Structure: Higher Highs forming (BULLISH)         │
│ • Recent BOS: 1.0856 (15:20)                               │
│ • Active Order Block: 1.0842-1.0847 (Bullish)             │
│ • Fair Value Gap: 1.0838-1.0841                           │
│ • Liquidity Pool: 1.0835 (weak)                           │
├─────────────────────────────────────────────────────────────┤
│ 🎯 PREDICTION ACCURACY                                      │
│ ┌─────────────────────────────────────────────────────┐   │
│ │  Today: 78% (14/18 correct)                         │   │
│ │  Week:  73% (52/71 correct)                         │   │
│ │  Month: 71% (215/303 correct)                       │   │
│ │  [Accuracy Trend Chart]                             │   │
│ └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│ 🏥 SYSTEM HEALTH                                            │
│ • MT5 Connection: ● Healthy (ping: 23ms)                   │
│ • Data Pipeline: ● Operational                             │
│ • ML Model: ● Active (v2.3.1)                              │
│ • Last Training: 2 hours ago                               │
│ • System Load: CPU 12% | RAM 34% | Disk 67%                │
├─────────────────────────────────────────────────────────────┤
│ 📥 ACTIONS                                                  │
│ [📊 Generate Report] [🔄 Force Retrain] [📋 View Logs]     │
└─────────────────────────────────────────────────────────────┘
```

### Sidebar Configuration
```
┌──────────────────────┐
│ ⚙️ CONFIGURATION     │
├──────────────────────┤
│ MT5 SETTINGS         │
│ • Account: ****5678  │
│ • Server: ICMarkets  │
│ • [Edit Credentials] │
├──────────────────────┤
│ ANALYSIS SETTINGS    │
│ • Symbols: [Manage]  │
│ • Timeframes: [✓]H1  │
│              [✓]H4  │
│              [✓]D1  │
│ • Update Freq: 5min  │
├──────────────────────┤
│ MODEL SETTINGS       │
│ • Auto-retrain: [✓]  │
│ • Confidence Min: 70%│
│ • Lookback: 1000 bars│
├──────────────────────┤
│ ALERTS               │
│ • Sentiment Change:✓ │
│ • High Confidence: ✓ │
│ • System Error: ✓    │
└──────────────────────┘
```

---

## 🏗️ Technical Architecture

### Project Structure
```
mt5-sentiment-bot/
├── app.py                          # Main Streamlit app
├── config/
│   ├── settings.py                 # Configuration management
│   ├── indicators_config.yaml      # Indicator parameters
│   └── smc_config.yaml            # SMC parameters
├── src/
│   ├── mt5/
│   │   ├── connection.py          # MT5 connection handler
│   │   ├── data_fetcher.py        # Data retrieval
│   │   └── validator.py           # Data validation
│   ├── indicators/
│   │   ├── technical.py           # Technical indicators
│   │   ├── smc.py                 # SMC analysis
│   │   └── calculator.py          # Indicator calculation engine
│   ├── analysis/
│   │   ├── sentiment_engine.py    # Sentiment generation
│   │   ├── multi_timeframe.py     # MTF analysis
│   │   └── confidence_scorer.py   # Confidence calculation
│   ├── ml/
│   │   ├── model_manager.py       # Model lifecycle
│   │   ├── feature_engineering.py # Feature creation
│   │   ├── training.py            # Training pipeline
│   │   └── evaluator.py           # Performance evaluation
│   ├── health/
│   │   ├── monitor.py             # Health monitoring
│   │   ├── diagnostics.py         # Self-diagnostics
│   │   └── recovery.py            # Auto-recovery
│   ├── reporting/
│   │   ├── pdf_generator.py       # PDF report creation
│   │   ├── charts.py              # Chart generation
│   │   └── metrics.py             # Metric calculations
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   └── repository.py          # Data access layer
│   └── utils/
│       ├── logger.py              # Logging configuration
│       ├── notifications.py       # Alert system
│       └── helpers.py             # Utility functions
├── gui/
│   ├── components/
│   │   ├── sentiment_card.py      # Sentiment display
│   │   ├── chart_panel.py         # Chart components
│   │   ├── indicator_table.py     # Indicator display
│   │   ├── health_dashboard.py    # Health monitor UI
│   │   └── settings_panel.py      # Settings UI
│   └── styles/
│       ├── custom.css             # Custom styling
│       └── theme.py               # Theme configuration
├── tests/
│   ├── unit/
│   ├── integration/
│   └── test_data/
├── logs/                           # Log files
├── models/                         # Saved ML models
├── reports/                        # Generated reports
├── data/                           # Local database
├── requirements.txt
├── .env.example
└── README.md
```

### Technology Stack

#### Core
- **Python 3.10+**
- **Streamlit** - Dashboard framework
- **MetaTrader5** - MT5 API
- **pandas** - Data manipulation
- **numpy** - Numerical computing

#### Indicators & Analysis
- **TA-Lib** - Technical analysis library
- **pandas-ta** - Additional indicators
- Custom SMC implementations

#### Machine Learning
- **scikit-learn** - ML algorithms
- **XGBoost** - Gradient boosting
- **TensorFlow/Keras** - Neural networks
- **joblib** - Model serialization

#### Visualization
- **plotly** - Interactive charts
- **matplotlib** - Static charts
- **seaborn** - Statistical visualization

#### Database & Storage
- **SQLAlchemy** - ORM
- **SQLite/PostgreSQL** - Database
- **Redis** (optional) - Caching

#### Reporting
- **reportlab** - PDF generation
- **matplotlib** - Chart exports
- **Jinja2** - Report templates

#### Monitoring & Logging
- **loguru** - Advanced logging
- **psutil** - System monitoring
- **prometheus_client** (optional) - Metrics

---

## 🚀 Enhancements for Accuracy & Reliability

### 1. **Multi-Timeframe Confluence**
- Analyze across M15, H1, H4, D1
- Weight higher timeframes more heavily
- Only signal when alignment exists

### 2. **Market Context Awareness**
- **Session Detection**: Asian, London, NY sessions
- **Volatility Regime**: Low/Normal/High
- **Trend Strength**: Weak/Moderate/Strong
- Adjust strategy based on context

### 3. **News & Fundamental Integration** (Optional Advanced Feature)
- Economic calendar integration
- News sentiment analysis
- Avoid trading during high-impact news

### 4. **Advanced SMC Features**
- **Inducement zones**
- **Mitigation blocks**
- **Smart money divergence**
- **Institutional candle patterns**

### 5. **Risk Management Signals**
- Suggest entry zones
- Stop-loss recommendations
- Take-profit levels
- Position sizing hints

### 6. **Backtesting Framework**
- Historical performance testing
- Walk-forward optimization
- Monte Carlo simulation
- Drawdown analysis

### 7. **Alert System**
- Telegram/Email notifications
- Webhook support
- Custom alert conditions
- Sound notifications in GUI

### 8. **Data Quality Assurance**
- Outlier detection
- Missing data interpolation
- Spike filtering
- Cross-broker validation (if multiple MT5 accounts)

### 9. **Model Ensemble Strategies**
- Multiple models voting
- Confidence-weighted predictions
- Disagreement detection (signals uncertainty)

### 10. **Performance Analytics**
- Win rate by time of day
- Win rate by session
- Win rate by volatility regime
- Best performing indicators

---

## 🔐 Security & Production Considerations

### Security
- Encrypted credential storage
- Environment variables for sensitive data
- API key rotation
- Audit logging

### Performance
- Async data fetching
- Caching frequently used calculations
- Database query optimization
- Lazy loading in GUI

### Reliability
- Graceful error handling
- Circuit breaker pattern
- Retry mechanisms with exponential backoff
- Data backup and recovery

### Scalability
- Support for multiple symbols
- Multi-account support
- Distributed processing (future)
- Cloud deployment ready

---

## 📊 Success Metrics

### Prediction Accuracy
- **Target**: >70% accuracy over 1 month
- Daily, weekly, monthly tracking
- Accuracy by confidence level
- Accuracy by market condition

### System Uptime
- **Target**: 99% uptime
- Connection stability
- Auto-recovery success rate

### User Experience
- Dashboard load time < 2s
- Real-time updates < 5s latency
- Report generation < 10s

---

## 🗓️ Development Phases

### Phase 1: Foundation (Week 1)
- Project setup
- MT5 connection module
- Basic data fetching
- Database setup
- Basic logging

### Phase 2: Analysis Engine (Week 2)
- Technical indicators implementation
- SMC concepts implementation
- Sentiment generation logic
- Multi-timeframe analysis

### Phase 3: ML Pipeline (Week 3)
- Feature engineering
- Model training pipeline
- Model evaluation
- Auto-retraining system

### Phase 4: GUI Development (Week 4)
- Streamlit dashboard
- Interactive charts
- Real-time updates
- Settings panel

### Phase 5: Health & Monitoring (Week 5)
- Health check module
- Self-diagnostics
- Auto-recovery
- Alert system

### Phase 6: Reporting (Week 6)
- PDF report generation
- Performance analytics
- Export functionality

### Phase 7: Testing & Polish (Week 7)
- Unit tests
- Integration tests
- Performance optimization
- UI/UX refinement

### Phase 8: Documentation & Deployment (Week 8)
- User documentation
- API documentation
- Deployment guide
- Production deployment

---

## 💡 Additional Ideas for Discussion

1. **Copy Trading Integration?**
   - Should the bot also execute trades automatically?
   - Or just provide signals?

2. **Mobile Access?**
   - Mobile-responsive Streamlit
   - Telegram bot for mobile alerts

3. **Social Features?**
   - Share predictions with community
   - Compare accuracy with other users

4. **Broker Agnostic?**
   - Support other platforms (cTrader, TradingView)

5. **Asset Classes?**
   - Forex, Crypto, Stocks, Commodities
   - Cross-market analysis

6. **Advanced Features?**
   - Portfolio sentiment (multiple symbols)
   - Correlation analysis
   - Pair trading signals

---

## ❓ Questions for Refinement

1. **Primary Use Case**: Personal trading or for distribution?
2. **Symbols**: Focus on specific pairs or all MT5 symbols?
3. **Trading Style**: Scalping, day trading, or swing trading focus?
4. **ML Preference**: Start simple or implement complex models from the start?
5. **Hosting**: Local machine or cloud deployment?
6. **Budget**: Any constraints on paid APIs or services?
7. **Timeline**: How quickly do you need this operational?

---

## 🎯 Next Steps

1. **Review & Feedback** on this design document
2. **Prioritize Features** (Must-have vs Nice-to-have)
3. **Create Visual Wireframe** (if needed)
4. **Set Up Development Environment**
5. **Begin Phase 1 Implementation**

---

*This is a living document. We'll refine as we progress.*
