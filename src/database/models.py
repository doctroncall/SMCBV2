"""
SQLAlchemy Database Models
Defines database schema for storing market data, predictions, and system metrics
"""
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from typing import Optional

from config.settings import DatabaseConfig

# Base class for all models
Base = declarative_base()


class Symbol(Base):
    """Trading symbols/instruments"""
    __tablename__ = "symbols"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(String(200))
    digits = Column(Integer)
    point = Column(Float)
    currency_base = Column(String(10))
    currency_profit = Column(String(10))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candles = relationship("Candle", back_populates="symbol", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="symbol", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Symbol {self.name}>"


class Candle(Base):
    """OHLCV candlestick data"""
    __tablename__ = "candles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    timeframe = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    spread = Column(Float)
    real_volume = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    symbol = relationship("Symbol", back_populates="candles")
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('symbol_id', 'timeframe', 'timestamp', name='uq_candle'),
        Index('idx_symbol_timeframe_timestamp', 'symbol_id', 'timeframe', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Candle {self.symbol.name if self.symbol else 'N/A'} {self.timeframe} {self.timestamp}>"


class ModelVersion(Base):
    """ML Model versions and metadata"""
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(50), unique=True, nullable=False)
    model_type = Column(String(50))  # ensemble, xgboost, random_forest, etc.
    
    # Training metadata
    training_date = Column(DateTime, nullable=False)
    training_samples = Column(Integer)
    training_duration_seconds = Column(Float)
    
    # Model parameters (JSON stored as text)
    parameters = Column(Text)
    feature_importance = Column(Text)
    
    # Performance metrics
    train_accuracy = Column(Float)
    test_accuracy = Column(Float)
    validation_accuracy = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=False)
    is_production = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="model_version")
    
    def __repr__(self):
        return f"<ModelVersion {self.version} accuracy={self.test_accuracy}>"


class Prediction(Base):
    """Sentiment predictions with outcomes"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    model_version_id = Column(Integer, ForeignKey("model_versions.id"))
    timeframe = Column(String(10), nullable=False)
    
    # Prediction details
    timestamp = Column(DateTime, nullable=False, index=True)
    sentiment = Column(String(20), nullable=False)  # BULLISH, BEARISH, NEUTRAL
    confidence = Column(Float, nullable=False)
    
    # Contributing factors (JSON stored as text)
    factors = Column(Text)
    indicator_signals = Column(Text)
    smc_signals = Column(Text)
    
    # Risk assessment
    risk_level = Column(String(20))  # LOW, MEDIUM, HIGH
    
    # Price at prediction time
    price_at_prediction = Column(Float)
    
    # Outcome tracking
    is_verified = Column(Boolean, default=False)
    actual_outcome = Column(String(20))  # BULLISH, BEARISH, NEUTRAL
    was_correct = Column(Boolean)
    price_change_pips = Column(Float)
    verification_timestamp = Column(DateTime)
    
    # Multi-timeframe confluence
    mtf_alignment = Column(Float)  # 0-1 score
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    symbol = relationship("Symbol", back_populates="predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")
    
    # Indexes
    __table_args__ = (
        Index('idx_prediction_timestamp', 'timestamp'),
        Index('idx_prediction_symbol_timeframe', 'symbol_id', 'timeframe', 'timestamp'),
    )
    
    def __repr__(self):
        symbol_name = self.symbol.name if self.symbol else 'N/A'
        return f"<Prediction {symbol_name} {self.sentiment} {self.confidence:.2f} @ {self.timestamp}>"


class PerformanceMetric(Base):
    """Aggregated performance metrics"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Time period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20))  # hourly, daily, weekly, monthly
    
    # Model/symbol context
    model_version = Column(String(50))
    symbol = Column(String(20))
    timeframe = Column(String(10))
    
    # Prediction statistics
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    incorrect_predictions = Column(Integer, default=0)
    accuracy = Column(Float)
    
    # Sentiment breakdown
    bullish_predictions = Column(Integer, default=0)
    bearish_predictions = Column(Integer, default=0)
    neutral_predictions = Column(Integer, default=0)
    
    bullish_correct = Column(Integer, default=0)
    bearish_correct = Column(Integer, default=0)
    neutral_correct = Column(Integer, default=0)
    
    # Confidence metrics
    avg_confidence = Column(Float)
    high_confidence_accuracy = Column(Float)  # Accuracy when confidence > 80%
    low_confidence_accuracy = Column(Float)   # Accuracy when confidence < 60%
    
    # Price movement
    avg_price_change_pips = Column(Float)
    max_price_change_pips = Column(Float)
    
    # Model performance
    feature_importance_top_3 = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_metrics_period', 'period_start', 'period_end'),
        Index('idx_metrics_symbol_period', 'symbol', 'period_type', 'period_start'),
    )
    
    def __repr__(self):
        return f"<PerformanceMetric {self.period_type} {self.period_start} accuracy={self.accuracy}>"


