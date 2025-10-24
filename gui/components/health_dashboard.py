"""
Health Dashboard Component
Display system health metrics
"""
import streamlit as st
from typing import Dict, Any


def render_health_dashboard(health_data: Dict[str, Any]):
    """
    Render system health dashboard
    
    Args:
        health_data: Health check results
    """
    st.subheader("🏥 System Health")
    
    overall_status = health_data.get('overall_status', 'UNKNOWN')
    
    # Status indicator
    status_colors = {
        'HEALTHY': '🟢',
        'WARNING': '🟡',
        'CRITICAL': '🔴',
        'UNKNOWN': '⚪'
    }
    
    status_emoji = status_colors.get(overall_status, '⚪')
    
    st.markdown(f"""
    <div style="text-align: center; padding: 10px; background-color: #1e293b; border-radius: 5px;">
        <h3>{status_emoji} {overall_status}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # Component health
    components = health_data.get('components', {})
    
    cols = st.columns(2)
    
    with cols[0]:
        # MT5 Connection
        if 'mt5' in components:
            mt5 = components['mt5']
            st.write("**MT5 Connection:**")
            st.write(f"Status: {status_colors.get(mt5.get('status'), '⚪')} {mt5.get('status')}")
            if mt5.get('ping_ms'):
                st.write(f"Ping: {mt5['ping_ms']}ms")
        
        # System Resources
        if 'system' in components:
            system = components['system']
            st.write("**System Resources:**")
            if 'cpu' in system:
                st.write(f"CPU: {system['cpu']['percent']:.1f}%")
            if 'memory' in system:
                st.write(f"Memory: {system['memory']['percent']:.1f}%")
    
    with cols[1]:
        # Data Pipeline
        if 'pipeline' in components:
            pipeline = components['pipeline']
            st.write("**Data Pipeline:**")
            st.write(f"Status: {status_colors.get(pipeline.get('status'), '⚪')} {pipeline.get('status')}")
            if 'symbols_count' in pipeline:
                st.write(f"Symbols: {pipeline['symbols_count']}")
        
        # ML Model
        if 'model' in components:
            model = components['model']
            st.write("**ML Model:**")
            st.write(f"Status: {status_colors.get(model.get('status'), '⚪')} {model.get('status')}")
            if model.get('accuracy'):
                st.write(f"Accuracy: {model['accuracy']:.1%}")


def render_system_metrics(health_data: Dict[str, Any]):
    """
    Render detailed system metrics
    
    Args:
        health_data: Health check results
    """
    if 'components' not in health_data:
        return
    
    system = health_data['components'].get('system', {})
    
    if 'cpu' in system and 'memory' in system and 'disk' in system:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            cpu_percent = system['cpu']['percent']
            st.metric("CPU Usage", f"{cpu_percent:.1f}%", 
                     delta=None,
                     delta_color="inverse")
        
        with col2:
            mem_percent = system['memory']['percent']
            st.metric("Memory Usage", f"{mem_percent:.1f}%",
                     delta=None,
                     delta_color="inverse")
        
        with col3:
            disk_percent = system['disk']['percent']
            st.metric("Disk Usage", f"{disk_percent:.1f}%",
                     delta=None,
                     delta_color="inverse")


def render_issues_list(health_data: Dict[str, Any]):
    """
    Render list of system issues
    
    Args:
        health_data: Health check results
    """
    issues = health_data.get('issues', [])
    
    if issues:
        st.warning(f"⚠️ {len(issues)} issue(s) detected:")
        for issue in issues:
            st.write(f"• {issue}")
    else:
        st.success("✓ All systems operational")
