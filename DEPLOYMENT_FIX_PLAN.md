# 🔧 Deployment Fix Plan - Priority Actions

**Based on**: CRITICAL_REVIEW.md  
**Target**: Production-ready bot in 6-8 weeks  
**Current Status**: ❌ NOT PRODUCTION READY

---

## 🚨 WEEK 1: CRITICAL SECURITY FIXES

### Day 1-2: Remove All Hardcoded Secrets

**File**: `config/settings.py`

**Current (DANGEROUS)**:
```python
LOGIN: int = int(os.getenv("MT5_LOGIN", "211744072") or 211744072)
PASSWORD: str = os.getenv("MT5_PASSWORD", "dFbKaNLWQ53@9@Z")
SERVER: str = os.getenv("MT5_SERVER", "ExnessKE-MT5Trial9")
```

**Fixed**:
```python
LOGIN: int = int(os.getenv("MT5_LOGIN", "0"))
PASSWORD: str = os.getenv("MT5_PASSWORD", "")
SERVER: str = os.getenv("MT5_SERVER", "")
TIMEOUT: int = int(os.getenv("MT5_TIMEOUT", "60000"))

# Add validation
@classmethod
def validate(cls):
    if not cls.LOGIN or cls.LOGIN == 0:
        raise ValueError("MT5_LOGIN environment variable required")
    if not cls.PASSWORD:
        raise ValueError("MT5_PASSWORD environment variable required")
    if not cls.SERVER:
        raise ValueError("MT5_SERVER environment variable required")
```

**Additional Tasks**:
1. Create `credentials.toml.example` without real credentials
2. Add `credentials.toml` to `.gitignore`
3. Add `config/settings.py` check on startup
4. Update documentation with credential setup

---

### Day 3: Fix Error Handling Pattern

**Create**: `src/exceptions.py`

```python
"""Custom exceptions for better error handling"""

class BotError(Exception):
    """Base exception for bot errors"""
    pass

class DataError(BotError):
    """Data-related errors"""
    pass

class InsufficientDataError(DataError):
    """Not enough data for analysis"""
    pass

class InvalidDataError(DataError):
    """Data validation failed"""
    pass

class MT5Error(BotError):
    """MT5-related errors"""
    pass

class MT5ConnectionError(MT5Error):
    """MT5 connection failed"""
    pass

class MT5DataFetchError(MT5Error):
    """MT5 data fetch failed"""
    pass

class AnalysisError(BotError):
    """Analysis-related errors"""
    pass

class SentimentAnalysisError(AnalysisError):
    """Sentiment analysis failed"""
    pass

class MLError(BotError):
    """ML-related errors"""
    pass

class ModelNotFoundError(MLError):
    """ML model not found"""
    pass

class PredictionError(MLError):
    """Prediction failed"""
    pass
```

**Update**: `src/analysis/sentiment_engine.py`

```python
from src.exceptions import SentimentAnalysisError, InsufficientDataError

def analyze_sentiment(self, df, symbol, timeframe):
    # Validate input
    if df is None or df.empty:
        raise InsufficientDataError(f"No data for {symbol} {timeframe}")
    
    if len(df) < 100:
        raise InsufficientDataError(f"Need at least 100 bars, got {len(df)}")
    
    try:
        # Analysis logic
        ...
    except InsufficientDataError:
        raise  # Re-raise data errors
    except Exception as e:
        raise SentimentAnalysisError(f"Analysis failed for {symbol}: {e}") from e
```

---

### Day 4-5: Add Input Validation

**Create**: `src/validation/data_validator.py`

