"""
ML Training Panel
GUI components for model training with v2.0 features
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

from src.ml.model_manager import ModelManager
from src.database.repository import get_repository
from src.utils.logger import get_logger

logger = get_logger()


def render_ml_training_panel():
    """
    Render ML model training panel with all v2.0 features
    
    Features:
    - Basic training
    - Advanced training with hyperparameter tuning
    - Feature selection
    - Probability calibration
    - Model versioning
    """
    st.markdown("### 🤖 ML Model Training")
    
    st.info("""
    **New in v2.0:** Train models with advanced features:
    - 🎯 Smart target definition (10+ pip meaningful moves)
    - 📊 70+ comprehensive features
    - ⚖️ Automatic class balancing (SMOTE)
    - 🔄 Time-series cross-validation
    - 🎛️ Hyperparameter optimization (optional)
    - 📉 Probability calibration
    - 🔍 Automatic feature selection
    """)
    
    # Training mode selection
    st.markdown("---")
    st.markdown("#### Training Mode")
    
    col1, col2 = st.columns(2)
    
    with col1:
        training_mode = st.radio(
            "Select training mode:",
            ["Quick Train (Optimized Defaults)", "Advanced Train (Custom Settings)"],
            help="Quick: Uses optimized defaults. Advanced: Full control over all parameters."
        )
    
    # Data source
    st.markdown("---")
    st.markdown("#### Data Source")
    
    data_source = st.radio(
        "Select data source:",
        ["From MT5 (Live Data)", "Upload CSV File"],
        help="Choose whether to train on live MT5 data or uploaded historical data"
    )
    
    if data_source == "From MT5 (Live Data)":
        col1, col2, col3 = st.columns(3)
        
        with col1:
            symbol = st.selectbox("Symbol", ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"])
        
        with col2:
            timeframe = st.selectbox("Timeframe", ["M15", "H1", "H4", "D1"])
        
        with col3:
            num_bars = st.number_input("Number of bars", min_value=500, max_value=10000, value=2000, step=500)
        
        if st.button("📥 Fetch MT5 Data"):
            with st.spinner("Fetching data from MT5..."):
                try:
                    from src.mt5.data_fetcher import MT5DataFetcher
                    
                    fetcher = MT5DataFetcher(connection=None)
                    df = fetcher.get_ohlcv(symbol, timeframe, count=num_bars)
                    
                    if df is not None and not df.empty:
                        st.session_state.training_data = df
                        st.session_state.training_symbol = symbol
                        st.session_state.training_timeframe = timeframe
                        st.success(f"✓ Fetched {len(df)} bars")
                        
                        # Show data preview
                        st.markdown("**Data Preview:**")
                        st.dataframe(df.tail(10))
                    else:
                        st.error("Failed to fetch data from MT5")
                        
                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")
    
    else:  # Upload CSV
        uploaded_file = st.file_uploader(
            "Upload OHLCV CSV file",
            type=['csv'],
            help="CSV must have columns: Open, High, Low, Close, Volume with datetime index"
        )
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, index_col=0, parse_dates=True)
                
                # Validate columns
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                if all(col in df.columns for col in required_cols):
                    st.session_state.training_data = df
                    st.session_state.training_symbol = "UPLOADED"
                    st.session_state.training_timeframe = "UNKNOWN"
                    st.success(f"✓ Loaded {len(df)} rows")
                    
                    # Show preview
                    st.markdown("**Data Preview:**")
                    st.dataframe(df.tail(10))
                else:
                    st.error(f"CSV must have columns: {', '.join(required_cols)}")
            
            except Exception as e:
                st.error(f"Error loading CSV: {str(e)}")
    
    # Training configuration
    if 'training_data' in st.session_state:
        st.markdown("---")
        st.markdown("#### Training Configuration")
        
        if training_mode == "Advanced Train (Custom Settings)":
            # Advanced settings
            with st.expander("⚙️ Advanced Settings", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Target Definition**")
                    min_move_pips = st.number_input(
                        "Minimum Move (pips)",
                        min_value=1.0,
                        max_value=50.0,
                        value=10.0,
                        step=1.0,
                        help="Minimum price movement to be considered a signal (filters noise)"
                    )
                    
                    lookforward_bars = st.number_input(
                        "Look Forward (bars)",
                        min_value=1,
                        max_value=10,
                        value=3,
                        help="Number of bars to look ahead for target prediction"
                    )
                    
                    st.markdown("**Feature Selection**")
                    enable_feature_selection = st.checkbox(
                        "Enable Feature Selection",
                        value=True,
                        help="Automatically select best features (recommended)"
                    )
                    
                    if enable_feature_selection:
                        n_features = st.slider(
                            "Target Features",
                            min_value=20,
                            max_value=70,
                            value=50,
                            help="Number of features to select"
                        )
                    else:
                        n_features = 70
                
                with col2:
                    st.markdown("**Model Configuration**")
                    use_class_balancing = st.checkbox(
                        "SMOTE Class Balancing",
                        value=True,
                        help="Balance bullish/bearish samples"
                    )
                    
                    calibrate_probabilities = st.checkbox(
                        "Calibrate Probabilities",
                        value=True,
                        help="Ensure confidence scores match reality"
                    )
                    
                    tune_hyperparameters = st.checkbox(
                        "Hyperparameter Tuning",
                        value=False,
                        help="⚠️ Slow but improves accuracy by 5-8% (30+ minutes)"
                    )
                    
                    if tune_hyperparameters:
                        n_trials = st.slider(
                            "Optimization Trials",
                            min_value=10,
                            max_value=100,
                            value=30,
                            help="More trials = better results but slower"
                        )
                    else:
                        n_trials = 0
        else:
            # Quick train - use defaults
            min_move_pips = 10.0
            lookforward_bars = 3
            enable_feature_selection = True
            n_features = 50
            use_class_balancing = True
            calibrate_probabilities = True
            tune_hyperparameters = False
            n_trials = 0
        
        # Model version
        st.markdown("---")
        model_version = st.text_input(
            "Model Version",
            value=f"v2.0.0_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            help="Unique version identifier for this model"
        )
        
        # Training button
        st.markdown("---")
        
        if st.button("🚀 Start Training", type="primary", use_container_width=True):
            train_model(
                df=st.session_state.training_data,
                version=model_version,
                min_move_pips=min_move_pips,
                lookforward_bars=lookforward_bars,
                enable_feature_selection=enable_feature_selection,
                n_features=n_features,
                use_class_balancing=use_class_balancing,
                calibrate_probabilities=calibrate_probabilities,
                tune_hyperparameters=tune_hyperparameters,
                n_trials=n_trials
            )
    
    else:
        st.info("👆 Select data source and fetch/upload data to begin training")
    
    # Show training results
    if 'training_results' in st.session_state:
        display_training_results(st.session_state.training_results)


def train_model(
    df,
    version,
    min_move_pips,
    lookforward_bars,
    enable_feature_selection,
    n_features,
    use_class_balancing,
    calibrate_probabilities,
    tune_hyperparameters,
    n_trials
):
    """Execute model training"""
    
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    try:
        # Initialize manager
        progress_placeholder.progress(0.1)
        status_placeholder.info("🔧 Initializing model manager...")
        
        manager = ModelManager(repository=get_repository())
        
        # Configure
        from config.settings import MLConfig
        MLConfig.MIN_MOVE_PIPS = min_move_pips
        MLConfig.LOOKFORWARD_BARS = lookforward_bars
        MLConfig.USE_CLASS_BALANCING = use_class_balancing
        
        # Train
        progress_placeholder.progress(0.2)
        status_placeholder.info(f"🚂 Training model {version}...")
        
        result = manager.train_new_model(
            df=df,
            version=version,
            tune_hyperparameters=tune_hyperparameters,
            select_features=enable_feature_selection,
            calibrate_probabilities=calibrate_probabilities,
            n_features=n_features
        )
        
        progress_placeholder.progress(1.0)
        status_placeholder.success(f"✅ Training complete!")
        
        # Store results
        st.session_state.training_results = result
        
        # Log success
        logger.info(f"Model {version} trained successfully via GUI", category="ml_training")
        
    except Exception as e:
        progress_placeholder.empty()
        status_placeholder.error(f"❌ Training failed: {str(e)}")
        logger.error(f"GUI training error: {str(e)}", category="ml_training")
        st.exception(e)


def display_training_results(results):
    """Display training results"""
    
    st.markdown("---")
    st.markdown("### 📊 Training Results")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Train Accuracy",
            f"{results['train_accuracy']:.2%}",
            delta=None
        )
    
    with col2:
        st.metric(
            "Test Accuracy",
            f"{results['test_accuracy']:.2%}",
            delta=f"+{(results['test_accuracy'] - 0.55):.2%}" if results['test_accuracy'] > 0.55 else None,
            delta_color="normal"
        )
    
    with col3:
        st.metric(
            "CV Score",
            f"{results['cv_mean']:.2%}",
            delta=f"±{results['cv_std']:.2%}",
            delta_color="off"
        )
    
    with col4:
        st.metric(
            "Training Time",
            f"{results['training_duration']:.1f}s",
            delta=None
        )
    
    # Ensemble information
    st.markdown("---")
    st.markdown("#### 🎭 Ensemble Models")
    
    if hasattr(results['model'], 'estimators'):
        models = [name for name, _ in results['model'].estimators]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"**Models Used:** {len(models)}")
            for model_name in models:
                st.markdown(f"- ✅ {model_name.upper()}")
        
        with col2:
            # Model weights
            if hasattr(results['model'], 'weights'):
                weights = results['model'].weights
                
                fig = go.Figure(data=[go.Bar(
                    x=[name.upper() for name in models],
                    y=weights,
                    marker_color=['#3B82F6', '#10B981', '#F59E0B', '#EF4444'][:len(models)]
                )])
                
                fig.update_layout(
                    title="Model Weights in Ensemble",
                    xaxis_title="Model",
                    yaxis_title="Weight",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Feature selection report
    if results.get('feature_selection_report'):
        st.markdown("---")
        st.markdown("#### 🔍 Feature Selection")
        
        report = results['feature_selection_report']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Original Features", report['original_features'])
        
        with col2:
            st.metric("Selected Features", report['final_features'])
        
        with col3:
            st.metric("Reduction", f"{report['reduction_percentage']:.1f}%")
        
        # Selection steps
        with st.expander("📋 Selection Steps"):
            for step in report['steps']:
                st.write(f"**{step['step']}:** Removed {step['removed']}, Kept {step['remaining']}")
    
    # Calibration metrics
    if results.get('calibration_metrics'):
        st.markdown("---")
        st.markdown("#### 📏 Probability Calibration")
        
        metrics = results['calibration_metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Brier Score", f"{metrics['brier_score']:.4f}", help="Lower is better")
        
        with col2:
            st.metric("Log Loss", f"{metrics['log_loss']:.4f}", help="Lower is better")
        
        with col3:
            st.metric("ECE", f"{metrics['expected_calibration_error']:.4f}", help="Expected Calibration Error - lower is better")
        
        with col4:
            st.metric("MCE", f"{metrics['maximum_calibration_error']:.4f}", help="Maximum Calibration Error - lower is better")
    
    # Feature importance
    if results.get('feature_importance'):
        st.markdown("---")
        st.markdown("#### 📊 Top Feature Importance")
        
        importance = results['feature_importance']
        
        # Sort and get top 15
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:15]
        
        features = [f for f, _ in sorted_importance]
        importances = [i for _, i in sorted_importance]
        
        fig = go.Figure(data=[go.Bar(
            x=importances,
            y=features,
            orientation='h',
            marker_color='#3B82F6'
        )])
        
        fig.update_layout(
            title="Top 15 Most Important Features",
            xaxis_title="Importance",
            yaxis_title="Feature",
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Download model info
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"✅ Model saved as: **{results['version']}**")
    
    with col2:
        if st.button("📥 Download Model Metadata"):
            # Create metadata JSON
            metadata = {
                'version': results['version'],
                'train_accuracy': float(results['train_accuracy']),
                'test_accuracy': float(results['test_accuracy']),
                'cv_mean': float(results['cv_mean']),
                'cv_std': float(results['cv_std']),
                'training_samples': int(results['training_samples']),
                'training_duration': float(results['training_duration']),
                'training_date': str(results['training_date']),
                'feature_count': len(results.get('selected_features', []))
            }
            
            import json
            metadata_json = json.dumps(metadata, indent=2)
            
            st.download_button(
                label="📥 Download",
                data=metadata_json,
                file_name=f"model_{results['version']}_metadata.json",
                mime="application/json"
            )


if __name__ == "__main__":
    # For testing
    st.set_page_config(layout="wide")
    render_ml_training_panel()
