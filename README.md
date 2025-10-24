# 🎯 MT5 Sentiment Analysis Bot

A professional, production-grade Python/Streamlit application that analyzes MT5 trading data using technical indicators and Smart Money Concepts (SMC) to provide real-time market sentiment analysis with self-learning capabilities.

## 📋 Features

- **MT5 Integration**: Secure connection to MetaTrader 5 with auto-reconnection
- **Real-time Data Collection**: OHLCV data across multiple timeframes (M15, H1, H4, D1)
- **Technical Analysis**: 15+ indicators including RSI, MACD, Bollinger Bands, ADX, and more
- **Smart Money Concepts**: Order blocks, Fair Value Gaps, liquidity analysis, supply/demand zones
- **Machine Learning**: Self-learning ensemble model (XGBoost + Random Forest + Neural Network)
- **Beautiful Dashboard**: Professional Streamlit UI with interactive charts
- **Health Monitoring**: Self-diagnostics and auto-recovery capabilities
- **PDF Reports**: Downloadable daily, weekly, and monthly performance reports
- **Detailed Logging**: Comprehensive logging for debugging and monitoring

## 🚀 Quick Start (Anaconda)

### Prerequisites

- **Anaconda or Miniconda** (recommended for stability)
- **MetaTrader 5** account access
- Internet connection (first-time setup)

### Installation (Automated!)

**Step 1: Install Anaconda/Miniconda**

Choose one:
- **Anaconda** (full): https://www.anaconda.com/download
- **Miniconda** (minimal): https://docs.conda.io/en/latest/miniconda.html

**Step 2: Run the launcher**

#### Windows:
```batch
start_bot.bat
```

#### Linux/Mac:
```bash
./start_bot.sh
```

**That's it!** The script automatically:
- ✅ Creates conda environment
- ✅ Installs all dependencies (including TA-Lib!)
- ✅ Sets up database
- ✅ Launches dashboard

**First run:** 5-15 minutes (one-time setup)  
**Subsequent runs:** Instant!

Dashboard opens at: **http://localhost:8501**

---

### Alternative: Manual Installation

If you prefer manual setup:

1. **Create conda environment**
   ```bash
   conda env create -f environment.yml
   ```

2. **Activate environment**
   ```bash
   conda activate mt5-sentiment-bot
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MT5 credentials
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## ⚙️ Configuration

Edit the `.env` file with your settings:

```env
# MT5 Connection
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server

# Analysis Settings
DEFAULT_SYMBOL=EURUSD
DEFAULT_TIMEFRAMES=M15,H1,H4,D1
UPDATE_FREQUENCY_MINUTES=5