```python
"""Data validation for OHLCV and analysis inputs"""
from typing import Tuple, List
import pandas as pd
import numpy as np

class DataValidator:
    """Validates market data integrity"""
    
    @staticmethod
    def validate_ohlcv(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate OHLCV data integrity
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required columns
        required = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required if col not in df.columns]
        if missing:
            errors.append(f"Missing columns: {missing}")
            return False, errors
        
        # Check for NaN
        if df[required].isnull().any().any():
            nan_cols = df[required].columns[df[required].isnull().any()].tolist()
            errors.append(f"NaN values in columns: {nan_cols}")
        
        # Check OHLC relationships
        invalid_hl = ~(df['High'] >= df['Low'])
        if invalid_hl.any():
            errors.append(f"High < Low in {invalid_hl.sum()} rows")
        
        invalid_hc = ~(df['High'] >= df['Close'])
        if invalid_hc.any():
            errors.append(f"High < Close in {invalid_hc.sum()} rows")
        
        invalid_ho = ~(df['High'] >= df['Open'])
        if invalid_ho.any():
            errors.append(f"High < Open in {invalid_ho.sum()} rows")
        
        invalid_lc = ~(df['Low'] <= df['Close'])
        if invalid_lc.any():
            errors.append(f"Low > Close in {invalid_lc.sum()} rows")
        
        invalid_lo = ~(df['Low'] <= df['Open'])
        if invalid_lo.any():
            errors.append(f"Low > Open in {invalid_lo.sum()} rows")
        
        # Check for price spikes (> 10% move in one bar)
        pct_change = df['Close'].pct_change().abs()
        spikes = pct_change > 0.10
        if spikes.any():
            errors.append(f"Price spikes detected: {spikes.sum()} bars with >10% move")
        
        # Check for zero/negative prices
        zero_prices = (df[['Open', 'High', 'Low', 'Close']] <= 0).any(axis=1)
        if zero_prices.any():
            errors.append(f"Zero or negative prices: {zero_prices.sum()} rows")
        
        # Check for zero volume (might be valid on weekends)
        zero_volume = df['Volume'] == 0
        if zero_volume.sum() > len(df) * 0.1:  # > 10%
            errors.append(f"Warning: {zero_volume.sum()} bars with zero volume")
        
        # Check for duplicates
        duplicates = df.index.duplicated()
        if duplicates.any():
            errors.append(f"Duplicate timestamps: {duplicates.sum()} rows")
        
        # Check monotonic index
        if not df.index.is_monotonic_increasing:
            errors.append("Timestamps are not monotonic increasing")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean OHLCV data
        
        Raises:
            InvalidDataError if data cannot be fixed
        """
        from src.exceptions import InvalidDataError
        
        is_valid, errors = DataValidator.validate_ohlcv(df)
        
        if not is_valid:
            # Try to fix some issues
            df = df.copy()
            
            # Remove duplicates
            df = df[~df.index.duplicated(keep='first')]
            
            # Sort by timestamp
            df = df.sort_index()
            
            # Fill NaN with forward fill (max 3 bars)
            df = df.fillna(method='ffill', limit=3)
            
            # Drop remaining NaN
            df = df.dropna()
            
            # Re-validate
            is_valid, errors = DataValidator.validate_ohlcv(df)
            
            if not is_valid:
                raise InvalidDataError(f"Data validation failed: {'; '.join(errors)}")
        
        return df
```

**Update**: `src/mt5/data_fetcher.py`

```python
from src.validation.data_validator import DataValidator
from src.exceptions import InvalidDataError

def get_ohlcv(self, symbol, timeframe, count):
    # ... existing fetch logic ...
    
    if df is not None and not df.empty:
        # VALIDATE DATA
        try:
            df = DataValidator.validate_and_clean(df)
        except InvalidDataError as e:
            logger.error(f"Data validation failed for {symbol} {timeframe}: {e}")
            raise
    
    return df
```

---

## 🧪 WEEK 2: TESTING INFRASTRUCTURE

### Day 6-7: Set Up Test Framework

**Create**: `tests/conftest.py`

