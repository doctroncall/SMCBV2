"""
Technical Indicators Calculator
Comprehensive technical analysis indicators using TA-Lib and pandas-ta
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
try:
    import talib
except Exception as e:  # pragma: no cover
    talib = None
try:
    import pandas_ta as pta
except Exception:
    pta = None

from config.settings import IndicatorConfig
from src.utils.logger import get_logger

logger = get_logger()


class TechnicalIndicators:
    """
    Calculate technical indicators for market analysis
    
    Features:
    - Trend indicators (MA, MACD, ADX, Ichimoku)
    - Momentum indicators (RSI, Stochastic, CCI, Williams %R)
    - Volatility indicators (Bollinger Bands, ATR, Keltner)
    - Volume indicators (Volume Profile, OBV, VWAP, MFI)
    - Signal generation with strength scoring
    """
    
    def __init__(self):
        """Initialize technical indicators calculator"""
        self.config = IndicatorConfig
        self.logger = logger
        self.cache = {}
    
    # ==================== Trend Indicators ====================
    
    def calculate_ema(
        self,
        df: pd.DataFrame,
        period: int = 20,
        column: str = 'Close'
    ) -> pd.Series:
        """Calculate Exponential Moving Average"""
        if talib is None:
            raise ImportError("TA-Lib is required for EMA. Please install TA-Lib.")
        return talib.EMA(df[column], timeperiod=period)
    
    def calculate_sma(
        self,
        df: pd.DataFrame,
        period: int = 20,
        column: str = 'Close'
    ) -> pd.Series:
        """Calculate Simple Moving Average"""
        if talib is None:
            raise ImportError("TA-Lib is required for SMA. Please install TA-Lib.")
        return talib.SMA(df[column], timeperiod=period)
    
    def calculate_macd(
        self,
        df: pd.DataFrame,
        fast: Optional[int] = None,
        slow: Optional[int] = None,
        signal: Optional[int] = None
    ) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Returns:
            Dict with 'macd', 'signal', 'histogram'
        """
        fast = fast or self.config.MACD_FAST
        slow = slow or self.config.MACD_SLOW
        signal = signal or self.config.MACD_SIGNAL
        
        if talib is None:
            raise ImportError("TA-Lib is required for MACD. Please install TA-Lib.")
        macd, signal_line, histogram = talib.MACD(
            df['Close'],
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal
        )
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_adx(
        self,
        df: pd.DataFrame,
        period: Optional[int] = None
    ) -> Dict[str, pd.Series]:
        """
        Calculate ADX (Average Directional Index)
        
        Returns:
            Dict with 'adx', 'plus_di', 'minus_di'
        """
        period = period or self.config.ADX_PERIOD
        
        if talib is None:
            raise ImportError("TA-Lib is required for ADX. Please install TA-Lib.")
        adx = talib.ADX(df['High'], df['Low'], df['Close'], timeperiod=period)
        plus_di = talib.PLUS_DI(df['High'], df['Low'], df['Close'], timeperiod=period)
        minus_di = talib.MINUS_DI(df['High'], df['Low'], df['Close'], timeperiod=period)
        
        return {
            'adx': adx,
            'plus_di': plus_di,
            'minus_di': minus_di
        }
    
    def calculate_ichimoku(
        self,
        df: pd.DataFrame,
        tenkan: int = 9,
        kijun: int = 26,
        senkou_b: int = 52
    ) -> Dict[str, pd.Series]:
        """
        Calculate Ichimoku Cloud
        
        Returns:
            Dict with all Ichimoku components
        """
        # Tenkan-sen (Conversion Line)
        tenkan_sen = (df['High'].rolling(window=tenkan).max() + 
                      df['Low'].rolling(window=tenkan).min()) / 2
        
        # Kijun-sen (Base Line)
        kijun_sen = (df['High'].rolling(window=kijun).max() + 
                     df['Low'].rolling(window=kijun).min()) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun)
        
        # Senkou Span B (Leading Span B)
        senkou_span_b = ((df['High'].rolling(window=senkou_b).max() + 
                         df['Low'].rolling(window=senkou_b).min()) / 2).shift(kijun)
        
        # Chikou Span (Lagging Span)
        chikou_span = df['Close'].shift(-kijun)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    # ==================== Momentum Indicators ====================
    
    def calculate_rsi(
        self,
        df: pd.DataFrame,
        period: Optional[int] = None
    ) -> pd.Series:
        """Calculate RSI (Relative Strength Index)"""
        period = period or self.config.RSI_PERIOD
        if talib is None:
            raise ImportError("TA-Lib is required for RSI. Please install TA-Lib.")
        return talib.RSI(df['Close'], timeperiod=period)
    
    def calculate_stochastic(
        self,
        df: pd.DataFrame,
        k_period: Optional[int] = None,
        d_period: Optional[int] = None,
        smooth: Optional[int] = None
    ) -> Dict[str, pd.Series]:
        """
        Calculate Stochastic Oscillator
        
        Returns:
            Dict with 'k' and 'd' lines
        """
        k_period = k_period or self.config.STOCH_K
        d_period = d_period or self.config.STOCH_D
        smooth = smooth or self.config.STOCH_SMOOTH
        
        if talib is None:
            raise ImportError("TA-Lib is required for Stochastic. Please install TA-Lib.")
        slowk, slowd = talib.STOCH(
            df['High'],
            df['Low'],
            df['Close'],
            fastk_period=k_period,
            slowk_period=smooth,
            slowd_period=d_period
        )
        
        return {
            'k': slowk,
            'd': slowd
        }
    
    def calculate_cci(
        self,
        df: pd.DataFrame,
        period: int = 20
    ) -> pd.Series:
        """Calculate CCI (Commodity Channel Index)"""
        if talib is None:
            raise ImportError("TA-Lib is required for CCI. Please install TA-Lib.")
        return talib.CCI(df['High'], df['Low'], df['Close'], timeperiod=period)
    
    def calculate_williams_r(
        self,
        df: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """Calculate Williams %R"""
        if talib is None:
            raise ImportError("TA-Lib is required for Williams %R. Please install TA-Lib.")
        return talib.WILLR(df['High'], df['Low'], df['Close'], timeperiod=period)
    
    # ==================== Volatility Indicators ====================
    
    def calculate_bollinger_bands(
        self,
        df: pd.DataFrame,
        period: Optional[int] = None,
        std_dev: Optional[float] = None
    ) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Returns:
            Dict with 'upper', 'middle', 'lower'
        """
        period = period or self.config.BB_PERIOD
        std_dev = std_dev or self.config.BB_STD
        
        if talib is None:
            raise ImportError("TA-Lib is required for Bollinger Bands. Please install TA-Lib.")
        upper, middle, lower = talib.BBANDS(
            df['Close'],
            timeperiod=period,
            nbdevup=std_dev,
            nbdevdn=std_dev
        )
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    def calculate_atr(
        self,
        df: pd.DataFrame,
        period: Optional[int] = None
    ) -> pd.Series:
        """Calculate ATR (Average True Range)"""
        period = period or self.config.ATR_PERIOD
        if talib is None:
            raise ImportError("TA-Lib is required for ATR. Please install TA-Lib.")
        return talib.ATR(df['High'], df['Low'], df['Close'], timeperiod=period)
    
    def calculate_keltner_channels(
        self,
        df: pd.DataFrame,
        period: int = 20,
        atr_multiplier: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        Calculate Keltner Channels
        
        Returns:
            Dict with 'upper', 'middle', 'lower'
        """
        middle = self.calculate_ema(df, period)
        atr = self.calculate_atr(df, period)
        
        upper = middle + (atr * atr_multiplier)
        lower = middle - (atr * atr_multiplier)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    # ==================== Volume Indicators ====================
    
    def calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate OBV (On Balance Volume)"""
        if talib is None:
            raise ImportError("TA-Lib is required for OBV. Please install TA-Lib.")
        return talib.OBV(df['Close'], df['Volume'])
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate VWAP (Volume Weighted Average Price)"""
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        return (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    def calculate_mfi(
        self,
        df: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """Calculate MFI (Money Flow Index)"""
        if talib is None:
            raise ImportError("TA-Lib is required for MFI. Please install TA-Lib.")
        return talib.MFI(df['High'], df['Low'], df['Close'], df['Volume'], timeperiod=period)
    
    def calculate_volume_profile(
        self,
        df: pd.DataFrame,
        bins: int = 24
    ) -> Dict[str, Any]:
        """
        Calculate Volume Profile
        
        Returns:
            Dict with volume profile data
        """
        price_range = df['High'].max() - df['Low'].min()
        bin_size = price_range / bins
        
        volume_profile = {}
        for i in range(bins):
            lower = df['Low'].min() + (i * bin_size)
            upper = lower + bin_size
            
            mask = (df['Low'] <= upper) & (df['High'] >= lower)
            volume = df.loc[mask, 'Volume'].sum()
            
            volume_profile[f"{lower:.5f}-{upper:.5f}"] = volume
        
        # Find POC (Point of Control) - price level with highest volume
        poc_range = max(volume_profile, key=volume_profile.get)
        poc_price = float(poc_range.split('-')[0])
        
        return {
            'profile': volume_profile,
            'poc': poc_price,
            'total_volume': df['Volume'].sum()
        }
    
    # ==================== Signal Generation ====================
    
    def get_trend_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate trend signal from multiple indicators
        
        Returns:
            Dict with signal, strength, and details
        """
        signals = []
        
        # EMA crossover
        ema_fast = self.calculate_ema(df, self.config.EMA_FAST)
        ema_slow = self.calculate_ema(df, self.config.EMA_SLOW)
        
        if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
            signals.append({'indicator': 'EMA', 'signal': 'BULLISH', 'strength': 0.15})
        elif ema_fast.iloc[-1] < ema_slow.iloc[-1]:
            signals.append({'indicator': 'EMA', 'signal': 'BEARISH', 'strength': 0.15})
        
        # MACD
        macd_data = self.calculate_macd(df)
        if macd_data['histogram'].iloc[-1] > 0:
            signals.append({'indicator': 'MACD', 'signal': 'BULLISH', 'strength': 0.20})
        elif macd_data['histogram'].iloc[-1] < 0:
            signals.append({'indicator': 'MACD', 'signal': 'BEARISH', 'strength': 0.20})
        
        # ADX
        adx_data = self.calculate_adx(df)
        if adx_data['adx'].iloc[-1] > self.config.ADX_THRESHOLD:
            if adx_data['plus_di'].iloc[-1] > adx_data['minus_di'].iloc[-1]:
                signals.append({'indicator': 'ADX', 'signal': 'BULLISH', 'strength': 0.15})
            else:
                signals.append({'indicator': 'ADX', 'signal': 'BEARISH', 'strength': 0.15})
        
        # Aggregate signals
        bullish_strength = sum(s['strength'] for s in signals if s['signal'] == 'BULLISH')
        bearish_strength = sum(s['strength'] for s in signals if s['signal'] == 'BEARISH')
        
        if bullish_strength > bearish_strength:
            overall_signal = 'BULLISH'
            confidence = bullish_strength
        elif bearish_strength > bullish_strength:
            overall_signal = 'BEARISH'
            confidence = bearish_strength
        else:
            overall_signal = 'NEUTRAL'
            confidence = 0.0
        
        return {
            'signal': overall_signal,
            'confidence': confidence,
            'indicators': signals
        }
    
    def get_momentum_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate momentum signal"""
        signals = []
        
        # RSI
        rsi = self.calculate_rsi(df)
        rsi_value = rsi.iloc[-1]
        
        if rsi_value > self.config.RSI_OVERBOUGHT:
            signals.append({'indicator': 'RSI', 'signal': 'BEARISH', 'strength': 0.20, 'value': rsi_value})
        elif rsi_value < self.config.RSI_OVERSOLD:
            signals.append({'indicator': 'RSI', 'signal': 'BULLISH', 'strength': 0.20, 'value': rsi_value})
        elif rsi_value > 50:
            signals.append({'indicator': 'RSI', 'signal': 'BULLISH', 'strength': 0.10, 'value': rsi_value})
        else:
            signals.append({'indicator': 'RSI', 'signal': 'BEARISH', 'strength': 0.10, 'value': rsi_value})
        
        # Stochastic
        stoch = self.calculate_stochastic(df)
        if stoch['k'].iloc[-1] > 80:
            signals.append({'indicator': 'Stochastic', 'signal': 'BEARISH', 'strength': 0.15})
        elif stoch['k'].iloc[-1] < 20:
            signals.append({'indicator': 'Stochastic', 'signal': 'BULLISH', 'strength': 0.15})
        
        # CCI
        cci = self.calculate_cci(df)
        if cci.iloc[-1] > 100:
            signals.append({'indicator': 'CCI', 'signal': 'BEARISH', 'strength': 0.10})
        elif cci.iloc[-1] < -100:
            signals.append({'indicator': 'CCI', 'signal': 'BULLISH', 'strength': 0.10})
        
        # Aggregate
        bullish_strength = sum(s['strength'] for s in signals if s['signal'] == 'BULLISH')
        bearish_strength = sum(s['strength'] for s in signals if s['signal'] == 'BEARISH')
        
        if bullish_strength > bearish_strength:
            overall_signal = 'BULLISH'
            confidence = bullish_strength
        elif bearish_strength > bullish_strength:
            overall_signal = 'BEARISH'
            confidence = bearish_strength
        else:
            overall_signal = 'NEUTRAL'
            confidence = 0.0
        
        return {
            'signal': overall_signal,
            'confidence': confidence,
            'indicators': signals
        }
    
    def get_volatility_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate volatility signal"""
        bb = self.calculate_bollinger_bands(df)
        atr = self.calculate_atr(df)
        
        current_price = df['Close'].iloc[-1]
        bb_position = (current_price - bb['lower'].iloc[-1]) / (bb['upper'].iloc[-1] - bb['lower'].iloc[-1])
        
        # ATR normalized
        atr_pct = (atr.iloc[-1] / current_price) * 100
        
        signals = []
        
        if bb_position > 0.8:
            signals.append({'indicator': 'BB', 'signal': 'BEARISH', 'strength': 0.10})
        elif bb_position < 0.2:
            signals.append({'indicator': 'BB', 'signal': 'BULLISH', 'strength': 0.10})
        
        volatility_level = 'NORMAL'
        if atr_pct > 1.5:
            volatility_level = 'HIGH'
        elif atr_pct < 0.5:
            volatility_level = 'LOW'
        
        bullish_strength = sum(s['strength'] for s in signals if s['signal'] == 'BULLISH')
        bearish_strength = sum(s['strength'] for s in signals if s['signal'] == 'BEARISH')
        
        if bullish_strength > bearish_strength:
            overall_signal = 'BULLISH'
        elif bearish_strength > bullish_strength:
            overall_signal = 'BEARISH'
        else:
            overall_signal = 'NEUTRAL'
        
        return {
            'signal': overall_signal,
            'confidence': max(bullish_strength, bearish_strength),
            'volatility': volatility_level,
            'atr_pct': atr_pct,
            'indicators': signals
        }
    
    def get_volume_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate volume signal"""
        obv = self.calculate_obv(df)
        vwap = self.calculate_vwap(df)
        mfi = self.calculate_mfi(df)
        
        signals = []
        
        # OBV trend
        obv_slope = (obv.iloc[-1] - obv.iloc[-5]) / 5
        if obv_slope > 0:
            signals.append({'indicator': 'OBV', 'signal': 'BULLISH', 'strength': 0.20})
        else:
            signals.append({'indicator': 'OBV', 'signal': 'BEARISH', 'strength': 0.20})
        
        # VWAP
        if df['Close'].iloc[-1] > vwap.iloc[-1]:
            signals.append({'indicator': 'VWAP', 'signal': 'BULLISH', 'strength': 0.20})
        else:
            signals.append({'indicator': 'VWAP', 'signal': 'BEARISH', 'strength': 0.20})
        
        # MFI
        mfi_value = mfi.iloc[-1]
        if mfi_value > 80:
            signals.append({'indicator': 'MFI', 'signal': 'BEARISH', 'strength': 0.15})
        elif mfi_value < 20:
            signals.append({'indicator': 'MFI', 'signal': 'BULLISH', 'strength': 0.15})
        
        bullish_strength = sum(s['strength'] for s in signals if s['signal'] == 'BULLISH')
        bearish_strength = sum(s['strength'] for s in signals if s['signal'] == 'BEARISH')
        
        if bullish_strength > bearish_strength:
            overall_signal = 'BULLISH'
            confidence = bullish_strength
        elif bearish_strength > bullish_strength:
            overall_signal = 'BEARISH'
            confidence = bearish_strength
        else:
            overall_signal = 'NEUTRAL'
            confidence = 0.0
        
        return {
            'signal': overall_signal,
            'confidence': confidence,
            'indicators': signals
        }
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all indicators and generate comprehensive analysis
        
        Returns:
            Dict with all indicator values and signals
        """
        try:
            return {
                # Trend
                'ema_fast': self.calculate_ema(df, self.config.EMA_FAST),
                'ema_slow': self.calculate_ema(df, self.config.EMA_SLOW),
                'macd': self.calculate_macd(df),
                'adx': self.calculate_adx(df),
                
                # Momentum
                'rsi': self.calculate_rsi(df),
                'stochastic': self.calculate_stochastic(df),
                'cci': self.calculate_cci(df),
                
                # Volatility
                'bollinger_bands': self.calculate_bollinger_bands(df),
                'atr': self.calculate_atr(df),
                
                # Volume
                'obv': self.calculate_obv(df),
                'vwap': self.calculate_vwap(df),
                'mfi': self.calculate_mfi(df),
                
                # Signals
                'trend_signal': self.get_trend_signal(df),
                'momentum_signal': self.get_momentum_signal(df),
                'volatility_signal': self.get_volatility_signal(df),
                'volume_signal': self.get_volume_signal(df),
            }
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {str(e)}", category="analysis")
            return {}


if __name__ == "__main__":
    # Test indicators
    print("📈 Testing Technical Indicators...")
    
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    np.random.seed(42)
    
    data = {
        'Open': np.random.uniform(1.08, 1.09, 200),
        'High': np.random.uniform(1.09, 1.10, 200),
        'Low': np.random.uniform(1.07, 1.08, 200),
        'Close': np.random.uniform(1.08, 1.09, 200),
        'Volume': np.random.randint(1000, 10000, 200),
    }
    df = pd.DataFrame(data, index=dates)
    
    indicators = TechnicalIndicators()
    
    # Test individual indicators
    print(f"✓ RSI: {indicators.calculate_rsi(df).iloc[-1]:.2f}")
    print(f"✓ ADX: {indicators.calculate_adx(df)['adx'].iloc[-1]:.2f}")
    print(f"✓ ATR: {indicators.calculate_atr(df).iloc[-1]:.5f}")
    
    # Test signals
    trend = indicators.get_trend_signal(df)
    print(f"✓ Trend Signal: {trend['signal']} ({trend['confidence']:.2f})")
    
    momentum = indicators.get_momentum_signal(df)
    print(f"✓ Momentum Signal: {momentum['signal']} ({momentum['confidence']:.2f})")
    
    # Test all indicators
    all_indicators = indicators.calculate_all_indicators(df)
    print(f"\n✓ Calculated {len(all_indicators)} indicator groups")
    
    print("\n✓ Technical indicators test completed")
