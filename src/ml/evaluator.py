"""
Model Evaluator
Evaluates model performance and calculates metrics
"""
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.utils.logger import get_logger

logger = get_logger()


class ModelEvaluator:
    """
    Evaluate ML model performance
    
    Metrics:
    - Accuracy, precision, recall, F1
    - Confusion matrix
    - Performance by confidence level
    - Performance by market condition
    """
    
    def __init__(self):
        """Initialize evaluator"""
        self.logger = logger
    
    def evaluate_model(
        self,
        model,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        scaler=None
    ) -> Dict[str, Any]:
        """
        Evaluate model performance
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            scaler: Feature scaler (optional)
            
        Returns:
            Dict with evaluation metrics
        """
        try:
            # Scale if scaler provided
            if scaler:
                X_test_scaled = scaler.transform(X_test)
            else:
                X_test_scaled = X_test
            
            # Predictions
            y_pred = model.predict(X_test_scaled)
            y_proba = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, 'predict_proba') else None
            
            # Basic metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='binary', zero_division=0)
            recall = recall_score(y_test, y_pred, average='binary', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            
            # Classification report
            report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
            
            result = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'confusion_matrix': cm.tolist(),
                'classification_report': report,
                'test_samples': len(y_test)
            }
            
            # Performance by confidence
            if y_proba is not None:
                confidence_analysis = self._analyze_by_confidence(y_test, y_pred, y_proba)
                result['confidence_analysis'] = confidence_analysis
            
            self.logger.info(
                f"Model evaluated: {accuracy:.2%} accuracy on {len(y_test)} samples",
                category="ml_training"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {str(e)}", category="ml_training")
            return {'error': str(e)}
    
    def _analyze_by_confidence(
        self,
        y_true: pd.Series,
        y_pred: pd.Series,
        y_proba: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze performance by confidence level"""
        results = {}
        
        confidence_bins = [
            (0.0, 0.6, 'low'),
            (0.6, 0.8, 'medium'),
            (0.8, 1.0, 'high')
        ]
        
        for min_conf, max_conf, label in confidence_bins:
            mask = (y_proba >= min_conf) & (y_proba < max_conf)
            
            if mask.sum() > 0:
                accuracy = accuracy_score(y_true[mask], y_pred[mask])
                count = mask.sum()
                
                results[label] = {
                    'accuracy': accuracy,
                    'count': int(count),
                    'percentage': float(count / len(y_true))
                }
        
        return results
    
    def calculate_prediction_stats(
        self,
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate statistics from prediction history
        
        Args:
            predictions: List of prediction dicts with 'was_correct' field
            
        Returns:
            Dict with statistics
        """
        if not predictions:
            return {'total': 0, 'correct': 0, 'incorrect': 0, 'accuracy': 0.0}
        
        verified = [p for p in predictions if p.get('is_verified', False)]
        
        if not verified:
            return {'total': 0, 'correct': 0, 'incorrect': 0, 'accuracy': 0.0}
        
        total = len(verified)
        correct = sum(1 for p in verified if p.get('was_correct', False))
        incorrect = total - correct
        accuracy = correct / total if total > 0 else 0.0
        
        # Average confidence
        avg_confidence = np.mean([p.get('confidence', 0.0) for p in verified])
        
        # Sentiment breakdown
        bullish = sum(1 for p in verified if p.get('sentiment') == 'BULLISH')
        bearish = sum(1 for p in verified if p.get('sentiment') == 'BEARISH')
        neutral = sum(1 for p in verified if p.get('sentiment') == 'NEUTRAL')
        
        return {
            'total': total,
            'correct': correct,
            'incorrect': incorrect,
            'accuracy': accuracy,
            'avg_confidence': avg_confidence,
            'bullish_count': bullish,
            'bearish_count': bearish,
            'neutral_count': neutral
        }
    
    def calculate_accuracy_trend(
        self,
        predictions: List[Dict[str, Any]],
        window_days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Calculate accuracy trend over time
        
        Args:
            predictions: List of predictions
            window_days: Rolling window in days
            
        Returns:
            List of trend data points
        """
        if not predictions:
            return []
        
        # Sort by timestamp
        sorted_preds = sorted(predictions, key=lambda x: x.get('timestamp', datetime.min))
        
        # Group by day
        daily_stats = {}
        
        for pred in sorted_preds:
            if not pred.get('is_verified'):
                continue
            
            date = pred.get('timestamp', datetime.now()).date()
            
            if date not in daily_stats:
                daily_stats[date] = {'correct': 0, 'total': 0}
            
            daily_stats[date]['total'] += 1
            if pred.get('was_correct', False):
                daily_stats[date]['correct'] += 1
        
        # Calculate rolling accuracy
        trend = []
        dates = sorted(daily_stats.keys())
        
        for date in dates:
            window_start = date - timedelta(days=window_days)
            window_dates = [d for d in dates if window_start <= d <= date]
            
            window_correct = sum(daily_stats[d]['correct'] for d in window_dates)
            window_total = sum(daily_stats[d]['total'] for d in window_dates)
            
            if window_total > 0:
                accuracy = window_correct / window_total
                trend.append({
                    'date': date,
                    'accuracy': accuracy,
                    'correct': window_correct,
                    'total': window_total
                })
        
        return trend


if __name__ == "__main__":
    # Test evaluator
    print("📊 Testing Model Evaluator...")
    
    evaluator = ModelEvaluator()
    
    # Create sample predictions
    y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0, 1, 1])
    y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0, 1, 1])
    
    # Mock model
    class MockModel:
        def predict(self, X):
            return y_pred
        
        def predict_proba(self, X):
            return np.column_stack([1 - y_pred, y_pred])
    
    model = MockModel()
    X_test = np.random.rand(10, 5)
    
    # Evaluate
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_test_scaled = scaler.fit_transform(X_test)
    
    result = evaluator.evaluate_model(model, X_test, pd.Series(y_true), scaler)
    
    print(f"✓ Evaluation complete:")
    print(f"   Accuracy: {result['accuracy']:.2%}")
    print(f"   Precision: {result['precision']:.2%}")
    print(f"   Recall: {result['recall']:.2%}")
    print(f"   F1 Score: {result['f1_score']:.2%}")
    
    print("\n✓ Model evaluator test completed")