```python
"""Pytest configuration and fixtures"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@pytest.fixture
def sample_ohlcv():
    """Generate sample OHLCV data for testing"""
    dates = pd.date_range('2024-01-01', periods=200, freq='1H')
    np.random.seed(42)
    
    close = np.cumsum(np.random.randn(200) * 0.001) + 1.0850
    high = close + np.random.rand(200) * 0.0010
    low = close - np.random.rand(200) * 0.0010
    open_price = close + np.random.randn(200) * 0.0005
    volume = np.random.randint(1000, 10000, 200)
    
    return pd.DataFrame({
        'Open': open_price,
        'High': high,
        'Low': low,
        'Close': close,
        'Volume': volume
    }, index=dates)

@pytest.fixture
def sample_ohlcv_with_issues():
    """Generate OHLCV with intentional problems"""
    df = sample_ohlcv()
    # Add NaN
    df.loc[df.index[10], 'Close'] = np.nan
    # Add price spike
    df.loc[df.index[50], 'Close'] = df.loc[df.index[50], 'Close'] * 2
    # Add invalid OHLC
    df.loc[df.index[100], 'High'] = df.loc[df.index[100], 'Low'] - 0.01
    return df
```

### Day 8-10: Write Core Tests

**Create**: `tests/unit/test_sentiment_engine.py`

```python
"""Unit tests for sentiment engine"""
import pytest
from src.analysis.sentiment_engine import SentimentEngine
from src.exceptions import InsufficientDataError

class TestSentimentEngine:
    def test_analyze_sentiment_success(self, sample_ohlcv):
        engine = SentimentEngine()
        result = engine.analyze_sentiment(sample_ohlcv, "EURUSD", "H1")
        
        assert result is not None
        assert 'sentiment' in result
        assert result['sentiment'] in ['BULLISH', 'BEARISH', 'NEUTRAL']
        assert 'confidence' in result
        assert 0 <= result['confidence'] <= 1
    
    def test_analyze_sentiment_insufficient_data(self):
        engine = SentimentEngine()
        small_df = sample_ohlcv().head(10)
        
        with pytest.raises(InsufficientDataError):
            engine.analyze_sentiment(small_df, "EURUSD", "H1")
    
    def test_analyze_sentiment_none_data(self):
        engine = SentimentEngine()
        
        with pytest.raises(InsufficientDataError):
            engine.analyze_sentiment(None, "EURUSD", "H1")
    
    def test_confidence_bounds(self, sample_ohlcv):
        """Test confidence stays within 0-1 bounds"""
        engine = SentimentEngine()
        
        # Run 100 times with different data
        for i in range(100):
            df = sample_ohlcv.sample(150)
            result = engine.analyze_sentiment(df, "TEST", "H1")
            
            assert result['confidence'] >= 0, f"Confidence below 0: {result['confidence']}"
            assert result['confidence'] <= 1, f"Confidence above 1: {result['confidence']}"
```

**Create**: `tests/unit/test_data_validator.py`

```python
"""Unit tests for data validation"""
import pytest
from src.validation.data_validator import DataValidator
from src.exceptions import InvalidDataError

class TestDataValidator:
    def test_valid_data(self, sample_ohlcv):
        is_valid, errors = DataValidator.validate_ohlcv(sample_ohlcv)
        assert is_valid
        assert len(errors) == 0
    
    def test_invalid_data(self, sample_ohlcv_with_issues):
        is_valid, errors = DataValidator.validate_ohlcv(sample_ohlcv_with_issues)
        assert not is_valid
        assert len(errors) > 0
    
    def test_clean_data_success(self, sample_ohlcv_with_issues):
        cleaned = DataValidator.validate_and_clean(sample_ohlcv_with_issues)
        is_valid, errors = DataValidator.validate_ohlcv(cleaned)
        
        # Should be fixed or raise
        if not is_valid:
            pytest.fail(f"Clean failed to fix data: {errors}")
    
    def test_missing_columns(self):
        df = pd.DataFrame({'A': [1, 2, 3]})
        is_valid, errors = DataValidator.validate_ohlcv(df)
        
        assert not is_valid
        assert any('Missing columns' in e for e in errors)
```

---

## ⚡ WEEK 3: SAFETY & PERFORMANCE

### Day 11-12: Add Rate Limiting

**Create**: `src/utils/rate_limiter.py`

