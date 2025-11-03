"""
Approvals page - human-in-loop approval system for autonomous agent actions.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import settings

st.set_page_config(page_title="Approvals", page_icon="⚙️", layout="wide")

st.title("⚙️ Human-in-Loop Approvals")
st.markdown("### Review and approve autonomous agent actions")

# Approval queue overview
st.subheader("📊 Approval Queue Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Pending Approvals", "3", delta="Requires attention", delta_color="inverse")
with col2:
    st.metric("Approved Today", "5", delta="+2 from yesterday")
with col3:
    st.metric("Rejected Today", "1", delta="Low risk")
with col4:
    st.metric("Auto-Executed", "12", delta="Safe actions")

st.divider()

# Pending approvals
st.subheader("🔔 Pending Approvals")

# Simulated pending actions (will be replaced with database queries)
pending_actions = [
    {
        "id": "ACT-001",
        "timestamp": datetime.now() - timedelta(minutes=15),
        "action_type": "Model Rollback",
        "reason": "Performance degradation detected (F1 < 0.70)",
        "risk_level": "🔴 High",
        "details": "Current model F1: 0.68, Previous model F1: 0.85",
        "recommendation": "Rollback to previous model version",
        "estimated_impact": "Service downtime: ~2 minutes"
    },
    {
        "id": "ACT-002",
        "timestamp": datetime.now() - timedelta(hours=1),
        "action_type": "Model Retrain",
        "reason": "Data drift detected on 3 features",
        "risk_level": "🟡 Medium",
        "details": "Features with drift: trestbps (0.12), chol (0.11), oldpeak (0.09)",
        "recommendation": "Retrain model with last 1000 samples",
        "estimated_impact": "Training time: ~15 minutes, Resources: 2 CPU cores"
    },
    {
        "id": "ACT-003",
        "timestamp": datetime.now() - timedelta(hours=2),
        "action_type": "Alert Configuration",
        "reason": "Frequent false positive alerts",
        "risk_level": "🟢 Low",
        "details": "Drift alert threshold too sensitive (0.05 → 0.10)",
        "recommendation": "Increase drift threshold to reduce noise",
        "estimated_impact": "May miss minor drift events"
    }
]

if not pending_actions:
    st.success("✅ No pending approvals! All actions have been processed.")
else:
    for action in pending_actions:
        with st.expander(f"**{action['id']}** - {action['action_type']} ({action['risk_level']})", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Timestamp:** {action['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Action Type:** {action['action_type']}")
                st.markdown(f"**Reason:** {action['reason']}")
                st.markdown(f"**Risk Level:** {action['risk_level']}")
                
                st.markdown("---")
                
                st.markdown("**Details:**")
                st.info(action['details'])
                
                st.markdown("**Recommendation:**")
                st.success(action['recommendation'])
                
                st.markdown("**Estimated Impact:**")
                st.warning(action['estimated_impact'])
            
            with col2:
                st.markdown("### Actions")
                
                col_approve, col_reject = st.columns(2)
                
                with col_approve:
                    if st.button("✅ Approve", key=f"approve_{action['id']}", type="primary"):
                        st.success(f"Action {action['id']} approved!")
                        st.balloons()
                        # TODO: Update database and trigger action
                
                with col_reject:
                    if st.button("❌ Reject", key=f"reject_{action['id']}"):
                        st.error(f"Action {action['id']} rejected!")
                        # TODO: Update database
                
                st.markdown("---")
                
                # Additional options
                if st.button("⏸️ Defer", key=f"defer_{action['id']}"):
                    st.info(f"Action {action['id']} deferred for 1 hour")
                
                if st.button("ℹ️ More Info", key=f"info_{action['id']}"):
                    st.markdown("""
                    **Additional Context:**
                    - Agent confidence: 85%
                    - Similar past actions: 12 (10 approved, 2 rejected)
                    - Estimated success rate: 83%
                    """)

st.divider()

# Approval history
st.subheader("📜 Recent Approval History")

# Filter options
col1, col2, col3 = st.columns(3)

with col1:
    date_range = st.selectbox(
        "Time Range",
        options=["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
        index=0
    )

with col2:
    status_filter = st.multiselect(
        "Status",
        options=["Approved", "Rejected", "Auto-Executed", "Deferred"],
        default=["Approved", "Rejected"]
    )

with col3:
    risk_filter = st.multiselect(
        "Risk Level",
        options=["🔴 High", "🟡 Medium", "🟢 Low"],
        default=["🔴 High", "🟡 Medium", "🟢 Low"]
    )

# Simulated history data
history_data = [
    {
        "ID": "ACT-000",
        "Timestamp": (datetime.now() - timedelta(hours=3)).strftime('%Y-%m-%d %H:%M'),
        "Action Type": "Model Retrain",
        "Risk Level": "🟡 Medium",
        "Status": "✅ Approved",
        "Approver": "admin@mlops.com",
        "Duration": "18 min",
        "Outcome": "Success"
    },
    {
        "ID": "ACT-999",
        "Timestamp": (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M'),
        "Action Type": "Threshold Adjustment",
        "Risk Level": "🟢 Low",
        "Status": "✅ Approved",
        "Approver": "admin@mlops.com",
        "Duration": "< 1 min",
        "Outcome": "Success"
    },
    {
        "ID": "ACT-998",
        "Timestamp": (datetime.now() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
        "Action Type": "Model Rollback",
        "Risk Level": "🔴 High",
        "Status": "❌ Rejected",
        "Approver": "admin@mlops.com",
        "Duration": "N/A",
        "Outcome": "N/A"
    },
    {
        "ID": "ACT-997",
        "Timestamp": (datetime.now() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M'),
        "Action Type": "Data Validation",
        "Risk Level": "🟢 Low",
        "Status": "🤖 Auto-Executed",
        "Approver": "System",
        "Duration": "5 min",
        "Outcome": "Success"
    },
    {
        "ID": "ACT-996",
        "Timestamp": (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M'),
        "Action Type": "Alert Email",
        "Risk Level": "🟢 Low",
        "Status": "🤖 Auto-Executed",
        "Approver": "System",
        "Duration": "< 1 min",
        "Outcome": "Success"
    }
]

df_history = pd.DataFrame(history_data)

# Apply filters
filtered_df = df_history.copy()

# Display history table
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# Export option
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Export to CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"approval_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📊 View Analytics"):
        st.info("Analytics dashboard coming soon!")

with col3:
    if st.button("🔄 Refresh"):
        st.rerun()

st.divider()

# Approval settings
st.subheader("⚙️ Approval Settings")

with st.expander("Configure Auto-Approval Rules"):
    st.markdown("""
    **Auto-Approval Criteria:**
    
    Actions meeting ALL of the following criteria will be auto-executed without human approval:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        auto_approve_low_risk = st.checkbox("Auto-approve Low Risk actions", value=True)
        auto_approve_data_validation = st.checkbox("Auto-approve Data Validation", value=True)
        auto_approve_alerts = st.checkbox("Auto-approve Alert Notifications", value=True)
    
    with col2:
        auto_approve_threshold = st.slider(
            "Confidence Threshold for Auto-Approval",
            min_value=0.0,
            max_value=1.0,
            value=0.90,
            step=0.05,
            help="Minimum confidence level required for auto-approval"
        )
        
        require_approval_high_risk = st.checkbox("Always require approval for High Risk actions", value=True)
    
    if st.button("💾 Save Settings"):
        st.success("✅ Auto-approval settings saved!")

# Statistics
st.divider()

st.subheader("📈 Approval Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Actions (30d)", "156", delta="+23 from prev period")
with col2:
    st.metric("Approval Rate", "78%", delta="+5%")
with col3:
    st.metric("Avg Response Time", "12 min", delta="-3 min")
with col4:
    st.metric("Success Rate", "94%", delta="+2%")
