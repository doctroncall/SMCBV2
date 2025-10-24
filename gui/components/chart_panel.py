"""
Chart Display Panel
Shows interactive charts
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from src.reporting.charts import ChartGenerator


def render_price_chart(df: pd.DataFrame, symbol: str, indicators: Optional[Dict] = None):
    """
    Render price chart with indicators
    
    Args:
        df: DataFrame with OHLCV data
        symbol: Trading symbol
        indicators: Optional indicators to overlay
    """
    st.subheader(f"📊 {symbol} Price Chart")
    
    chart_gen = ChartGenerator()
    fig = chart_gen.create_candlestick_chart(df, symbol, indicators)
    
    st.plotly_chart(fig, use_container_width=True)


def render_indicator_charts(indicators_data: Dict[str, Any]):
    """
    Render indicator charts
    
    Args:
        indicators_data: Indicator calculation results
    """
    st.subheader("📈 Technical Indicators")
    
    # Create tabs for different indicator groups
    tabs = st.tabs(["Trend", "Momentum", "Volatility", "Volume"])
    
    with tabs[0]:
        st.write("**Trend Indicators**")
        if 'trend_signal' in indicators_data:
            trend = indicators_data['trend_signal']
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Signal", trend.get('signal', 'N/A'))
            with col2:
                st.metric("Confidence", f"{trend.get('confidence', 0):.0%}")
    
    with tabs[1]:
        st.write("**Momentum Indicators**")
        if 'momentum_signal' in indicators_data:
            momentum = indicators_data['momentum_signal']
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Signal", momentum.get('signal', 'N/A'))
            with col2:
                st.metric("Confidence", f"{momentum.get('confidence', 0):.0%}")
    
    with tabs[2]:
        st.write("**Volatility Indicators**")
        if 'volatility_signal' in indicators_data:
            volatility = indicators_data['volatility_signal']
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Volatility Level", volatility.get('volatility', 'N/A'))
            with col2:
                st.metric("ATR %", f"{volatility.get('atr_pct', 0):.2f}%")
    
    with tabs[3]:
        st.write("**Volume Indicators**")
        if 'volume_signal' in indicators_data:
            volume = indicators_data['volume_signal']
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Signal", volume.get('signal', 'N/A'))
            with col2:
                st.metric("Confidence", f"{volume.get('confidence', 0):.0%}")


def render_smc_analysis(smc_data: Dict[str, Any]):
    """
    Render SMC analysis panel
    
    Args:
        smc_data: SMC analysis results
    """
    st.subheader("🧠 Smart Money Concepts")
    
    # Market Structure
    if 'market_structure' in smc_data:
        structure = smc_data['market_structure']
        st.write("**Market Structure:**", structure.get('structure', 'N/A'))
        st.write("**Trend:**", structure.get('trend', 'N/A'))
    
    # Order Blocks
    if 'order_blocks' in smc_data:
        obs = smc_data['order_blocks']
        if obs:
            st.write(f"**Active Order Blocks:** {len([ob for ob in obs if ob.active])}")
            
            for ob in obs[:3]:  # Show top 3
                color = "🟢" if ob.type == 'bullish' else "🔴"
                st.write(f"{color} {ob.type.upper()}: {ob.start_price:.5f} - {ob.end_price:.5f} (Strength: {ob.strength:.2f})")
    
    # Fair Value Gaps
    if 'fair_value_gaps' in smc_data:
        fvgs = smc_data['fair_value_gaps']
        active_fvgs = [fvg for fvg in fvgs if fvg.active]
        if active_fvgs:
            st.write(f"**Active FVGs:** {len(active_fvgs)}")
    
    # Premium/Discount
    if 'premium_discount' in smc_data:
        pd_zone = smc_data['premium_discount']
        zone = pd_zone.get('zone', 'N/A')
        sentiment = pd_zone.get('sentiment', 'N/A')
        
        zone_color = {
            'PREMIUM': '🔴',
            'DISCOUNT': '🟢',
            'EQUILIBRIUM': '🟡'
        }.get(zone, '⚪')
        
        st.write(f"**Current Zone:** {zone_color} {zone}")
        st.write(f"**Zone Sentiment:** {sentiment}")


def render_mtf_chart(mtf_results: Dict[str, Dict[str, Any]]):
    """
    Render multi-timeframe analysis chart
    
    Args:
        mtf_results: Multi-timeframe results
    """
    st.subheader("🔍 Multi-Timeframe Analysis")
    
    chart_gen = ChartGenerator()
    fig = chart_gen.create_multi_timeframe_chart(mtf_results)
    
    st.plotly_chart(fig, use_container_width=True)
