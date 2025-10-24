"""
MT5 Sentiment Analysis Bot - Main Streamlit Application
Professional trading bot with Smart Money Concepts and ML-powered sentiment analysis
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import AppConfig, DataConfig
# REMOVED: Old MT5Connection import - now using mt5_connector.py via GUI components
from src.mt5.data_fetcher import MT5DataFetcher
from src.analysis.sentiment_engine import SentimentEngine
from src.analysis.multi_timeframe import MultiTimeframeAnalyzer
from src.health.monitor import HealthMonitor
from src.database.repository import get_repository
from src.utils.logger import setup_logging, get_logger
from src.reporting.pdf_generator import PDFReportGenerator

# GUI Components
from gui.components.sentiment_card import render_sentiment_card, render_confidence_bar, render_factors_table
from gui.components.chart_panel import render_price_chart, render_indicator_charts, render_smc_analysis, render_mtf_chart
from gui.components.health_dashboard import render_health_dashboard, render_system_metrics, render_issues_list
from gui.components.metrics_panel import (
    render_metrics_panel, render_performance_chart, render_data_metrics,
    render_model_metrics, render_live_metrics_ticker
)
from gui.components.settings_panel import (
    render_mt5_settings, render_analysis_settings, render_model_settings,
    render_alert_settings, render_display_settings, render_data_management
)
from gui.components.live_logs import (
    render_live_logs, render_module_status, render_activity_feed,
    render_debug_console, update_module_status, add_activity, log_to_console
)
from gui.components.connection_panel import (
    render_connection_panel, render_connection_widget, get_mt5_connector
)
# New v2.0 Components
from gui.components.ml_training_panel import render_ml_training_panel
from gui.components.regime_panel import render_regime_panel

# Initialize logging
setup_logging()
logger = get_logger()

# Page configuration
st.set_page_config(
    page_title=AppConfig.PAGE_TITLE,
    page_icon=AppConfig.PAGE_ICON,
    layout=AppConfig.LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E40AF;
        text-align: center;
        padding: 1rem 0;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .status-healthy {
        background-color: #10B981;
        color: white;
    }
    .status-warning {
        background-color: #F59E0B;
        color: white;
    }
    .status-critical {
        background-color: #EF4444;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_components():
    """Initialize bot components (cached)"""
    try:
        logger.info("Initializing bot components", category="general")
        
        components = {
            'sentiment_engine': SentimentEngine(),
            'mtf_analyzer': MultiTimeframeAnalyzer(),
            'health_monitor': HealthMonitor(),
            'repository': get_repository(),
            'pdf_generator': PDFReportGenerator()
        }
        
        logger.info("Components initialized successfully", category="general")
        return components
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}", category="general")
        st.error(f"Failed to initialize components: {str(e)}")
        return None


def get_mt5_data(symbol: str, timeframes: list, data_fetcher):
    """Fetch MT5 data for multiple timeframes"""
    data_dict = {}
    
    for tf in timeframes:
        with st.spinner(f"Fetching {symbol} {tf} data..."):
            log_to_console(f"Fetching {symbol} {tf}...", "DEBUG")
            df = data_fetcher.get_ohlcv(symbol, tf, count=1000)
            if df is not None and not df.empty:
                data_dict[tf] = df
                log_to_console(f"✓ Fetched {len(df)} bars for {tf}", "DEBUG")
            else:
                log_to_console(f"✗ Failed to fetch {tf}", "WARNING")
    
    return data_dict


def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎯 MT5 Sentiment Analysis Bot</h1>', unsafe_allow_html=True)
    
    # Connection status widget at top
    render_connection_widget()
    
    # Live metrics ticker
    render_live_metrics_ticker()
    
    # Initialize components
    components = initialize_components()
    
    if components is None:
        st.error("Failed to initialize. Please check configuration and try again.")
        return
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Symbol selection
        symbol = st.selectbox(
            "Symbol",
            ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"],
            index=0
        )
        
        # Timeframe selection
        primary_tf = st.selectbox(
            "Primary Timeframe",
            ["M15", "H1", "H4", "D1"],
            index=1
        )
        
        # Multi-timeframe analysis
        enable_mtf = st.checkbox("Multi-Timeframe Analysis", value=True)
        
        if enable_mtf:
            mtf_timeframes = st.multiselect(
                "Additional Timeframes",
                ["M15", "H1", "H4", "D1"],
                default=["M15", "H4", "D1"]
            )
        
        # Auto-refresh
        auto_refresh = st.checkbox("Auto-Refresh", value=False)
        if auto_refresh:
            refresh_interval = st.slider("Refresh Interval (sec)", 30, 300, 60)
        
        st.divider()
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            analyze_button = st.button("🔄 Analyze", use_container_width=True, type="primary")
        with col2:
            health_check_button = st.button("🏥 Health Check", use_container_width=True)
    
    # Main content tabs (Added new v2.0 tabs)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📊 Analysis",
        "📈 Indicators",
        "📊 Metrics",
        "🧠 SMC",
        "🌡️ Market Regime",  # NEW v2.0
        "🤖 ML Training",  # NEW v2.0
        "🏥 Health",
        "⚙️ Settings",
        "📋 Logs & Debug"
    ])
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'health_results' not in st.session_state:
        st.session_state.health_results = None
    
    # Analysis Tab
    with tab1:
        st.header("Sentiment Analysis")
        
        if analyze_button or (auto_refresh and st.session_state.analysis_results is None):
            try:
                # Log to console and activity feed
                log_to_console("=== Starting Analysis ===", "INFO")
                add_activity("Analysis started", "🔍", "info")
                
                # MT5 Connection - use new connector
                update_module_status('mt5_connection', 'running', 'Checking MT5 connection...')
                log_to_console("Checking MT5 connection...", "INFO")
                
                # Get connection from session state
                connector = get_mt5_connector()
                log_to_console(f"Got connection instance from session state", "DEBUG")
                
                is_connected = connector.is_connected()
                log_to_console(f"Connector.is_connected() returned: {is_connected}", "DEBUG")
                
                if not is_connected:
                    st.error("❌ MT5 not connected. Please go to Settings → MT5 Connection and click CONNECT first.")
                    update_module_status('mt5_connection', 'error', 'Not connected')
                    add_activity("Analysis failed: MT5 not connected", "❌", "error")
                    log_to_console("MT5 not connected - user must connect manually", "ERROR")
                    return
                
                log_to_console("MT5 connected", "INFO")
                
                with st.spinner("Fetching data from MT5..."):
                    # Use managed connection for data fetcher
                    from src.mt5.connection import MT5Connection
                    data_fetcher = MT5DataFetcher(connection=connector)
                    
                update_module_status('mt5_connection', 'success', 'Connected successfully')
                add_activity("Connected to MT5", "✅", "success")
                log_to_console("MT5 connected successfully", "INFO")
                
                # Fetch data
                update_module_status('data_fetcher', 'running', f'Fetching data for {symbol}...')
                log_to_console(f"Fetching data for {symbol}", "INFO")
                
                if enable_mtf and mtf_timeframes:
                    all_timeframes = list(set([primary_tf] + mtf_timeframes))
                    log_to_console(f"Multi-timeframe enabled: {', '.join(all_timeframes)}", "DEBUG")
                else:
                    all_timeframes = [primary_tf]
                    log_to_console(f"Single timeframe: {primary_tf}", "DEBUG")
                
                data_dict = get_mt5_data(symbol, all_timeframes, data_fetcher)
                
                if not data_dict:
                    update_module_status('data_fetcher', 'error', 'Failed to fetch data')
                    add_activity("Data fetch failed", "❌", "error")
                    log_to_console("Failed to fetch data from MT5", "ERROR")
                    st.error("Failed to fetch data. Please check MT5 connection.")
                    return
                
                bars_fetched = sum(len(df) for df in data_dict.values())
                update_module_status('data_fetcher', 'success', f'Fetched {bars_fetched} bars')
                add_activity(f"Fetched {bars_fetched} bars across {len(data_dict)} timeframe(s)", "📊", "success")
                log_to_console(f"Data fetched successfully: {bars_fetched} total bars", "INFO")
                
                # Perform analysis
                if enable_mtf and len(data_dict) > 1:
                    log_to_console("Starting multi-timeframe analysis...", "INFO")
                    update_module_status('sentiment_engine', 'running', 'Multi-timeframe analysis...')
                    
                    with st.spinner("Performing multi-timeframe analysis..."):
                        results = components['mtf_analyzer'].analyze_multiple_timeframes(
                            data_dict, symbol
                        )
                        st.session_state.analysis_results = results
                        
                    update_module_status('sentiment_engine', 'success', 'MTF analysis complete')
                    add_activity(f"Multi-timeframe analysis complete for {symbol}", "🎯", "success")
                    log_to_console(f"MTF analysis completed for {len(data_dict)} timeframes", "INFO")
                else:
                    log_to_console(f"Starting sentiment analysis for {primary_tf}...", "INFO")
                    update_module_status('sentiment_engine', 'running', f'Analyzing {primary_tf}...')
                    
                    with st.spinner("Analyzing sentiment..."):
                        df = data_dict.get(primary_tf)
                        if df is None or df.empty:
                            update_module_status('sentiment_engine', 'error', f'No data for {primary_tf}')
                            log_to_console(f"No data returned for primary timeframe {primary_tf}", "ERROR")
                            st.error(f"No data returned for primary timeframe {primary_tf}")
                            return
                        log_to_console(f"Running technical indicators on {len(df)} bars...", "DEBUG")
                        
                        results = components['sentiment_engine'].analyze_sentiment(
                            df, symbol, primary_tf
                        )
                        st.session_state.analysis_results = results
                        
                    sentiment = results.get('sentiment', 'NEUTRAL')
                    confidence = results.get('confidence', 0) * 100
                    update_module_status('sentiment_engine', 'success', f'Analysis complete: {sentiment}')
                    add_activity(f"Sentiment: {sentiment} ({confidence:.0f}% confidence)", "🎯", "success")
                    log_to_console(f"Analysis complete: {sentiment} with {confidence:.1f}% confidence", "INFO")
                
                st.success("✓ Analysis complete!")
                log_to_console("=== Analysis Complete ===", "INFO")
                
            except Exception as e:
                logger.error(f"Error during analysis: {str(e)}", category="general")
                update_module_status('sentiment_engine', 'error', f'Error: {str(e)[:50]}')
                add_activity(f"Analysis failed: {str(e)[:50]}", "❌", "error")
                log_to_console(f"ERROR: {str(e)}", "ERROR")
                st.error(f"Analysis failed: {str(e)}")
                return
        
        # Display results
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            if enable_mtf and 'dominant_sentiment' in results:
                # Multi-timeframe results
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    sentiment_data = {
                        'sentiment': results['dominant_sentiment']['sentiment'],
                        'confidence': results['overall_confidence'],
                        'risk_level': 'MEDIUM'  # Could be calculated
                    }
                    render_sentiment_card(sentiment_data)
                
                with col2:
                    st.subheader("Timeframe Alignment")
                    alignment = results.get('alignment', {})
                    
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Alignment Score", f"{alignment.get('score', 0):.0%}")
                    col_b.metric("Aligned", "Yes" if alignment.get('aligned') else "No")
                    col_c.metric("Timeframes", alignment.get('total_timeframes', 0))
                    
                    # MTF Chart
                    if 'timeframe_results' in results:
                        render_mtf_chart(results['timeframe_results'])
                
                # Suggestions
                if 'suggestions' in results:
                    st.subheader("💡 Trading Suggestions")
                    for suggestion in results['suggestions']:
                        st.info(suggestion)
                
            else:
                # Single timeframe results
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    render_sentiment_card(results)
                    render_confidence_bar(results.get('confidence', 0.0))
                
                with col2:
                    st.subheader("Analysis Details")
                    st.write(f"**Symbol:** {results.get('symbol', 'N/A')}")
                    st.write(f"**Timeframe:** {results.get('timeframe', 'N/A')}")
                    st.write(f"**Price:** {results.get('price', 0):.5f}")
                    st.write(f"**Timestamp:** {results.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Contributing factors
                if 'factors' in results:
                    render_factors_table(results['factors'])
                
                # Insights
                if 'insights' in results:
                    st.subheader("💡 Key Insights")
                    for insight in results['insights']:
                        st.info(insight)
        
        else:
            st.info("👆 Click 'Analyze' to start sentiment analysis")
    
    # Indicators Tab
    with tab2:
        st.header("Technical Indicators")
        
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            if enable_mtf and 'timeframe_results' in results:
                # Show indicators for selected timeframe
                selected_tf = st.selectbox("Select Timeframe", list(results['timeframe_results'].keys()))
                tf_result = results['timeframe_results'][selected_tf]
                
                if 'technical_signals' in tf_result:
                    render_indicator_charts(tf_result['technical_signals'])
            elif 'technical_signals' in results:
                render_indicator_charts(results['technical_signals'])
            else:
                st.info("No indicator data available")
        else:
            st.info("Run analysis first to see indicators")
    
    # Metrics Tab
    with tab3:
        st.header("📊 Performance Metrics")
        
        # Store last update time in session state
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
        
        # Update timestamp after analysis
        if analyze_button:
            st.session_state.last_update = datetime.now()
        
        # Main metrics panel
        render_metrics_panel(
            repository=components['repository'],
            last_update=st.session_state.last_update,
            update_frequency=DataConfig.UPDATE_FREQUENCY,
            symbol=symbol,
            timeframe=primary_tf
        )
        
        st.markdown("---")
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            render_performance_chart(components['repository'])
        
        with col2:
            render_model_metrics(components['repository'])
        
        st.markdown("---")
        
        # Data metrics
        render_data_metrics(components['repository'], symbol, primary_tf)
    
    # SMC Tab
    with tab4:
        st.header("Smart Money Concepts")
        
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            if enable_mtf and 'timeframe_results' in results:
                selected_tf = st.selectbox("Timeframe", list(results['timeframe_results'].keys()), key="smc_tf")
                tf_result = results['timeframe_results'][selected_tf]
                
                if 'smc_signals' in tf_result:
                    render_smc_analysis(tf_result['smc_signals'])
            elif 'smc_signals' in results:
                render_smc_analysis(results['smc_signals'])
            else:
                st.info("No SMC data available")
        else:
            st.info("Run analysis first to see SMC analysis")
    
    # Market Regime Tab (NEW v2.0)
    with tab5:
        st.header("🌡️ Market Regime Detection")
        
        st.markdown("""
        <div style="background-color: #EEF2FF; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h4 style="color: #3B82F6; margin: 0;">✨ New in v2.0</h4>
            <p style="margin: 10px 0 0 0;">
                Intelligent market regime detection helps you adapt your trading to current market conditions.
                System analyzes trend strength, volatility levels, and volume patterns.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get data for regime analysis
        from gui.components.connection_panel import get_mt5_connector
        if get_mt5_connector().is_connected():
            # Fetch fresh data for regime analysis
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                regime_symbol = st.selectbox(
                    "Symbol for Regime Analysis",
                    ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"],
                    key="regime_symbol"
                )
            
            with col2:
                regime_tf = st.selectbox(
                    "Timeframe",
                    ["M15", "H1", "H4", "D1"],
                    index=2,  # Default to H4
                    key="regime_tf"
                )
            
            with col3:
                if st.button("🔍 Analyze Regime", type="primary"):
                    with st.spinner(f"Fetching {regime_symbol} {regime_tf} data..."):
                        try:
                            from src.mt5.data_fetcher import MT5DataFetcher
                            fetcher = MT5DataFetcher(connection=get_mt5_connector())
                            regime_df = fetcher.get_ohlcv(regime_symbol, regime_tf, count=500)
                            
                            if regime_df is not None and not regime_df.empty:
                                st.session_state.regime_data = regime_df
                                st.session_state.regime_symbol = regime_symbol
                                st.session_state.regime_tf = regime_tf
                                st.success(f"✓ Loaded {len(regime_df)} bars")
                            else:
                                st.error("Failed to fetch data")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
            # Display regime analysis
            if 'regime_data' in st.session_state:
                render_regime_panel(
                    st.session_state.regime_data,
                    st.session_state.get('regime_symbol', symbol),
                    st.session_state.get('regime_tf', primary_tf)
                )
            else:
                st.info("👆 Click 'Analyze Regime' to detect market conditions")
        else:
            st.warning("⚠️ Please connect to MT5 first (Settings → MT5 Connection)")
    
    # ML Training Tab (NEW v2.0)
    with tab6:
        st.header("🤖 ML Model Training")
        
        st.markdown("""
        <div style="background-color: #F0FDF4; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h4 style="color: #10B981; margin: 0;">✨ New in v2.0 - Professional ML Training</h4>
            <ul style="margin: 10px 0 0 20px;">
                <li><strong>70+ Features:</strong> Comprehensive market analysis</li>
                <li><strong>Smart Targets:</strong> 10+ pip meaningful moves only</li>
                <li><strong>SMOTE Balancing:</strong> Prevent bias</li>
                <li><strong>4-Model Ensemble:</strong> XGBoost, RF, LightGBM, CatBoost</li>
                <li><strong>Hyperparameter Tuning:</strong> Automated optimization (optional)</li>
                <li><strong>Calibrated Probabilities:</strong> Reliable confidence scores</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        render_ml_training_panel()
    
    # Health Tab
    with tab7:
        st.header("System Health")
        
        if health_check_button or st.session_state.health_results is None:
            with st.spinner("Running health check..."):
                try:
                    # Get connector (same instance used for connection)
                    connector = get_mt5_connector()
                    health_results = components['health_monitor'].perform_health_check(
                        connector=connector,
                        repository=components['repository']
                    )
                    st.session_state.health_results = health_results
                    st.success("✓ Health check complete")
                except Exception as e:
                    st.error(f"Health check failed: {str(e)}")
        
        if st.session_state.health_results:
            health_results = st.session_state.health_results
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                render_health_dashboard(health_results)
            
            with col2:
                render_system_metrics(health_results)
            
            st.divider()
            render_issues_list(health_results)
        else:
            st.info("👆 Click 'Health Check' to view system status")
    
    # Settings Tab
    with tab8:
        st.header("⚙️ Configuration")
        
        st.info("💡 **Configuration Settings:** Adjust bot parameters and preferences below.")
        
        settings_tab1, settings_tab2, settings_tab3, settings_tab4 = st.tabs([
            "🔌 MT5 Connection", "📊 Analysis", "🔔 Alerts", "💾 Data"
        ])
        
        with settings_tab1:
            # Use new connection panel
            render_connection_panel()
            
            st.markdown("---")
            st.markdown("### Advanced MT5 Settings")
            render_mt5_settings()
        
        with settings_tab2:
            st.markdown("### Analysis Configuration")
            st.markdown("---")
            render_analysis_settings()
            st.markdown("---")
            st.markdown("### ML Model Settings")
            render_model_settings()
        
        with settings_tab3:
            st.markdown("### Alert Configuration")
            st.markdown("---")
            render_alert_settings()
        
        with settings_tab4:
            st.markdown("### Display Settings")
            render_display_settings()
            st.markdown("---")
            st.markdown("### Data Management")
            render_data_management()
    
    # Logs & Debug Tab
    with tab9:
        st.header("📋 Logs & Debug Console")
        
        debug_tab1, debug_tab2, debug_tab3, debug_tab4 = st.tabs([
            "📋 Live Logs", "🔧 Module Status", "📡 Activity Feed", "🐛 Debug Console"
        ])
        
        with debug_tab1:
            render_live_logs(max_lines=100, auto_refresh=False, refresh_interval=5)
        
        with debug_tab2:
            render_module_status()
            
            if st.button("🔄 Refresh Module Status"):
                st.rerun()
        
        with debug_tab3:
            render_activity_feed()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh Activity"):
                    st.rerun()
            with col2:
                if st.button("🗑️ Clear Activity"):
                    st.session_state.activity_feed = []
                    st.success("Activity feed cleared!")
        
        with debug_tab4:
            render_debug_console()
            
            # Add test messages
            st.markdown("---")
            st.markdown("**Test Console:**")
            test_col1, test_col2 = st.columns(2)
            with test_col1:
                if st.button("📝 Add Test Log"):
                    log_to_console("Test log message", "INFO")
                    st.success("Test log added!")
            with test_col2:
                if st.button("⚠️ Add Test Warning"):
                    log_to_console("Test warning message", "WARNING")
                    st.warning("Test warning added!")
    
    # Footer Actions
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generate Report"):
            if st.session_state.analysis_results:
                try:
                    with st.spinner("Generating PDF report..."):
                        results = st.session_state.analysis_results
                        
                        # Prepare data for report
                        if 'dominant_sentiment' in results:
                            # Multi-timeframe results
                            analysis_data = {
                                'sentiment': results['dominant_sentiment']['sentiment'],
                                'confidence': results['overall_confidence'],
                                'risk_level': 'MEDIUM',
                                'insights': results.get('suggestions', [])
                            }
                        else:
                            # Single timeframe results
                            analysis_data = results
                        
                        # Get recent predictions from database
                        predictions = []
                        try:
                            recent_preds = components['repository'].get_predictions(
                                symbol_name=symbol,
                                limit=10
                            )
                            for pred in recent_preds:
                                predictions.append({
                                    'time': pred.timestamp.strftime('%Y-%m-%d %H:%M'),
                                    'sentiment': pred.sentiment,
                                    'confidence': pred.confidence,
                                    'result': pred.actual_outcome or 'Pending'
                                })
                        except:
                            pass
                        
                        # Calculate stats
                        stats = {
                            'total': len(predictions),
                            'correct': sum(1 for p in predictions if p['result'] == p['sentiment']),
                            'incorrect': sum(1 for p in predictions if p['result'] not in [p['sentiment'], 'Pending', None]),
                            'accuracy': 0.0
                        }
                        if stats['total'] > 0:
                            stats['accuracy'] = stats['correct'] / stats['total']
                        
                        # Generate report
                        report_path = components['pdf_generator'].generate_daily_report(
                            symbol=symbol,
                            analysis_results=analysis_data,
                            predictions=predictions,
                            stats=stats
                        )
                        
                        st.success(f"✓ Report generated successfully!")
                        
                        # Offer download
                        with open(report_path, 'rb') as f:
                            st.download_button(
                                label="📥 Download Report",
                                data=f,
                                file_name=Path(report_path).name,
                                mime="application/pdf"
                            )
                        
                        log_to_console(f"Generated report: {report_path}", "INFO")
                        add_activity(f"PDF report generated for {symbol}", "📊", "success")
                        
                except Exception as e:
                    st.error(f"Failed to generate report: {str(e)}")
                    logger.error(f"Report generation error: {str(e)}", category="reporting")
            else:
                st.warning("⚠️ Run analysis first to generate a report")
    
    with col2:
        if st.button("📥 Export Data"):
            if st.session_state.analysis_results:
                try:
                    results = st.session_state.analysis_results
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Prepare export data
                    if 'timeframe_results' in results:
                        # Multi-timeframe export
                        export_data = []
                        for tf, tf_result in results['timeframe_results'].items():
                            export_data.append({
                                'Timeframe': tf,
                                'Sentiment': tf_result.get('sentiment', 'N/A'),
                                'Confidence': f"{tf_result.get('confidence', 0):.2%}",
                                'Risk Level': tf_result.get('risk_level', 'N/A'),
                                'Price': tf_result.get('price', 0),
                                'Timestamp': tf_result.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
                            })
                        
                        # Add overall summary
                        export_data.append({
                            'Timeframe': 'OVERALL',
                            'Sentiment': results['dominant_sentiment']['sentiment'],
                            'Confidence': f"{results['overall_confidence']:.2%}",
                            'Risk Level': 'N/A',
                            'Price': '',
                            'Timestamp': results.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
                        })
                    else:
                        # Single timeframe export
                        export_data = [{
                            'Symbol': results.get('symbol', 'N/A'),
                            'Timeframe': results.get('timeframe', 'N/A'),
                            'Sentiment': results.get('sentiment', 'N/A'),
                            'Confidence': f"{results.get('confidence', 0):.2%}",
                            'Risk Level': results.get('risk_level', 'N/A'),
                            'Price': results.get('price', 0),
                            'Timestamp': results.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
                        }]
                    
                    # Convert to CSV
                    df_export = pd.DataFrame(export_data)
                    csv = df_export.to_csv(index=False)
                    
                    # Offer download
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"{symbol}_analysis_{timestamp}.csv",
                        mime="text/csv"
                    )
                    
                    st.success("✓ Data ready for export!")
                    log_to_console(f"Exported analysis data for {symbol}", "INFO")
                    add_activity(f"Analysis data exported for {symbol}", "📥", "success")
                    
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")
                    logger.error(f"Export error: {str(e)}", category="general")
            else:
                st.warning("⚠️ Run analysis first to export data")
    
    with col3:
        if st.button("📋 View Logs"):
            try:
                from config.settings import LOGS_DIR
                log_files = list(LOGS_DIR.glob("*.log"))
                
                if log_files:
                    # Sort by modification time (newest first)
                    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                    
                    st.subheader("📋 Log Files")
                    
                    # Show log file selector
                    selected_log = st.selectbox(
                        "Select log file:",
                        log_files,
                        format_func=lambda x: f"{x.name} ({x.stat().st_size / 1024:.1f} KB)"
                    )
                    
                    if selected_log:
                        # Show last N lines
                        num_lines = st.slider("Number of lines to display:", 10, 500, 100)
                        
                        try:
                            with open(selected_log, 'r') as f:
                                lines = f.readlines()
                                last_lines = lines[-num_lines:] if len(lines) > num_lines else lines
                                
                            st.code(''.join(last_lines), language='log')
                            
                            # Offer download
                            with open(selected_log, 'r') as f:
                                st.download_button(
                                    label="📥 Download Full Log",
                                    data=f.read(),
                                    file_name=selected_log.name,
                                    mime="text/plain"
                                )
                            
                            log_to_console(f"Viewed log file: {selected_log.name}", "INFO")
                            
                        except Exception as e:
                            st.error(f"Error reading log file: {str(e)}")
                else:
                    st.info("No log files found in logs directory")
                    
            except Exception as e:
                st.error(f"Failed to access logs: {str(e)}")
                logger.error(f"Log viewer error: {str(e)}", category="general")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}", category="general")
        st.error(f"Application error: {str(e)}")
