"""
Live Logs Component
Real-time log viewer for the GUI
"""
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import time


class LiveLogViewer:
    """Real-time log viewer for Streamlit"""
    
    def __init__(self, log_file: str = "logs/app.log"):
        self.log_file = Path(log_file)
        self.max_lines = 100
        
    def get_recent_logs(self, lines: int = 50, level_filter: str = "ALL") -> List[str]:
        """Get recent log entries"""
        try:
            if not self.log_file.exists():
                return ["📝 No logs available yet. Start analyzing to generate logs."]
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            # Get last N lines
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Filter by level
            if level_filter != "ALL":
                recent = [line for line in recent if f"| {level_filter} " in line]
            
            return recent if recent else ["📝 No logs matching filter."]
            
        except Exception as e:
            return [f"❌ Error reading logs: {str(e)}"]
    
    def parse_log_entry(self, line: str) -> Dict[str, Any]:
        """Parse a log line into components"""
        try:
            parts = line.split("|")
            if len(parts) >= 3:
                return {
                    'timestamp': parts[0].strip(),
                    'level': parts[1].strip(),
                    'message': "|".join(parts[2:]).strip(),
                    'raw': line
                }
            return {'raw': line}
        except:
            return {'raw': line}
    
    def get_log_color(self, level: str) -> str:
        """Get color for log level"""
        colors = {
            'DEBUG': '#6c757d',
            'INFO': '#17a2b8',
            'WARNING': '#ffc107',
            'ERROR': '#dc3545',
            'CRITICAL': '#8b0000'
        }
        return colors.get(level, '#6c757d')
    
    def format_log_html(self, entry: Dict[str, Any]) -> str:
        """Format log entry as HTML"""
        if 'level' not in entry:
            return f"<div style='padding: 2px; font-family: monospace; font-size: 12px;'>{entry['raw']}</div>"
        
        level = entry['level']
        color = self.get_log_color(level)
        
        # Emoji mapping
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🔥'
        }
        emoji = emoji_map.get(level, '📝')
        
        return f"""
        <div style='padding: 5px; margin: 2px 0; border-left: 3px solid {color}; background-color: #1e1e1e; font-family: monospace; font-size: 11px;'>
            <span style='color: #888;'>{entry['timestamp']}</span>
            <span style='color: {color}; font-weight: bold; margin: 0 10px;'>{emoji} {level}</span>
            <span style='color: #fff;'>{entry['message']}</span>
        </div>
        """


