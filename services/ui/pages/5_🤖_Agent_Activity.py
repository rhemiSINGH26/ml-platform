"""
Agent Activity page - audit log and monitoring of autonomous agent actions.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import settings

st.set_page_config(page_title="Agent Activity", page_icon="🤖", layout="wide")

st.title("🤖 Autonomous Agent Activity")
st.markdown("### Monitor and audit all autonomous agent actions")

# Agent status overview
st.subheader("🎯 Agent Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Agent Status", "🟢 Active", delta="Running")
with col2:
    st.metric("Actions Today", "18", delta="+5 from yesterday")
with col3:
    st.metric("Success Rate", "94%", delta="+2%")
with col4:
    st.metric("Pending Queue", "3", delta="Awaiting approval")

st.divider()

# Agent capabilities
st.subheader("🛠️ Agent Capabilities")

with st.expander("View Agent Capabilities & Rules"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**✅ Auto-Execute (Low Risk):**")
        st.markdown("""
        - Data validation checks
        - Log rotation and cleanup
        - Performance metric collection
        - Email/Slack notifications
        - Report generation
        - Minor threshold adjustments (< 10%)
        - Cache clearing
        - Diagnostic data collection
        """)
    
    with col2:
        st.markdown("**⚠️ Requires Approval (Medium/High Risk):**")
        st.markdown("""
        - Model retraining
        - Model deployment/rollback
        - Major configuration changes
        - Database schema changes
        - Resource scaling
        - Alert rule modifications
        - Data pipeline changes
        - Service restarts
        """)

st.divider()

# Recent activity timeline
st.subheader("📋 Recent Activity Timeline")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    time_filter = st.selectbox(
        "Time Range",
        options=["Last Hour", "Last 24 Hours", "Last 7 Days", "All Time"],
        index=1
    )

with col2:
    action_filter = st.multiselect(
        "Action Type",
        options=["Data Validation", "Model Retrain", "Alert", "Notification", "Rollback", "Report", "Other"],
        default=["Data Validation", "Model Retrain", "Alert"]
    )

with col3:
    status_filter = st.multiselect(
        "Status",
        options=["Success", "Failed", "Pending", "Cancelled"],
        default=["Success", "Failed"]
    )

# Simulated activity log
activities = [
    {
        "timestamp": datetime.now() - timedelta(minutes=5),
        "action_id": "AG-2025-1103-001",
        "action_type": "Data Validation",
        "description": "Validated incoming prediction batch (n=50)",
        "risk_level": "🟢 Low",
        "execution": "🤖 Auto",
        "duration": "2.3s",
        "status": "✅ Success",
        "output": "All validations passed"
    },
    {
        "timestamp": datetime.now() - timedelta(minutes=30),
        "action_id": "AG-2025-1103-002",
        "action_type": "Alert",
        "description": "Drift detected on feature 'trestbps'",
        "risk_level": "🟡 Medium",
        "execution": "🤖 Auto",
        "duration": "0.8s",
        "status": "✅ Success",
        "output": "Email sent to team@mlops.com"
    },
    {
        "timestamp": datetime.now() - timedelta(hours=2),
        "action_id": "AG-2025-1103-003",
        "action_type": "Model Retrain",
        "description": "Retrain triggered by drift detection",
        "risk_level": "🟡 Medium",
        "execution": "👤 Approved",
        "duration": "18m 24s",
        "status": "✅ Success",
        "output": "New model F1: 0.87 (prev: 0.82)"
    },
    {
        "timestamp": datetime.now() - timedelta(hours=4),
        "action_id": "AG-2025-1103-004",
        "action_type": "Report",
        "description": "Generated weekly performance report",
        "risk_level": "🟢 Low",
        "execution": "🤖 Auto",
        "duration": "12.5s",
        "status": "✅ Success",
        "output": "Report saved and emailed"
    },
    {
        "timestamp": datetime.now() - timedelta(hours=6),
        "action_id": "AG-2025-1103-005",
        "action_type": "Notification",
        "description": "Slack notification: Model performance update",
        "risk_level": "🟢 Low",
        "execution": "🤖 Auto",
        "duration": "1.2s",
        "status": "✅ Success",
        "output": "Message posted to #ml-alerts"
    },
    {
        "timestamp": datetime.now() - timedelta(hours=8),
        "action_id": "AG-2025-1103-006",
        "action_type": "Rollback",
        "description": "Rollback model due to performance degradation",
        "risk_level": "🔴 High",
        "execution": "👤 Approved",
        "duration": "3m 15s",
        "status": "✅ Success",
        "output": "Reverted to model v1.2.5"
    },
    {
        "timestamp": datetime.now() - timedelta(hours=10),
        "action_id": "AG-2025-1103-007",
        "action_type": "Data Validation",
        "description": "Validated training dataset",
        "risk_level": "🟢 Low",
        "execution": "🤖 Auto",
        "duration": "5.7s",
        "status": "⚠️ Failed",
        "output": "Schema validation failed: missing column 'ca'"
    },
]

# Display activity cards
for activity in activities:
    with st.expander(
        f"**{activity['action_id']}** - {activity['action_type']} ({activity['status']})",
        expanded=False
    ):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**Description:** {activity['description']}")
            st.markdown(f"**Output:** {activity['output']}")
        
        with col2:
            st.markdown(f"**Timestamp:** {activity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**Risk Level:** {activity['risk_level']}")
            st.markdown(f"**Duration:** {activity['duration']}")
        
        with col3:
            st.markdown(f"**Execution:** {activity['execution']}")
            st.markdown(f"**Status:** {activity['status']}")
            
            if st.button("📋 View Logs", key=f"logs_{activity['action_id']}"):
                st.code(f"""
