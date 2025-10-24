"""
Hyperparameter Optimization
Uses Optuna for automated hyperparameter tuning
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Callable
import time
from datetime import datetime

try:
    import optuna
    from optuna.samplers import TPESampler
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier

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

from config.settings import MLConfig
from src.utils.logger import get_logger

logger = get_logger()


class HyperparameterTuner:
    """
    Automated hyperparameter tuning using Optuna
    
    Features:
    - Bayesian optimization
    - Time-series aware cross-validation
    - Multi-model support (XGBoost, LightGBM, CatBoost, RandomForest)
    - Parallel trials
    - Pruning of unpromising trials
    """
    
    def __init__(self, random_state: int = 42):
        """Initialize hyperparameter tuner"""
        self.random_state = random_state
        self.logger = logger
        self.best_params = {}
        
        if not OPTUNA_AVAILABLE:
            self.logger.warning(
                "Optuna not available. Hyperparameter tuning disabled.",
                category="ml_training"
            )
    
    def tune_xgboost(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_trials: int = 100,
        cv_folds: int = 5,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Tune XGBoost hyperparameters
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_trials: Number of optimization trials
            cv_folds: Number of cross-validation folds
            timeout: Maximum optimization time in seconds
            
        Returns:
            Dict with best parameters and score
        """
        if not OPTUNA_AVAILABLE:
            return self._get_default_xgboost_params()
        
        self.logger.info("Starting XGBoost hyperparameter tuning", category="ml_training")
        
        def objective(trial):
            """Optuna objective function for XGBoost"""
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'gamma': trial.suggest_float('gamma', 0, 5),
                'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
                'reg_lambda': trial.suggest_float('reg_lambda', 0, 1),
                'random_state': self.random_state,
                'n_jobs': -1,
                'eval_metric': 'logloss'
            }
            
            # Time-series cross-validation
            tscv = TimeSeriesSplit(n_splits=cv_folds)
            scores = []
            
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                model = xgb.XGBClassifier(**params)
                model.fit(X_train, y_train, verbose=False)
                
                y_pred = model.predict(X_val)
                score = accuracy_score(y_val, y_pred)
                scores.append(score)
            
            return np.mean(scores)
        
        # Create study
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=self.random_state),
            pruner=optuna.pruners.MedianPruner(n_warmup_steps=10)
        )
        
        # Optimize
        study.optimize(
            objective,
            n_trials=n_trials,
            timeout=timeout,
            show_progress_bar=True,
            n_jobs=1  # Parallel trials can cause issues with XGBoost
        )
        
        best_params = study.best_params
        best_params['random_state'] = self.random_state
        best_params['n_jobs'] = -1
        best_params['eval_metric'] = 'logloss'
        
        self.best_params['xgboost'] = best_params
        
        self.logger.info(
            f"XGBoost tuning complete. Best score: {study.best_value:.4f}",
            category="ml_training"
        )
        
        return {
            'params': best_params,
            'best_score': study.best_value,
            'n_trials': len(study.trials),
            'study': study
        }
    
    def tune_lightgbm(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_trials: int = 100,
        cv_folds: int = 5,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Tune LightGBM hyperparameters"""
        if not OPTUNA_AVAILABLE or not LIGHTGBM_AVAILABLE:
            return self._get_default_lightgbm_params()
        
        self.logger.info("Starting LightGBM hyperparameter tuning", category="ml_training")
        
        def objective(trial):
            """Optuna objective function for LightGBM"""
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'num_leaves': trial.suggest_int('num_leaves', 20, 100),
                'min_child_samples': trial.suggest_int('min_child_samples', 5, 50),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'reg_alpha': trial.suggest_float('reg_alpha', 0, 1),
                'reg_lambda': trial.suggest_float('reg_lambda', 0, 1),
                'random_state': self.random_state,
                'n_jobs': -1,
                'verbose': -1
            }
            
            tscv = TimeSeriesSplit(n_splits=cv_folds)
            scores = []
            
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                model = lgb.LGBMClassifier(**params)
                model.fit(X_train, y_train)
                
                y_pred = model.predict(X_val)
                score = accuracy_score(y_val, y_pred)
                scores.append(score)
            
            return np.mean(scores)
        
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=self.random_state),
            pruner=optuna.pruners.MedianPruner(n_warmup_steps=10)
        )
        
        study.optimize(objective, n_trials=n_trials, timeout=timeout, show_progress_bar=True)
        
        best_params = study.best_params
        best_params['random_state'] = self.random_state
        best_params['n_jobs'] = -1
        best_params['verbose'] = -1
        
        self.best_params['lightgbm'] = best_params
        
        self.logger.info(
            f"LightGBM tuning complete. Best score: {study.best_value:.4f}",
            category="ml_training"
        )
        
        return {
            'params': best_params,
            'best_score': study.best_value,
            'n_trials': len(study.trials),
            'study': study
        }
    
    def tune_random_forest(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_trials: int = 100,
        cv_folds: int = 5,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Tune Random Forest hyperparameters"""
        if not OPTUNA_AVAILABLE:
            return self._get_default_rf_params()
        
        self.logger.info("Starting Random Forest hyperparameter tuning", category="ml_training")
        
        def objective(trial):
            """Optuna objective function for Random Forest"""
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 100, 500),
                'max_depth': trial.suggest_int('max_depth', 5, 15),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', 0.5, 0.8]),
                'random_state': self.random_state,
                'n_jobs': -1
            }
            
            tscv = TimeSeriesSplit(n_splits=cv_folds)
            scores = []
            
            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                
                model = RandomForestClassifier(**params)
                model.fit(X_train, y_train)
                
                y_pred = model.predict(X_val)
                score = accuracy_score(y_val, y_pred)
                scores.append(score)
            
            return np.mean(scores)
        
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=self.random_state)
        )
        
        study.optimize(objective, n_trials=n_trials, timeout=timeout, show_progress_bar=True)
        
        best_params = study.best_params
        best_params['random_state'] = self.random_state
        best_params['n_jobs'] = -1
        
        self.best_params['random_forest'] = best_params
        
        self.logger.info(
            f"Random Forest tuning complete. Best score: {study.best_value:.4f}",
            category="ml_training"
        )
        
        return {
            'params': best_params,
            'best_score': study.best_value,
            'n_trials': len(study.trials),
            'study': study
        }
    
    def tune_all(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_trials_per_model: int = 50,
        cv_folds: int = 5,
        timeout_per_model: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Tune all available models
        
        Args:
            X: Feature DataFrame
            y: Target Series
            n_trials_per_model: Trials for each model
            cv_folds: CV folds
            timeout_per_model: Max time per model
            
        Returns:
            Dict with results for all models
        """
        results = {}
        start_time = time.time()
        
        # XGBoost
        xgb_result = self.tune_xgboost(X, y, n_trials_per_model, cv_folds, timeout_per_model)
        results['xgboost'] = xgb_result
        
        # LightGBM
        if LIGHTGBM_AVAILABLE:
            lgb_result = self.tune_lightgbm(X, y, n_trials_per_model, cv_folds, timeout_per_model)
            results['lightgbm'] = lgb_result
        
        # Random Forest
        rf_result = self.tune_random_forest(X, y, n_trials_per_model, cv_folds, timeout_per_model)
        results['random_forest'] = rf_result
        
        duration = time.time() - start_time
        
        self.logger.info(
            f"All hyperparameter tuning complete in {duration:.2f}s",
            category="ml_training"
        )
        
        return {
            'results': results,
            'duration': duration,
            'best_params': self.best_params
        }
    
    def _get_default_xgboost_params(self) -> Dict[str, Any]:
        """Get default XGBoost parameters"""
        return {
            'params': {
                'n_estimators': 200,
                'max_depth': 5,
                'learning_rate': 0.05,
                'min_child_weight': 3,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'gamma': 0.1,
                'random_state': self.random_state,
                'n_jobs': -1
            },
            'best_score': None,
            'n_trials': 0
        }
    
    def _get_default_lightgbm_params(self) -> Dict[str, Any]:
        """Get default LightGBM parameters"""
        return {
            'params': {
                'n_estimators': 200,
                'max_depth': 5,
                'learning_rate': 0.05,
                'num_leaves': 31,
                'min_child_samples': 20,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': self.random_state,
                'n_jobs': -1,
                'verbose': -1
            },
            'best_score': None,
            'n_trials': 0
        }
    
    def _get_default_rf_params(self) -> Dict[str, Any]:
        """Get default Random Forest parameters"""
        return {
            'params': {
                'n_estimators': 200,
                'max_depth': 8,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'max_features': 'sqrt',
                'random_state': self.random_state,
                'n_jobs': -1
            },
            'best_score': None,
            'n_trials': 0
        }


if __name__ == "__main__":
    # Test hyperparameter tuner
    print("🔧 Testing Hyperparameter Tuner...")
    
    if not OPTUNA_AVAILABLE:
        print("⚠️  Optuna not available. Install with: pip install optuna")
    else:
        # Create sample data
        dates = pd.date_range('2024-01-01', periods=1000, freq='1H')
        X = pd.DataFrame(np.random.randn(1000, 10), columns=[f'feature_{i}' for i in range(10)])
        y = pd.Series(np.random.randint(0, 2, 1000))
        
        tuner = HyperparameterTuner()
        
        # Quick test with few trials
        print("\n✓ Testing XGBoost tuning (5 trials)...")
        result = tuner.tune_xgboost(X, y, n_trials=5, cv_folds=3)
        print(f"   Best score: {result['best_score']:.4f}")
        print(f"   Best params: {result['params']}")
        
        print("\n✓ Hyperparameter tuner test completed")
