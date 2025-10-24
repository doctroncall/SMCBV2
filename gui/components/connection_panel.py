"""
MT5 Connection Panel
Dedicated UI for connecting/disconnecting from MT5
"""
import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.mt5.connection import get_mt5_connection, MT5Connection


def render_connection_panel():
    """Render MT5 connection control panel"""
    
    st.markdown("### 🔌 MT5 Connection Manager")
    
    # Initialize session state
    if 'mt5_connection' not in st.session_state:
        st.session_state.mt5_connection = get_mt5_connection()

    connection: MT5Connection = st.session_state.mt5_connection
    is_connected = connection.is_connected()
    
    # Connection status display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if is_connected:
            st.success("🟢 **CONNECTED**")
            
            # Show account info
            account_info = connection.get_account_info()
            if account_info:
                st.markdown(f"""
                **Account:** {account_info['login']}  
                **Server:** {account_info['server']}  
                **Balance:** {account_info['balance']} {account_info['currency']}  
                **Company:** {account_info['company']}
                """)
                
                if connection._last_connection_time:
                    elapsed = datetime.now() - connection._last_connection_time
                    hours = int(elapsed.total_seconds() // 3600)
                    minutes = int((elapsed.total_seconds() % 3600) // 60)
                    st.caption(f"Connected for: {hours}h {minutes}m")
        else:
            st.error("🔴 **DISCONNECTED**")
            
            # No last error accessor; rely on reconnect feedback
    
    with col2:
        # Connection time indicator
        if is_connected and connector.connection_time:
            st.metric(
                "Uptime",
                f"{int((datetime.now() - connector.connection_time).total_seconds() // 60)}m"
            )
    
    st.markdown("---")
    
    # Credentials display removed to avoid leaking details
    
    st.markdown("---")
    
    # Control buttons
    st.markdown("#### 🎮 Controls")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button(
            "🔌 CONNECT" if not is_connected else "🔌 RECONNECT",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Connecting to MT5..."):
                try:
                    if is_connected:
                        connection.disconnect()
                    success = connection.connect()
                    message = "Connected" if success else "Failed"
                except Exception as e:
                    success = False
                    message = str(e)
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    with col2:
        if st.button(
            "⛔ DISCONNECT",
            type="secondary",
            use_container_width=True,
            disabled=not is_connected
        ):
            with st.spinner("Disconnecting..."):
                success = connection.disconnect()
                message = "✓ Disconnected successfully" if success else "Disconnect failed"
                
                if success:
                    st.info(f"ℹ️ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    with col3:
        if st.button(
            "🔄 Check Status",
            use_container_width=True
        ):
            st.rerun()
    
    # Connection instructions
    if not is_connected:
        st.markdown("---")
        st.markdown("#### 💡 Connection Instructions")
        
        st.info("""
        **To connect:**
        1. Click the **🔌 CONNECT** button
        2. Wait for connection to establish (5-10 seconds)
        3. Check the green status indicator
        
        **If connection fails:**
        - Check that MT5 is installed
        - Verify internet connection
        - Check firewall settings
        - See console output for detailed errors
        """)


def render_connection_widget():
    """Render minimal connection status widget for other pages"""
    
    if 'mt5_connection' not in st.session_state:
        st.session_state.mt5_connection = get_mt5_connection()

    connection: MT5Connection = st.session_state.mt5_connection
    if connection.is_connected():
        account_info = connection.get_account_info()
        if account_info:
            st.success(f"🟢 MT5 Connected: {account_info['login']} @ {account_info['server']}")
        else:
            st.success("🟢 MT5 Connected")
    else:
        st.error("🔴 MT5 Disconnected - Go to Settings tab → MT5 Connection to connect")


def get_connection_status() -> dict:
    """Get current MT5 connection status (for use in other components)"""
    
    if 'mt5_connection' not in st.session_state:
        st.session_state.mt5_connection = get_mt5_connection()

    connection: MT5Connection = st.session_state.mt5_connection
    return connection.get_connection_status()


def get_mt5_connector():
    """Backward-compat: return MT5Connection as 'connector'"""
    if 'mt5_connection' not in st.session_state:
        st.session_state.mt5_connection = get_mt5_connection()
    return st.session_state.mt5_connection
