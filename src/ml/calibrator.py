"""
Probability Calibration
Calibrates model prediction probabilities for better confidence scores
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import brier_score_loss, log_loss
import matplotlib.pyplot as plt

from src.utils.logger import get_logger

logger = get_logger()


class ProbabilityCalibrator:
    """
    Calibrate prediction probabilities for reliability
    
    Features:
    - Isotonic and sigmoid calibration
    - Calibration curve analysis
    - Reliability metrics
    - Time-series aware calibration
    
    Ensures that when model says 70% confidence,
    it's actually correct 70% of the time.
    """
    
    def __init__(self, method: str = 'isotonic'):
        """
        Initialize calibrator
        
        Args:
            method: 'isotonic' or 'sigmoid'
                - isotonic: Non-parametric, flexible (recommended for large datasets)
                - sigmoid: Parametric, assumes sigmoid relationship
        """
        self.method = method
        self.logger = logger
        self.calibrated_model = None
        self.calibration_metrics = {}
    
    def calibrate(
        self,
        model,
        X: pd.DataFrame,
        y: pd.Series,
        cv: Optional[int] = 5
    ) -> Any:
        """
        Calibrate model probabilities
        
        Args:
            model: Trained model to calibrate
            X: Feature DataFrame
            y: Target Series
            cv: Number of CV folds (None for no CV)
            
        Returns:
            Calibrated model
        """
        self.logger.info(
            f"Calibrating model probabilities using {self.method} method",
            category="ml_training"
        )
        
        # Use TimeSeriesSplit for time-aware calibration
        if cv is not None:
            cv_splitter = TimeSeriesSplit(n_splits=cv)
        else:
            cv_splitter = 'prefit'  # Assume model is already fitted
        
        try:
            self.calibrated_model = CalibratedClassifierCV(
                base_estimator=model,
                method=self.method,
                cv=cv_splitter,
                n_jobs=-1
            )
            
            if cv_splitter != 'prefit':
                self.calibrated_model.fit(X, y)
            
            self.logger.info("Model calibration complete", category="ml_training")
            
            return self.calibrated_model
            
        except Exception as e:
            self.logger.error(f"Error calibrating model: {e}", category="ml_training")
            return model  # Return uncalibrated model on failure
    
    def evaluate_calibration(
        self,
        model,
        X: pd.DataFrame,
        y: pd.Series,
        n_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Evaluate calibration quality
        
        Args:
            model: Model to evaluate
            X: Feature DataFrame
            y: Target Series
            n_bins: Number of bins for calibration curve
            
        Returns:
            Dict with calibration metrics
        """
        # Get predictions
        y_proba = model.predict_proba(X)[:, 1]
        
        # Calculate calibration curve
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y, y_proba, n_bins=n_bins, strategy='quantile'
        )
        
        # Calculate metrics
        brier_score = brier_score_loss(y, y_proba)
        log_loss_score = log_loss(y, y_proba)
        
        # Expected Calibration Error (ECE)
        ece = self._calculate_ece(y, y_proba, n_bins)
        
        # Maximum Calibration Error (MCE)
        mce = self._calculate_mce(y, y_proba, n_bins)
        
        metrics = {
            'brier_score': brier_score,
            'log_loss': log_loss_score,
            'expected_calibration_error': ece,
            'maximum_calibration_error': mce,
            'calibration_curve': {
                'fraction_of_positives': fraction_of_positives.tolist(),
                'mean_predicted_value': mean_predicted_value.tolist()
            }
        }
        
        self.calibration_metrics = metrics
        
        self.logger.info(
            f"Calibration metrics: Brier={brier_score:.4f}, ECE={ece:.4f}",
            category="ml_training"
        )
        
        return metrics
    
    def compare_calibration(
        self,
        original_model,
        calibrated_model,
        X: pd.DataFrame,
        y: pd.Series,
        n_bins: int = 10
    ) -> Dict[str, Any]:
        """
        Compare original vs calibrated model
        
        Args:
            original_model: Uncalibrated model
            calibrated_model: Calibrated model
            X: Feature DataFrame
            y: Target Series
            n_bins: Number of bins
            
        Returns:
            Comparison metrics
        """
        self.logger.info("Comparing calibration quality", category="ml_training")
        
        # Evaluate both
        original_metrics = self.evaluate_calibration(original_model, X, y, n_bins)
        calibrated_metrics = self.evaluate_calibration(calibrated_model, X, y, n_bins)
        
        # Calculate improvement
        improvements = {
            'brier_score': original_metrics['brier_score'] - calibrated_metrics['brier_score'],
            'log_loss': original_metrics['log_loss'] - calibrated_metrics['log_loss'],
            'ece': original_metrics['expected_calibration_error'] - calibrated_metrics['expected_calibration_error'],
            'mce': original_metrics['maximum_calibration_error'] - calibrated_metrics['maximum_calibration_error']
        }
        
        return {
            'original': original_metrics,
            'calibrated': calibrated_metrics,
            'improvements': improvements
        }
    
    def _calculate_ece(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        n_bins: int = 10
    ) -> float:
        """
        Calculate Expected Calibration Error (ECE)
        
        ECE measures average difference between predicted probabilities
        and actual frequencies across bins.
        """
        bins = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(y_proba, bins) - 1
        
        ece = 0.0
        total_samples = len(y_true)
        
        for i in range(n_bins):
            mask = bin_indices == i
            if mask.sum() > 0:
                bin_accuracy = y_true[mask].mean()
                bin_confidence = y_proba[mask].mean()
                bin_weight = mask.sum() / total_samples
                ece += bin_weight * abs(bin_accuracy - bin_confidence)
        
        return ece
    
    def _calculate_mce(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray,
        n_bins: int = 10
    ) -> float:
        """
        Calculate Maximum Calibration Error (MCE)
        
        MCE is the maximum difference between predicted probabilities
        and actual frequencies across all bins.
        """
        bins = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(y_proba, bins) - 1
        
        max_error = 0.0
        
        for i in range(n_bins):
            mask = bin_indices == i
            if mask.sum() > 0:
                bin_accuracy = y_true[mask].mean()
                bin_confidence = y_proba[mask].mean()
                error = abs(bin_accuracy - bin_confidence)
                max_error = max(max_error, error)
        
        return max_error
    
    def plot_calibration_curve(
        self,
        original_model,
        calibrated_model,
        X: pd.DataFrame,
        y: pd.Series,
        save_path: Optional[str] = None
    ):
        """
        Plot calibration curves for comparison
        
        Args:
            original_model: Uncalibrated model
            calibrated_model: Calibrated model
            X: Feature DataFrame
            y: Target Series
            save_path: Path to save plot
        """
        # Get predictions
        y_proba_original = original_model.predict_proba(X)[:, 1]
        y_proba_calibrated = calibrated_model.predict_proba(X)[:, 1]
        
        # Calculate calibration curves
        frac_pos_original, mean_pred_original = calibration_curve(
            y, y_proba_original, n_bins=10, strategy='quantile'
        )
        frac_pos_calibrated, mean_pred_calibrated = calibration_curve(
            y, y_proba_calibrated, n_bins=10, strategy='quantile'
        )
        
        # Plot
        plt.figure(figsize=(10, 6))
        
        # Perfect calibration line
        plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration', linewidth=2)
        
        # Original model
        plt.plot(
            mean_pred_original, frac_pos_original, 's-',
            label='Original Model', linewidth=2, markersize=8
        )
        
        # Calibrated model
        plt.plot(
            mean_pred_calibrated, frac_pos_calibrated, 'o-',
            label='Calibrated Model', linewidth=2, markersize=8
        )
        
        plt.xlabel('Mean Predicted Probability', fontsize=12)
        plt.ylabel('Fraction of Positives', fontsize=12)
        plt.title('Calibration Curve Comparison', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Calibration plot saved to {save_path}", category="ml_training")
        else:
            plt.show()
        
        plt.close()
    
    def get_confidence_bins(
        self,
        model,
        X: pd.DataFrame,
        y: pd.Series,
        bins: Optional[list] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyze accuracy by confidence level
        
        Args:
            model: Calibrated model
            X: Feature DataFrame
            y: Target Series
            bins: Custom bin edges (default: [0, 0.6, 0.8, 1.0])
            
        Returns:
            Dict with accuracy stats per confidence bin
        """
        if bins is None:
            bins = [0, 0.6, 0.8, 1.0]
            bin_labels = ['low', 'medium', 'high']
        else:
            bin_labels = [f'bin_{i}' for i in range(len(bins) - 1)]
        
        y_proba = model.predict_proba(X)[:, 1]
        y_pred = model.predict(X)
        
        results = {}
        
        for i, (low, high) in enumerate(zip(bins[:-1], bins[1:])):
            mask = (y_proba >= low) & (y_proba < high)
            
            if mask.sum() > 0:
                actual_accuracy = (y_pred[mask] == y[mask]).mean()
                predicted_confidence = y_proba[mask].mean()
                count = mask.sum()
                
                results[bin_labels[i]] = {
                    'range': (low, high),
                    'count': int(count),
                    'percentage': float(count / len(y)),
                    'predicted_confidence': float(predicted_confidence),
                    'actual_accuracy': float(actual_accuracy),
                    'calibration_error': abs(predicted_confidence - actual_accuracy)
                }
        
        return results


if __name__ == "__main__":
    # Test probability calibrator
    print("📊 Testing Probability Calibrator...")
    
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    
    # Create sample data
    np.random.seed(42)
    X = pd.DataFrame(np.random.randn(1000, 10), columns=[f'feature_{i}' for i in range(10)])
    y = pd.Series(np.random.randint(0, 2, 1000))
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train a model
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    # Test calibrator
    calibrator = ProbabilityCalibrator(method='isotonic')
    
    print("\n✓ Calibrating model...")
    calibrated_model = calibrator.calibrate(model, X_train, y_train, cv=3)
    
    print("\n✓ Evaluating calibration...")
    comparison = calibrator.compare_calibration(model, calibrated_model, X_test, y_test)
    
    print(f"\nOriginal Brier Score: {comparison['original']['brier_score']:.4f}")
    print(f"Calibrated Brier Score: {comparison['calibrated']['brier_score']:.4f}")
    print(f"Improvement: {comparison['improvements']['brier_score']:.4f}")
    
    print(f"\nOriginal ECE: {comparison['original']['expected_calibration_error']:.4f}")
    print(f"Calibrated ECE: {comparison['calibrated']['expected_calibration_error']:.4f}")
    print(f"Improvement: {comparison['improvements']['ece']:.4f}")
    
    print("\n✓ Confidence bins analysis...")
    bins = calibrator.get_confidence_bins(calibrated_model, X_test, y_test)
    for bin_name, stats in bins.items():
        print(f"\n   {bin_name.upper()}:")
        print(f"      Count: {stats['count']}")
        print(f"      Predicted: {stats['predicted_confidence']:.2%}")
        print(f"      Actual: {stats['actual_accuracy']:.2%}")
        print(f"      Error: {stats['calibration_error']:.2%}")
    
    print("\n✓ Probability calibrator test completed")
