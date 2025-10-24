"""
Feature Selection
Selects most important features for model training
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sklearn.feature_selection import (
    SelectKBest, f_classif, mutual_info_classif,
    RFE, SelectFromModel
)
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

from src.utils.logger import get_logger

logger = get_logger()


class FeatureSelector:
    """
    Feature selection using multiple methods
    
    Methods:
    - Statistical (F-test, mutual information)
    - Model-based (feature importance from tree models)
    - Recursive Feature Elimination (RFE)
    - SHAP values (if available)
    - Correlation-based (remove redundant features)
    """
    
    def __init__(self):
        """Initialize feature selector"""
        self.logger = logger
        self.selected_features = []
        self.feature_scores = {}
        self.removed_features = []
    
    def select_by_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_features: int = 50,
        method: str = 'xgboost'
    ) -> List[str]:
        """
        Select features by model-based importance
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_features: Number of features to select
            method: 'xgboost', 'random_forest', or 'both'
            
        Returns:
            List of selected feature names
        """
        self.logger.info(
            f"Selecting {n_features} features using {method}",
            category="ml_training"
        )
        
        if method in ['xgboost', 'both']:
            xgb_importance = self._get_xgboost_importance(X, y)
        else:
            xgb_importance = {}
        
        if method in ['random_forest', 'both']:
            rf_importance = self._get_rf_importance(X, y)
        else:
            rf_importance = {}
        
        # Combine importances
        if method == 'both':
            combined_importance = {}
            all_features = set(xgb_importance.keys()) | set(rf_importance.keys())
            
            for feature in all_features:
                xgb_score = xgb_importance.get(feature, 0)
                rf_score = rf_importance.get(feature, 0)
                combined_importance[feature] = (xgb_score + rf_score) / 2
            
            importance_dict = combined_importance
        elif method == 'xgboost':
            importance_dict = xgb_importance
        else:
            importance_dict = rf_importance
        
        # Sort and select top features
        sorted_features = sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        self.selected_features = [f for f, _ in sorted_features[:n_features]]
        self.feature_scores = dict(sorted_features)
        
        self.logger.info(
            f"Selected {len(self.selected_features)} features",
            category="ml_training"
        )
        
        return self.selected_features
    
    def select_by_rfe(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_features: int = 50,
        step: float = 0.1
    ) -> List[str]:
        """
        Select features using Recursive Feature Elimination
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_features: Number of features to select
            step: Fraction of features to remove at each iteration
            
        Returns:
            List of selected feature names
        """
        self.logger.info(
            f"Performing RFE to select {n_features} features",
            category="ml_training"
        )
        
        # Use Random Forest as base estimator
        estimator = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        
        # Perform RFE
        selector = RFE(
            estimator=estimator,
            n_features_to_select=n_features,
            step=step
        )
        
        selector.fit(X, y)
        
        # Get selected features
        self.selected_features = X.columns[selector.support_].tolist()
        
        # Get feature rankings
        self.feature_scores = dict(zip(X.columns, selector.ranking_))
        
        self.logger.info(
            f"RFE selected {len(self.selected_features)} features",
            category="ml_training"
        )
        
        return self.selected_features
    
    def select_by_correlation(
        self,
        X: pd.DataFrame,
        threshold: float = 0.95
    ) -> List[str]:
        """
        Remove highly correlated features
        
        Args:
            X: Feature DataFrame
            threshold: Correlation threshold (default 0.95)
            
        Returns:
            List of features to keep
        """
        self.logger.info(
            f"Removing features with correlation > {threshold}",
            category="ml_training"
        )
        
        # Calculate correlation matrix
        corr_matrix = X.corr().abs()
        
        # Find features to remove
        upper_triangle = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )
        
        to_drop = [
            column for column in upper_triangle.columns
            if any(upper_triangle[column] > threshold)
        ]
        
        self.removed_features = to_drop
        self.selected_features = [col for col in X.columns if col not in to_drop]
        
        self.logger.info(
            f"Removed {len(to_drop)} correlated features, kept {len(self.selected_features)}",
            category="ml_training"
        )
        
        return self.selected_features
    
    def select_by_variance(
        self,
        X: pd.DataFrame,
        threshold: float = 0.01
    ) -> List[str]:
        """
        Remove low-variance features
        
        Args:
            X: Feature DataFrame
            threshold: Minimum variance threshold
            
        Returns:
            List of features to keep
        """
        self.logger.info(
            f"Removing features with variance < {threshold}",
            category="ml_training"
        )
        
        # Calculate variance
        variances = X.var()
        
        # Select features above threshold
        self.selected_features = variances[variances > threshold].index.tolist()
        self.removed_features = variances[variances <= threshold].index.tolist()
        
        self.logger.info(
            f"Removed {len(self.removed_features)} low-variance features",
            category="ml_training"
        )
        
        return self.selected_features
    
    def select_comprehensive(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_features: int = 50,
        correlation_threshold: float = 0.95,
        variance_threshold: float = 0.01
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        Comprehensive feature selection pipeline
        
        Steps:
        1. Remove low-variance features
        2. Remove highly correlated features
        3. Select top features by importance
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_features: Final number of features
            correlation_threshold: Correlation threshold
            variance_threshold: Variance threshold
            
        Returns:
            Tuple of (selected_features, selection_report)
        """
        self.logger.info("Starting comprehensive feature selection", category="ml_training")
        
        original_features = X.columns.tolist()
        report = {
            'original_features': len(original_features),
            'steps': []
        }
        
        # Step 1: Remove low variance
        step1_features = self.select_by_variance(X, variance_threshold)
        X_step1 = X[step1_features]
        report['steps'].append({
            'step': 'variance_threshold',
            'removed': len(original_features) - len(step1_features),
            'remaining': len(step1_features)
        })
        
        # Step 2: Remove correlation
        step2_features = self.select_by_correlation(X_step1, correlation_threshold)
        X_step2 = X_step1[step2_features]
        report['steps'].append({
            'step': 'correlation_threshold',
            'removed': len(step1_features) - len(step2_features),
            'remaining': len(step2_features)
        })
        
        # Step 3: Select by importance
        if len(step2_features) > n_features:
            final_features = self.select_by_importance(X_step2, y, n_features, method='both')
        else:
            final_features = step2_features
        
        report['steps'].append({
            'step': 'importance_selection',
            'removed': len(step2_features) - len(final_features),
            'remaining': len(final_features)
        })
        
        report['final_features'] = len(final_features)
        report['total_removed'] = len(original_features) - len(final_features)
        report['reduction_percentage'] = (report['total_removed'] / len(original_features)) * 100
        
        self.selected_features = final_features
        
        self.logger.info(
            f"Feature selection complete: {len(original_features)} → {len(final_features)} "
            f"({report['reduction_percentage']:.1f}% reduction)",
            category="ml_training"
        )
        
        return final_features, report
    
    def get_shap_importance(
        self,
        model,
        X: pd.DataFrame,
        n_samples: int = 100
    ) -> Dict[str, float]:
        """
        Calculate SHAP importance values
        
        Args:
            model: Trained model
            X: Feature DataFrame
            n_samples: Number of samples to use for SHAP
            
        Returns:
            Dict of feature: importance
        """
        if not SHAP_AVAILABLE:
            self.logger.warning("SHAP not available", category="ml_training")
            return {}
        
        self.logger.info("Calculating SHAP values", category="ml_training")
        
        try:
            # Sample data for efficiency
            X_sample = X.sample(min(n_samples, len(X)), random_state=42)
            
            # Create explainer
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample)
            
            # Get mean absolute SHAP values
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # For binary classification
            
            mean_shap = np.abs(shap_values).mean(axis=0)
            
            importance_dict = dict(zip(X.columns, mean_shap))
            
            return importance_dict
            
        except Exception as e:
            self.logger.warning(f"SHAP calculation failed: {e}", category="ml_training")
            return {}
    
    def _get_xgboost_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Dict[str, float]:
        """Get feature importance from XGBoost"""
        model = xgb.XGBClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss'
        )
        
        model.fit(X, y, verbose=False)
        
        importance_dict = dict(zip(X.columns, model.feature_importances_))
        
        return importance_dict
    
    def _get_rf_importance(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Dict[str, float]:
        """Get feature importance from Random Forest"""
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X, y)
        
        importance_dict = dict(zip(X.columns, model.feature_importances_))
        
        return importance_dict
    
    def get_feature_report(self) -> pd.DataFrame:
        """
        Get detailed feature selection report
        
        Returns:
            DataFrame with feature scores and selection status
        """
        if not self.feature_scores:
            return pd.DataFrame()
        
        df = pd.DataFrame([
            {
                'feature': feature,
                'score': score,
                'selected': feature in self.selected_features,
                'rank': rank + 1
            }
            for rank, (feature, score) in enumerate(
                sorted(self.feature_scores.items(), key=lambda x: x[1], reverse=True)
            )
        ])
        
        return df


