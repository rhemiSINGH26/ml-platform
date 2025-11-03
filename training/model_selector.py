"""
Model selector - selects the best model based on evaluation metrics.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings


class ModelSelector:
    """Select the best model from multiple trained models."""
    
    # Map config metric names to actual metric dictionary keys
    METRIC_NAME_MAP = {
        "f1": "f1_score",
        "roc_auc": "roc_auc",
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall"
    }
    
    def __init__(self, primary_metric: str = None, minimize: bool = False):
        """
        Initialize model selector.
        
        Args:
            primary_metric: Metric to use for selection (default: from config)
            minimize: Whether to minimize the metric (default: False for maximize)
        """
        config_metric = primary_metric or settings.model_selection_metric
        # Map config metric name to actual metric key
        self.primary_metric = self.METRIC_NAME_MAP.get(config_metric, config_metric)
        self.minimize = minimize
        self.results = []
        self.best_model = None
        self.best_model_name = None
        self.best_metrics = None
    
    def add_model_result(
        self,
        model_name: str,
        model: Any,
        metrics: Dict[str, float],
        artifacts: Dict[str, Any] = None
    ):
        """
        Add a model's results for comparison.
        
        Args:
            model_name: Name of the model
            model: Trained model object
            metrics: Dictionary of evaluation metrics
            artifacts: Optional artifacts (plots, etc.)
        """
        result = {
            "name": model_name,
            "model": model,
            "metrics": metrics,
            "artifacts": artifacts or {},
            "primary_metric_value": metrics.get(self.primary_metric, 0.0)
        }
        self.results.append(result)
        logger.info(
            f"Added model '{model_name}' with {self.primary_metric}="
            f"{result['primary_metric_value']:.4f}"
        )
    
    def select_best_model(self) -> Tuple[str, Any, Dict[str, float]]:
        """
        Select the best model based on primary metric.
        
        Returns:
            Tuple of (model_name, model, metrics)
        """
        if not self.results:
            logger.error("No models to select from")
            return None, None, None
        
        # Sort by primary metric
        if self.minimize:
            best_result = min(self.results, key=lambda x: x["primary_metric_value"])
        else:
            best_result = max(self.results, key=lambda x: x["primary_metric_value"])
        
        self.best_model_name = best_result["name"]
        self.best_model = best_result["model"]
        self.best_metrics = best_result["metrics"]
        
        logger.info(
            f"Selected best model: '{self.best_model_name}' with "
            f"{self.primary_metric}={best_result['primary_metric_value']:.4f}"
        )
        
        return self.best_model_name, self.best_model, self.best_metrics
    
    def get_comparison_dataframe(self) -> pd.DataFrame:
        """
        Get a DataFrame comparing all models.
        
        Returns:
            DataFrame with model comparison
        """
        if not self.results:
            return pd.DataFrame()
        
        data = []
        for result in self.results:
            row = {"model_name": result["name"]}
            row.update(result["metrics"])
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # Sort by primary metric
        df = df.sort_values(by=self.primary_metric, ascending=self.minimize)
        
        return df
    
    def print_comparison(self):
        """Print a formatted comparison of all models."""
        df = self.get_comparison_dataframe()
        
        if df.empty:
            logger.warning("No models to compare")
            return
        
        logger.info("\nModel Comparison:")
        logger.info("=" * 80)
        logger.info(f"\n{df.to_string(index=False)}\n")
        logger.info("=" * 80)
        logger.info(
            f"Best model: {self.best_model_name} "
            f"({self.primary_metric}={self.best_metrics[self.primary_metric]:.4f})"
        )
    
    def save_comparison(self, output_path: Path):
        """
        Save model comparison to CSV.
        
        Args:
            output_path: Path to save CSV file
        """
        df = self.get_comparison_dataframe()
        
        if df.empty:
            logger.warning("No models to save")
            return
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved model comparison to {output_path}")
    
    def meets_minimum_threshold(
        self,
        threshold: float = None,
        metric: str = None
    ) -> bool:
        """
        Check if the best model meets a minimum threshold.
        
        Args:
            threshold: Minimum threshold value
            metric: Metric to check (default: primary_metric)
            
        Returns:
            True if threshold is met, False otherwise
        """
        if not self.best_metrics:
            logger.warning("No best model selected yet")
            return False
        
        metric = metric or self.primary_metric
        threshold = threshold or 0.0
        
        value = self.best_metrics.get(metric, 0.0)
        meets_threshold = value >= threshold
        
        logger.info(
            f"Model {self.best_model_name} {metric}={value:.4f} "
            f"{'meets' if meets_threshold else 'does not meet'} "
            f"threshold {threshold:.4f}"
        )
        
        return meets_threshold
    
    def get_model_by_name(self, name: str) -> Optional[Tuple[Any, Dict[str, float]]]:
        """
        Get a specific model by name.
        
        Args:
            name: Model name
            
        Returns:
            Tuple of (model, metrics) or None if not found
        """
        for result in self.results:
            if result["name"] == name:
                return result["model"], result["metrics"]
        
        logger.warning(f"Model '{name}' not found")
        return None, None
    
    def get_all_models(self) -> Dict[str, Tuple[Any, Dict[str, float]]]:
        """
        Get all models with their metrics.
        
        Returns:
            Dictionary mapping model names to (model, metrics) tuples
        """
        return {
            result["name"]: (result["model"], result["metrics"])
            for result in self.results
        }
