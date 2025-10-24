"""
Multi-Timeframe Analyzer
Analyzes sentiment across multiple timeframes for confluence
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from .sentiment_engine import SentimentEngine
from config.settings import SentimentConfig
from src.utils.logger import get_logger

logger = get_logger()


class MultiTimeframeAnalyzer:
    """
    Analyze sentiment across multiple timeframes
    
    Features:
    - Multi-timeframe sentiment analysis
    - Timeframe alignment detection
    - Weighted confluence scoring
    - Dominant timeframe identification
    - Entry/exit timing suggestions
    """
    
    def __init__(self):
        """Initialize multi-timeframe analyzer"""
        self.sentiment_engine = SentimentEngine()
        self.config = SentimentConfig
        self.logger = logger
        
        # Timeframe weights from config
        self.timeframe_weights = self.config.MTF_WEIGHTS
    
    def analyze_multiple_timeframes(
        self,
        data_dict: Dict[str, pd.DataFrame],
        symbol: str
    ) -> Dict[str, Any]:
        """
        Analyze sentiment across multiple timeframes
        
        Args:
            data_dict: Dict mapping timeframe to DataFrame
            symbol: Trading symbol
            
        Returns:
            Dict with multi-timeframe analysis
        """
        try:
            self.logger.info(
                f"Performing multi-timeframe analysis for {symbol}",
                category="analysis"
            )
            
            # Analyze each timeframe
            tf_results = {}
            for timeframe, df in data_dict.items():
                if df is not None and not df.empty:
                    result = self.sentiment_engine.analyze_sentiment(df, symbol, timeframe)
                    tf_results[timeframe] = result
            
            if not tf_results:
                return {'error': 'No valid timeframe data'}
            
            # Calculate alignment
            alignment = self._calculate_alignment(tf_results)
            
            # Get dominant sentiment
            dominant = self._get_dominant_sentiment(tf_results)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(tf_results, alignment)
            
            # Generate trading suggestions
            suggestions = self._generate_suggestions(tf_results, alignment, dominant)
            
            return {
                'symbol': symbol,
                'timeframe_results': tf_results,
                'alignment': alignment,
                'dominant_sentiment': dominant,
                'overall_confidence': overall_confidence,
                'suggestions': suggestions,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error in multi-timeframe analysis: {str(e)}", category="analysis")
            return {'error': str(e)}
    
    def _calculate_alignment(self, tf_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate alignment across timeframes
        
        Returns alignment score and details
        """
        if not tf_results:
            return {'aligned': False, 'score': 0.0}
        
        sentiments = [r.get('sentiment', 'NEUTRAL') for r in tf_results.values()]
        
        # Count each sentiment
        bullish_count = sentiments.count('BULLISH')
        bearish_count = sentiments.count('BEARISH')
        neutral_count = sentiments.count('NEUTRAL')
        total = len(sentiments)
        
        # Calculate alignment score
        max_count = max(bullish_count, bearish_count, neutral_count)
        alignment_score = max_count / total if total > 0 else 0.0
        
        # Determine if aligned (>70% agreement)
        is_aligned = alignment_score >= 0.7
        
        # Identify aligned sentiment
        if bullish_count == max_count:
            aligned_sentiment = 'BULLISH'
        elif bearish_count == max_count:
            aligned_sentiment = 'BEARISH'
        else:
            aligned_sentiment = 'NEUTRAL'
        
        # Timeframe breakdown
        breakdown = {
            'BULLISH': bullish_count,
            'BEARISH': bearish_count,
            'NEUTRAL': neutral_count
        }
        
        return {
            'aligned': is_aligned,
            'score': alignment_score,
            'sentiment': aligned_sentiment,
            'breakdown': breakdown,
            'total_timeframes': total
        }
    
    def _get_dominant_sentiment(self, tf_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get dominant sentiment using weighted voting
        
        Higher timeframes have more weight
        """
        weighted_scores = {
            'BULLISH': 0.0,
            'BEARISH': 0.0,
            'NEUTRAL': 0.0
        }
        
        total_weight = 0.0
        
        for timeframe, result in tf_results.items():
            sentiment = result.get('sentiment', 'NEUTRAL')
            confidence = result.get('confidence', 0.0)
            weight = self.timeframe_weights.get(timeframe, 0.25)
            
            # Weighted vote
            weighted_scores[sentiment] += weight * confidence
            total_weight += weight
        
        # Normalize
        if total_weight > 0:
            for sentiment in weighted_scores:
                weighted_scores[sentiment] /= total_weight
        
        # Get dominant
        dominant_sentiment = max(weighted_scores, key=weighted_scores.get)
        dominant_score = weighted_scores[dominant_sentiment]
        
        return {
            'sentiment': dominant_sentiment,
            'score': dominant_score,
            'all_scores': weighted_scores
        }
    
    def _calculate_overall_confidence(
        self,
        tf_results: Dict[str, Dict[str, Any]],
        alignment: Dict[str, Any]
    ) -> float:
        """
        Calculate overall confidence considering all timeframes
        
        Factors:
        - Individual timeframe confidences
        - Alignment between timeframes
        - Higher timeframe weight
        """
        if not tf_results:
            return 0.0
        
        # Weighted average of individual confidences
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for timeframe, result in tf_results.items():
            confidence = result.get('confidence', 0.0)
            weight = self.timeframe_weights.get(timeframe, 0.25)
            
            weighted_confidence += confidence * weight
            total_weight += weight
        
        base_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.0
        
        # Bonus for alignment
        alignment_bonus = alignment['score'] * 0.15  # Up to 15% bonus
        
        # Final confidence
        overall_confidence = min(base_confidence + alignment_bonus, 1.0)
        
        return overall_confidence
    
    def _generate_suggestions(
        self,
        tf_results: Dict[str, Dict[str, Any]],
        alignment: Dict[str, Any],
        dominant: Dict[str, Any]
    ) -> List[str]:
        """Generate trading suggestions based on multi-timeframe analysis"""
        suggestions = []
        
        sentiment = dominant['sentiment']
        is_aligned = alignment['aligned']
        
        # Alignment-based suggestions
        if is_aligned and dominant['score'] > 0.70:
            suggestions.append(f"Strong {sentiment.lower()} confluence across all timeframes")
            if sentiment == 'BULLISH':
                suggestions.append("Consider long positions with higher timeframe confirmation")
            elif sentiment == 'BEARISH':
                suggestions.append("Consider short positions with higher timeframe confirmation")
        elif not is_aligned:
            suggestions.append("Mixed signals across timeframes - wait for clearer direction")
            suggestions.append("Consider reducing position size due to lack of confluence")
        
        # Higher timeframe check
        higher_tfs = ['D1', 'H4']
        higher_tf_sentiments = []
        
        for tf in higher_tfs:
            if tf in tf_results:
                higher_tf_sentiments.append(tf_results[tf].get('sentiment'))
        
        if higher_tf_sentiments and all(s == sentiment for s in higher_tf_sentiments):
            suggestions.append(f"Higher timeframes confirm {sentiment.lower()} bias")
        
        # Entry timing
        if 'M15' in tf_results or 'H1' in tf_results:
            lower_tf = tf_results.get('M15') or tf_results.get('H1')
            if lower_tf and lower_tf.get('sentiment') == sentiment:
                suggestions.append("Lower timeframe provides good entry timing")
        
        # Risk management
        risk_levels = [r.get('risk_level', 'MEDIUM') for r in tf_results.values()]
        if 'HIGH' in risk_levels:
            suggestions.append("High risk detected on some timeframes - use tight stops")
        
        return suggestions[:5]  # Return top 5
    
    def get_mtf_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable multi-timeframe summary"""
        if 'error' in analysis:
            return f"Error: {analysis['error']}"
        
        alignment = analysis.get('alignment', {})
        dominant = analysis.get('dominant_sentiment', {})
        confidence = analysis.get('overall_confidence', 0.0)
        
        summary = (
            f"{dominant.get('sentiment', 'NEUTRAL')} sentiment with {confidence:.0%} confidence. "
        )
        
        if alignment.get('aligned'):
            summary += f"All timeframes aligned ({alignment.get('score', 0):.0%} agreement). "
        else:
            summary += f"Mixed signals ({alignment.get('score', 0):.0%} agreement). "
        
        # Add key suggestion
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            summary += suggestions[0]
        
        return summary


if __name__ == "__main__":
    # Test multi-timeframe analyzer
    print("🔍 Testing Multi-Timeframe Analyzer...")
    
    import numpy as np
    
    # Create sample data for multiple timeframes
    def create_data(periods, trend_strength=1.0):
        dates = pd.date_range(start='2024-01-01', periods=periods, freq='1H')
        trend = np.linspace(1.08, 1.08 + (0.02 * trend_strength), periods)
        noise = np.random.normal(0, 0.0005, periods)
        close = trend + noise
        
        return pd.DataFrame({
            'Open': close - np.random.uniform(0, 0.0005, periods),
            'High': close + np.random.uniform(0, 0.001, periods),
            'Low': close - np.random.uniform(0, 0.001, periods),
            'Close': close,
            'Volume': np.random.randint(1000, 10000, periods),
        }, index=dates)
    
    # Create data for different timeframes
    np.random.seed(42)
    data_dict = {
        'M15': create_data(400, 0.8),
        'H1': create_data(200, 1.0),
        'H4': create_data(100, 1.2),
        'D1': create_data(50, 1.5),
    }
    
    # Test analyzer
    analyzer = MultiTimeframeAnalyzer()
    
    result = analyzer.analyze_multiple_timeframes(data_dict, "EURUSD")
    
    print(f"\n📊 Multi-Timeframe Analysis:")
    print(f"   Symbol: {result['symbol']}")
    print(f"   Dominant Sentiment: {result['dominant_sentiment']['sentiment']}")
    print(f"   Overall Confidence: {result['overall_confidence']:.2%}")
    
    print(f"\n🎯 Alignment:")
    alignment = result['alignment']
    print(f"   Aligned: {alignment['aligned']}")
    print(f"   Score: {alignment['score']:.2%}")
    print(f"   Breakdown: {alignment['breakdown']}")
    
    print(f"\n📋 Timeframe Results:")
    for tf, tf_result in result['timeframe_results'].items():
        print(f"   {tf}: {tf_result['sentiment']} ({tf_result['confidence']:.0%})")
    
    print(f"\n💡 Suggestions:")
    for suggestion in result['suggestions']:
        print(f"   - {suggestion}")
    
    print(f"\n📝 Summary:")
    summary = analyzer.get_mtf_summary(result)
    print(f"   {summary}")
    
    print("\n✓ Multi-timeframe analyzer test completed")
