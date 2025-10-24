"""
Configuration Management Module
Centralized configuration loading and validation
"""
import os
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
for directory in [DATA_DIR, LOGS_DIR, MODELS_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)


class MT5Config:
    """MT5 Connection Configuration"""
    # Hardcoded dummy credentials for testing
    LOGIN: int = int(os.getenv("MT5_LOGIN", "211744072") or 211744072)
    PASSWORD: str = os.getenv("MT5_PASSWORD", "dFbKaNLWQ53@9@Z")
    SERVER: str = os.getenv("MT5_SERVER", "ExnessKE-MT5Trial9")
    TIMEOUT: int = int(os.getenv("MT5_TIMEOUT", "60000"))
    PATH: str = os.getenv("MT5_PATH", r"C:\Program Files\MetaTrader 5\terminal64.exe")
    PORTABLE: bool = os.getenv("MT5_PORTABLE", "False").lower() == "true"


class DatabaseConfig:
    """Database Configuration"""
    URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/mt5_sentiment.db")
    ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))


class AppConfig:
    """Application Configuration"""
    ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("APP_DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    
    # Page config
    PAGE_TITLE: str = "MT5 Sentiment Analysis Bot"
    PAGE_ICON: str = "🎯"
    LAYOUT: str = "wide"


class MLConfig:
    """Machine Learning Configuration"""
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "v1.0.0")
    AUTO_RETRAIN: bool = os.getenv("AUTO_RETRAIN", "True").lower() == "true"
    RETRAIN_SCHEDULE: str = os.getenv("RETRAIN_SCHEDULE", "daily")
    MIN_CONFIDENCE: float = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.70"))
    LOOKBACK_BARS: int = int(os.getenv("LOOKBACK_BARS", "1000"))
    
    # Model files
    MODEL_PATH: Path = MODELS_DIR / f"ensemble_{MODEL_VERSION}.joblib"
    SCALER_PATH: Path = MODELS_DIR / f"scaler_{MODEL_VERSION}.joblib"
    FEATURE_NAMES_PATH: Path = MODELS_DIR / f"features_{MODEL_VERSION}.json"
    
    # Training parameters
    TEST_SIZE: float = 0.2
    RANDOM_STATE: int = 42
    CV_FOLDS: int = 5
    
    # NEW: Improved target definition
    MIN_MOVE_PIPS: float = float(os.getenv("MIN_MOVE_PIPS", "10.0"))  # Minimum meaningful move
    LOOKFORWARD_BARS: int = int(os.getenv("LOOKFORWARD_BARS", "3"))  # Multi-horizon target
    
    # NEW: Class balancing
    USE_CLASS_BALANCING: bool = os.getenv("USE_CLASS_BALANCING", "True").lower() == "true"
    USE_TSCV: bool = os.getenv("USE_TSCV", "True").lower() == "true"  # Time-series CV
    
    # Model ensemble weights
    XGBOOST_WEIGHT: float = 0.4
    RANDOM_FOREST_WEIGHT: float = 0.3
    NEURAL_NET_WEIGHT: float = 0.3


class DataConfig:
    """Data Collection Configuration"""
    UPDATE_FREQUENCY: int = int(os.getenv("UPDATE_FREQUENCY_MINUTES", "5"))
    DEFAULT_SYMBOL: str = os.getenv("DEFAULT_SYMBOL", "EURUSD")
    DEFAULT_TIMEFRAMES: List[str] = os.getenv(
        "DEFAULT_TIMEFRAMES", 
        "M15,H1,H4,D1"
    ).split(",")
    
    # Data validation
    MAX_MISSING_PERCENTAGE: float = 1.0
    MAX_SPIKE_MULTIPLIER: float = 5.0
    
    # Timeframe mappings
    TIMEFRAME_MAP = {
        "M1": 1,
        "M5": 5,
        "M15": 15,
        "M30": 30,
        "H1": 60,
        "H4": 240,
        "D1": 1440,
        "W1": 10080,
        "MN1": 43200,
    }


