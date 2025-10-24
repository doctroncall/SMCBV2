"""
Confidence Scorer
Calculates confidence scores for sentiment predictions
"""
from typing import Dict, Any, List
import numpy as np


class ConfidenceScorer:
    """
    Calculate confidence scores for sentiment predictions
    
    Factors considered:
    - Signal strength
    - Agreement between indicators
    - Historical accuracy
    - Volatility conditions
    - Volume confirmation
    """
    
    def __init__(self):
        """Initialize confidence scorer"""
        self.base_confidence = 0.5
    
    def calculate_confidence(
        self,
        sentiment_data: Dict[str, Any],
        tech_signals: Dict[str, Any],
        smc_signals: Dict[str, Any]
    ) -> float:
        """
        Calculate overall confidence score (0-1)
        
        Args:
            sentiment_data: Aggregated sentiment data
            tech_signals: Technical indicator signals
            smc_signals: SMC analysis signals
            
        Returns:
            float: Confidence score between 0 and 1
        """
        scores = []
        
        # Factor 1: Raw signal strength
        raw_score = sentiment_data.get('raw_score', 0.0)
        scores.append(('raw_strength', min(raw_score, 1.0), 0.30))
        
        # Factor 2: Agreement between components
        agreement_score = self._calculate_agreement(sentiment_data)
        scores.append(('agreement', agreement_score, 0.25))
        
        # Factor 3: Signal clarity (not too many neutrals)
        clarity_score = self._calculate_clarity(sentiment_data)
        scores.append(('clarity', clarity_score, 0.20))
        
        # Factor 4: Volatility adjustment
        volatility_score = self._calculate_volatility_factor(tech_signals)
        scores.append(('volatility', volatility_score, 0.15))
        
        # Factor 5: Volume confirmation
        volume_score = self._calculate_volume_factor(tech_signals, sentiment_data)
        scores.append(('volume', volume_score, 0.10))
        
        # Calculate weighted average
        weighted_sum = sum(score * weight for _, score, weight in scores)
        total_weight = sum(weight for _, _, weight in scores)
        
        confidence = weighted_sum / total_weight if total_weight > 0 else 0.5
        
        # Ensure confidence is between 0 and 1
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
    
    def _calculate_agreement(self, sentiment_data: Dict[str, Any]) -> float:
        """
        Calculate agreement score between components
        
        Higher score when more components agree on the same direction
        """
        factors = sentiment_data.get('factors', [])
        
        if not factors:
            return 0.5
        
        sentiment = sentiment_data.get('sentiment', 'NEUTRAL')
        
        # Count agreeing and disagreeing factors
        agreeing = sum(1 for f in factors if f['signal'] == sentiment)
        total = len(factors)
        
        # Calculate agreement ratio
        agreement_ratio = agreeing / total if total > 0 else 0.5
        
        return agreement_ratio
    
    def _calculate_clarity(self, sentiment_data: Dict[str, Any]) -> float:
        """
        Calculate clarity score
        
        Higher score when signals are clearly directional (not neutral)
        """
        factors = sentiment_data.get('factors', [])
        
        if not factors:
            return 0.5
        
        # Count neutral signals
        neutral_count = sum(1 for f in factors if f['signal'] == 'NEUTRAL')
        total = len(factors)
        
        # Higher score with fewer neutral signals
        clarity = 1.0 - (neutral_count / total) if total > 0 else 0.5
        
        return clarity
    
    def _calculate_volatility_factor(self, tech_signals: Dict[str, Any]) -> float:
        """
        Calculate volatility factor
        
        Normal volatility = higher confidence
        High volatility = lower confidence
        Low volatility = moderate confidence
        """
        if 'volatility' not in tech_signals:
            return 0.7  # Default moderate confidence
        
        volatility = tech_signals['volatility']
        vol_level = volatility.get('volatility', 'NORMAL')
        
        if vol_level == 'NORMAL':
            return 0.9
        elif vol_level == 'LOW':
            return 0.7  # Low volatility can mean indecision
        else:  # HIGH
            return 0.5  # High volatility = less confidence
    
    def _calculate_volume_factor(
        self,
        tech_signals: Dict[str, Any],
        sentiment_data: Dict[str, Any]
    ) -> float:
        """
        Calculate volume confirmation factor
        
        Higher score when volume confirms the sentiment
        """
        if 'volume' not in tech_signals:
            return 0.6  # Neutral if no volume data
        
        volume_signal = tech_signals['volume'].get('signal', 'NEUTRAL')
        sentiment = sentiment_data.get('sentiment', 'NEUTRAL')
        
        if volume_signal == sentiment:
            return 1.0  # Volume confirms
        elif volume_signal == 'NEUTRAL':
            return 0.6  # Volume neutral
        else:
            return 0.3  # Volume diverges
    
    def calculate_signal_strength(self, factors: List[Dict[str, Any]]) -> float:
        """
        Calculate overall signal strength from contributing factors
        
        Args:
            factors: List of contributing factors
            
        Returns:
            float: Signal strength (0-1)
        """
        if not factors:
            return 0.0
        
        # Sum of all contributions
        total_contribution = sum(f.get('contribution', 0) for f in factors)
        
        # Normalize to 0-1 range
        strength = min(total_contribution, 1.0)
        
        return strength
    
    def get_confidence_label(self, confidence: float) -> str:
        """
        Get descriptive label for confidence level
        
        Args:
            confidence: Confidence score (0-1)
            
        Returns:
            str: Confidence label
        """
        if confidence >= 0.85:
            return "VERY HIGH"
        elif confidence >= 0.70:
            return "HIGH"
        elif confidence >= 0.55:
            return "MODERATE"
        elif confidence >= 0.40:
            return "LOW"
        else:
            return "VERY LOW"


