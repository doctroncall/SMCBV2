"""
Settings Panel Component
Configuration and settings interface
"""
import streamlit as st
from typing import Dict, Any, List


def render_mt5_settings():
    """Render MT5 connection settings"""
    st.subheader("🔌 MT5 Connection")
    
    with st.expander("MT5 Settings", expanded=False):
        login = st.text_input("Account Number", type="password", key="mt5_login")
        password = st.text_input("Password", type="password", key="mt5_password")
        server = st.text_input("Server", key="mt5_server")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Settings"):
                st.success("Settings saved!")
        with col2:
            if st.button("🔄 Test Connection"):
                st.info("Testing connection...")


def render_analysis_settings():
    """Render analysis settings"""
    st.subheader("📊 Analysis Settings")
    
    with st.expander("Analysis Configuration", expanded=False):
        # Symbol selection
        symbols = st.multiselect(
            "Tracked Symbols",
            ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"],
            default=["EURUSD"]
        )
        
        # Timeframe selection
        timeframes = st.multiselect(
            "Active Timeframes",
            ["M15", "H1", "H4", "D1"],
            default=["H1", "H4"]
        )
        
        # Update frequency
        update_freq = st.slider(
            "Update Frequency (minutes)",
            min_value=1,
            max_value=60,
            value=5,
            step=1
        )
        
        # Lookback period
        lookback = st.number_input(
            "Lookback Bars",
            min_value=100,
            max_value=5000,
            value=1000,
            step=100
        )


def render_model_settings():
    """Render ML model settings"""
    st.subheader("🤖 Model Settings")
    
    with st.expander("Model Configuration", expanded=False):
        # Auto-retrain
        auto_retrain = st.checkbox("Auto-Retrain", value=True)
        
        if auto_retrain:
            retrain_schedule = st.selectbox(
                "Retrain Schedule",
                ["Hourly", "Daily", "Weekly"],
                index=1
            )
        
        # Confidence threshold
        min_confidence = st.slider(
            "Minimum Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.70,
            step=0.05,
            format="%.0%"
        )
        
        # Model version
        model_version = st.selectbox(
            "Active Model Version",
            ["v1.0.0", "v1.1.0", "v1.2.0"],
            index=0
        )


def render_alert_settings():
    """Render alert and notification settings"""
    st.subheader("🔔 Alerts & Notifications")
    
    with st.expander("Notification Settings", expanded=False):
        # Alert types
        st.write("**Alert Types:**")
        sentiment_change = st.checkbox("Sentiment Change", value=True)
        high_confidence = st.checkbox("High Confidence Signal (>85%)", value=True)
        system_error = st.checkbox("System Errors", value=True)
        connection_issues = st.checkbox("Connection Issues", value=True)
        
        st.write("")
        st.write("**Notification Methods:**")
        
        # Notification channels
        in_app = st.checkbox("In-App Notifications", value=True)
        email = st.checkbox("Email Notifications", value=False)
        
        if email:
            email_address = st.text_input("Email Address")
        
        telegram = st.checkbox("Telegram Notifications", value=False)
        
        if telegram:
            bot_token = st.text_input("Bot Token", type="password")
            chat_id = st.text_input("Chat ID")


def render_display_settings():
    """Render display settings"""
    st.subheader("🎨 Display Settings")
    
    with st.expander("Display Configuration", expanded=False):
        # Theme
        theme = st.selectbox(
            "Theme",
            ["Dark", "Light"],
            index=0
        )
        
        # Chart type
        chart_type = st.selectbox(
            "Chart Type",
            ["Candlestick", "Line", "Area"],
            index=0
        )
        
        # Display options
        show_grid = st.checkbox("Show Grid", value=True)
        show_volume = st.checkbox("Show Volume", value=True)
        show_indicators = st.checkbox("Show Indicators", value=True)
        animations = st.checkbox("Enable Animations", value=True)


def render_data_management():
    """Render data management settings"""
    st.subheader("💾 Data Management")
    
    with st.expander("Data Settings", expanded=False):
        # Database info
        st.write("**Database:**")
        st.info("SQLite - 234 MB / 127,845 records")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Backup Now"):
                st.success("Backup created!")
        
        with col2:
            if st.button("🗑️ Clean Old Data"):
                st.warning("Cleaning data...")
        
        with col3:
            if st.button("📥 Export Database"):
                st.info("Exporting...")