class IndicatorConfig:
    """Technical Indicator Configuration"""
    # RSI
    RSI_PERIOD: int = 14
    RSI_OVERBOUGHT: float = 70.0
    RSI_OVERSOLD: float = 30.0
    
    # MACD
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    
    # Moving Averages
    EMA_FAST: int = 20
    EMA_SLOW: int = 50
    SMA_PERIOD: int = 200
    
    # Bollinger Bands
    BB_PERIOD: int = 20
    BB_STD: float = 2.0
    
    # ATR
    ATR_PERIOD: int = 14
    
    # ADX
    ADX_PERIOD: int = 14
    ADX_THRESHOLD: float = 25.0
    
    # Stochastic
    STOCH_K: int = 14
    STOCH_D: int = 3
    STOCH_SMOOTH: int = 3


class SMCConfig:
    """Smart Money Concepts Configuration"""
    # Structure
    SWING_LOOKBACK: int = 5
    MIN_STRUCTURE_POINTS: int = 3
    
    # Order Blocks
    OB_MIN_BODY_PERCENTAGE: float = 0.6
    OB_MIN_VOLUME_MULTIPLIER: float = 1.5
    OB_PROXIMITY_PIPS: int = 20
    
    # Fair Value Gaps
    FVG_MIN_SIZE_PIPS: int = 10
    FVG_FILL_THRESHOLD: float = 0.5
    
    # Liquidity
    LIQUIDITY_PROXIMITY_PIPS: int = 5
    LIQUIDITY_MIN_TOUCHES: int = 2
    
    # Supply/Demand
    ZONE_STRENGTH_BARS: int = 10
    ZONE_TEST_PROXIMITY_PIPS: int = 15


class SentimentConfig:
    """Sentiment Analysis Configuration"""
    # Weights for different components
    TREND_WEIGHT: float = 0.20
    SMC_WEIGHT: float = 0.35  # Increased for better FVG/structure detection
    MOMENTUM_WEIGHT: float = 0.20
    VOLUME_WEIGHT: float = 0.15
    VOLATILITY_WEIGHT: float = 0.10
    
    # Thresholds (lowered to reduce neutral bias)
    BULLISH_THRESHOLD: float = 0.35  # Symmetric thresholds
    BEARISH_THRESHOLD: float = 0.35  # Symmetric thresholds
    
    # Multi-timeframe weights (D1 primary, H4 secondary)
    MTF_WEIGHTS = {
        "M15": 0.10,
        "H1": 0.20,
        "H4": 0.30,  # Secondary importance
        "D1": 0.40,  # Primary timeframe
    }


class AlertConfig:
    """Alert and Notification Configuration"""
    ENABLE_ALERTS: bool = os.getenv("ENABLE_ALERTS", "True").lower() == "true"
    EMAIL_NOTIFICATIONS: bool = os.getenv("EMAIL_NOTIFICATIONS", "False").lower() == "true"
    TELEGRAM_NOTIFICATIONS: bool = os.getenv("TELEGRAM_NOTIFICATIONS", "False").lower() == "true"
    
    # Email settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    NOTIFICATION_EMAIL: str = os.getenv("NOTIFICATION_EMAIL", "")
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")


class HealthConfig:
    """Health Monitoring Configuration"""
    CHECK_INTERVAL_SECONDS: int = 60
    CONNECTION_TIMEOUT_SECONDS: int = 30
    MAX_FAILED_ATTEMPTS: int = 3
    
    # Resource thresholds
    CPU_WARNING_THRESHOLD: float = 80.0
    CPU_CRITICAL_THRESHOLD: float = 95.0
    MEMORY_WARNING_THRESHOLD: float = 80.0
    MEMORY_CRITICAL_THRESHOLD: float = 95.0
    DISK_WARNING_THRESHOLD: float = 85.0
    DISK_CRITICAL_THRESHOLD: float = 95.0
    
    # Model health
    MIN_PREDICTION_CONFIDENCE: float = 0.50
    ACCURACY_WARNING_THRESHOLD: float = 0.60
    ACCURACY_CRITICAL_THRESHOLD: float = 0.50