if __name__ == "__main__":
    # Test feature selector
    print("🔍 Testing Feature Selector...")
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 100
    
    # Create features with varying importance
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    
    # Create target with some features being relevant
    y = pd.Series(
        (X['feature_0'] + X['feature_1'] - X['feature_2'] + np.random.randn(n_samples) * 0.5 > 0).astype(int)
    )
    
    # Add some correlated features
    X['feature_100'] = X['feature_0'] + np.random.randn(n_samples) * 0.01  # Highly correlated
    X['feature_101'] = np.random.randn(n_samples) * 0.0001  # Low variance
    
    selector = FeatureSelector()
    
    print("\n✓ Testing comprehensive selection...")
    selected, report = selector.select_comprehensive(X, y, n_features=30)
    
    print(f"\nSelection Report:")
    print(f"   Original features: {report['original_features']}")
    print(f"   Final features: {report['final_features']}")
    print(f"   Reduction: {report['reduction_percentage']:.1f}%")
    
    for step in report['steps']:
        print(f"\n   {step['step']}:")
        print(f"      Removed: {step['removed']}")
        print(f"      Remaining: {step['remaining']}")
    
    print(f"\n✓ Top 10 selected features:")
    feature_report = selector.get_feature_report()
    print(feature_report.head(10).to_string(index=False))
    
    print("\n✓ Feature selector test completed")
