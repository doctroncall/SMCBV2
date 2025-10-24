"""
Model Trainer
Trains ML models for sentiment prediction
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
import xgboost as xgb

try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
from typing import Dict, Any, Tuple
import time
from datetime import datetime

from .feature_engineering import FeatureEngineer
from config.settings import MLConfig
from src.utils.logger import get_logger

logger = get_logger()


class ModelTrainer:
    """
    Train ML models for sentiment prediction
    
    Uses ensemble approach:
    - XGBoost
    - Random Forest
    - Voting classifier
    """
    
    def __init__(self):
        """Initialize trainer"""
        self.feature_engineer = FeatureEngineer()
        self.config = MLConfig
        self.logger = logger
        self.scaler = StandardScaler()
    
    def prepare_training_data(
        self,
        df: pd.DataFrame,
        target_col: str = 'target',
        min_move_pips: float = 10.0,
        lookforward_bars: int = 3
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare data for training with improved target definition
        
        Args:
            df: DataFrame with OHLCV data
            target_col: Name of target column
            min_move_pips: Minimum meaningful move in pips (default 10)
            lookforward_bars: Number of bars to look forward (default 3)
            
        Returns:
            Tuple of (features_df, target_series)
        """
        # Create features
        features_df = self.feature_engineer.create_features(df)
        
        # Create target (future price movement) with improved definition
        if target_col not in features_df.columns:
            # Multi-horizon target: look ahead multiple bars instead of just 1
            features_df['future_high'] = features_df['High'].rolling(lookforward_bars).max().shift(-lookforward_bars)
            features_df['future_low'] = features_df['Low'].rolling(lookforward_bars).min().shift(-lookforward_bars)
            features_df['future_close'] = features_df['Close'].shift(-lookforward_bars)
            
            # Calculate potential upside and downside
            features_df['upside_pips'] = (features_df['future_high'] - features_df['Close']) * 10000
            features_df['downside_pips'] = (features_df['Close'] - features_df['future_low']) * 10000
            
            # Target: 1 if clear uptrend, 0 if clear downtrend, -1 if noise (to be filtered)
            features_df['target_raw'] = np.where(
                (features_df['upside_pips'] > min_move_pips) & 
                (features_df['upside_pips'] > features_df['downside_pips'] * 1.5),
                1,  # Clear bullish move
                np.where(
                    (features_df['downside_pips'] > min_move_pips) & 
                    (features_df['downside_pips'] > features_df['upside_pips'] * 1.5),
                    0,  # Clear bearish move
                    -1  # Noise/ranging - exclude from training
                )
            )
            
            # Filter out noisy samples
            features_df = features_df[features_df['target_raw'] != -1].copy()
            features_df['target'] = features_df['target_raw']
            
            # Drop temporary columns
            features_df = features_df.drop(['future_high', 'future_low', 'future_close', 
                                           'upside_pips', 'downside_pips', 'target_raw'], axis=1)
            features_df = features_df.dropna()
            target_col = 'target'
            
            self.logger.info(
                f"Target created: {features_df['target'].sum()} bullish, "
                f"{(features_df['target'] == 0).sum()} bearish samples",
                category="ml_training"
            )
        
        # Split features and target
        feature_cols = self.feature_engineer.get_feature_names()
        X = features_df[feature_cols]
        y = features_df[target_col]
        
        return X, y
    
    def train_model(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        model_version: str = None,
        use_class_balancing: bool = True,
        use_tscv: bool = True
    ) -> Dict[str, Any]:
        """
        Train ensemble model with improved techniques
        
        Args:
            X: Feature DataFrame
            y: Target Series
            model_version: Model version string
            use_class_balancing: Whether to balance classes with SMOTE
            use_tscv: Whether to use time-series cross-validation
            
        Returns:
            Dict with trained model and metrics
        """
        try:
            start_time = time.time()
            model_version = model_version or self.config.MODEL_VERSION
            
            self.logger.info(f"Training model {model_version}", category="ml_training")
            
            # Split data (preserve time order for time-series)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=self.config.TEST_SIZE,
                random_state=self.config.RANDOM_STATE,
                shuffle=False  # Don't shuffle for time-series data
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Class balancing
            if use_class_balancing and SMOTE_AVAILABLE:
                try:
                    smote = SMOTE(random_state=self.config.RANDOM_STATE, k_neighbors=5)
                    X_train_scaled, y_train = smote.fit_resample(X_train_scaled, y_train)
                    self.logger.info(
                        f"Applied SMOTE: {len(y_train)} samples after balancing",
                        category="ml_training"
                    )
                except Exception as e:
                    self.logger.warning(f"SMOTE failed: {e}, using class weights instead", category="ml_training")
                    use_class_balancing = False
            
            # Calculate class weights
            class_weights = compute_class_weight(
                'balanced',
                classes=np.unique(y_train),
                y=y_train
            )
            scale_pos_weight = class_weights[1] / class_weights[0] if not use_class_balancing or not SMOTE_AVAILABLE else 1.0
            
            # Train XGBoost with improved hyperparameters
            xgb_model = xgb.XGBClassifier(
                n_estimators=200,  # Increased from 100
                max_depth=5,  # Reduced to prevent overfitting
                learning_rate=0.05,  # Reduced for better convergence
                min_child_weight=3,  # Added regularization
                subsample=0.8,  # Added for robustness
                colsample_bytree=0.8,  # Added for feature diversity
                scale_pos_weight=scale_pos_weight,  # Class balancing
                random_state=self.config.RANDOM_STATE,
                n_jobs=-1,
                eval_metric='logloss'
            )
            xgb_model.fit(X_train_scaled, y_train)
            
            # Train Random Forest with improved hyperparameters
            rf_model = RandomForestClassifier(
                n_estimators=200,  # Increased from 100
                max_depth=8,  # Reduced to prevent overfitting
                min_samples_split=5,  # Added regularization
                min_samples_leaf=2,  # Added regularization
                max_features='sqrt',  # Feature diversity
                class_weight='balanced' if not use_class_balancing or not SMOTE_AVAILABLE else None,
                random_state=self.config.RANDOM_STATE,
                n_jobs=-1
            )
            rf_model.fit(X_train_scaled, y_train)
            
            # Initialize estimators list for ensemble
            estimators = [
                ('xgb', xgb_model),
                ('rf', rf_model)
            ]
            weights = [self.config.XGBOOST_WEIGHT, self.config.RANDOM_FOREST_WEIGHT]
            
            # Train LightGBM if available
            if LIGHTGBM_AVAILABLE:
                lgb_model = lgb.LGBMClassifier(
                    n_estimators=200,
                    max_depth=5,
                    learning_rate=0.05,
                    num_leaves=31,
                    min_child_samples=20,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    class_weight='balanced' if not use_class_balancing or not SMOTE_AVAILABLE else None,
                    random_state=self.config.RANDOM_STATE,
                    n_jobs=-1,
                    verbose=-1
                )
                lgb_model.fit(X_train_scaled, y_train)
                estimators.append(('lgb', lgb_model))
                weights.append(0.15)
                self.logger.info("LightGBM added to ensemble", category="ml_training")
            
            # Train CatBoost if available
            if CATBOOST_AVAILABLE:
                cat_model = cb.CatBoostClassifier(
                    iterations=200,
                    depth=5,
                    learning_rate=0.05,
                    l2_leaf_reg=3,
                    class_weights=[1, scale_pos_weight] if not use_class_balancing or not SMOTE_AVAILABLE else None,
                    random_state=self.config.RANDOM_STATE,
                    verbose=False,
                    thread_count=-1
                )
                cat_model.fit(X_train_scaled, y_train)
                estimators.append(('cat', cat_model))
                weights.append(0.15)
                self.logger.info("CatBoost added to ensemble", category="ml_training")
            
            # Normalize weights
            weights = [w / sum(weights) for w in weights]
            
            # Create ensemble
            ensemble = VotingClassifier(
                estimators=estimators,
                voting='soft',
                weights=weights
            )
            ensemble.fit(X_train_scaled, y_train)
            
            self.logger.info(
                f"Ensemble created with {len(estimators)} models: {[name for name, _ in estimators]}",
                category="ml_training"
            )
            
            # Evaluate
            train_score = ensemble.score(X_train_scaled, y_train)
            test_score = ensemble.score(X_test_scaled, y_test)
            
            # Time-series cross-validation
            if use_tscv:
                tscv = TimeSeriesSplit(n_splits=5)
                cv_scores = []
                for train_idx, val_idx in tscv.split(X_train_scaled):
                    X_cv_train, X_cv_val = X_train_scaled[train_idx], X_train_scaled[val_idx]
                    y_cv_train, y_cv_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
                    
                    temp_ensemble = VotingClassifier(
                        estimators=[('xgb', xgb_model), ('rf', rf_model)],
                        voting='soft',
                        weights=[self.config.XGBOOST_WEIGHT, self.config.RANDOM_FOREST_WEIGHT]
                    )
                    temp_ensemble.fit(X_cv_train, y_cv_train)
                    score = temp_ensemble.score(X_cv_val, y_cv_val)
                    cv_scores.append(score)
                cv_scores = np.array(cv_scores)
            else:
                cv_scores = cross_val_score(
                    ensemble, X_train_scaled, y_train,
                    cv=self.config.CV_FOLDS,
                    scoring='accuracy'
                )
            
            duration = time.time() - start_time
            
            # Feature importance (from XGBoost)
            feature_importance = dict(zip(
                X.columns,
                xgb_model.feature_importances_
            ))
            
            result = {
                'model': ensemble,
                'scaler': self.scaler,
                'version': model_version,
                'train_accuracy': train_score,
                'test_accuracy': test_score,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'feature_importance': feature_importance,
                'training_samples': len(X_train),
                'training_duration': duration,
                'training_date': datetime.now()
            }
            
            self.logger.log_ml_training(
                model_version,
                len(X_train),
                test_score,
                duration
            )
            
            self.logger.info(
                f"Model trained: {test_score:.2%} accuracy in {duration:.2f}s",
                category="ml_training"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}", category="ml_training")
            raise


