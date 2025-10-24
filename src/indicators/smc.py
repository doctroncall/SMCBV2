"""
Smart Money Concepts (SMC) Analyzer
Advanced market structure analysis using institutional trading concepts
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass

from config.settings import SMCConfig
from src.utils.logger import get_logger

logger = get_logger()


@dataclass
class SwingPoint:
    """Represents a swing high or swing low"""
    index: int
    price: float
    type: str  # 'high' or 'low'
    timestamp: datetime


@dataclass
class OrderBlock:
    """Represents an order block"""
    start_price: float
    end_price: float
    timestamp: datetime
    type: str  # 'bullish' or 'bearish'
    strength: float
    tested: int = 0
    active: bool = True


@dataclass
class FairValueGap:
    """Represents a Fair Value Gap (imbalance)"""
    start_price: float
    end_price: float
    timestamp: datetime
    filled_percentage: float = 0.0
    active: bool = True


@dataclass
class LiquidityZone:
    """Represents a liquidity pool"""
    price: float
    type: str  # 'resistance' or 'support'
    strength: float
    touches: int


class SMCAnalyzer:
    """
    Smart Money Concepts analyzer for institutional trading patterns
    
    Features:
    - Market structure analysis (BOS, ChOCh)
    - Order block identification
    - Fair Value Gap detection
    - Liquidity pool analysis
    - Supply & Demand zones
    - Premium/Discount analysis
    """
    
    def __init__(self):
        """Initialize SMC analyzer"""
        self.config = SMCConfig
        self.logger = logger
        
        # Cache for swing points
        self._swing_cache = {}
    
    # ==================== Market Structure ====================
    
    def identify_swing_points(
        self,
        df: pd.DataFrame,
        lookback_left: Optional[int] = None,
        lookback_right: Optional[int] = None
    ) -> Dict[str, List[SwingPoint]]:
        """
        Identify swing highs and swing lows
        
        Args:
            df: DataFrame with OHLCV data
            lookback_left: Bars to look back
            lookback_right: Bars to look forward
            
        Returns:
            Dict with 'highs' and 'lows' lists
        """
        lookback_left = lookback_left or self.config.SWING_LOOKBACK
        lookback_right = lookback_right or self.config.SWING_LOOKBACK
        
        swing_highs = []
        swing_lows = []
        
        for i in range(lookback_left, len(df) - lookback_right):
            # Check for swing high
            current_high = df['High'].iloc[i]
            is_swing_high = True
            
            for j in range(i - lookback_left, i + lookback_right + 1):
                if j != i and df['High'].iloc[j] >= current_high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.append(SwingPoint(
                    index=i,
                    price=current_high,
                    type='high',
                    timestamp=df.index[i]
                ))
            
            # Check for swing low
            current_low = df['Low'].iloc[i]
            is_swing_low = True
            
            for j in range(i - lookback_left, i + lookback_right + 1):
                if j != i and df['Low'].iloc[j] <= current_low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.append(SwingPoint(
                    index=i,
                    price=current_low,
                    type='low',
                    timestamp=df.index[i]
                ))
        
        return {
            'highs': swing_highs,
            'lows': swing_lows
        }
    
    def detect_market_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect market structure (Higher Highs/Higher Lows vs Lower Highs/Lower Lows)
        
        Returns:
            Dict with market structure analysis
        """
        swings = self.identify_swing_points(df)
        
        if len(swings['highs']) < 2 or len(swings['lows']) < 2:
            return {
                'trend': 'UNDEFINED',
                'structure': 'INSUFFICIENT_DATA',
                'swing_highs': [],
                'swing_lows': []
            }
        
        # Analyze highs
        recent_highs = swings['highs'][-3:]
        higher_highs = sum(1 for i in range(1, len(recent_highs)) 
                          if recent_highs[i].price > recent_highs[i-1].price)
        
        # Analyze lows
        recent_lows = swings['lows'][-3:]
        higher_lows = sum(1 for i in range(1, len(recent_lows)) 
                         if recent_lows[i].price > recent_lows[i-1].price)
        
        # Determine structure
        if higher_highs >= 2 and higher_lows >= 2:
            trend = 'BULLISH'
            structure = 'HIGHER_HIGHS_HIGHER_LOWS'
        elif higher_highs == 0 and higher_lows == 0:
            trend = 'BEARISH'
            structure = 'LOWER_HIGHS_LOWER_LOWS'
        else:
            trend = 'NEUTRAL'
            structure = 'CONSOLIDATION'
        
        return {
            'trend': trend,
            'structure': structure,
            'swing_highs': swings['highs'],
            'swing_lows': swings['lows'],
            'latest_swing_high': swings['highs'][-1] if swings['highs'] else None,
            'latest_swing_low': swings['lows'][-1] if swings['lows'] else None,
        }
    
    def detect_bos_choch(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect Break of Structure (BOS) and Change of Character (ChOCh)
        
        Returns:
            Dict with BOS and ChOCh events
        """
        structure = self.detect_market_structure(df)
        
        bos_events = []
        choch_events = []
        
        swings = structure['swing_highs'] + structure['swing_lows']
        swings.sort(key=lambda x: x.index)
        
        for i in range(1, len(swings)):
            prev_swing = swings[i-1]
            curr_swing = swings[i]
            
            # BOS: Breaking recent high in uptrend or low in downtrend
            if structure['trend'] == 'BULLISH' and curr_swing.type == 'high':
                if curr_swing.price > prev_swing.price:
                    bos_events.append({
                        'type': 'BOS',
                        'direction': 'BULLISH',
                        'price': curr_swing.price,
                        'timestamp': curr_swing.timestamp
                    })
            
            elif structure['trend'] == 'BEARISH' and curr_swing.type == 'low':
                if curr_swing.price < prev_swing.price:
                    bos_events.append({
                        'type': 'BOS',
                        'direction': 'BEARISH',
                        'price': curr_swing.price,
                        'timestamp': curr_swing.timestamp
                    })
            
            # ChOCh: Reversal pattern
            if i >= 2:
                if curr_swing.type != prev_swing.type:
                    choch_events.append({
                        'type': 'ChOCh',
                        'from': prev_swing.type,
                        'to': curr_swing.type,
                        'price': curr_swing.price,
                        'timestamp': curr_swing.timestamp
                    })
        
        return {
            'bos': bos_events[-5:] if bos_events else [],
            'choch': choch_events[-5:] if choch_events else [],
            'latest_bos': bos_events[-1] if bos_events else None,
            'latest_choch': choch_events[-1] if choch_events else None,
        }
    
    # ==================== Order Blocks ====================
    
    def identify_order_blocks(self, df: pd.DataFrame) -> List[OrderBlock]:
        """
        Identify bullish and bearish order blocks
        
        Returns:
            List of OrderBlock objects
        """
        order_blocks = []
        
        for i in range(2, len(df) - 1):
            current = df.iloc[i]
            next_candle = df.iloc[i + 1]
            
            # Bullish order block: Down candle followed by strong up move
            if (current['Close'] < current['Open'] and  # Down candle
                next_candle['Close'] > next_candle['Open'] and  # Up candle
                (next_candle['Close'] - next_candle['Open']) > 
                (current['Open'] - current['Close']) * 1.5):  # Strong move
                
                # Check body percentage
                body_pct = abs(current['Close'] - current['Open']) / (current['High'] - current['Low'])
                
                if body_pct >= self.config.OB_MIN_BODY_PERCENTAGE:
                    # Check volume if available
                    volume_strength = 1.0
                    if i > 5:
                        avg_volume = df['Volume'].iloc[i-5:i].mean()
                        if current['Volume'] > avg_volume * self.config.OB_MIN_VOLUME_MULTIPLIER:
                            volume_strength = 1.5
                    
                    order_blocks.append(OrderBlock(
                        start_price=min(current['Open'], current['Close']),
                        end_price=max(current['Open'], current['Close']),
                        timestamp=df.index[i],
                        type='bullish',
                        strength=0.8 * volume_strength,
                        tested=0,
                        active=True
                    ))
            
            # Bearish order block: Up candle followed by strong down move
            elif (current['Close'] > current['Open'] and  # Up candle
                  next_candle['Close'] < next_candle['Open'] and  # Down candle
                  (next_candle['Open'] - next_candle['Close']) > 
                  (current['Close'] - current['Open']) * 1.5):  # Strong move
                
                body_pct = abs(current['Close'] - current['Open']) / (current['High'] - current['Low'])
                
                if body_pct >= self.config.OB_MIN_BODY_PERCENTAGE:
                    volume_strength = 1.0
                    if i > 5:
                        avg_volume = df['Volume'].iloc[i-5:i].mean()
                        if current['Volume'] > avg_volume * self.config.OB_MIN_VOLUME_MULTIPLIER:
                            volume_strength = 1.5
                    
                    order_blocks.append(OrderBlock(
                        start_price=min(current['Open'], current['Close']),
                        end_price=max(current['Open'], current['Close']),
                        timestamp=df.index[i],
                        type='bearish',
                        strength=0.8 * volume_strength,
                        tested=0,
                        active=True
                    ))
        
        # Keep only most recent and untested order blocks
        return sorted(order_blocks, key=lambda x: x.timestamp, reverse=True)[:10]
    
    # ==================== Fair Value Gaps ====================
    
    def identify_fvg(self, df: pd.DataFrame) -> List[FairValueGap]:
        """
        Identify Fair Value Gaps (imbalances)
        
        Returns:
            List of FairValueGap objects
        """
        fvgs = []
        
        for i in range(1, len(df) - 1):
            prev_candle = df.iloc[i - 1]
            current = df.iloc[i]
            next_candle = df.iloc[i + 1]
            
            # Bullish FVG: Gap between prev low and next high
            if current['Low'] > prev_candle['High'] and current['Low'] > next_candle['High']:
                gap_size = current['Low'] - max(prev_candle['High'], next_candle['High'])
                
                if gap_size > 0:  # Positive gap
                    fvgs.append(FairValueGap(
                        start_price=max(prev_candle['High'], next_candle['High']),
                        end_price=current['Low'],
                        timestamp=df.index[i],
                        filled_percentage=0.0,
                        active=True
                    ))
            
            # Bearish FVG: Gap between prev high and next low
            elif current['High'] < prev_candle['Low'] and current['High'] < next_candle['Low']:
                gap_size = min(prev_candle['Low'], next_candle['Low']) - current['High']
                
                if gap_size > 0:  # Positive gap
                    fvgs.append(FairValueGap(
                        start_price=current['High'],
                        end_price=min(prev_candle['Low'], next_candle['Low']),
                        timestamp=df.index[i],
                        filled_percentage=0.0,
                        active=True
                    ))
        
        # Check which FVGs have been filled
        current_price = df['Close'].iloc[-1]
        for fvg in fvgs:
            if fvg.start_price < current_price < fvg.end_price:
                # Calculate fill percentage
                fvg.filled_percentage = abs(current_price - fvg.start_price) / abs(fvg.end_price - fvg.start_price)
            elif current_price >= fvg.end_price or current_price <= fvg.start_price:
                fvg.filled_percentage = 1.0
                fvg.active = False
        
        return sorted(fvgs, key=lambda x: x.timestamp, reverse=True)[:10]
    
    # ==================== Liquidity Analysis ====================
    
    def identify_liquidity_zones(self, df: pd.DataFrame) -> List[LiquidityZone]:
        """
        Identify liquidity pools (equal highs/lows)
        
        Returns:
            List of LiquidityZone objects
        """
        swings = self.identify_swing_points(df)
        liquidity_zones = []
        
        # Find equal highs (resistance)
        highs = swings['highs']
        for i in range(len(highs) - 1):
            for j in range(i + 1, len(highs)):
                price_diff = abs(highs[i].price - highs[j].price)
                avg_price = (highs[i].price + highs[j].price) / 2
                
                # If prices are within small tolerance (equal highs)
                if price_diff / avg_price < 0.001:  # 0.1% tolerance
                    # Count touches at this level
                    touches = sum(1 for h in highs if abs(h.price - avg_price) / avg_price < 0.001)
                    
                    if touches >= self.config.LIQUIDITY_MIN_TOUCHES:
                        liquidity_zones.append(LiquidityZone(
                            price=avg_price,
                            type='resistance',
                            strength=min(touches / 5.0, 1.0),
                            touches=touches
                        ))
                    break
        
        # Find equal lows (support)
        lows = swings['lows']
        for i in range(len(lows) - 1):
            for j in range(i + 1, len(lows)):
                price_diff = abs(lows[i].price - lows[j].price)
                avg_price = (lows[i].price + lows[j].price) / 2
                
                if price_diff / avg_price < 0.001:
                    touches = sum(1 for l in lows if abs(l.price - avg_price) / avg_price < 0.001)
                    
                    if touches >= self.config.LIQUIDITY_MIN_TOUCHES:
                        liquidity_zones.append(LiquidityZone(
                            price=avg_price,
                            type='support',
                            strength=min(touches / 5.0, 1.0),
                            touches=touches
                        ))
                    break
        
        return liquidity_zones
    
    def detect_stop_hunts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect potential stop hunts (wicks through liquidity)
        
        Returns:
            List of stop hunt events
        """
        stop_hunts = []
        liquidity_zones = self.identify_liquidity_zones(df)
        
        for i in range(len(df)):
            candle = df.iloc[i]
            
            # Check for wick through resistance (bearish stop hunt)
            for zone in liquidity_zones:
                if zone.type == 'resistance':
                    if (candle['High'] > zone.price and 
                        candle['Close'] < zone.price and
                        (candle['High'] - candle['Close']) / (candle['High'] - candle['Low']) > 0.6):
                        
                        stop_hunts.append({
                            'type': 'bearish_stop_hunt',
                            'price': zone.price,
                            'wick_high': candle['High'],
                            'close': candle['Close'],
                            'timestamp': df.index[i]
                        })
                
                # Check for wick through support (bullish stop hunt)
                elif zone.type == 'support':
                    if (candle['Low'] < zone.price and 
                        candle['Close'] > zone.price and
                        (candle['Close'] - candle['Low']) / (candle['High'] - candle['Low']) > 0.6):
                        
                        stop_hunts.append({
                            'type': 'bullish_stop_hunt',
                            'price': zone.price,
                            'wick_low': candle['Low'],
                            'close': candle['Close'],
                            'timestamp': df.index[i]
                        })
        
        return stop_hunts[-5:]  # Return last 5
    
    # ==================== Premium/Discount Analysis ====================
    
    def calculate_premium_discount(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate premium/discount zones using Fibonacci
        
        Returns:
            Dict with premium/discount analysis
        """
        # Get swing high and low for range
        swings = self.identify_swing_points(df)
        
        if not swings['highs'] or not swings['lows']:
            return {'status': 'insufficient_data'}
        
        swing_high = max(swings['highs'], key=lambda x: x.price).price
        swing_low = min(swings['lows'], key=lambda x: x.price).price
        
        range_size = swing_high - swing_low
        current_price = df['Close'].iloc[-1]
        
        # Calculate Fibonacci levels
        levels = {
            'high': swing_high,
            'premium_high': swing_high - (range_size * 0.236),  # 76.4%
            'premium_low': swing_high - (range_size * 0.382),   # 61.8%
            'equilibrium': swing_high - (range_size * 0.5),     # 50%
            'discount_high': swing_high - (range_size * 0.618), # 38.2%
            'discount_low': swing_high - (range_size * 0.764),  # 23.6%
            'low': swing_low
        }
        
        # Determine current zone
        if current_price > levels['premium_low']:
            zone = 'PREMIUM'
            sentiment = 'BEARISH'
        elif current_price < levels['discount_high']:
            zone = 'DISCOUNT'
            sentiment = 'BULLISH'
        else:
            zone = 'EQUILIBRIUM'
            sentiment = 'NEUTRAL'
        
        # Calculate position percentage
        position = (current_price - swing_low) / range_size if range_size > 0 else 0.5
        
        return {
            'zone': zone,
            'sentiment': sentiment,
            'position': position,
            'levels': levels,
            'current_price': current_price,
            'swing_high': swing_high,
            'swing_low': swing_low
        }
    
    # ==================== Comprehensive SMC Analysis ====================
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive SMC analysis
        
        Returns:
            Dict with all SMC analysis results
        """
        try:
            self.logger.info("Performing SMC analysis", category="analysis")
            
            # Market structure
            market_structure = self.detect_market_structure(df)
            bos_choch = self.detect_bos_choch(df)
            
            # Order blocks and FVGs
            order_blocks = self.identify_order_blocks(df)
            fvgs = self.identify_fvg(df)
            
            # Liquidity
            liquidity_zones = self.identify_liquidity_zones(df)
            stop_hunts = self.detect_stop_hunts(df)
            
            # Premium/Discount
            premium_discount = self.calculate_premium_discount(df)
            
            # Generate overall signal
            smc_signal = self._generate_smc_signal(
                market_structure,
                order_blocks,
                fvgs,
                liquidity_zones,
                premium_discount
            )
            
            return {
                'market_structure': market_structure,
                'bos_choch': bos_choch,
                'order_blocks': order_blocks,
                'fair_value_gaps': fvgs,
                'liquidity_zones': liquidity_zones,
                'stop_hunts': stop_hunts,
                'premium_discount': premium_discount,
                'signal': smc_signal,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error in SMC analysis: {str(e)}", category="analysis")
            return {'error': str(e)}
    
    def _generate_smc_signal(
        self,
        structure: Dict,
        order_blocks: List,
        fvgs: List,
        liquidity: List,
        premium_discount: Dict
    ) -> Dict[str, Any]:
        """Generate overall SMC signal"""
        signals = []
        
        # Market structure signal
        if structure['trend'] == 'BULLISH':
            signals.append(('structure', 'BULLISH', 0.25))
        elif structure['trend'] == 'BEARISH':
            signals.append(('structure', 'BEARISH', 0.25))
        
        # Order block signal
        active_bullish_obs = [ob for ob in order_blocks if ob.type == 'bullish' and ob.active]
        active_bearish_obs = [ob for ob in order_blocks if ob.type == 'bearish' and ob.active]
        
        if len(active_bullish_obs) > len(active_bearish_obs):
            signals.append(('order_blocks', 'BULLISH', 0.20))
        elif len(active_bearish_obs) > len(active_bullish_obs):
            signals.append(('order_blocks', 'BEARISH', 0.20))
        
        # Premium/Discount signal
        if premium_discount.get('zone') == 'DISCOUNT':
            signals.append(('premium_discount', 'BULLISH', 0.20))
        elif premium_discount.get('zone') == 'PREMIUM':
            signals.append(('premium_discount', 'BEARISH', 0.20))
        
        # Aggregate
        bullish_strength = sum(weight for _, signal, weight in signals if signal == 'BULLISH')
        bearish_strength = sum(weight for _, signal, weight in signals if signal == 'BEARISH')
        
        if bullish_strength > bearish_strength:
            overall = 'BULLISH'
            confidence = bullish_strength
        elif bearish_strength > bullish_strength:
            overall = 'BEARISH'
            confidence = bearish_strength
        else:
            overall = 'NEUTRAL'
            confidence = 0.0
        
        return {
            'signal': overall,
            'confidence': confidence,
            'components': signals
        }


if __name__ == "__main__":
    # Test SMC analyzer
    print("🧠 Testing SMC Analyzer...")
    
    # Create sample trending data
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    np.random.seed(42)
    
    # Create uptrend
    trend = np.linspace(1.08, 1.10, 200)
    noise = np.random.normal(0, 0.001, 200)
    close = trend + noise
    
    data = {
        'Open': close - np.random.uniform(0, 0.001, 200),
        'High': close + np.random.uniform(0, 0.002, 200),
        'Low': close - np.random.uniform(0, 0.002, 200),
        'Close': close,
        'Volume': np.random.randint(1000, 10000, 200),
    }
    df = pd.DataFrame(data, index=dates)
    
    smc = SMCAnalyzer()
    
    # Test components
    print("\n📊 Market Structure:")
    structure = smc.detect_market_structure(df)
    print(f"   Trend: {structure['trend']}")
    print(f"   Structure: {structure['structure']}")
    print(f"   Swing Highs: {len(structure['swing_highs'])}")
    print(f"   Swing Lows: {len(structure['swing_lows'])}")
    
    print("\n📦 Order Blocks:")
    obs = smc.identify_order_blocks(df)
    print(f"   Found: {len(obs)} order blocks")
    for ob in obs[:3]:
        print(f"   - {ob.type.upper()}: {ob.start_price:.5f}-{ob.end_price:.5f} (strength: {ob.strength:.2f})")
    
    print("\n📊 Fair Value Gaps:")
    fvgs = smc.identify_fvg(df)
    print(f"   Found: {len(fvgs)} FVGs")
    for fvg in fvgs[:3]:
        print(f"   - {fvg.start_price:.5f}-{fvg.end_price:.5f} (filled: {fvg.filled_percentage*100:.1f}%)")
    
    print("\n💧 Liquidity Zones:")
    liquidity = smc.identify_liquidity_zones(df)
    print(f"   Found: {len(liquidity)} zones")
    for zone in liquidity[:3]:
        print(f"   - {zone.type.upper()}: {zone.price:.5f} (touches: {zone.touches})")
    
    print("\n📏 Premium/Discount:")
    pd_analysis = smc.calculate_premium_discount(df)
    print(f"   Zone: {pd_analysis.get('zone', 'N/A')}")
    print(f"   Sentiment: {pd_analysis.get('sentiment', 'N/A')}")
    print(f"   Position: {pd_analysis.get('position', 0)*100:.1f}%")
    
    print("\n🎯 Complete Analysis:")
    analysis = smc.analyze(df)
    if 'signal' in analysis:
        print(f"   Signal: {analysis['signal']['signal']}")
        print(f"   Confidence: {analysis['signal']['confidence']:.2f}")
    
    print("\n✓ SMC Analyzer test completed")
