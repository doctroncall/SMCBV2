"""
Indicator Calculator
Helper class for batch indicator calculations and caching
"""
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime

from .technical import TechnicalIndicators
from src.utils.logger import get_logger

logger = get_logger()


class IndicatorCalculator:
    """
    High-level indicator calculator with caching and batch operations
    
    Features:
    - Batch calculation across multiple timeframes
    - Result caching for performance
    - Indicator comparison across timeframes
    - Signal aggregation
    """
    
    def __init__(self):
        """Initialize calculator"""
        self.tech_indicators = TechnicalIndicators()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.logger = logger
    
    def calculate_for_timeframe(
        self,
        df: pd.DataFrame,
        symbol: str,
        timeframe: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate all indicators for a specific timeframe
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Symbol name
            timeframe: Timeframe string
            use_cache: Whether to use cached results
            
        Returns:
            Dict with all indicator results
        """
        cache_key = f"{symbol}_{timeframe}_{len(df)}"
        
        # Check cache
        if use_cache and cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            age = (datetime.now() - timestamp).total_seconds()
            if age < self.cache_ttl:
                self.logger.debug(f"Using cached indicators for {symbol} {timeframe}")
                return cached_data
        
        # Calculate indicators
        try:
            self.logger.info(f"Calculating indicators for {symbol} {timeframe}", category="analysis")
            
            results = self.tech_indicators.calculate_all_indicators(df)
            
            # Add metadata
            results['symbol'] = symbol
            results['timeframe'] = timeframe
            results['timestamp'] = datetime.now()
            results['bar_count'] = len(df)
            results['latest_close'] = df['Close'].iloc[-1]
            
            # Cache results
            self.cache[cache_key] = (results, datetime.now())
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators for {symbol} {timeframe}: {str(e)}", category="analysis")
            return {}
    
    def calculate_multi_timeframe(
        self,
        data_dict: Dict[str, pd.DataFrame],
        symbol: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calculate indicators for multiple timeframes
        
        Args:
            data_dict: Dict mapping timeframe to DataFrame
            symbol: Symbol name
            
        Returns:
            Dict mapping timeframe to indicator results
        """
        results = {}
        
        for timeframe, df in data_dict.items():
            if df is not None and not df.empty:
                results[timeframe] = self.calculate_for_timeframe(df, symbol, timeframe)
        
        return results
    
    def get_timeframe_alignment(
        self,
        mtf_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check alignment of signals across timeframes
        
        Args:
            mtf_results: Multi-timeframe indicator results
            
        Returns:
            Dict with alignment analysis
        """
        if not mtf_results:
            return {'aligned': False, 'alignment_score': 0.0}
        
        # Extract signals from each timeframe
        trend_signals = []
        momentum_signals = []
        
        for tf, results in mtf_results.items():
            if 'trend_signal' in results:
                trend_signals.append(results['trend_signal']['signal'])
            if 'momentum_signal' in results:
                momentum_signals.append(results['momentum_signal']['signal'])
        
        # Calculate alignment
        def signal_alignment(signals: List[str]) -> float:
            if not signals:
                return 0.0
            bullish = signals.count('BULLISH')
            bearish = signals.count('BEARISH')
            total = len(signals)
            return max(bullish, bearish) / total
        
        trend_alignment = signal_alignment(trend_signals)
        momentum_alignment = signal_alignment(momentum_signals)
        overall_alignment = (trend_alignment + momentum_alignment) / 2
        
        # Determine primary signal
        if trend_signals:
            primary_signal = max(set(trend_signals), key=trend_signals.count)
        else:
            primary_signal = 'NEUTRAL'
        
        return {
            'aligned': overall_alignment > 0.7,
            'alignment_score': overall_alignment,
            'trend_alignment': trend_alignment,
            'momentum_alignment': momentum_alignment,
            'primary_signal': primary_signal,
            'timeframes_analyzed': len(mtf_results)
        }
    
    def get_indicator_table(
        self,
        results: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Create a summary table of indicator values and signals
        
        Args:
            results: Indicator calculation results
            
        Returns:
            DataFrame with indicator summary
        """
        rows = []
        
        # RSI
        if 'rsi' in results:
            rsi_value = results['rsi'].iloc[-1]
            rsi_signal = 'BULLISH' if rsi_value < 30 else 'BEARISH' if rsi_value > 70 else 'NEUTRAL'
            rows.append({
                'Indicator': 'RSI(14)',
                'Value': f"{rsi_value:.2f}",
                'Signal': rsi_signal,
                'Strength': 8 if abs(rsi_value - 50) > 20 else 5
            })
        
        # MACD
        if 'macd' in results:
            macd_hist = results['macd']['histogram'].iloc[-1]
            macd_signal = 'BULLISH' if macd_hist > 0 else 'BEARISH'
            rows.append({
                'Indicator': 'MACD',
                'Value': f"{macd_hist:.5f}",
                'Signal': macd_signal,
                'Strength': 9 if abs(macd_hist) > 0.001 else 6
            })
        
        # ADX
        if 'adx' in results:
            adx_value = results['adx']['adx'].iloc[-1]
            plus_di = results['adx']['plus_di'].iloc[-1]
            minus_di = results['adx']['minus_di'].iloc[-1]
            adx_signal = 'BULLISH' if plus_di > minus_di else 'BEARISH'
            rows.append({
                'Indicator': 'ADX(14)',
                'Value': f"{adx_value:.2f}",
                'Signal': 'TRENDING' if adx_value > 25 else 'RANGING',
                'Strength': 7 if adx_value > 25 else 4
            })
        
        # Bollinger Bands
        if 'bollinger_bands' in results and 'latest_close' in results:
            bb = results['bollinger_bands']
            close = results['latest_close']
            upper = bb['upper'].iloc[-1]
            lower = bb['lower'].iloc[-1]
            
            bb_position = (close - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
            if bb_position > 0.8:
                bb_signal = 'BEARISH'
            elif bb_position < 0.2:
                bb_signal = 'BULLISH'
            else:
                bb_signal = 'NEUTRAL'
            
            rows.append({
                'Indicator': 'Bollinger Bands',
                'Value': f"{bb_position*100:.1f}%",
                'Signal': bb_signal,
                'Strength': 5
            })
        
        # Volume (OBV)
        if 'obv' in results:
            obv = results['obv']
            obv_slope = (obv.iloc[-1] - obv.iloc[-5]) / 5 if len(obv) >= 5 else 0
            obv_signal = 'BULLISH' if obv_slope > 0 else 'BEARISH'
            rows.append({
                'Indicator': 'OBV',
                'Value': f"{obv.iloc[-1]:.0f}",
                'Signal': obv_signal,
                'Strength': 8
            })
        
        return pd.DataFrame(rows)
    
    def clear_cache(self):
        """Clear indicator cache"""
        self.cache.clear()
        self.logger.debug("Indicator cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cached_items': len(self.cache),
            'cache_ttl_seconds': self.cache_ttl
        }


if __name__ == "__main__":
    # Test calculator
    print("🧮 Testing Indicator Calculator...")
    
    import numpy as np
    
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
    
    calculator = IndicatorCalculator()
    
    # Test single timeframe
    results = calculator.calculate_for_timeframe(df, "EURUSD", "H1")
    print(f"✓ Calculated indicators for H1: {len(results)} items")
    
    # Test indicator table
    table = calculator.get_indicator_table(results)
    print(f"\n✓ Indicator Table:")
    print(table.to_string(index=False))
    
    # Test multi-timeframe
    mtf_data = {
        'M15': df.iloc[::4],  # Resample
        'H1': df,
        'H4': df.iloc[::4],
    }
    mtf_results = calculator.calculate_multi_timeframe(mtf_data, "EURUSD")
    print(f"\n✓ Multi-timeframe: {len(mtf_results)} timeframes calculated")
    
    # Test alignment
    alignment = calculator.get_timeframe_alignment(mtf_results)
    print(f"✓ Alignment: {alignment['aligned']} (score: {alignment['alignment_score']:.2f})")
    
    # Cache stats
    stats = calculator.get_cache_stats()
    print(f"✓ Cache: {stats['cached_items']} items")
    
    print("\n✓ Calculator test completed")
