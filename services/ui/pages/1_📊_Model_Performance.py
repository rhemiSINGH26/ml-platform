"""
Model Performance page - displays current model metrics and evaluation plots.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import settings

st.set_page_config(page_title="Model Performance", page_icon="📊", layout="wide")

st.title("📊 Model Performance Dashboard")
st.markdown("### Current Production Model Metrics & Evaluation")

# Load model metadata
metadata_files = list(settings.production_model_dir.glob("*_metadata.yaml"))

if not metadata_files:
    st.error("⚠️ No model metadata found. Please train a model first.")
    st.stop()

# Load latest metadata
import yaml
metadata_path = max(metadata_files, key=lambda p: p.stat().st_mtime)
with open(metadata_path, "r") as f:
    metadata = yaml.safe_load(f)

# Model information
st.subheader("🎯 Model Information")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Model Name", metadata.get("model_name", "Unknown"))
with col2:
    st.metric("Training Samples", metadata.get("training_samples", "N/A"))
with col3:
    st.metric("Selection Metric", metadata.get("selection_metric", "N/A"))

st.divider()

# Performance metrics
st.subheader("📈 Performance Metrics")

metrics = metadata.get("metrics", {})

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    accuracy = metrics.get("accuracy", 0.0)
    st.metric("Accuracy", f"{accuracy:.4f}", delta=f"{accuracy*100:.1f}%")

with col2:
    f1 = metrics.get("f1_score", 0.0)
    st.metric("F1 Score", f"{f1:.4f}", delta=f"{f1*100:.1f}%")

with col3:
    precision = metrics.get("precision", 0.0)
    st.metric("Precision", f"{precision:.4f}", delta=f"{precision*100:.1f}%")

with col4:
    recall = metrics.get("recall", 0.0)
    st.metric("Recall", f"{recall:.4f}", delta=f"{recall*100:.1f}%")

with col5:
    roc_auc = metrics.get("roc_auc", 0.0)
    st.metric("ROC AUC", f"{roc_auc:.4f}", delta=f"{roc_auc*100:.1f}%")

st.divider()

# Evaluation plots
st.subheader("📊 Evaluation Plots")

model_name = metadata.get("model_name", "unknown")
plots_dir = settings.reports_dir / "plots" / model_name

# Check for test plots
test_plots_dir = settings.reports_dir / "plots" / f"{model_name}_test"
if test_plots_dir.exists():
    plots_dir = test_plots_dir
    st.info("📍 Showing test set evaluation plots")

if not plots_dir.exists():
    st.warning("⚠️ No evaluation plots found. Plots are generated during training.")
else:
    # Create tabs for different plots
    tab1, tab2, tab3, tab4 = st.tabs(["Confusion Matrix", "ROC Curve", "Precision-Recall", "Feature Importance"])
    
    with tab1:
        cm_path = plots_dir / "confusion_matrix.png"
        if cm_path.exists():
            image = Image.open(cm_path)
            st.image(image, caption="Confusion Matrix", use_container_width=True)
        else:
            st.warning("Confusion matrix plot not found")
    
    with tab2:
        roc_path = plots_dir / "roc_curve.png"
        if roc_path.exists():
            image = Image.open(roc_path)
            st.image(image, caption="ROC Curve", use_container_width=True)
        else:
            st.warning("ROC curve plot not found")
    
    with tab3:
        pr_path = plots_dir / "precision_recall_curve.png"
        if pr_path.exists():
            image = Image.open(pr_path)
            st.image(image, caption="Precision-Recall Curve", use_container_width=True)
        else:
            st.warning("Precision-recall curve plot not found")
    
    with tab4:
        fi_path = plots_dir / "feature_importance.png"
        if fi_path.exists():
            image = Image.open(fi_path)
            st.image(image, caption="Feature Importance", use_container_width=True)
        else:
            st.warning("Feature importance plot not found")

st.divider()

# Model comparison
st.subheader("🔄 Model Comparison")

comparison_path = settings.reports_dir / "model_comparison.csv"

if comparison_path.exists():
    df_comparison = pd.read_csv(comparison_path)
    
    # Highlight best model
    def highlight_best(s):
        is_max = s == s.max()
        return ['background-color: lightgreen' if v else '' for v in is_max]
    
    # Apply styling
    styled_df = df_comparison.style.apply(highlight_best, subset=df_comparison.columns[1:])
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Visualize comparison
    st.subheader("📊 Metrics Comparison Chart")
    
    # Melt dataframe for plotting
    df_melted = df_comparison.melt(id_vars=['model_name'], var_name='metric', value_name='value')
    
    fig = px.bar(
        df_melted,
        x='metric',
        y='value',
        color='model_name',
        barmode='group',
        title='Model Performance Comparison',
        labels={'value': 'Score', 'metric': 'Metric', 'model_name': 'Model'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.info("ℹ️ Model comparison data not available. Train multiple models to see comparison.")

st.divider()

# Feature details
st.subheader("🔍 Feature Details")

feature_names = metadata.get("feature_names", [])

if feature_names:
    st.write(f"**Number of features:** {len(feature_names)}")
    
    # Display features in columns
    n_cols = 3
    cols = st.columns(n_cols)
    
    for idx, feature in enumerate(feature_names):
        with cols[idx % n_cols]:
            st.text(f"• {feature}")
else:
    st.info("Feature information not available in metadata")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.rerun()
