"""
Model evaluator - calculates metrics and generates evaluation plots.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    precision_recall_curve,
    auc
)
import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))


class ModelEvaluator:
    """Evaluate trained models."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.metrics = {}
        self.plots = {}
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray = None
    ) -> Dict[str, float]:
        """
        Evaluate model predictions.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional)
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, average="binary", zero_division=0),
            "recall": recall_score(y_true, y_pred, average="binary", zero_division=0),
            "f1_score": f1_score(y_true, y_pred, average="binary", zero_division=0),
        }
        
        # Add ROC AUC if probabilities available
        if y_pred_proba is not None:
            try:
                metrics["roc_auc"] = roc_auc_score(y_true, y_pred_proba)
                # Calculate PR AUC
                precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
                metrics["pr_auc"] = auc(recall, precision)
            except ValueError as e:
                logger.warning(f"Could not calculate AUC metrics: {e}")
                metrics["roc_auc"] = 0.0
                metrics["pr_auc"] = 0.0
        
        self.metrics = metrics
        return metrics
    
    def get_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """
        Calculate confusion matrix.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            Confusion matrix
        """
        return confusion_matrix(y_true, y_pred)
    
    def get_classification_report(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> str:
        """
        Get classification report.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            Classification report string
        """
        return classification_report(y_true, y_pred)
    
    def plot_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        save_path: Path = None
    ) -> plt.Figure:
        """
        Plot confusion matrix.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            save_path: Path to save plot (optional)
            
        Returns:
            Matplotlib figure
        """
        cm = self.get_confusion_matrix(y_true, y_pred)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            ax=ax,
            cbar=True,
            square=True
        )
        ax.set_xlabel("Predicted Label")
        ax.set_ylabel("True Label")
        ax.set_title("Confusion Matrix")
        ax.set_xticklabels(["No Disease", "Disease"])
        ax.set_yticklabels(["No Disease", "Disease"])
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            logger.info(f"Saved confusion matrix to {save_path}")
        
        return fig
    
    def plot_roc_curve(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        save_path: Path = None
    ) -> plt.Figure:
        """
        Plot ROC curve.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            save_path: Path to save plot (optional)
            
        Returns:
            Matplotlib figure
        """
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(fpr, tpr, color="darkorange", lw=2, label=f"ROC curve (AUC = {roc_auc:.2f})")
        ax.plot([0, 1], [0, 1], color="navy", lw=2, linestyle="--", label="Random")
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("Receiver Operating Characteristic (ROC) Curve")
        ax.legend(loc="lower right")
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            logger.info(f"Saved ROC curve to {save_path}")
        
        return fig
    
    def plot_precision_recall_curve(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        save_path: Path = None
    ) -> plt.Figure:
        """
        Plot precision-recall curve.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            save_path: Path to save plot (optional)
            
        Returns:
            Matplotlib figure
        """
        precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
        pr_auc = auc(recall, precision)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(recall, precision, color="darkorange", lw=2, label=f"PR curve (AUC = {pr_auc:.2f})")
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        ax.set_title("Precision-Recall Curve")
        ax.legend(loc="lower left")
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            logger.info(f"Saved PR curve to {save_path}")
        
        return fig
    
    def plot_feature_importance(
        self,
        model: Any,
        feature_names: list,
        save_path: Path = None,
        top_n: int = 13
    ) -> plt.Figure:
        """
        Plot feature importance.
        
        Args:
            model: Trained model with feature_importances_ attribute
            feature_names: List of feature names
            save_path: Path to save plot (optional)
            top_n: Number of top features to show
            
        Returns:
            Matplotlib figure
        """
        if not hasattr(model, "feature_importances_"):
            logger.warning("Model does not have feature_importances_ attribute")
            return None
        
        importance = model.feature_importances_
        indices = np.argsort(importance)[-top_n:]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(indices)), importance[indices], align="center")
        ax.set_yticks(range(len(indices)))
        ax.set_yticklabels([feature_names[i] for i in indices])
        ax.set_xlabel("Feature Importance")
        ax.set_title(f"Top {top_n} Feature Importances")
        ax.grid(True, alpha=0.3, axis="x")
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            logger.info(f"Saved feature importance to {save_path}")
        
        return fig
    
    def generate_all_plots(
        self,
        model: Any,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray,
        feature_names: list,
        output_dir: Path
    ) -> Dict[str, Path]:
        """
        Generate all evaluation plots.
        
        Args:
            model: Trained model
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities
            feature_names: List of feature names
            output_dir: Directory to save plots
            
        Returns:
            Dictionary of plot names to file paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        plot_paths = {}
        
        # Confusion matrix
        cm_path = output_dir / "confusion_matrix.png"
        self.plot_confusion_matrix(y_true, y_pred, cm_path)
        plot_paths["confusion_matrix"] = cm_path
        
        # ROC curve
        if y_pred_proba is not None:
            roc_path = output_dir / "roc_curve.png"
            self.plot_roc_curve(y_true, y_pred_proba, roc_path)
            plot_paths["roc_curve"] = roc_path
            
            # PR curve
            pr_path = output_dir / "precision_recall_curve.png"
            self.plot_precision_recall_curve(y_true, y_pred_proba, pr_path)
            plot_paths["pr_curve"] = pr_path
        
        # Feature importance
        if hasattr(model, "feature_importances_"):
            fi_path = output_dir / "feature_importance.png"
            self.plot_feature_importance(model, feature_names, fi_path)
            plot_paths["feature_importance"] = fi_path
        
        # Close all figures to free memory
        plt.close("all")
        
        return plot_paths
    
    def print_metrics(self):
        """Print metrics in a formatted way."""
        if not self.metrics:
            logger.warning("No metrics to print")
            return
        
        logger.info("Model Evaluation Metrics:")
        logger.info("=" * 40)
        for metric, value in self.metrics.items():
            logger.info(f"{metric:15s}: {value:.4f}")
        logger.info("=" * 40)