[INFO] Action initiated: {activity['action_id']}
[INFO] Type: {activity['action_type']}
[INFO] Risk assessment: {activity['risk_level']}
[INFO] Executing action...
[INFO] {activity['output']}
[INFO] Status: {activity['status']}
[INFO] Duration: {activity['duration']}
                """, language="log")

st.divider()

# Activity statistics
st.subheader("📊 Activity Statistics")

# Action type distribution
action_types_data = {
    "Data Validation": 45,
    "Alert": 28,
    "Notification": 32,
    "Report": 15,
    "Model Retrain": 8,
    "Rollback": 3,
    "Other": 12
}

col1, col2 = st.columns(2)

with col1:
    fig_actions = px.pie(
        values=list(action_types_data.values()),
        names=list(action_types_data.keys()),
        title="Action Type Distribution (Last 30 Days)"
    )
    st.plotly_chart(fig_actions, use_container_width=True)

with col2:
    # Execution mode distribution
    execution_data = {
        "Auto-Executed": 125,
        "Approved": 15,
        "Rejected": 3
    }
    
    fig_execution = px.bar(
        x=list(execution_data.keys()),
        y=list(execution_data.values()),
        title="Execution Mode Distribution (Last 30 Days)",
        labels={"x": "Execution Mode", "y": "Count"},
        color=list(execution_data.keys()),
        color_discrete_map={
            "Auto-Executed": "#2ca02c",
            "Approved": "#1f77b4",
            "Rejected": "#d62728"
        }
    )
    st.plotly_chart(fig_execution, use_container_width=True)

st.divider()

# Agent performance metrics
st.subheader("⚡ Agent Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Avg Response Time", "2.8s", delta="-0.4s")
with col2:
    st.metric("Actions/Hour", "3.2", delta="+0.5")
with col3:
    st.metric("Error Rate", "2.1%", delta="-0.8%")
with col4:
    st.metric("Approval Rate", "89%", delta="+3%")

# Activity over time
days = 30
dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
import numpy as np

daily_actions = np.random.randint(10, 25, days)

df_daily = pd.DataFrame({
    'Date': dates,
    'Actions': daily_actions
})

fig_daily = px.line(
    df_daily,
    x='Date',
    y='Actions',
    title='Daily Agent Activity (Last 30 Days)',
    markers=True
)

st.plotly_chart(fig_daily, use_container_width=True)

st.divider()

# Agent configuration
st.subheader("⚙️ Agent Configuration")

with st.expander("View/Edit Agent Settings"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Monitoring Settings:**")
        check_interval = st.slider("Check Interval (minutes)", 1, 60, 5)
        enable_auto_remediation = st.checkbox("Enable Auto-Remediation", value=True)
        enable_notifications = st.checkbox("Enable Notifications", value=True)
    
    with col2:
        st.markdown("**Action Limits:**")
        max_retries = st.number_input("Max Retries", 1, 10, 3)
        timeout_seconds = st.number_input("Action Timeout (seconds)", 10, 600, 300)
        cooldown_minutes = st.number_input("Cooldown Between Actions (minutes)", 1, 60, 5)
    
    if st.button("💾 Save Configuration"):
        st.success("✅ Agent configuration saved!")

st.divider()

# Action queue
st.subheader("📬 Action Queue")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Pending Actions:** 3")
    st.progress(0.3, text="30% queue utilization")

with col2:
    st.markdown("**Scheduled Actions:** 5")
    st.caption("Next action in 2 minutes")

# Quick actions
st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 Run Diagnostics"):
        with st.spinner("Running diagnostics..."):
            import time
            time.sleep(2)
            st.success("✅ All systems operational")

with col2:
    if st.button("⏸️ Pause Agent"):
        st.warning("⚠️ Agent paused - manual mode enabled")

with col3:
    if st.button("📊 Export Logs"):
        st.download_button(
            label="Download Activity Log",
            data="Activity log data...",
            file_name=f"agent_activity_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col4:
    if st.button("🔄 Refresh"):
        st.rerun()