if __name__ == "__main__":
    # Test confidence scorer
    print("📊 Testing Confidence Scorer...")
    
    scorer = ConfidenceScorer()
    
    # Test case 1: Strong bullish with agreement
    sentiment_data1 = {
        'sentiment': 'BULLISH',
        'raw_score': 0.75,
        'factors': [
            {'signal': 'BULLISH', 'contribution': 0.20},
            {'signal': 'BULLISH', 'contribution': 0.18},
            {'signal': 'BULLISH', 'contribution': 0.22},
            {'signal': 'BULLISH', 'contribution': 0.15},
        ]
    }
    
    tech_signals1 = {
        'volatility': {'volatility': 'NORMAL'},
        'volume': {'signal': 'BULLISH'}
    }
    
    smc_signals1 = {}
    
    confidence1 = scorer.calculate_confidence(sentiment_data1, tech_signals1, smc_signals1)
    print(f"\n✓ Test 1 (Strong Bullish):")
    print(f"   Confidence: {confidence1:.2%}")
    print(f"   Label: {scorer.get_confidence_label(confidence1)}")
    
    # Test case 2: Weak with disagreement
    sentiment_data2 = {
        'sentiment': 'BEARISH',
        'raw_score': 0.45,
        'factors': [
            {'signal': 'BEARISH', 'contribution': 0.15},
            {'signal': 'BULLISH', 'contribution': 0.12},
            {'signal': 'NEUTRAL', 'contribution': 0.10},
            {'signal': 'BEARISH', 'contribution': 0.08},
        ]
    }
    
    tech_signals2 = {
        'volatility': {'volatility': 'HIGH'},
        'volume': {'signal': 'NEUTRAL'}
    }
    
    smc_signals2 = {}
    
    confidence2 = scorer.calculate_confidence(sentiment_data2, tech_signals2, smc_signals2)
    print(f"\n✓ Test 2 (Weak Bearish):")
    print(f"   Confidence: {confidence2:.2%}")
    print(f"   Label: {scorer.get_confidence_label(confidence2)}")
    
    # Test signal strength
    strength = scorer.calculate_signal_strength(sentiment_data1['factors'])
    print(f"\n✓ Signal Strength:")
    print(f"   Test 1: {strength:.2%}")
    
    print("\n✓ Confidence scorer test completed")
