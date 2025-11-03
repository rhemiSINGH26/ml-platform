"""
Streamlit dashboard main entry point.
"""

import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.logging_config import setup_logging

# Setup logging
setup_logging()

# Page configuration
st.set_page_config(
    page_title="MLOps Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Main page
st.markdown('<div class="main-header">🏥 MLOps Heart Disease Prediction</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Production ML System with Autonomous Monitoring & Remediation</div>', unsafe_allow_html=True)

# Introduction
st.write("""
Welcome to the MLOps Dashboard! This system provides:

- 📊 **Real-time Model Performance Monitoring** - Track accuracy, F1 score, and other metrics
- 🔍 **Data & Model Drift Detection** - Automatic detection using Evidently AI
- ⚙️ **Human-in-Loop Approvals** - Review and approve autonomous agent actions
- 📈 **Historical Trends** - Visualize performance over time
- 🤖 **Autonomous Agent Activity** - Monitor automated remediation actions
""")

# System overview
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🎯 Active Model",
        value="Random Forest",
        delta="Best performer"
    )

with col2:
    st.metric(
        label="📊 Validation F1",
        value="0.87",
        delta="+0.03"
    )

with col3:
    st.metric(
        label="🔄 Last Training",
        value="2 hours ago",
        delta="Auto-triggered"
    )

with col4:
    st.metric(
        label="✅ System Status",
        value="Healthy",
        delta="All systems operational"
    )

st.divider()

# Quick links
st.subheader("📑 Quick Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📊 **Model Performance**\n\nView current model metrics, confusion matrix, ROC curves, and feature importance.")

with col2:
    st.warning("🔍 **Drift Analysis**\n\nMonitor data and prediction drift with Evidently reports and alerts.")

with col3:
    st.success("⚙️ **Approvals**\n\nReview pending actions from the autonomous agent requiring human approval.")

st.divider()

# Recent activity
st.subheader("📋 Recent Activity")

activity_data = [
    {"time": "5 min ago", "event": "Data validation passed", "status": "✅ Success"},
    {"time": "2 hours ago", "event": "Model retrained - drift detected", "status": "🔄 Completed"},
    {"time": "4 hours ago", "event": "Alert: Prediction drift threshold exceeded", "status": "⚠️ Warning"},
    {"time": "1 day ago", "event": "Model deployed to production", "status": "✅ Success"},
]

for activity in activity_data:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.text(activity["time"])
    with col2:
        st.text(activity["event"])
    with col3:
        st.text(activity["status"])

st.divider()

# Instructions
with st.expander("ℹ️ How to Use This Dashboard"):
    st.markdown("""
    **Navigation:**
    - Use the sidebar to navigate between different pages
    - Each page provides specific functionality for monitoring and management
    
    **Pages:**
    1. **📊 Model Performance** - View detailed model metrics and evaluation plots
    2. **🔍 Drift Analysis** - Monitor data and prediction drift over time
    3. **⚙️ Approvals** - Approve or reject autonomous agent actions
    4. **📈 Historical Trends** - Analyze performance trends and patterns
    5. **🤖 Agent Activity** - Audit log of all autonomous actions
    
    **Alerts & Notifications:**
    - The system automatically monitors for issues
    - Critical alerts require human approval before remediation
    - Non-critical issues are handled autonomously
    
    **Data Refresh:**
    - Most data refreshes automatically every 30 seconds
    - Use the refresh button to manually update data
    """)

# Footer
st.divider()
st.caption("MLOps Platform v1.0.0 | Powered by MLflow, Evidently, FastAPI & Streamlit")
