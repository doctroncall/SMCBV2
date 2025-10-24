"""
Sentiment Engine
Aggregates technical indicators and SMC analysis to generate market sentiment
"""
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from src.indicators.technical import TechnicalIndicators
from src.indicators.smc import SMCAnalyzer
from src.indicators.calculator import IndicatorCalculator
from .confidence_scorer import ConfidenceScorer
from .regime_detector import RegimeDetector  # v2.0
from config.settings import SentimentConfig, RegimeConfig  # v2.0
from src.utils.logger import get_logger

logger = get_logger()


class Sentiment(Enum):
    """Sentiment enumeration"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class RiskLevel(Enum):
    """Risk level enumeration"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SentimentEngine:
    """
    Market sentiment analysis engine
    
    Combines:
    - Technical indicators (trend, momentum, volatility, volume)
    - Smart Money Concepts (structure, order blocks, liquidity)
    - Multi-timeframe analysis
    - Confidence scoring
    
    Generates:
    - Primary sentiment (BULLISH/BEARISH/NEUTRAL)
    - Confidence score (0-100%)
    - Risk level assessment
    - Contributing factors
    - Actionable insights
    """
    
    def __init__(self):
        """Initialize sentiment engine"""
        self.tech_indicators = TechnicalIndicators()
        self.smc_analyzer = SMCAnalyzer()
        self.calculator = IndicatorCalculator()
        self.confidence_scorer = ConfidenceScorer()
        self.regime_detector = RegimeDetector()  # v2.0
        self.config = SentimentConfig
        self.regime_config = RegimeConfig  # v2.0
        self.logger = logger
    
    def analyze_sentiment(
        self,
        df: pd.DataFrame,
        symbol: str = "UNKNOWN",
        timeframe: str = "H1"
    ) -> Dict[str, Any]:
        """
        Analyze market sentiment for a single timeframe
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            timeframe: Timeframe string
            
        Returns:
            Dict with sentiment analysis
        """
        try:
            self.logger.info(f"Analyzing sentiment for {symbol} {timeframe}", category="analysis")
            
            # Get technical analysis
            tech_signals = self._analyze_technical(df)
            
            # Get SMC analysis
            smc_signals = self._analyze_smc(df)
            
            # v2.0: Get market regime analysis (if enabled)
            regime_data = None
            if self.regime_config.ENABLE_REGIME_DETECTION and self.regime_config.AUTO_DETECT_REGIME:
                try:
                    regime_data = self.regime_detector.detect_regime(
                        df, 
                        lookback=self.regime_config.REGIME_LOOKBACK_BARS
                    )
                    self.logger.info(
                        f"Regime detected: {regime_data['composite']['favorability']}", 
                        category="analysis"
                    )
                except Exception as e:
                    self.logger.warning(f"Regime detection failed: {str(e)}", category="analysis")
                    regime_data = None
            
            # Aggregate signals
            sentiment_data = self._aggregate_signals(tech_signals, smc_signals)
            
            # Calculate confidence
            confidence = self.confidence_scorer.calculate_confidence(
                sentiment_data,
                tech_signals,
                smc_signals
            )
            
            # v2.0: Adjust confidence based on regime favorability
            if regime_data and self.regime_config.USE_REGIME_POSITION_SIZING:
                favorability = regime_data['composite']['favorability']
                multiplier = self.regime_config.REGIME_SIZE_MULTIPLIERS.get(favorability, 1.0)
                confidence = confidence * multiplier
            
            # Determine risk level
            risk_level = self._assess_risk_level(
                sentiment_data,
                tech_signals,
                confidence
            )
            
            # Generate insights
            insights = self._generate_insights(
                sentiment_data,
                tech_signals,
                smc_signals,
                regime_data  # v2.0: Include regime in insights
            )
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'sentiment': sentiment_data['sentiment'],
                'confidence': confidence,
                'risk_level': risk_level,
                'factors': sentiment_data['factors'],
                'technical_signals': tech_signals,
                'smc_signals': smc_signals,
                'insights': insights,
                'price': df['Close'].iloc[-1],
                'timestamp': datetime.now(),
                'regime': regime_data  # v2.0: Include regime data
            }
            
            # v2.0: Check regime filtering
            if regime_data and self.regime_config.FILTER_BY_REGIME:
                favorability = regime_data['composite']['favorability']
                if favorability not in self.regime_config.ALLOWED_REGIMES:
                    result['regime_warning'] = f"⚠️ Current regime ({favorability}) is not in allowed trading regimes"
                    result['confidence'] = result['confidence'] * 0.5  # Reduce confidence if not in allowed regime
            
            self.logger.log_analysis(
                symbol,
                timeframe,
                sentiment_data['sentiment'],
                confidence
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}", category="analysis")
            return {
                'error': str(e),
                'sentiment': 'NEUTRAL',
                'confidence': 0.0
            }
    
    def _analyze_technical(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze technical indicators"""
        # Get all signals
        trend_signal = self.tech_indicators.get_trend_signal(df)
        momentum_signal = self.tech_indicators.get_momentum_signal(df)
        volatility_signal = self.tech_indicators.get_volatility_signal(df)
        volume_signal = self.tech_indicators.get_volume_signal(df)
        
        return {
            'trend': trend_signal,
            'momentum': momentum_signal,
            'volatility': volatility_signal,
            'volume': volume_signal
        }
    
    def _analyze_smc(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze Smart Money Concepts"""
        return self.smc_analyzer.analyze(df)
    
    def _aggregate_signals(
        self,
        tech_signals: Dict[str, Any],
        smc_signals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aggregate all signals into final sentiment
        
        Uses weighted scoring from configuration
        """
        scores = {
            'BULLISH': 0.0,
            'BEARISH': 0.0,
            'NEUTRAL': 0.0
        }
        
        factors = []
        
        # Technical signals with weights
        weights = {
            'trend': self.config.TREND_WEIGHT,
            'momentum': self.config.MOMENTUM_WEIGHT,
            'volatility': self.config.VOLATILITY_WEIGHT,
            'volume': self.config.VOLUME_WEIGHT
        }
        
        for component, weight in weights.items():
            if component in tech_signals:
                signal = tech_signals[component]
                signal_type = signal.get('signal', 'NEUTRAL')
                signal_confidence = signal.get('confidence', 0.0)
                
                scores[signal_type] += weight * signal_confidence
                
                factors.append({
                    'component': component.capitalize(),
                    'signal': signal_type,
                    'confidence': signal_confidence,
                    'weight': weight,
                    'contribution': weight * signal_confidence
                })
        
        # SMC signals
        if 'signal' in smc_signals:
            smc_signal = smc_signals['signal']
            signal_type = smc_signal.get('signal', 'NEUTRAL')
            signal_confidence = smc_signal.get('confidence', 0.0)
            weight = self.config.SMC_WEIGHT
            
            scores[signal_type] += weight * signal_confidence
            
            factors.append({
                'component': 'SMC Structure',
                'signal': signal_type,
                'confidence': signal_confidence,
                'weight': weight,
                'contribution': weight * signal_confidence
            })
        
        # Determine primary sentiment
        max_score = max(scores.values())
        
        if scores['BULLISH'] == max_score and scores['BULLISH'] >= self.config.BULLISH_THRESHOLD:
            sentiment = 'BULLISH'
        elif scores['BEARISH'] == max_score and scores['BEARISH'] >= self.config.BEARISH_THRESHOLD:
            sentiment = 'BEARISH'
        else:
            sentiment = 'NEUTRAL'
        
        return {
            'sentiment': sentiment,
            'scores': scores,
            'factors': factors,
            'raw_score': max_score
        }
    
    def _assess_risk_level(
        self,
        sentiment_data: Dict[str, Any],
        tech_signals: Dict[str, Any],
        confidence: float
    ) -> str:
        """Assess risk level based on various factors"""
        risk_factors = []
        
        # Low confidence = higher risk
        if confidence < 0.60:
            risk_factors.append('low_confidence')
        
        # High volatility = higher risk
        if 'volatility' in tech_signals:
            vol_level = tech_signals['volatility'].get('volatility', 'NORMAL')
            if vol_level == 'HIGH':
                risk_factors.append('high_volatility')
        
        # Conflicting signals = higher risk
        factors = sentiment_data.get('factors', [])
        bullish_count = sum(1 for f in factors if f['signal'] == 'BULLISH')
        bearish_count = sum(1 for f in factors if f['signal'] == 'BEARISH')
        
        if abs(bullish_count - bearish_count) <= 1:
            risk_factors.append('conflicting_signals')
        
        # Determine risk level
        if len(risk_factors) == 0:
            return 'LOW'
        elif len(risk_factors) <= 1:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _generate_insights(
        self,
        sentiment_data: Dict[str, Any],
        tech_signals: Dict[str, Any],
        smc_signals: Dict[str, Any],
        regime_data: Optional[Dict[str, Any]] = None  # v2.0
    ) -> List[str]:
        """Generate actionable insights"""
        insights = []
        
        sentiment = sentiment_data['sentiment']
        
        # v2.0: Regime-based insights (priority - shown first)
        if regime_data:
            composite = regime_data.get('composite', {})
            favorability = composite.get('favorability', 'UNKNOWN')
            
            if favorability == 'FAVORABLE':
                insights.append("✅ FAVORABLE market regime - ideal trading conditions")
            elif favorability == 'MODERATE':
                insights.append("⚠️ MODERATE market regime - trade with caution")
            elif favorability == 'CAUTIOUS':
                insights.append("⚠️ CAUTIOUS regime - consider reducing exposure")
            elif favorability == 'UNFAVORABLE':
                insights.append("🛑 UNFAVORABLE regime - avoid trading or use minimal size")
            
            # Trend regime insight
            trend = regime_data.get('trend', {})
            if trend.get('is_trending'):
                insights.append(f"Strong {trend.get('direction', '').lower()} trend detected (ADX: {trend.get('adx', 0):.1f})")
            else:
                insights.append("Market is ranging - trend-following strategies may struggle")
            
            # Volatility insight
            vol = regime_data.get('volatility', {})
            if vol.get('regime') in ['VERY_HIGH', 'HIGH']:
                insights.append(f"⚠️ {vol.get('regime').replace('_', ' ')} volatility - reduce position size")
            elif vol.get('regime') == 'VERY_LOW':
                insights.append("📊 Very low volatility - potential breakout ahead")
        
        # Market structure insight
        if 'market_structure' in smc_signals:
            structure = smc_signals['market_structure']
            if structure.get('trend') == sentiment:
                insights.append(f"Market structure confirms {sentiment.lower()} bias")
            else:
                insights.append(f"Market structure shows {structure.get('trend', 'NEUTRAL').lower()} bias, conflicting with {sentiment.lower()} sentiment")
        
        # Order block insight
        if 'order_blocks' in smc_signals:
            obs = smc_signals['order_blocks']
            active_obs = [ob for ob in obs if ob.active]
            if active_obs:
                ob_type = active_obs[0].type
                insights.append(f"Active {ob_type} order block at {active_obs[0].start_price:.5f}-{active_obs[0].end_price:.5f}")
        
        # Premium/discount insight
        if 'premium_discount' in smc_signals:
            pd = smc_signals['premium_discount']
            if pd.get('zone') == 'PREMIUM' and sentiment == 'BEARISH':
                insights.append("Price in premium zone - favorable for shorts")
            elif pd.get('zone') == 'DISCOUNT' and sentiment == 'BULLISH':
                insights.append("Price in discount zone - favorable for longs")
            elif pd.get('zone') == 'EQUILIBRIUM':
                insights.append("Price at equilibrium - waiting for direction")
        
        # Momentum insight
        if 'momentum' in tech_signals:
            momentum = tech_signals['momentum']
            rsi_indicator = next((i for i in momentum.get('indicators', []) if i['indicator'] == 'RSI'), None)
            if rsi_indicator:
                rsi_value = rsi_indicator.get('value')
                if rsi_value:
                    if rsi_value > 70:
                        insights.append(f"RSI overbought at {rsi_value:.1f} - watch for reversal")
                    elif rsi_value < 30:
                        insights.append(f"RSI oversold at {rsi_value:.1f} - watch for bounce")
        
        # Volume insight
        if 'volume' in tech_signals:
            volume = tech_signals['volume']
            if volume.get('signal') == sentiment:
                insights.append("Volume confirms price action")
            else:
                insights.append("Volume divergence detected - proceed with caution")
        
        return insights[:5]  # Return top 5 insights
    
    def get_sentiment_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable sentiment summary"""
        sentiment = analysis.get('sentiment', 'NEUTRAL')
        confidence = analysis.get('confidence', 0.0)
        risk = analysis.get('risk_level', 'MEDIUM')
        
        confidence_desc = "high" if confidence > 0.75 else "moderate" if confidence > 0.60 else "low"
        
        summary = (
            f"{sentiment} sentiment with {confidence_desc} confidence ({confidence:.0%}). "
            f"Risk level: {risk}."
        )
        
        # Add key insight
        insights = analysis.get('insights', [])
        if insights:
            summary += f" Key insight: {insights[0]}"
        
        return summary


if __name__ == "__main__":
    # Test sentiment engine
    print("🎯 Testing Sentiment Engine...")
    
    import numpy as np
    
    # Create sample data with bullish trend
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    np.random.seed(42)
    
    trend = np.linspace(1.08, 1.10, 200)
    noise = np.random.normal(0, 0.0005, 200)
    close = trend + noise
    
    data = {
        'Open': close - np.random.uniform(0, 0.0005, 200),
        'High': close + np.random.uniform(0, 0.001, 200),
        'Low': close - np.random.uniform(0, 0.001, 200),
        'Close': close,
        'Volume': np.random.randint(1000, 10000, 200),
    }
    df = pd.DataFrame(data, index=dates)
    
    # Test sentiment engine
    engine = SentimentEngine()
    
    result = engine.analyze_sentiment(df, "EURUSD", "H1")
    
    print(f"\n📊 Sentiment Analysis Results:")
    print(f"   Symbol: {result['symbol']}")
    print(f"   Timeframe: {result['timeframe']}")
    print(f"   Sentiment: {result['sentiment']}")
    print(f"   Confidence: {result['confidence']:.2%}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Price: {result['price']:.5f}")
    
    print(f"\n🎯 Contributing Factors:")
    for factor in result['factors'][:5]:
        print(f"   - {factor['component']}: {factor['signal']} (contribution: {factor['contribution']:.3f})")
    
    print(f"\n💡 Insights:")
    for insight in result['insights']:
        print(f"   - {insight}")
    
    print(f"\n📝 Summary:")
    summary = engine.get_sentiment_summary(result)
    print(f"   {summary}")
    
    print("\n✓ Sentiment engine test completed")
