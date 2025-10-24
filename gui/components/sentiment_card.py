"""
Sentiment Display Card
Shows current sentiment with visual indicator
"""
import streamlit as st
from typing import Dict, Any


def render_sentiment_card(sentiment_data: Dict[str, Any]):
    """
    Render sentiment display card
    
    Args:
        sentiment_data: Sentiment analysis results
    """
    sentiment = sentiment_data.get('sentiment', 'NEUTRAL')
    confidence = sentiment_data.get('confidence', 0.0)
    risk_level = sentiment_data.get('risk_level', 'MEDIUM')
    
    # Color mapping
    colors = {
        'BULLISH': '🟢',
        'BEARISH': '🔴',
        'NEUTRAL': '🟡'
    }
    
    emoji = colors.get(sentiment, '⚪')
    
    # Main sentiment display
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background-color: #1e293b; border-radius: 10px;">
        <h1 style="font-size: 4em; margin: 0;">{emoji}</h1>
        <h2 style="color: white; margin: 10px 0;">{sentiment}</h2>
        <h3 style="color: #94a3b8; margin: 5px 0;">Confidence: {confidence:.0%}</h3>
        <p style="color: #64748b;">Risk Level: {risk_level}</p>
    </div>
    """, unsafe_allow_html=True)


def render_confidence_bar(confidence: float):
    """
    Render confidence progress bar
    
    Args:
        confidence: Confidence value (0-1)
    """
    st.progress(confidence)
    
    # Confidence label
    if confidence >= 0.85:
        label = "VERY HIGH"
        color = "green"
    elif confidence >= 0.70:
        label = "HIGH"
        color = "green"
    elif confidence >= 0.55:
        label = "MODERATE"
        color = "orange"
    else:
        label = "LOW"
        color = "red"
    
    st.markdown(f"<p style='color: {color}; text-align: center;'>{label} ({confidence:.0%})</p>", 
                unsafe_allow_html=True)


def render_factors_table(factors: list):
    """
    Render contributing factors table
    
    Args:
        factors: List of factor dicts
    """
    if not factors:
        st.info("No factors available")
        return
    
    st.subheader("Contributing Factors")
    
    # Create table data
    import pandas as pd
    df = pd.DataFrame(factors)
    
    if 'component' in df.columns:
        df = df[['component', 'signal', 'confidence', 'contribution']]
        df.columns = ['Component', 'Signal', 'Confidence', 'Contribution']
        df['Confidence'] = df['Confidence'].apply(lambda x: f"{x:.0%}")
        df['Contribution'] = df['Contribution'].apply(lambda x: f"{x:.3f}")
        
        # Style based on signal
        def color_signal(val):
            if val == 'BULLISH':
                return 'background-color: #10B981; color: white'
            elif val == 'BEARISH':
                return 'background-color: #EF4444; color: white'
            else:
                return 'background-color: #F59E0B; color: white'
        
        styled_df = df.style.applymap(color_signal, subset=['Signal'])
        st.dataframe(styled_df, use_container_width=True)