class SystemLog(Base):
    """System events and diagnostics log"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Log details
    level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    category = Column(String(50), nullable=False, index=True)  # mt5, analysis, ml, health, etc.
    message = Column(Text, nullable=False)
    
    # Additional context
    details = Column(Text)  # JSON with additional details
    exception = Column(Text)  # Stack trace if error
    
    # Source information
    function = Column(String(100))
    module = Column(String(100))
    
    # System metrics at time of log
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_log_timestamp_level', 'timestamp', 'level'),
        Index('idx_log_category', 'category', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SystemLog {self.level} {self.category} @ {self.timestamp}>"


# Database initialization
def init_database(database_url: Optional[str] = None) -> sessionmaker:
    """
    Initialize database and create all tables
    
    Args:
        database_url: Database connection URL (uses config if not provided)
        
    Returns:
        sessionmaker: Session factory
    """
    url = database_url or DatabaseConfig.URL
    
    engine = create_engine(
        url,
        echo=DatabaseConfig.ECHO,
        pool_size=DatabaseConfig.POOL_SIZE,
        max_overflow=DatabaseConfig.MAX_OVERFLOW,
    )
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = sessionmaker(bind=engine)
    
    return Session


def drop_all_tables(database_url: Optional[str] = None):
    """
    Drop all tables (use with caution!)
    
    Args:
        database_url: Database connection URL
    """
    url = database_url or DatabaseConfig.URL
    engine = create_engine(url)
    Base.metadata.drop_all(engine)


if __name__ == "__main__":
    # Test database models
    print("🗄️  Testing Database Models...")
    
    # Initialize database
    Session = init_database()
    session = Session()
    
    try:
        # Create test symbol
        symbol = Symbol(
            name="EURUSD",
            description="Euro vs US Dollar",
            digits=5,
            point=0.00001,
            currency_base="EUR",
            currency_profit="USD"
        )
        session.add(symbol)
        session.commit()
        print(f"✓ Created symbol: {symbol}")
        
        # Create test candle
        candle = Candle(
            symbol_id=symbol.id,
            timeframe="H1",
            timestamp=datetime.utcnow(),
            open=1.0850,
            high=1.0865,
            low=1.0845,
            close=1.0860,
            volume=1000
        )
        session.add(candle)
        session.commit()
        print(f"✓ Created candle: {candle}")
        
        # Create test model version
        model = ModelVersion(
            version="v1.0.0",
            model_type="ensemble",
            training_date=datetime.utcnow(),
            training_samples=10000,
            train_accuracy=0.78,
            test_accuracy=0.73,
            is_active=True
        )
        session.add(model)
        session.commit()
        print(f"✓ Created model version: {model}")
        
        # Create test prediction
        prediction = Prediction(
            symbol_id=symbol.id,
            model_version_id=model.id,
            timeframe="H1",
            timestamp=datetime.utcnow(),
            sentiment="BULLISH",
            confidence=0.82,
            risk_level="MEDIUM",
            price_at_prediction=1.0860
        )
        session.add(prediction)
        session.commit()
        print(f"✓ Created prediction: {prediction}")
        
        # Query test
        symbols = session.query(Symbol).all()
        print(f"\n✓ Query test: Found {len(symbols)} symbols")
        
        print("\n✓ Database models test completed successfully")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        session.rollback()
    finally:
        session.close()