def render_live_logs(
    max_lines: int = 100,
    auto_refresh: bool = True,
    refresh_interval: int = 5
):
    """
    Render live log viewer
    
    Args:
        max_lines: Maximum number of log lines to display
        auto_refresh: Enable auto-refresh
        refresh_interval: Refresh interval in seconds
    """
    st.markdown("### 📋 Live System Logs")
    
    # Controls
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    
    with col1:
        level_filter = st.selectbox(
            "Filter Level",
            ["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            key="log_level_filter"
        )
    
    with col2:
        log_count = st.selectbox(
            "Show Lines",
            [25, 50, 100, 200, 500],
            index=2,
            key="log_count"
        )
    
    with col3:
        auto_scroll = st.checkbox("Auto-scroll to bottom", value=True, key="auto_scroll")
    
    with col4:
        if st.button("🔄 Refresh", key="refresh_logs"):
            st.rerun()
    
    # Log viewer
    viewer = LiveLogViewer()
    logs = viewer.get_recent_logs(lines=log_count, level_filter=level_filter)
    
    # Stats
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Total Lines", len(logs))
    with col_b:
        error_count = sum(1 for log in logs if "ERROR" in log or "CRITICAL" in log)
        st.metric("Errors/Critical", error_count, delta="⚠️" if error_count > 0 else "✓")
    with col_c:
        warning_count = sum(1 for log in logs if "WARNING" in log)
        st.metric("Warnings", warning_count)
    
    st.markdown("---")
    
    # Display logs
    log_container = st.container()
    
    with log_container:
        if logs:
            # Format logs as HTML for better styling
            html_logs = []
            for log_line in logs:
                entry = viewer.parse_log_entry(log_line)
                html_logs.append(viewer.format_log_html(entry))
            
            # Combine and display
            combined_html = f"""
            <div style='background-color: #0e0e0e; padding: 15px; border-radius: 5px; max-height: 600px; overflow-y: auto;'>
                {''.join(html_logs)}
            </div>
            """
            st.markdown(combined_html, unsafe_allow_html=True)
        else:
            st.info("📝 No logs available. Start analyzing to generate logs.")
    
    # Auto-refresh indicator
    if auto_refresh:
        st.caption(f"🔄 Auto-refreshing every {refresh_interval} seconds...")
        time.sleep(refresh_interval)
        st.rerun()


def render_module_status():
    """Render real-time module status"""
    st.markdown("### 🔧 Module Status")
    
    # Initialize session state for module tracking
    if 'module_status' not in st.session_state:
        st.session_state.module_status = {
            'mt5_connection': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'data_fetcher': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'indicators': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'smc_analyzer': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'sentiment_engine': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'database': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'health_monitor': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
        }
    
    # Display module status
    col1, col2 = st.columns(2)
    
    status_emoji = {
        'idle': '⚪',
        'running': '🔵',
        'success': '🟢',
        'warning': '🟡',
        'error': '🔴'
    }
    
    modules_col1 = ['mt5_connection', 'data_fetcher', 'indicators', 'smc_analyzer']
    modules_col2 = ['sentiment_engine', 'database', 'health_monitor']
    
    with col1:
        for module_key in modules_col1:
            module = st.session_state.module_status[module_key]
            status = module['status']
            emoji = status_emoji.get(status, '⚪')
            
            st.markdown(f"""
            **{emoji} {module_key.replace('_', ' ').title()}**  
            Status: `{status}`  
            Last Action: {module['last_action']}  
            {f"Time: {module['timestamp'].strftime('%H:%M:%S')}" if module['timestamp'] else ""}
            """)
            st.markdown("---")
    
    with col2:
        for module_key in modules_col2:
            module = st.session_state.module_status[module_key]
            status = module['status']
            emoji = status_emoji.get(status, '⚪')
            
            st.markdown(f"""
            **{emoji} {module_key.replace('_', ' ').title()}**  
            Status: `{status}`  
            Last Action: {module['last_action']}  
            {f"Time: {module['timestamp'].strftime('%H:%M:%S')}" if module['timestamp'] else ""}
            """)
            st.markdown("---")


def update_module_status(module_name: str, status: str, action: str):
    """Update module status in session state"""
    if 'module_status' not in st.session_state:
        st.session_state.module_status = {
            'mt5_connection': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'data_fetcher': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'indicators': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'smc_analyzer': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'sentiment_engine': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'database': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
            'health_monitor': {'status': 'idle', 'last_action': 'Not started', 'timestamp': None},
        }
    
    # Update the specific module
    st.session_state.module_status[module_name] = {
        'status': status,
        'last_action': action,
        'timestamp': datetime.now()
    }
    
    # Print to console for debugging
    print(f"[DEBUG] update_module_status({module_name}) -> status={status}, action={action}")


def render_activity_feed():
    """Render real-time activity feed"""
    st.markdown("### 📡 Recent Activity")
    
    # Initialize activity feed in session state
    if 'activity_feed' not in st.session_state:
        st.session_state.activity_feed = []
    
    # Display recent activities
    if st.session_state.activity_feed:
        for activity in reversed(st.session_state.activity_feed[-20:]):  # Last 20 activities
            timestamp = activity['timestamp'].strftime('%H:%M:%S')
            icon = activity.get('icon', '📌')
            message = activity.get('message', '')
            level = activity.get('level', 'info')
            
            # Color based on level
            color_map = {
                'info': '#17a2b8',
                'success': '#28a745',
                'warning': '#ffc107',
                'error': '#dc3545'
            }
            color = color_map.get(level, '#17a2b8')
            
            st.markdown(f"""
            <div style='padding: 8px; margin: 5px 0; border-left: 3px solid {color}; background-color: #1e1e1e;'>
                <span style='color: #888; font-size: 11px;'>{timestamp}</span>
                <span style='margin: 0 10px;'>{icon}</span>
                <span style='color: #fff;'>{message}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("📝 No recent activity. Start analyzing to see real-time updates.")


def add_activity(message: str, icon: str = "📌", level: str = "info"):
    """Add activity to the feed"""
    if 'activity_feed' not in st.session_state:
        st.session_state.activity_feed = []
    
    st.session_state.activity_feed.append({
        'timestamp': datetime.now(),
        'icon': icon,
        'message': message,
        'level': level
    })
    
    # Keep only last 100 activities
    if len(st.session_state.activity_feed) > 100:
        st.session_state.activity_feed = st.session_state.activity_feed[-100:]


def render_debug_console():
    """Render interactive debug console"""
    st.markdown("### 🔧 Debug Console")
    
    st.info("💡 **Tip:** This console shows detailed execution flow. Enable 'Verbose Mode' for maximum detail.")
    
    # Console controls
    col1, col2 = st.columns(2)
    
    with col1:
        verbose_mode = st.checkbox("🔍 Verbose Mode", value=False, help="Show detailed debug information")
    
    with col2:
        if st.button("🗑️ Clear Console"):
            if 'debug_console' in st.session_state:
                st.session_state.debug_console = []
            st.success("Console cleared!")
    
    # Initialize console in session state
    if 'debug_console' not in st.session_state:
        st.session_state.debug_console = []
    
    # Display console output
    console_container = st.container()
    
    with console_container:
        if st.session_state.debug_console:
            console_text = "\n".join(st.session_state.debug_console[-100:])  # Last 100 lines
            st.code(console_text, language="log")
        else:
            st.caption("Console is empty. Start an operation to see debug output.")


def log_to_console(message: str, level: str = "INFO"):
    """Log message to debug console"""
    if 'debug_console' not in st.session_state:
        st.session_state.debug_console = []
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    formatted_message = f"[{timestamp}] [{level}] {message}"
    
    st.session_state.debug_console.append(formatted_message)
    
    # Keep only last 500 lines
    if len(st.session_state.debug_console) > 500:
        st.session_state.debug_console = st.session_state.debug_console[-500:]
