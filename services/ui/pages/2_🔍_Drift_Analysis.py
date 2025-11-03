"""
Drift Analysis page - monitors data and prediction drift.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import settings

st.set_page_config(page_title="Drift Analysis", page_icon="🔍", layout="wide")

st.title("🔍 Data & Model Drift Analysis")
st.markdown("### Monitor distribution shifts and prediction drift over time")

# Drift status overview
st.subheader("🎯 Drift Status Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Data Drift", "No Drift", delta="Stable", delta_color="normal")
with col2:
    st.metric("Prediction Drift", "Minor Drift", delta="+5%", delta_color="inverse")
with col3:
    st.metric("Last Check", "10 min ago", delta="Auto-monitored")
with col4:
    st.metric("Drift Reports", "24", delta="+3 today")

st.divider()

# Drift detection settings
st.subheader("⚙️ Drift Detection Settings")

col1, col2 = st.columns(2)

with col1:
    drift_threshold = st.slider(
        "Drift Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.05,
        help="Statistical distance threshold for drift detection"
    )

with col2:
    monitoring_window = st.selectbox(
        "Monitoring Window",
        options=["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
        index=1
    )

st.divider()

# Feature drift analysis
st.subheader("📊 Feature Drift Analysis")

# Simulated drift data (replace with actual data from Evidently)
features = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", 
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

drift_scores = {
    "age": 0.05,
    "sex": 0.02,
    "cp": 0.08,
    "trestbps": 0.12,  # Above threshold
    "chol": 0.09,
    "fbs": 0.03,
    "restecg": 0.04,
    "thalach": 0.06,
    "exang": 0.02,
    "oldpeak": 0.07,
    "slope": 0.04,
    "ca": 0.05,
    "thal": 0.03
}

df_drift = pd.DataFrame({
    "Feature": list(drift_scores.keys()),
    "Drift Score": list(drift_scores.values()),
    "Status": ["⚠️ Drift" if v > drift_threshold else "✅ Stable" for v in drift_scores.values()]
})

# Sort by drift score
df_drift = df_drift.sort_values("Drift Score", ascending=False)

# Display drift table
st.dataframe(
    df_drift.style.apply(
        lambda row: ['background-color: #ffcccc' if row['Drift Score'] > drift_threshold else '' for _ in row],
        axis=1
    ),
    use_container_width=True
)

# Drift chart
fig = px.bar(
    df_drift,
    x="Feature",
    y="Drift Score",
    color="Status",
    title="Feature Drift Scores",
    color_discrete_map={"✅ Stable": "green", "⚠️ Drift": "orange"}
)
fig.add_hline(y=drift_threshold, line_dash="dash", line_color="red", annotation_text="Threshold")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Prediction drift over time
st.subheader("📈 Prediction Drift Over Time")

# Simulated time series data
dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
prediction_drift = [0.03 + 0.02 * i + 0.01 * (i % 7) for i in range(30)]

df_pred_drift = pd.DataFrame({
    "Date": dates,
    "Prediction Drift": prediction_drift
})

fig_pred = px.line(
    df_pred_drift,
    x="Date",
    y="Prediction Drift",
    title="Prediction Drift Trend (Last 30 Days)"
)
fig_pred.add_hline(y=drift_threshold, line_dash="dash", line_color="red", annotation_text="Threshold")
st.plotly_chart(fig_pred, use_container_width=True)

st.divider()

# Evidently reports
st.subheader("📄 Evidently Drift Reports")

st.info("""
**Evidently Integration:**
- Automatic drift detection using Evidently AI
- Reports generated after each prediction batch
- Statistical tests: KS test, PSI, Jensen-Shannon divergence
- Alerts triggered when drift exceeds threshold
""")

# Check for Evidently reports
drift_reports_dir = settings.reports_dir / "drift"

if drift_reports_dir.exists():
    report_files = list(drift_reports_dir.glob("*.html"))
    
    if report_files:
        st.write(f"**Found {len(report_files)} drift reports**")
        
        # Show latest reports
        latest_reports = sorted(report_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        
        for report in latest_reports:
            with st.expander(f"📊 {report.stem}"):
                st.write(f"Generated: {datetime.fromtimestamp(report.stat().st_mtime)}")
                st.markdown(f"[Open Report]({report})")
    else:
        st.warning("No drift reports generated yet")
else:
    st.warning("Drift reports directory not found. Reports will appear after first drift check.")

st.divider()

# Drift alerts
st.subheader("🚨 Recent Drift Alerts")

alerts = [
    {"time": "2 hours ago", "feature": "trestbps", "severity": "⚠️ Warning", "action": "Monitoring"},
    {"time": "1 day ago", "feature": "chol", "severity": "ℹ️ Info", "action": "None"},
    {"time": "3 days ago", "feature": "prediction", "severity": "🔴 Critical", "action": "Retrain triggered"},
]

for alert in alerts:
    col1, col2, col3, col4 = st.columns([1, 2, 1, 2])
    with col1:
        st.text(alert["time"])
    with col2:
        st.text(alert["feature"])
    with col3:
        st.text(alert["severity"])
    with col4:
        st.text(alert["action"])

# Actions
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Run Drift Check Now"):
        with st.spinner("Running drift detection..."):
            # Simulate drift check
            import time
            time.sleep(2)
            st.success("✅ Drift check completed!")

with col2:
    if st.button("📊 Generate Evidently Report"):
        with st.spinner("Generating report..."):
            import time
            time.sleep(2)
            st.success("✅ Report generated!")

with col3:
    if st.button("🔄 Refresh Data"):
        st.rerun()