class RegimeConfig:
    """Market Regime Detection Configuration (v2.0)"""
    # Enable regime-based features
    ENABLE_REGIME_DETECTION: bool = os.getenv("ENABLE_REGIME_DETECTION", "True").lower() == "true"
    REGIME_LOOKBACK_BARS: int = int(os.getenv("REGIME_LOOKBACK_BARS", "50"))
    
    # Auto regime detection during analysis
    AUTO_DETECT_REGIME: bool = os.getenv("AUTO_DETECT_REGIME", "False").lower() == "true"
    
    # Regime-based filtering
    FILTER_BY_REGIME: bool = os.getenv("FILTER_BY_REGIME", "False").lower() == "true"
    ALLOWED_REGIMES: List[str] = os.getenv(
        "ALLOWED_REGIMES",
        "FAVORABLE,MODERATE"  # Only trade in favorable/moderate conditions
    ).split(",")
    
    # Regime-based position sizing
    USE_REGIME_POSITION_SIZING: bool = os.getenv("USE_REGIME_POSITION_SIZING", "False").lower() == "true"
    REGIME_SIZE_MULTIPLIERS = {
        "FAVORABLE": 1.0,      # Full position size
        "MODERATE": 0.7,       # 70% position size
        "CAUTIOUS": 0.4,       # 40% position size
        "UNFAVORABLE": 0.0     # No trading
    }
    
    # Regime thresholds
    ADX_TRENDING_THRESHOLD: float = 25.0
    ADX_STRONG_THRESHOLD: float = 40.0
    EFFICIENCY_THRESHOLD: float = 0.5
    
    # Volatility percentile thresholds
    VOL_VERY_LOW: float = 0.2
    VOL_LOW: float = 0.4
    VOL_NORMAL_MAX: float = 0.7
    VOL_HIGH: float = 0.9
    
    # Volume percentile thresholds
    VOLUME_DRY: float = 0.25
    VOLUME_NORMAL_MAX: float = 0.75
    VOLUME_ELEVATED: float = 0.95


class PerformanceConfig:
    """Performance and Caching Configuration"""
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    
    # Data retention
    KEEP_CANDLES_DAYS: int = 365
    KEEP_PREDICTIONS_DAYS: int = 90
    KEEP_LOGS_DAYS: int = 30


class BackupConfig:
    """Backup Configuration"""
    AUTO_BACKUP: bool = os.getenv("AUTO_BACKUP", "True").lower() == "true"
    BACKUP_INTERVAL_HOURS: int = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    BACKUP_DIR: Path = BASE_DIR / "backups"


# Create backup directory
BackupConfig.BACKUP_DIR.mkdir(exist_ok=True)


# Validation function
def validate_config() -> bool:
    """Validate critical configuration parameters"""
    issues = []
    
    if not MT5Config.LOGIN or not MT5Config.PASSWORD or not MT5Config.SERVER:
        issues.append("MT5 credentials not configured properly")
    
    if AppConfig.ENV == "production" and AppConfig.SECRET_KEY == "change-me-in-production":
        issues.append("SECRET_KEY must be changed in production")
    
    if MLConfig.MIN_CONFIDENCE < 0 or MLConfig.MIN_CONFIDENCE > 1:
        issues.append("MIN_CONFIDENCE must be between 0 and 1")
    
    if issues:
        print("⚠️  Configuration Issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    return True


if __name__ == "__main__":
    print("🔧 Configuration Summary:")
    print(f"   Environment: {AppConfig.ENV}")
    print(f"   Debug Mode: {AppConfig.DEBUG}")
    print(f"   MT5 Server: {MT5Config.SERVER}")
    print(f"   Database: {DatabaseConfig.URL}")
    print(f"   Default Symbol: {DataConfig.DEFAULT_SYMBOL}")
    print(f"   Model Version: {MLConfig.MODEL_VERSION}")
    print(f"\n✓ Configuration validated: {validate_config()}")