# ML Settings
AUTO_RETRAIN=True
MIN_CONFIDENCE_THRESHOLD=0.70
```

See `.env.example` for all available configuration options.

## 📁 Project Structure

```
mt5-sentiment-bot/
├── app.py                          # Main Streamlit application
├── config/                         # Configuration files
│   ├── settings.py                 # Settings management
│   ├── indicators_config.yaml      # Indicator parameters
│   └── smc_config.yaml            # SMC parameters
├── src/                           # Source code
│   ├── mt5/                       # MT5 integration
│   ├── indicators/                # Technical indicators & SMC
│   ├── analysis/                  # Sentiment analysis
│   ├── ml/                        # Machine learning
│   ├── health/                    # Health monitoring
│   ├── reporting/                 # Report generation
│   ├── database/                  # Data storage
│   └── utils/                     # Utilities
├── gui/                           # GUI components
│   ├── components/                # Reusable UI components
│   └── styles/                    # CSS styling
├── tests/                         # Test suite
├── logs/                          # Application logs
├── models/                        # Saved ML models
├── reports/                       # Generated reports
└── data/                          # Database storage
```

## 🔧 Usage

### Basic Usage

1. Launch the application: `streamlit run app.py`
2. Configure MT5 credentials in the sidebar
3. Select your symbol and timeframe
4. Monitor real-time sentiment analysis
5. Generate reports as needed

### Advanced Features

- **Multi-Timeframe Analysis**: Enable multiple timeframes for confluence
- **Auto-Retraining**: Model automatically retrains daily to improve accuracy
- **Custom Alerts**: Configure notifications for sentiment changes
- **PDF Reports**: Download detailed performance analytics

## 📊 Indicators & Analysis

### Technical Indicators
- Trend: EMA, SMA, MACD, ADX, Ichimoku
- Momentum: RSI, Stochastic, CCI, Williams %R
- Volatility: Bollinger Bands, ATR, Keltner Channels
- Volume: Volume Profile, OBV, VWAP, MFI

### Smart Money Concepts
- Market Structure (BOS, ChOCh)
- Order Blocks (Bullish/Bearish/Breaker)
- Fair Value Gaps
- Liquidity Pools & Stop Hunts
- Supply & Demand Zones
- Premium/Discount Analysis

## 🤖 Machine Learning

The bot uses an ensemble approach:
- **XGBoost**: Gradient boosting for predictions
- **Random Forest**: Feature importance analysis
- **Neural Network**: Pattern recognition

Features automatically retrain daily using:
- Historical sentiment predictions
- Actual price movements
- Performance metrics
- Feature importance updates

## 📈 Performance Metrics

Track bot performance with:
- Prediction accuracy (daily, weekly, monthly)
- Confidence level statistics
- Win rate by market condition
- Best/worst performing indicators
- System health metrics

## 🏥 Health Monitoring

Built-in health checks for:
- MT5 connection status
- Data quality & freshness
- System resources (CPU, RAM, Disk)
- Model performance
- Auto-recovery on failures

## 📄 Reports

Generate professional PDF reports:
- **Daily Summary**: Performance overview, predictions, accuracy
- **Weekly Report**: Trends, best indicators, insights
- **Monthly Analytics**: Comprehensive statistics and recommendations

## 🔒 Security

- Encrypted credential storage
- Environment variable configuration
- No hardcoded sensitive data
- Secure database connections

## 🧪 Testing

Run tests:
```bash
# All tests
pytest

# With coverage
pytest --cov=src tests/

# Specific module
pytest tests/unit/test_indicators.py
```

## 📝 Logging

Logs are stored in the `logs/` directory with rotation:
- Application logs: `app.log`
- MT5 connection: `mt5_connection.log`
- Analysis: `analysis.log`
- ML training: `ml_training.log`

Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## 🚧 Roadmap

- [ ] Copy trading integration
- [ ] Multiple symbol tracking
- [ ] Telegram bot for mobile alerts
- [ ] Cloud deployment support
- [ ] Backtesting framework
- [ ] Economic calendar integration

## 🔧 Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'loguru'"

**Quick Fix:**
```batch
fix_loguru.bat
```

Or manually:
```batch
conda activate smc_bot
conda install -c conda-forge loguru -y
```

See `LOGURU_FIX_GUIDE.md` for detailed instructions.

#### "ModuleNotFoundError: No module named 'talib'"

```batch
conda activate smc_bot
conda install -c conda-forge ta-lib -y
```

#### "Could not connect to MT5"

1. Ensure MetaTrader 5 is running
2. Check your credentials in `.env`
3. Verify your broker allows API connections
4. See `MT5_CONNECTION_DEBUG.md` for detailed help

#### Environment Not Found

```batch
# Recreate the environment
conda env remove -n smc_bot
conda env create -f environment.yml
```

### Verify All Dependencies

Run the verification script:
```batch
verify_dependencies.bat
```

Or on Linux/Mac:
```bash
python verify_dependencies.py
```

This will check all required packages and show which ones are missing.

### Getting Help

- Check `TROUBLESHOOTING.md` for detailed solutions
- Review logs in the `logs/` directory
- Run `verify_dependencies.bat` to check your setup
- See individual fix guides (e.g., `LOGURU_FIX_GUIDE.md`)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is for educational and informational purposes only. It does not constitute financial advice. Trading forex and CFDs carries a high level of risk and may not be suitable for all investors. Past performance is not indicative of future results.

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the documentation
- Review logs for debugging

## 🙏 Acknowledgments

- MetaTrader 5 API
- TA-Lib for technical analysis
- Streamlit for the amazing framework
- The SMC trading community

---

**Built with ❤️ for traders by traders**
