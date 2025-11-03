"""
Historical Trends page - visualizes performance metrics over time.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import settings

st.set_page_config(page_title="Historical Trends", page_icon="📈", layout="wide")

st.title("📈 Historical Performance Trends")
st.markdown("### Track model performance and system metrics over time")

# Time range selector
st.subheader("⏱️ Time Range")

col1, col2, col3 = st.columns(3)

with col1:
    time_range = st.selectbox(
        "Select Time Range",
        options=["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
        index=2
    )

with col2:
    granularity = st.selectbox(
        "Data Granularity",
        options=["Hourly", "Daily", "Weekly"],
        index=1
    )

with col3:
    metric_type = st.selectbox(
        "Primary Metric",
        options=["F1 Score", "Accuracy", "Precision", "Recall", "ROC AUC"],
        index=0
    )

st.divider()

# Generate simulated time series data
days = 30
dates = pd.date_range(end=datetime.now(), periods=days, freq='D')

# Model performance over time
f1_scores = 0.85 + 0.05 * np.sin(np.linspace(0, 4*np.pi, days)) + np.random.normal(0, 0.02, days)
accuracy = 0.88 + 0.04 * np.sin(np.linspace(0, 4*np.pi, days)) + np.random.normal(0, 0.015, days)
precision = 0.86 + 0.05 * np.sin(np.linspace(0, 4*np.pi, days)) + np.random.normal(0, 0.02, days)
recall = 0.84 + 0.06 * np.sin(np.linspace(0, 4*np.pi, days)) + np.random.normal(0, 0.025, days)

# Ensure values stay in [0, 1]
f1_scores = np.clip(f1_scores, 0.7, 0.95)
accuracy = np.clip(accuracy, 0.75, 0.95)
precision = np.clip(precision, 0.75, 0.95)
recall = np.clip(recall, 0.7, 0.95)

df_metrics = pd.DataFrame({
    'Date': dates,
    'F1 Score': f1_scores,
    'Accuracy': accuracy,
    'Precision': precision,
    'Recall': recall
})

# Model performance trends
st.subheader("📊 Model Performance Trends")

# Multi-line chart
fig_performance = go.Figure()

fig_performance.add_trace(go.Scatter(
    x=df_metrics['Date'],
    y=df_metrics['F1 Score'],
    mode='lines+markers',
    name='F1 Score',
    line=dict(color='#1f77b4', width=2)
))

fig_performance.add_trace(go.Scatter(
    x=df_metrics['Date'],
    y=df_metrics['Accuracy'],
    mode='lines+markers',
    name='Accuracy',
    line=dict(color='#ff7f0e', width=2)
))

fig_performance.add_trace(go.Scatter(
    x=df_metrics['Date'],
    y=df_metrics['Precision'],
    mode='lines+markers',
    name='Precision',
    line=dict(color='#2ca02c', width=2)
))

fig_performance.add_trace(go.Scatter(
    x=df_metrics['Date'],
    y=df_metrics['Recall'],
    mode='lines+markers',
    name='Recall',
    line=dict(color='#d62728', width=2)
))

# Add threshold line
fig_performance.add_hline(
    y=0.75,
    line_dash="dash",
    line_color="red",
    annotation_text="Minimum Threshold"
)

fig_performance.update_layout(
    title="Model Performance Metrics Over Time",
    xaxis_title="Date",
    yaxis_title="Score",
    yaxis_range=[0.65, 1.0],
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_performance, use_container_width=True)

st.divider()

# Prediction volume and latency
st.subheader("🔢 Prediction Volume & Latency")

col1, col2 = st.columns(2)

# Prediction volume
predictions_per_day = np.random.randint(800, 1200, days)
df_volume = pd.DataFrame({
    'Date': dates,
    'Predictions': predictions_per_day
})

with col1:
    fig_volume = px.bar(
        df_volume,
        x='Date',
        y='Predictions',
        title='Daily Prediction Volume',
        labels={'Predictions': 'Number of Predictions'}
    )
    st.plotly_chart(fig_volume, use_container_width=True)

# Latency
latency = 15 + 5 * np.sin(np.linspace(0, 4*np.pi, days)) + np.random.normal(0, 2, days)
latency = np.clip(latency, 10, 30)

df_latency = pd.DataFrame({
    'Date': dates,
    'Latency (ms)': latency
})

with col2:
    fig_latency = px.line(
        df_latency,
        x='Date',
        y='Latency (ms)',
        title='Average Prediction Latency',
        markers=True
    )
    fig_latency.add_hline(
        y=25,
        line_dash="dash",
        line_color="orange",
        annotation_text="SLA Target (25ms)"
    )
    st.plotly_chart(fig_latency, use_container_width=True)

st.divider()

# Drift detection history
st.subheader("🔍 Drift Detection History")

# Simulated drift events
drift_events = []
for i in range(8):
    event_date = datetime.now() - timedelta(days=np.random.randint(1, 30))
    drift_events.append({
        'Date': event_date,
        'Feature': np.random.choice(['trestbps', 'chol', 'age', 'thalach', 'oldpeak']),
        'Drift Score': np.random.uniform(0.08, 0.15),
        'Action': np.random.choice(['Retrain Triggered', 'Monitoring', 'Alert Sent'])
    })

df_drift_events = pd.DataFrame(drift_events).sort_values('Date', ascending=False)

col1, col2 = st.columns([2, 1])

with col1:
    # Drift events timeline
    fig_drift = px.scatter(
        df_drift_events,
        x='Date',
        y='Drift Score',
        color='Feature',
        size='Drift Score',
        title='Drift Events Timeline',
        hover_data=['Action']
    )
    fig_drift.add_hline(
        y=0.10,
        line_dash="dash",
        line_color="red",
        annotation_text="Drift Threshold"
    )
    st.plotly_chart(fig_drift, use_container_width=True)

with col2:
    st.markdown("#### Recent Drift Events")
    for idx, event in df_drift_events.head(5).iterrows():
        with st.container():
            st.markdown(f"**{event['Feature']}**")
            st.caption(f"{event['Date'].strftime('%Y-%m-%d %H:%M')}")
            st.progress(event['Drift Score'])
            st.caption(f"Score: {event['Drift Score']:.3f} | {event['Action']}")
            st.divider()

st.divider()

# Model retraining history
st.subheader("🔄 Model Retraining History")

# Simulated retraining events
retraining_events = [
    {
        'Date': datetime.now() - timedelta(days=2),
        'Trigger': 'Drift Detection',
        'Model': 'Random Forest',
        'F1 Before': 0.82,
        'F1 After': 0.87,
        'Duration': '18 min',
        'Status': '✅ Success'
    },
    {
        'Date': datetime.now() - timedelta(days=7),
        'Trigger': 'Scheduled',
        'Model': 'XGBoost',
        'F1 Before': 0.84,
        'F1 After': 0.85,
        'Duration': '22 min',
        'Status': '✅ Success'
    },
    {
        'Date': datetime.now() - timedelta(days=14),
        'Trigger': 'Performance Degradation',
        'Model': 'Random Forest',
        'F1 Before': 0.78,
        'F1 After': 0.86,
        'Duration': '20 min',
        'Status': '✅ Success'
    },
    {
        'Date': datetime.now() - timedelta(days=21),
        'Trigger': 'Manual',
        'Model': 'LightGBM',
        'F1 Before': 0.83,
        'F1 After': 0.84,
        'Duration': '15 min',
        'Status': '✅ Success'
    }
]

df_retraining = pd.DataFrame(retraining_events)

# Format dates
df_retraining['Date'] = df_retraining['Date'].dt.strftime('%Y-%m-%d %H:%M')

# Display table
st.dataframe(
    df_retraining,
    use_container_width=True,
    hide_index=True
)

# Improvement visualization
fig_improvement = go.Figure()

fig_improvement.add_trace(go.Bar(
    name='Before Retraining',
    x=df_retraining['Date'],
    y=df_retraining['F1 Before'],
    marker_color='lightblue'
))

fig_improvement.add_trace(go.Bar(
    name='After Retraining',
    x=df_retraining['Date'],
    y=df_retraining['F1 After'],
    marker_color='darkblue'
))

fig_improvement.update_layout(
    title='F1 Score Improvement from Retraining',
    xaxis_title='Retraining Date',
    yaxis_title='F1 Score',
    barmode='group',
    yaxis_range=[0.7, 0.95]
)

st.plotly_chart(fig_improvement, use_container_width=True)

st.divider()

# System health metrics
st.subheader("💚 System Health Metrics")

col1, col2, col3 = st.columns(3)

# Uptime
uptime_data = np.random.uniform(99.5, 100, days)
df_uptime = pd.DataFrame({
    'Date': dates,
    'Uptime (%)': uptime_data
})

with col1:
    fig_uptime = px.line(
        df_uptime,
        x='Date',
        y='Uptime (%)',
        title='Service Uptime',
        markers=True
    )
    fig_uptime.update_layout(yaxis_range=[98, 100])
    st.plotly_chart(fig_uptime, use_container_width=True)

# Error rate
error_rate = np.random.uniform(0, 2, days)
df_errors = pd.DataFrame({
    'Date': dates,
    'Error Rate (%)': error_rate
})

with col2:
    fig_errors = px.area(
        df_errors,
        x='Date',
        y='Error Rate (%)',
        title='Error Rate',
    )
    fig_errors.add_hline(
        y=5,
        line_dash="dash",
        line_color="red",
        annotation_text="SLA Limit"
    )
    st.plotly_chart(fig_errors, use_container_width=True)

# Resource usage
cpu_usage = 30 + 20 * np.sin(np.linspace(0, 4*np.pi, days)) + np.random.normal(0, 5, days)
cpu_usage = np.clip(cpu_usage, 10, 80)

df_cpu = pd.DataFrame({
    'Date': dates,
    'CPU Usage (%)': cpu_usage
})

with col3:
    fig_cpu = px.line(
        df_cpu,
        x='Date',
        y='CPU Usage (%)',
        title='Average CPU Usage',
        markers=True
    )
    fig_cpu.add_hline(
        y=80,
        line_dash="dash",
        line_color="red",
        annotation_text="Critical Threshold"
    )
    st.plotly_chart(fig_cpu, use_container_width=True)

# Actions
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Export Data"):
        # Combine all dataframes
        csv = df_metrics.to_csv(index=False)
        st.download_button(
            label="Download Metrics CSV",
            data=csv,
            file_name=f"metrics_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📊 Generate Report"):
        st.info("📄 Generating comprehensive performance report...")

with col3:
    if st.button("🔄 Refresh Data"):
        st.rerun()