```python
"""Rate limiting to prevent API abuse"""
import time
from collections import deque
from threading import Lock

class RateLimitError(Exception):
    """Rate limit exceeded"""
    pass

class RateLimiter:
    """Simple token bucket rate limiter"""
    
    def __init__(self, max_calls: int, period_seconds: int = 60):
        self.max_calls = max_calls
        self.period = period_seconds
        self.calls = deque()
        self.lock = Lock()
    
    def check_limit(self) -> None:
        """
        Check if rate limit allows another call
        
        Raises:
            RateLimitError if limit exceeded
        """
        with self.lock:
            now = time.time()
            
            # Remove old calls outside window
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
            
            # Check limit
            if len(self.calls) >= self.max_calls:
                wait_time = self.calls[0] + self.period - now
                raise RateLimitError(
                    f"Rate limit exceeded: {len(self.calls)}/{self.max_calls} "
                    f"calls in {self.period}s. Retry in {wait_time:.1f}s"
                )
            
            # Record this call
            self.calls.append(now)
    
    def reset(self) -> None:
        """Reset rate limiter"""
        with self.lock:
            self.calls.clear()

# Global rate limiters
analysis_limiter = RateLimiter(max_calls=10, period_seconds=60)  # 10/min
mt5_limiter = RateLimiter(max_calls=100, period_seconds=60)  # 100/min
```

**Update**: `app.py`

```python
from src.utils.rate_limiter import analysis_limiter, RateLimitError

# In analysis section (around line 213)
if analyze_button:
    try:
        # Check rate limit
        analysis_limiter.check_limit()
        
        # Proceed with analysis
        ...
        
    except RateLimitError as e:
        st.error(f"⚠️ {str(e)}")
        st.info("Please wait a moment before analyzing again.")
        return
```

### Day 13-14: Fix Confidence Calculation

**Update**: `src/analysis/sentiment_engine.py`

```python
def analyze_sentiment(self, df, symbol, timeframe):
    ...
    
    # Calculate base confidence (0-1)
    confidence = self.confidence_scorer.calculate_confidence(
        sentiment_data, tech_signals, smc_signals
    )
    
    # v2.0: Get regime info but DON'T modify confidence
    regime_adjustment = 1.0
    if regime_data and self.regime_config.USE_REGIME_POSITION_SIZING:
        favorability = regime_data['composite']['favorability']
        regime_adjustment = self.regime_config.REGIME_SIZE_MULTIPLIERS.get(favorability, 1.0)
    
    # Check regime filtering
    trade_allowed = True
    if regime_data and self.regime_config.FILTER_BY_REGIME:
        favorability = regime_data['composite']['favorability']
        trade_allowed = favorability in self.regime_config.ALLOWED_REGIMES
    
    result = {
        'symbol': symbol,
        'timeframe': timeframe,
        'sentiment': sentiment_data['sentiment'],
        'confidence': confidence,  # Unchanged prediction confidence
        'risk_level': risk_level,
        'regime': regime_data,
        'regime_adjustment': regime_adjustment,  # Separate multiplier
        'recommended_position_size': 1.0 * regime_adjustment,  # Separate sizing
        'trade_allowed': trade_allowed,  # Separate filter
        ...
    }
    
    if not trade_allowed:
        result['regime_warning'] = f"⚠️ Trading not recommended in {favorability} regime"
    
    return result
```

### Day 15: Add Model Validation

**Create**: `src/ml/model_validator.py`

```python
"""ML model validation before deployment"""
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import numpy as np

class ModelValidator:
    """Validates ML model performance before deployment"""
    
    MIN_ACCURACY = 0.55  # Must beat random (0.5)
    MIN_PRECISION = 0.55
    MIN_F1 = 0.55
    
    @staticmethod
    def validate_model(model, X_test, y_test) -> Tuple[bool, Dict]:
        """
        Validate model meets minimum requirements
        
        Returns:
            Tuple of (passes_validation, metrics_dict)
        """
        y_pred = model.predict(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0)
        }
        
        # Check minimums
        passes = (
            metrics['accuracy'] >= ModelValidator.MIN_ACCURACY and
            metrics['precision'] >= ModelValidator.MIN_PRECISION and
            metrics['f1'] >= ModelValidator.MIN_F1
        )
        
        return passes, metrics
```

