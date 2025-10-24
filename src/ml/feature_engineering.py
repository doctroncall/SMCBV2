"""
Feature Engineering
Creates ML features from market data and indicators
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime
import warnings

from src.indicators.technical import TechnicalIndicators
from src.indicators.smc import SMCAnalyzer
from src.utils.logger import get_logger

warnings.filterwarnings('ignore', category=RuntimeWarning)

logger = get_logger()


class FeatureEngineer:
    """
    Create ML features from raw market data
    
    Features include:
    - Technical indicators
    - SMC patterns
    - Price patterns
    - Volume patterns
    - Time-based features
    """
    
    def __init__(self):
        """Initialize feature engineer"""
        self.tech_indicators = TechnicalIndicators()
        self.smc_analyzer = SMCAnalyzer()
        self.logger = logger
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create all ML features from OHLCV data
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with features
        """
        try:
            self.logger.info("Creating ML features", category="ml_training")
            
            features_df = df.copy()
            
            # Technical indicator features
            features_df = self._add_indicator_features(features_df)
            
            # Price pattern features
            features_df = self._add_price_features(features_df)
            
            # Volume features
            features_df = self._add_volume_features(features_df)
            
            # Time-based features
            features_df = self._add_time_features(features_df)
            
            # SMC features
            features_df = self._add_smc_features(features_df)
            
            # NEW: Advanced features
            features_df = self._add_candlestick_patterns(features_df)
            features_df = self._add_feature_interactions(features_df)
            features_df = self._add_market_regime_features(features_df)
            features_df = self._add_lagged_features(features_df)
            
            # Drop NaN values
            features_df = features_df.dropna()
            
            self.logger.info(f"Created {len(features_df.columns)} features", category="ml_training")
            
            return features_df
            
        except Exception as e:
            self.logger.error(f"Error creating features: {str(e)}", category="ml_training")
            return df
    
    def _add_indicator_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicator features"""
        # RSI
        df['rsi'] = self.tech_indicators.calculate_rsi(df)
        
        # MACD
        macd = self.tech_indicators.calculate_macd(df)
        df['macd'] = macd['macd']
        df['macd_signal'] = macd['signal']
        df['macd_hist'] = macd['histogram']
        
        # ADX
        adx = self.tech_indicators.calculate_adx(df)
        df['adx'] = adx['adx']
        df['plus_di'] = adx['plus_di']
        df['minus_di'] = adx['minus_di']
        
        # Bollinger Bands
        bb = self.tech_indicators.calculate_bollinger_bands(df)
        df['bb_upper'] = bb['upper']
        df['bb_middle'] = bb['middle']
        df['bb_lower'] = bb['lower']
        df['bb_width'] = (bb['upper'] - bb['lower']) / bb['middle']
        
        # ATR
        df['atr'] = self.tech_indicators.calculate_atr(df)
        df['atr_pct'] = df['atr'] / df['Close']
        
        # Moving averages
        df['ema_20'] = self.tech_indicators.calculate_ema(df, 20)
        df['ema_50'] = self.tech_indicators.calculate_ema(df, 50)
        df['sma_200'] = self.tech_indicators.calculate_sma(df, 200)
        
        # Volume indicators
        df['obv'] = self.tech_indicators.calculate_obv(df)
        df['mfi'] = self.tech_indicators.calculate_mfi(df)
        
        return df
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price-based features"""
        # Price changes
        df['price_change'] = df['Close'].pct_change()
        df['price_change_5'] = df['Close'].pct_change(periods=5)
        df['price_change_10'] = df['Close'].pct_change(periods=10)
        
        # High-Low range
        df['hl_range'] = (df['High'] - df['Low']) / df['Close']
        
        # Body vs wick
        df['body_size'] = abs(df['Close'] - df['Open']) / df['Close']
        df['upper_wick'] = (df['High'] - df[['Open', 'Close']].max(axis=1)) / df['Close']
        df['lower_wick'] = (df[['Open', 'Close']].min(axis=1) - df['Low']) / df['Close']
        
        # Price position
        df['close_position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'])
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features"""
        # Volume changes
        df['volume_change'] = df['Volume'].pct_change()
        df['volume_ma_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['is_london_session'] = ((df['hour'] >= 8) & (df['hour'] < 17)).astype(int)
        df['is_ny_session'] = ((df['hour'] >= 13) & (df['hour'] < 22)).astype(int)
        
        return df
    
    def _add_smc_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add SMC-based features (simplified for performance)"""
        try:
            # Swing points count (simplified)
            df['recent_highs'] = df['High'].rolling(20).apply(lambda x: (x == x.max()).sum())
            df['recent_lows'] = df['Low'].rolling(20).apply(lambda x: (x == x.min()).sum())
            
            # Trend strength
            df['trend_strength'] = (df['Close'] - df['Close'].shift(20)) / df['Close'].shift(20)
            
            # Higher highs / lower lows detection
            df['higher_high'] = ((df['High'] > df['High'].shift(1)) & 
                                (df['High'].shift(1) > df['High'].shift(2))).astype(int)
            df['lower_low'] = ((df['Low'] < df['Low'].shift(1)) & 
                              (df['Low'].shift(1) < df['Low'].shift(2))).astype(int)
            
            # Market structure score (simple version)
            df['structure_score'] = df['higher_high'].rolling(10).sum() - df['lower_low'].rolling(10).sum()
            
        except Exception as e:
            self.logger.warning(f"Error adding SMC features: {str(e)}", category="ml_training")
        
        return df
    
    def _add_candlestick_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add candlestick pattern features"""
        try:
            # Body and wick sizes
            body = abs(df['Close'] - df['Open'])
            upper_wick = df['High'] - df[['Open', 'Close']].max(axis=1)
            lower_wick = df[['Open', 'Close']].min(axis=1) - df['Low']
            candle_range = df['High'] - df['Low']
            
            # Doji (small body, long wicks)
            df['is_doji'] = ((body / candle_range) < 0.1).astype(int)
            
            # Hammer / Hanging Man (small upper wick, long lower wick, small body)
            df['is_hammer'] = ((lower_wick > 2 * body) & 
                              (upper_wick < body) & 
                              (body / candle_range < 0.3)).astype(int)
            
            # Shooting Star / Inverted Hammer
            df['is_shooting_star'] = ((upper_wick > 2 * body) & 
                                     (lower_wick < body) & 
                                     (body / candle_range < 0.3)).astype(int)
            
            # Engulfing patterns
            bullish_engulf = ((df['Close'] > df['Open']) & 
                             (df['Close'].shift(1) < df['Open'].shift(1)) &
                             (df['Open'] < df['Close'].shift(1)) &
                             (df['Close'] > df['Open'].shift(1)))
            df['bullish_engulfing'] = bullish_engulf.astype(int)
            
            bearish_engulf = ((df['Close'] < df['Open']) & 
                             (df['Close'].shift(1) > df['Open'].shift(1)) &
                             (df['Open'] > df['Close'].shift(1)) &
                             (df['Close'] < df['Open'].shift(1)))
            df['bearish_engulfing'] = bearish_engulf.astype(int)
            
            # Candle momentum (consecutive same-color candles)
            df['is_bullish_candle'] = (df['Close'] > df['Open']).astype(int)
            df['consecutive_bullish'] = df['is_bullish_candle'].rolling(3).sum()
            df['consecutive_bearish'] = (1 - df['is_bullish_candle']).rolling(3).sum()
            
        except Exception as e:
            self.logger.warning(f"Error adding candlestick patterns: {e}", category="ml_training")
        
        return df
    
    def _add_feature_interactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add feature interaction terms"""
        try:
            # RSI * Volume ratio
            if 'rsi' in df.columns and 'volume_ma_ratio' in df.columns:
                df['rsi_volume_interaction'] = df['rsi'] * df['volume_ma_ratio']
            
            # Trend * Momentum alignment
            if 'ema_20' in df.columns and 'ema_50' in df.columns and 'macd' in df.columns:
                df['trend_momentum_align'] = ((df['ema_20'] > df['ema_50']).astype(int) * 
                                             np.sign(df['macd']))
            
            # Volatility * Price position
            if 'bb_width' in df.columns and 'close_position' in df.columns:
                df['vol_position_interaction'] = df['bb_width'] * df['close_position']
            
            # ADX * RSI (trend strength * momentum)
            if 'adx' in df.columns and 'rsi' in df.columns:
                df['adx_rsi_interaction'] = df['adx'] * (df['rsi'] / 100)
            
        except Exception as e:
            self.logger.warning(f"Error adding feature interactions: {e}", category="ml_training")
        
        return df
    
    def _add_market_regime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market regime detection features"""
        try:
            # Volatility regime
            if 'atr_pct' in df.columns:
                atr_ma = df['atr_pct'].rolling(50).mean()
                df['volatility_regime'] = (df['atr_pct'] / atr_ma).fillna(1.0)
            
            # Trend regime (ADX-based)
            if 'adx' in df.columns:
                df['is_trending'] = (df['adx'] > 25).astype(int)
            
            # Volume regime
            if 'Volume' in df.columns:
                vol_ma = df['Volume'].rolling(50).mean()
                df['volume_regime'] = (df['Volume'] / vol_ma).fillna(1.0)
            
            # Price efficiency (trending vs choppy)
            price_change = abs(df['Close'] - df['Close'].shift(10))
            path_length = df['Close'].diff().abs().rolling(10).sum()
            df['price_efficiency'] = (price_change / path_length).fillna(0.5)
            
        except Exception as e:
            self.logger.warning(f"Error adding market regime features: {e}", category="ml_training")
        
        return df
    
    def _add_lagged_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lagged features for temporal patterns"""
        try:
            # Lagged returns
            for lag in [1, 2, 3, 5]:
                df[f'return_lag_{lag}'] = df['Close'].pct_change(lag)
            
            # Lagged RSI
            if 'rsi' in df.columns:
                df['rsi_lag_1'] = df['rsi'].shift(1)
                df['rsi_change'] = df['rsi'] - df['rsi'].shift(1)
            
            # Lagged volume
            if 'Volume' in df.columns:
                df['volume_lag_1'] = df['Volume'].shift(1)
            
            # Price acceleration (rate of change of returns)
            df['price_acceleration'] = df['Close'].pct_change().diff()
            
        except Exception as e:
            self.logger.warning(f"Error adding lagged features: {e}", category="ml_training")
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names (dynamically generated based on actual features)"""
        # Base features that should always exist
        base_features = [
            'rsi', 'macd', 'macd_signal', 'macd_hist',
            'adx', 'plus_di', 'minus_di',
            'bb_width', 'atr_pct',
            'ema_20', 'ema_50', 'sma_200',
            'obv', 'mfi',
            'price_change', 'price_change_5', 'price_change_10',
            'hl_range', 'body_size', 'upper_wick', 'lower_wick',
            'close_position',
            'volume_change', 'volume_ma_ratio',
            'hour', 'day_of_week', 'is_london_session', 'is_ny_session',
            'recent_highs', 'recent_lows', 'trend_strength',
            'higher_high', 'lower_low', 'structure_score',
        ]
        
        # Advanced features (newly added)
        advanced_features = [
            # Candlestick patterns
            'is_doji', 'is_hammer', 'is_shooting_star',
            'bullish_engulfing', 'bearish_engulfing',
            'is_bullish_candle', 'consecutive_bullish', 'consecutive_bearish',
            # Feature interactions
            'rsi_volume_interaction', 'trend_momentum_align',
            'vol_position_interaction', 'adx_rsi_interaction',
            # Market regimes
            'volatility_regime', 'is_trending', 'volume_regime', 'price_efficiency',
            # Lagged features
            'return_lag_1', 'return_lag_2', 'return_lag_3', 'return_lag_5',
            'rsi_lag_1', 'rsi_change', 'volume_lag_1', 'price_acceleration',
        ]
        
        return base_features + advanced_features


if __name__ == "__main__":
    # Test feature engineering
    print("🔧 Testing Feature Engineer...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=500, freq='1H')
    data = {
        'Open': np.random.uniform(1.08, 1.09, 500),
        'High': np.random.uniform(1.09, 1.10, 500),
        'Low': np.random.uniform(1.07, 1.08, 500),
        'Close': np.random.uniform(1.08, 1.09, 500),
        'Volume': np.random.randint(1000, 10000, 500),
    }
    df = pd.DataFrame(data, index=dates)
    
    engineer = FeatureEngineer()
    
    features_df = engineer.create_features(df)
    
    print(f"✓ Original columns: {len(df.columns)}")
    print(f"✓ Feature columns: {len(features_df.columns)}")
    print(f"✓ Rows after feature engineering: {len(features_df)}")
    print(f"✓ Feature names: {engineer.get_feature_names()}")
    
    print("\n✓ Feature engineer test completed")
