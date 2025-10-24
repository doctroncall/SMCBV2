"""
Market Regime Visualization Panel
Display market regime detection results
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.analysis.regime_detector import RegimeDetector


def render_regime_panel(df, symbol="UNKNOWN", timeframe="H1"):
    """
    Render market regime detection panel
    
    Args:
        df: DataFrame with OHLCV data
        symbol: Trading symbol
        timeframe: Timeframe string
    """
    st.markdown("### 🌡️ Market Regime Detection")
    
    st.info("""
    **New in v2.0:** Intelligent market regime detection for adaptive trading.
    System analyzes trend, volatility, and volume to identify optimal trading conditions.
    """)
    
    if df is None or df.empty:
        st.warning("No data available. Run analysis first.")
        return
    
    try:
        # Initialize detector
        detector = RegimeDetector()
        
        # Detect current regime
        with st.spinner("Analyzing market regimes..."):
            regime = detector.detect_regime(df, lookback=50)
        
        # Display current regime
        st.markdown("---")
        st.markdown("#### 📍 Current Market Regime")
        
        col1, col2, col3 = st.columns(3)
        
        # Trend regime
        with col1:
            trend = regime['trend']
            
            # Color based on trend
            trend_colors = {
                'STRONG_UPTREND': '#10B981',
                'UPTREND': '#34D399',
                'RANGING': '#6B7280',
                'DOWNTREND': '#F87171',
                'STRONG_DOWNTREND': '#EF4444'
            }
            
            color = trend_colors.get(trend['regime'], '#6B7280')
            
            st.markdown(f"""
            <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="color: white; margin: 0;">Trend</h3>
                <h2 style="color: white; margin: 10px 0;">{trend['regime'].replace('_', ' ')}</h2>
                <p style="color: white; margin: 0;">ADX: {trend['adx']:.1f}</p>
                <p style="color: white; margin: 0;">Efficiency: {trend['efficiency']:.2%}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Volatility regime
        with col2:
            vol = regime['volatility']
            
            vol_colors = {
                'VERY_LOW': '#3B82F6',
                'LOW': '#60A5FA',
                'NORMAL': '#10B981',
                'HIGH': '#F59E0B',
                'VERY_HIGH': '#EF4444'
            }
            
            color = vol_colors.get(vol['regime'], '#10B981')
            
            st.markdown(f"""
            <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="color: white; margin: 0;">Volatility</h3>
                <h2 style="color: white; margin: 10px 0;">{vol['regime'].replace('_', ' ')}</h2>
                <p style="color: white; margin: 0;">ATR: {vol['atr_pct']:.3f}%</p>
                <p style="color: white; margin: 0;">Percentile: {vol['atr_percentile']:.0%}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Volume regime
        with col3:
            volume = regime['volume']
            
            volume_colors = {
                'DRY': '#94A3B8',
                'NORMAL': '#10B981',
                'ELEVATED': '#F59E0B',
                'SURGE': '#EF4444'
            }
            
            color = volume_colors.get(volume['regime'], '#10B981')
            
            st.markdown(f"""
            <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="color: white; margin: 0;">Volume</h3>
                <h2 style="color: white; margin: 10px 0;">{volume['regime']}</h2>
                <p style="color: white; margin: 0;">Relative: {volume['relative_volume']:.2f}x</p>
                <p style="color: white; margin: 0;">OBV: {volume['obv_trend']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Composite assessment
        st.markdown("---")
        st.markdown("#### 🎯 Trading Favorability Assessment")
        
        composite = regime['composite']
        
        # Favorability meter
        favorability_colors = {
            'FAVORABLE': '#10B981',
            'MODERATE': '#F59E0B',
            'CAUTIOUS': '#6B7280',
            'UNFAVORABLE': '#EF4444'
        }
        
        color = favorability_colors.get(composite['favorability'], '#6B7280')
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div style="background-color: {color}; padding: 30px; border-radius: 10px; text-align: center;">
                <h2 style="color: white; margin: 0; font-size: 2.5rem;">{composite['favorability']}</h2>
                <p style="color: white; margin-top: 10px; font-size: 1.2rem;">Trading Conditions</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Regime Scores:**")
            
            # Trend score gauge
            fig_trend = go.Figure(go.Indicator(
                mode="gauge+number",
                value=composite['trend_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Trend Direction"},
                gauge={
                    'axis': {'range': [-1, 1]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [-1, -0.3], 'color': "#EF4444"},
                        {'range': [-0.3, 0.3], 'color': "#6B7280"},
                        {'range': [0.3, 1], 'color': "#10B981"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0
                    }
                }
            ))
            
            fig_trend.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Detailed metrics
        st.markdown("---")
        st.markdown("#### 📊 Detailed Regime Metrics")
        
        with st.expander("📈 Trend Details", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("ADX", f"{trend['adx']:.2f}")
                st.metric("Direction", trend['direction'])
            
            with col2:
                st.metric("Efficiency", f"{trend['efficiency']:.2%}")
                st.metric("Strength", f"{trend['strength']:.2%}")
            
            with col3:
                st.metric("vs EMA20", f"{trend['price_vs_ema20']:.2f}%")
                st.metric("vs EMA50", f"{trend['price_vs_ema50']:.2f}%")
        
        with st.expander("📊 Volatility Details", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("ATR %", f"{vol['atr_pct']:.3f}%")
                st.metric("BB Width", f"{vol['bb_width']:.3f}%")
            
            with col2:
                st.metric("ATR Percentile", f"{vol['atr_percentile']:.0%}")
                st.metric("Expanding", "Yes" if vol['is_expanding'] else "No")
            
            with col3:
                st.metric("Hist. Vol", f"{vol['historical_volatility']:.2f}%")
        
        with st.expander("📊 Volume Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Relative Volume", f"{volume['relative_volume']:.2f}x")
                st.metric("Volume Percentile", f"{volume['percentile']:.0%}")
            
            with col2:
                st.metric("OBV Trend", volume['obv_trend'])
        
        # Trading recommendations
        st.markdown("---")
        st.markdown("#### 💡 Regime-Based Trading Recommendations")
        
        recommendations = get_trading_recommendations(regime)
        
        for rec_type, rec_text in recommendations.items():
            if rec_type == "warning":
                st.warning(f"⚠️ {rec_text}")
            elif rec_type == "success":
                st.success(f"✅ {rec_text}")
            elif rec_type == "info":
                st.info(f"ℹ️ {rec_text}")
        
        # Historical regime chart
        st.markdown("---")
        st.markdown("#### 📈 Regime History (Last 100 bars)")
        
        render_regime_history(df, detector)
        
    except Exception as e:
        st.error(f"Error analyzing regimes: {str(e)}")
        st.exception(e)


def get_trading_recommendations(regime):
    """Generate trading recommendations based on regime"""
    recommendations = {}
    
    composite = regime['composite']
    trend = regime['trend']
    vol = regime['volatility']
    
    if composite['favorability'] == 'FAVORABLE':
        recommendations['success'] = "Excellent trading conditions. All regimes aligned."
        
        if trend['regime'] in ['STRONG_UPTREND', 'UPTREND']:
            recommendations['info'] = "Consider long positions with trend. Use pullbacks for entry."
        else:
            recommendations['info'] = "Consider short positions with trend. Use rallies for entry."
    
    elif composite['favorability'] == 'MODERATE':
        recommendations['info'] = "Moderate trading conditions. Trade with caution."
        recommendations['warning'] = "Use tighter stops and smaller position sizes."
    
    elif composite['favorability'] == 'CAUTIOUS':
        recommendations['warning'] = "Mixed signals. Wait for clearer direction."
        recommendations['info'] = "Consider reducing exposure or staying flat."
    
    else:  # UNFAVORABLE
        recommendations['warning'] = "Unfavorable conditions for trading."
        recommendations['info'] = "Consider staying out of market until conditions improve."
    
    # Volatility warnings
    if vol['regime'] == 'VERY_HIGH':
        recommendations['warning'] = "Extreme volatility detected. Expect large price swings."
    elif vol['regime'] == 'VERY_LOW':
        recommendations['info'] = "Very low volatility - potential breakout coming."
    
    return recommendations


def render_regime_history(df, detector):
    """Render historical regime visualization"""
    try:
        # Add regime features to dataframe
        df_with_regimes = detector.add_regime_features(df.copy(), lookback=50)
        
        # Get last 100 bars
        df_plot = df_with_regimes.tail(100)
        
        # Create subplot
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price with Trend Regime', 'Volatility Regime', 'Composite Score'),
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # Price with trend regime coloring
        colors = []
        for val in df_plot['regime_trend']:
            if val >= 1:
                colors.append('#10B981')  # Green for uptrend
            elif val <= -1:
                colors.append('#EF4444')  # Red for downtrend
            else:
                colors.append('#6B7280')  # Gray for ranging
        
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot['Close'],
                mode='markers+lines',
                name='Price',
                marker=dict(color=colors, size=4),
                line=dict(width=1)
            ),
            row=1, col=1
        )
        
        # Volatility regime
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot['regime_volatility'],
                mode='lines',
                name='Volatility',
                fill='tozeroy',
                line=dict(color='#F59E0B', width=2)
            ),
            row=2, col=1
        )
        
        # Composite score
        fig.add_trace(
            go.Scatter(
                x=df_plot.index,
                y=df_plot['regime_composite'],
                mode='lines',
                name='Composite',
                fill='tozeroy',
                line=dict(color='#3B82F6', width=2)
            ),
            row=3, col=1
        )
        
        # Add zero line to composite
        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=3, col=1)
        
        fig.update_layout(
            height=600,
            showlegend=False,
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volatility", row=2, col=1)
        fig.update_yaxes(title_text="Score", row=3, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering regime history: {str(e)}")


if __name__ == "__main__":
    # For testing
    import pandas as pd
    import numpy as np
    
    st.set_page_config(layout="wide")
    
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=200, freq='1H')
    trend = np.linspace(1.08, 1.10, 200)
    noise = np.random.normal(0, 0.0005, 200)
    
    df = pd.DataFrame({
        'Open': trend + noise - 0.0001,
        'High': trend + noise + 0.0002,
        'Low': trend + noise - 0.0002,
        'Close': trend + noise,
        'Volume': np.random.randint(1000, 10000, 200)
    }, index=dates)
    
    render_regime_panel(df, "EURUSD", "H1")
