"""
Database Repository
Data access layer providing high-level database operations
"""
import pandas as pd
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, and_, or_, func, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json

from .models import (
    Base,
    Symbol,
    Candle,
    Prediction,
    ModelVersion,
    PerformanceMetric,
    SystemLog,
    init_database,
)
from config.settings import DatabaseConfig


class DatabaseRepository:
    """
    Repository pattern for database operations
    
    Provides high-level methods for:
    - Storing and retrieving market data
    - Managing predictions and outcomes
    - Tracking model versions
    - Logging system events
    - Querying performance metrics
    """
    
    def __init__(self, session: Optional[Session] = None):
        """
        Initialize repository
        
        Args:
            session: SQLAlchemy session (creates new if not provided)
        """
        if session:
            self.session = session
            self._own_session = False
        else:
            SessionFactory = init_database()
            self.session = SessionFactory()
            self._own_session = True
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._own_session:
            self.session.close()
    
    # ==================== Symbol Operations ====================
    
    def create_or_get_symbol(self, name: str, **kwargs) -> Symbol:
        """Create symbol or get existing"""
        symbol = self.session.query(Symbol).filter_by(name=name).first()
        if not symbol:
            symbol = Symbol(name=name, **kwargs)
            self.session.add(symbol)
            self.session.commit()
        return symbol
    
    def get_symbol(self, name: str) -> Optional[Symbol]:
        """Get symbol by name"""
        return self.session.query(Symbol).filter_by(name=name).first()
    
    def get_all_symbols(self, active_only: bool = True) -> List[Symbol]:
        """Get all symbols"""
        query = self.session.query(Symbol)
        if active_only:
            query = query.filter_by(active=True)
        return query.all()
    
    # ==================== Candle Operations ====================
    
    def save_candles(self, symbol_name: str, timeframe: str, df: pd.DataFrame) -> int:
        """
        Save candles from DataFrame
        
        Args:
            symbol_name: Symbol name
            timeframe: Timeframe string
            df: DataFrame with OHLCV data
            
        Returns:
            int: Number of candles saved
        """
        symbol = self.create_or_get_symbol(symbol_name)
        count = 0
        
        for timestamp, row in df.iterrows():
            # Check if candle already exists
            existing = self.session.query(Candle).filter(
                and_(
                    Candle.symbol_id == symbol.id,
                    Candle.timeframe == timeframe,
                    Candle.timestamp == timestamp
                )
            ).first()
            
            if not existing:
                candle = Candle(
                    symbol_id=symbol.id,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=row['Volume'],
                    spread=row.get('Spread'),
                    real_volume=row.get('RealVolume')
                )
                self.session.add(candle)
                count += 1
        
        self.session.commit()
        return count
    
    def get_candles(
        self,
        symbol_name: str,
        timeframe: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Get candles as DataFrame
        
        Args:
            symbol_name: Symbol name
            timeframe: Timeframe string
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of candles
            
        Returns:
            pd.DataFrame: OHLCV data
        """
        symbol = self.get_symbol(symbol_name)
        if not symbol:
            return pd.DataFrame()
        
        query = self.session.query(Candle).filter(
            and_(
                Candle.symbol_id == symbol.id,
                Candle.timeframe == timeframe
            )
        )
        
        if start_date:
            query = query.filter(Candle.timestamp >= start_date)
        if end_date:
            query = query.filter(Candle.timestamp <= end_date)
        
        query = query.order_by(Candle.timestamp.desc()).limit(limit)
        
        candles = query.all()
        
        if not candles:
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = {
            'Open': [c.open for c in candles],
            'High': [c.high for c in candles],
            'Low': [c.low for c in candles],
            'Close': [c.close for c in candles],
            'Volume': [c.volume for c in candles],
        }
        
        df = pd.DataFrame(data, index=[c.timestamp for c in candles])
        df.sort_index(inplace=True)
        
        return df
    
    # ==================== Model Version Operations ====================
    
    def create_model_version(self, **kwargs) -> ModelVersion:
        """Create new model version"""
        model = ModelVersion(**kwargs)
        self.session.add(model)
        self.session.commit()
        return model
    
    def get_active_model(self) -> Optional[ModelVersion]:
        """Get currently active model version"""
        return self.session.query(ModelVersion).filter_by(
            is_active=True
        ).order_by(desc(ModelVersion.training_date)).first()
    
    def get_model_by_version(self, version: str) -> Optional[ModelVersion]:
        """Get model by version string"""
        return self.session.query(ModelVersion).filter_by(version=version).first()
    
    def set_active_model(self, version: str) -> bool:
        """Set model as active"""
        # Deactivate all models
        self.session.query(ModelVersion).update({ModelVersion.is_active: False})
        
        # Activate specified model
        model = self.get_model_by_version(version)
        if model:
            model.is_active = True
            self.session.commit()
            return True
        return False
    
    # ==================== Prediction Operations ====================
    
    def save_prediction(
        self,
        symbol_name: str,
        timeframe: str,
        sentiment: str,
        confidence: float,
        **kwargs
    ) -> Prediction:
        """Save a new prediction"""
        symbol = self.create_or_get_symbol(symbol_name)
        active_model = self.get_active_model()
        
        prediction = Prediction(
            symbol_id=symbol.id,
            model_version_id=active_model.id if active_model else None,
            timeframe=timeframe,
            timestamp=datetime.utcnow(),
            sentiment=sentiment,
            confidence=confidence,
            **kwargs
        )
        
        self.session.add(prediction)
        self.session.commit()
        return prediction
    
    def get_predictions(
        self,
        symbol_name: Optional[str] = None,
        timeframe: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        verified_only: bool = False,
        limit: int = 100
    ) -> List[Prediction]:
        """Get predictions with filters"""
        query = self.session.query(Prediction)
        
        if symbol_name:
            symbol = self.get_symbol(symbol_name)
            if symbol:
                query = query.filter(Prediction.symbol_id == symbol.id)
        
        if timeframe:
            query = query.filter(Prediction.timeframe == timeframe)
        
        if start_date:
            query = query.filter(Prediction.timestamp >= start_date)
        
        if end_date:
            query = query.filter(Prediction.timestamp <= end_date)
        
        if verified_only:
            query = query.filter(Prediction.is_verified == True)
        
        query = query.order_by(desc(Prediction.timestamp)).limit(limit)
        
        return query.all()
    
    def update_prediction_outcome(
        self,
        prediction_id: int,
        actual_outcome: str,
        was_correct: bool,
        price_change_pips: float
    ) -> bool:
        """Update prediction with actual outcome"""
        prediction = self.session.get(Prediction, prediction_id)
        if prediction:
            prediction.is_verified = True
            prediction.actual_outcome = actual_outcome
            prediction.was_correct = was_correct
            prediction.price_change_pips = price_change_pips
            prediction.verification_timestamp = datetime.utcnow()
            self.session.commit()
            return True
        return False
    
    # ==================== Performance Metrics ====================
    
    def save_performance_metric(self, **kwargs) -> PerformanceMetric:
        """Save performance metric"""
        metric = PerformanceMetric(**kwargs)
        self.session.add(metric)
        self.session.commit()
        return metric
    
    def get_accuracy_stats(
        self,
        symbol_name: Optional[str] = None,
        timeframe: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate accuracy statistics
        
        Args:
            symbol_name: Filter by symbol
            timeframe: Filter by timeframe
            days: Number of days to analyze
            
        Returns:
            Dict with accuracy statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.session.query(Prediction).filter(
            and_(
                Prediction.is_verified == True,
                Prediction.timestamp >= start_date
            )
        )
        
        if symbol_name:
            symbol = self.get_symbol(symbol_name)
            if symbol:
                query = query.filter(Prediction.symbol_id == symbol.id)
        
        if timeframe:
            query = query.filter(Prediction.timeframe == timeframe)
        
        predictions = query.all()
        
        if not predictions:
            return {
                "total": 0,
                "correct": 0,
                "incorrect": 0,
                "accuracy": 0.0,
                "avg_confidence": 0.0
            }
        
        total = len(predictions)
        correct = sum(1 for p in predictions if p.was_correct)
        incorrect = total - correct
        accuracy = (correct / total) * 100 if total > 0 else 0
        avg_confidence = sum(p.confidence for p in predictions) / total
        
        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "accuracy": accuracy,
            "avg_confidence": avg_confidence,
            "predictions": predictions
        }
    
    # ==================== System Logs ====================
    
    def log(
        self,
        level: str,
        category: str,
        message: str,
        **kwargs
    ) -> SystemLog:
        """Create system log entry"""
        log = SystemLog(
            level=level,
            category=category,
            message=message,
            **kwargs
        )
        self.session.add(log)
        self.session.commit()
        return log
    
    def get_logs(
        self,
        level: Optional[str] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SystemLog]:
        """Get system logs with filters"""
        query = self.session.query(SystemLog)
        
        if level:
            query = query.filter(SystemLog.level == level)
        
        if category:
            query = query.filter(SystemLog.category == category)
        
        if start_date:
            query = query.filter(SystemLog.timestamp >= start_date)
        
        query = query.order_by(desc(SystemLog.timestamp)).limit(limit)
        
        return query.all()
    
    # ==================== Cleanup Operations ====================
    
    def cleanup_old_data(self, days: int = 365) -> Dict[str, int]:
        """
        Clean up old data
        
        Args:
            days: Keep data newer than this many days
            
        Returns:
            Dict with counts of deleted records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old candles
        candles_deleted = self.session.query(Candle).filter(
            Candle.timestamp < cutoff_date
        ).delete()
        
        # Delete old logs
        logs_deleted = self.session.query(SystemLog).filter(
            SystemLog.timestamp < cutoff_date
        ).delete()
        
        self.session.commit()
        
        return {
            "candles": candles_deleted,
            "logs": logs_deleted
        }


# Singleton pattern for global repository
_repository_instance = None

def get_repository() -> DatabaseRepository:
    """Get global repository instance"""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = DatabaseRepository()
    return _repository_instance


if __name__ == "__main__":
    # Test repository
    print("🗄️  Testing Database Repository...")
    
    with DatabaseRepository() as repo:
        # Test symbol operations
        symbol = repo.create_or_get_symbol("EURUSD", description="Euro vs US Dollar")
        print(f"✓ Symbol: {symbol}")
        
        # Test saving candles
        test_data = pd.DataFrame({
            'Open': [1.0850, 1.0860],
            'High': [1.0865, 1.0875],
            'Low': [1.0845, 1.0855],
            'Close': [1.0860, 1.0870],
            'Volume': [1000, 1100]
        }, index=pd.date_range(start='2024-01-01', periods=2, freq='1H'))
        
        count = repo.save_candles("EURUSD", "H1", test_data)
        print(f"✓ Saved {count} candles")
        
        # Test retrieving candles
        df = repo.get_candles("EURUSD", "H1", limit=10)
        print(f"✓ Retrieved {len(df)} candles")
        
        # Test prediction
        pred = repo.save_prediction(
            "EURUSD",
            "H1",
            "BULLISH",
            0.82,
            risk_level="MEDIUM",
            price_at_prediction=1.0860
        )
        print(f"✓ Saved prediction: {pred}")
        
        # Test accuracy stats
        stats = repo.get_accuracy_stats("EURUSD", "H1", days=30)
        print(f"✓ Accuracy stats: {stats}")
        
        # Test logging
        log = repo.log("INFO", "test", "Test log message")
        print(f"✓ Created log: {log}")
        
        print("\n✓ Repository test completed successfully")