---

## 📊 WEEK 4: MONITORING & DEPLOYMENT

### Day 16-17: Add Monitoring

**Create**: `src/monitoring/metrics.py`

```python
"""Application metrics collection"""
from collections import defaultdict
from datetime import datetime
import json

class MetricsCollector:
    """Collect and track application metrics"""
    
    def __init__(self):
        self.counters = defaultdict(int)
        self.timings = defaultdict(list)
        self.errors = defaultdict(int)
    
    def increment(self, metric: str, value: int = 1):
        """Increment a counter"""
        self.counters[metric] += value
    
    def record_timing(self, metric: str, duration_ms: float):
        """Record operation timing"""
        self.timings[metric].append(duration_ms)
    
    def record_error(self, error_type: str):
        """Record error occurrence"""
        self.errors[error_type] += 1
    
    def get_summary(self) -> Dict:
        """Get metrics summary"""
        return {
            'counters': dict(self.counters),
            'timings': {
                k: {
                    'count': len(v),
                    'avg': sum(v) / len(v) if v else 0,
                    'min': min(v) if v else 0,
                    'max': max(v) if v else 0
                }
                for k, v in self.timings.items()
            },
            'errors': dict(self.errors),
            'timestamp': datetime.now().isoformat()
        }
    
    def save_to_file(self, filepath: str):
        """Save metrics to file"""
        with open(filepath, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)

# Global instance
metrics = MetricsCollector()
```

### Day 18-19: Database Fixes

**Update**: `src/database/repository.py`

```python
def save_candles(self, symbol_name: str, timeframe: str, df: pd.DataFrame) -> int:
    """Save candles with proper transaction handling"""
    try:
        symbol = self.create_or_get_symbol(symbol_name)
        
        # Prepare bulk insert
        candles = []
        for timestamp, row in df.iterrows():
            candle = Candle(
                symbol_id=symbol.id,
                timeframe=timeframe,
                timestamp=timestamp,
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row.get('Volume', 0))
            )
            candles.append(candle)
        
        # Single transaction bulk insert
        self.session.bulk_save_objects(candles)
        self.session.commit()
        
        logger.info(f"Saved {len(candles)} candles for {symbol_name} {timeframe}")
        return len(candles)
        
    except Exception as e:
        self.session.rollback()
        logger.error(f"Failed to save candles: {e}")
        raise
```

### Day 20: Logging Rotation

**Update**: `src/utils/logger.py`

```python
from loguru import logger
import sys

def setup_logging():
    """Setup logging with rotation"""
    logger.remove()  # Remove default handler
    
    # Console handler
    logger.add(
        sys.stdout,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>"
    )
    
    # File handler with rotation
    logger.add(
        "logs/bot_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # Rotate at midnight
        retention="30 days",  # Keep 30 days
        compression="zip",  # Compress old logs
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}"
    )
    
    # Error file
    logger.add(
        "logs/errors_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} | {message}\n{exception}"
    )
```

---

## ✅ TESTING CHECKLIST

Before deployment, verify:

- [ ] All hardcoded credentials removed
- [ ] All unit tests passing (>70% coverage)
- [ ] Integration tests passing
- [ ] Data validation working
- [ ] Rate limiting active
- [ ] Error handling uses exceptions
- [ ] Monitoring collecting metrics
- [ ] Logging rotation configured
- [ ] Database transactions safe
- [ ] Confidence calculation fixed
- [ ] Model validation added
- [ ] Paper trading successful (30 days)

---

## 📈 SUCCESS CRITERIA

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Test Coverage | >70% | `pytest --cov` |
| Security Issues | 0 | Manual audit |
| Error Rate | <1% | Monitor logs |
| Uptime | >99% | Health checks |
| API Errors | <5% | MT5 connection stats |
| Data Validation Failures | 0 | Validation logs |

---

**Follow this plan systematically. Do not skip steps. Each week builds on the previous.**

