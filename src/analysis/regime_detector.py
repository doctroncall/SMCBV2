"""
Market Regime Detection
Identifies market conditions (trending/ranging, volatility states)
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from enum import Enum

from src.indicators.technical import TechnicalIndicators
from src.utils.logger import get_logger

logger = get_logger()


class TrendRegime(Enum):
    """Trend regime states"""
    STRONG_UPTREND = "STRONG_UPTREND"
    UPTREND = "UPTREND"
    RANGING = "RANGING"
    DOWNTREND = "DOWNTREND"
    STRONG_DOWNTREND = "STRONG_DOWNTREND"


class VolatilityRegime(Enum):
    """Volatility regime states"""
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class VolumeRegime(Enum):
    """Volume regime states"""
    DRY = "DRY"
    NORMAL = "NORMAL"
    ELEVATED = "ELEVATED"
    SURGE = "SURGE"


class RegimeDetector:
    """
    Detect market regimes for adaptive trading
    
    Identifies:
    - Trend regime (trending vs ranging)
    - Volatility regime (calm vs volatile)
    - Volume regime (thin vs heavy)
    
    Use cases:
    - Train separate models per regime
    - Adjust position sizing
    - Filter trades by regime
    - Adapt indicators
    """
    
    def __init__(self):
        """Initialize regime detector"""
        self.tech_indicators = TechnicalIndicators()
        self.logger = logger
    
    def detect_regime(
        self,
        df: pd.DataFrame,
        lookback: int = 50
    ) -> Dict[str, Any]:
        """
        Detect current market regime
        
        Args:
            df: DataFrame with OHLCV data
            lookback: Lookback period for regime calculation
            
        Returns:
            Dict with regime information
        """
        regime = {
            'trend': self.detect_trend_regime(df, lookback),
            'volatility': self.detect_volatility_regime(df, lookback),
            'volume': self.detect_volume_regime(df, lookback),
            'composite': None
        }
        
        # Composite regime score
        regime['composite'] = self._calculate_composite_regime(regime)
        
        return regime
    
    def detect_trend_regime(
        self,
        df: pd.DataFrame,
        lookback: int = 50
    ) -> Dict[str, Any]:
        """
        Detect trend regime
        
        Uses multiple indicators:
        - ADX (trend strength)
        - Price vs moving averages
        - Higher highs / lower lows
        - Price efficiency
        
        Returns:
            Dict with trend regime details
        """
        # Calculate ADX
        adx_data = self.tech_indicators.calculate_adx(df)
        adx = adx_data['adx'].iloc[-1]
        plus_di = adx_data['plus_di'].iloc[-1]
        minus_di = adx_data['minus_di'].iloc[-1]
        
        # Calculate moving averages
        ema_20 = self.tech_indicators.calculate_ema(df, 20).iloc[-1]
        ema_50 = self.tech_indicators.calculate_ema(df, 50).iloc[-1]
        sma_200 = self.tech_indicators.calculate_sma(df, 200).iloc[-1]
        
        current_price = df['Close'].iloc[-1]
        
        # Price efficiency (trending vs choppy)
        price_change = abs(df['Close'].iloc[-1] - df['Close'].iloc[-lookback])
        path_length = df['Close'].diff().abs().iloc[-lookback:].sum()
        efficiency = price_change / path_length if path_length > 0 else 0
        
        # Determine regime
        is_trending = adx > 25
        is_strong_trend = adx > 40
        
        if is_trending:
            if plus_di > minus_di:
                if is_strong_trend and efficiency > 0.5:
                    regime_type = TrendRegime.STRONG_UPTREND
                else:
                    regime_type = TrendRegime.UPTREND
            else:
                if is_strong_trend and efficiency > 0.5:
                    regime_type = TrendRegime.STRONG_DOWNTREND
                else:
                    regime_type = TrendRegime.DOWNTREND
        else:
            regime_type = TrendRegime.RANGING
        
        return {
            'regime': regime_type.value,
            'adx': adx,
            'efficiency': efficiency,
            'is_trending': is_trending,
            'direction': 'BULLISH' if plus_di > minus_di else 'BEARISH',
            'strength': adx / 100,
            'price_vs_ema20': (current_price / ema_20 - 1) * 100,
            'price_vs_ema50': (current_price / ema_50 - 1) * 100,
            'price_vs_sma200': (current_price / sma_200 - 1) * 100
        }
    
    def detect_volatility_regime(
        self,
        df: pd.DataFrame,
        lookback: int = 50
    ) -> Dict[str, Any]:
        """
        Detect volatility regime
        
        Uses:
        - ATR (Average True Range)
        - Historical volatility
        - Bollinger Band width
        
        Returns:
            Dict with volatility regime details
        """
        # Calculate ATR
        atr = self.tech_indicators.calculate_atr(df).iloc[-1]
        atr_pct = (atr / df['Close'].iloc[-1]) * 100
        
        # Historical ATR percentiles
        atr_series = self.tech_indicators.calculate_atr(df)
        atr_pct_series = (atr_series / df['Close']) * 100
        
        historical_atr_pct = atr_pct_series.iloc[-lookback:]
        atr_percentile = (historical_atr_pct < atr_pct).mean()
        
        # Bollinger Bands width
        bb = self.tech_indicators.calculate_bollinger_bands(df)
        bb_width = ((bb['upper'].iloc[-1] - bb['lower'].iloc[-1]) / bb['middle'].iloc[-1]) * 100
        
        # Historical volatility
        returns = df['Close'].pct_change()
        hist_vol = returns.iloc[-lookback:].std() * np.sqrt(252) * 100  # Annualized
        
        # Determine regime
        if atr_percentile < 0.2:
            regime_type = VolatilityRegime.VERY_LOW
        elif atr_percentile < 0.4:
            regime_type = VolatilityRegime.LOW
        elif atr_percentile < 0.7:
            regime_type = VolatilityRegime.NORMAL
        elif atr_percentile < 0.9:
            regime_type = VolatilityRegime.HIGH
        else:
            regime_type = VolatilityRegime.VERY_HIGH
        
        return {
            'regime': regime_type.value,
            'atr_pct': atr_pct,
            'atr_percentile': atr_percentile,
            'bb_width': bb_width,
            'historical_volatility': hist_vol,
            'is_expanding': atr_pct > historical_atr_pct.mean()
        }
    
    def detect_volume_regime(
        self,
        df: pd.DataFrame,
        lookback: int = 50
    ) -> Dict[str, Any]:
        """
        Detect volume regime
        
        Uses:
        - Volume vs moving average
        - Volume percentiles
        - OBV trend
        
        Returns:
            Dict with volume regime details
        """
        if 'Volume' not in df.columns:
            return {
                'regime': VolumeRegime.NORMAL.value,
                'relative_volume': 1.0,
                'percentile': 0.5,
                'obv_trend': 'NEUTRAL'
            }
        
        current_volume = df['Volume'].iloc[-1]
        volume_ma = df['Volume'].iloc[-lookback:].mean()
        relative_volume = current_volume / volume_ma if volume_ma > 0 else 1.0
        
        # Volume percentile
        historical_volume = df['Volume'].iloc[-lookback:]
        volume_percentile = (historical_volume < current_volume).mean()
        
        # OBV trend
        obv = self.tech_indicators.calculate_obv(df)
        obv_ma = obv.iloc[-lookback:].mean()
        obv_trend = 'RISING' if obv.iloc[-1] > obv_ma else 'FALLING'
        
        # Determine regime
        if volume_percentile < 0.25:
            regime_type = VolumeRegime.DRY
        elif volume_percentile < 0.75:
            regime_type = VolumeRegime.NORMAL
        elif volume_percentile < 0.95:
            regime_type = VolumeRegime.ELEVATED
        else:
            regime_type = VolumeRegime.SURGE
        
        return {
            'regime': regime_type.value,
            'relative_volume': relative_volume,
            'percentile': volume_percentile,
            'obv_trend': obv_trend
        }
    
    def _calculate_composite_regime(self, regime: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate composite regime score
        
        Combines trend, volatility, and volume into single assessment
        """
        trend_data = regime['trend']
        vol_data = regime['volatility']
        
        # Trend favorability (-1 to 1)
        if 'UPTREND' in trend_data['regime']:
            trend_score = 0.5 if trend_data['regime'] == 'UPTREND' else 1.0
        elif 'DOWNTREND' in trend_data['regime']:
            trend_score = -0.5 if trend_data['regime'] == 'DOWNTREND' else -1.0
        else:
            trend_score = 0.0
        
        # Volatility favorability (0 to 1, higher is better for trading)
        vol_map = {
            'VERY_LOW': 0.2,
            'LOW': 0.5,
            'NORMAL': 1.0,
            'HIGH': 0.7,
            'VERY_HIGH': 0.3
        }
        vol_score = vol_map.get(vol_data['regime'], 0.5)
        
        # Trading favorability
        is_trending = trend_data['is_trending']
        is_good_volatility = vol_data['regime'] in ['NORMAL', 'LOW']
        
        if is_trending and is_good_volatility:
            favorability = "FAVORABLE"
        elif is_trending:
            favorability = "MODERATE"
        elif is_good_volatility:
            favorability = "CAUTIOUS"
        else:
            favorability = "UNFAVORABLE"
        
        return {
            'trend_score': trend_score,
            'volatility_score': vol_score,
            'favorability': favorability,
            'is_trending': is_trending,
            'is_stable_volatility': is_good_volatility
        }
    
    def get_regime_label(self, df: pd.DataFrame, lookback: int = 50) -> int:
        """
        Get simple regime label for classification
        
        Args:
            df: DataFrame with OHLCV data
            lookback: Lookback period
            
        Returns:
            Integer regime label:
            0 = ranging/low_vol
            1 = trending_up/normal_vol
            2 = trending_down/normal_vol
            3 = high_volatility
        """
        regime = self.detect_regime(df, lookback)
        
        trend = regime['trend']['regime']
        vol = regime['volatility']['regime']
        
        # High volatility gets its own class
        if vol in ['HIGH', 'VERY_HIGH']:
            return 3
        
        # Trending regimes
        if 'UPTREND' in trend:
            return 1
        elif 'DOWNTREND' in trend:
            return 2
        else:
            return 0  # Ranging
    
    def add_regime_features(
        self,
        df: pd.DataFrame,
        lookback: int = 50
    ) -> pd.DataFrame:
        """
        Add regime features to DataFrame
        
        Args:
            df: DataFrame with OHLCV data
            lookback: Lookback period
            
        Returns:
            DataFrame with added regime features
        """
        df = df.copy()
        
        regimes = []
        for i in range(len(df)):
            if i < lookback:
                regimes.append({
                    'regime_trend': 0,
                    'regime_volatility': 0,
                    'regime_composite': 0
                })
            else:
                df_window = df.iloc[:i+1]
                regime = self.detect_regime(df_window, lookback)
                
                # Encode regimes as numbers
                trend_map = {
                    'STRONG_UPTREND': 2,
                    'UPTREND': 1,
                    'RANGING': 0,
                    'DOWNTREND': -1,
                    'STRONG_DOWNTREND': -2
                }
                
                vol_map = {
                    'VERY_LOW': -2,
                    'LOW': -1,
                    'NORMAL': 0,
                    'HIGH': 1,
                    'VERY_HIGH': 2
                }
                
                regimes.append({
                    'regime_trend': trend_map.get(regime['trend']['regime'], 0),
                    'regime_volatility': vol_map.get(regime['volatility']['regime'], 0),
                    'regime_composite': regime['composite']['trend_score']
                })
        
        # Add to DataFrame
        regime_df = pd.DataFrame(regimes, index=df.index)
        df = pd.concat([df, regime_df], axis=1)
        
        return df