if __name__ == "__main__":
    # Test model trainer
    print("🎓 Testing Model Trainer...")
    
    # Create sample data with target
    dates = pd.date_range(start='2024-01-01', periods=1000, freq='1H')
    trend = np.linspace(1.08, 1.10, 1000) + np.random.normal(0, 0.001, 1000)
    
    data = {
        'Open': trend - np.random.uniform(0, 0.001, 1000),
        'High': trend + np.random.uniform(0, 0.002, 1000),
        'Low': trend - np.random.uniform(0, 0.002, 1000),
        'Close': trend,
        'Volume': np.random.randint(1000, 10000, 1000),
    }
    df = pd.DataFrame(data, index=dates)
    
    trainer = ModelTrainer()
    
    # Prepare data
    X, y = trainer.prepare_training_data(df)
    print(f"✓ Prepared data: {len(X)} samples, {len(X.columns)} features")
    
    # Train model
    result = trainer.train_model(X, y, "v1.0.0-test")
    print(f"✓ Model trained:")
    print(f"   Train accuracy: {result['train_accuracy']:.2%}")
    print(f"   Test accuracy: {result['test_accuracy']:.2%}")
    print(f"   CV mean: {result['cv_mean']:.2%} ± {result['cv_std']:.2%}")
    print(f"   Duration: {result['training_duration']:.2f}s")
    
    print("\n✓ Model trainer test completed")