if __name__ == "__main__":
    # Test regime detector
    print("🔍 Testing Regime Detector...")
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=200, freq='1H')
    
    # Create trending data
    trend = np.linspace(1.08, 1.10, 200)
    noise = np.random.normal(0, 0.0005, 200)
    close = trend + noise
    
    df = pd.DataFrame({
        'Open': close - 0.0001,
        'High': close + 0.0002,
        'Low': close - 0.0002,
        'Close': close,
        'Volume': np.random.randint(1000, 10000, 200)
    }, index=dates)
    
    detector = RegimeDetector()
    
    print("\n✓ Detecting current regime...")
    regime = detector.detect_regime(df, lookback=50)
    
    print(f"\nTrend Regime:")
    print(f"   Type: {regime['trend']['regime']}")
    print(f"   ADX: {regime['trend']['adx']:.2f}")
    print(f"   Efficiency: {regime['trend']['efficiency']:.2%}")
    print(f"   Direction: {regime['trend']['direction']}")
    
    print(f"\nVolatility Regime:")
    print(f"   Type: {regime['volatility']['regime']}")
    print(f"   ATR %: {regime['volatility']['atr_pct']:.3f}%")
    print(f"   Percentile: {regime['volatility']['atr_percentile']:.0%}")
    
    print(f"\nVolume Regime:")
    print(f"   Type: {regime['volume']['regime']}")
    print(f"   Relative: {regime['volume']['relative_volume']:.2f}x")
    
    print(f"\nComposite Assessment:")
    print(f"   Favorability: {regime['composite']['favorability']}")
    print(f"   Trend Score: {regime['composite']['trend_score']:.2f}")
    print(f"   Volatility Score: {regime['composite']['volatility_score']:.2f}")
    
    print(f"\n✓ Regime label: {detector.get_regime_label(df)}")
    
    print("\n✓ Regime detector test completed")
