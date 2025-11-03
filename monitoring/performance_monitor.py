"""
Performance monitor - tracks model performance metrics over time.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import json
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings


class PerformanceMonitor:
    """Monitor and track model performance metrics."""
    
    def __init__(self, metrics_file: Path = None):
        """
        Initialize performance monitor.
        
        Args:
            metrics_file: Path to metrics history file
        """
        self.metrics_file = metrics_file or (settings.reports_dir / "performance_history.jsonl")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create file if it doesn't exist
        if not self.metrics_file.exists():
            self.metrics_file.touch()
            logger.info(f"Created metrics file: {self.metrics_file}")
    
    def log_metrics(
        self,
        metrics: Dict[str, float],
        metadata: Dict[str, Any] = None
    ):
        """
        Log performance metrics.
        
        Args:
            metrics: Dictionary of metric names to values
            metadata: Optional metadata (model name, version, etc.)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "metadata": metadata or {}
        }
        
        # Append to JSONL file
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        logger.info(f"Logged metrics: {metrics}")
    
    def get_metrics_history(
        self,
        metric_name: str = None,
        limit: int = None
    ) -> pd.DataFrame:
        """
        Get metrics history.
        
        Args:
            metric_name: Specific metric to retrieve (None for all)
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with metrics history
        """
        if not self.metrics_file.exists() or self.metrics_file.stat().st_size == 0:
            logger.warning("No metrics history available")
            return pd.DataFrame()
        
        # Read JSONL file
        records = []
        with open(self.metrics_file, "r") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        
        if not records:
            return pd.DataFrame()
        
        # Convert to DataFrame
        rows = []
        for record in records:
            row = {"timestamp": record["timestamp"]}
            row.update(record["metrics"])
            row.update(record.get("metadata", {}))
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Filter by metric name if specified
        if metric_name and metric_name in df.columns:
            df = df[["timestamp", metric_name]]
        
        # Apply limit
        if limit:
            df = df.tail(limit)
        
        return df
    
    def get_latest_metrics(self) -> Dict[str, float]:
        """
        Get the most recent metrics.
        
        Returns:
            Dictionary of latest metrics
        """
        if not self.metrics_file.exists() or self.metrics_file.stat().st_size == 0:
            logger.warning("No metrics available")
            return {}
        
        # Read last line
        with open(self.metrics_file, "r") as f:
            lines = f.readlines()
        
        if not lines:
            return {}
        
        last_record = json.loads(lines[-1])
        return last_record.get("metrics", {})
    
    def check_performance_degradation(
        self,
        metric_name: str,
        threshold: float,
        window: int = 10
    ) -> bool:
        """
        Check if performance has degraded below threshold.
        
        Args:
            metric_name: Name of metric to check
            threshold: Minimum acceptable value
            window: Number of recent samples to check
            
        Returns:
            True if degradation detected, False otherwise
        """
        df = self.get_metrics_history(metric_name=metric_name, limit=window)
        
        if df.empty or metric_name not in df.columns:
            logger.warning(f"No data for metric: {metric_name}")
            return False
        
        recent_values = df[metric_name].values
        below_threshold = recent_values < threshold
        
        # Check if majority of recent values are below threshold
        degradation = np.mean(below_threshold) > 0.5
        
        if degradation:
            logger.warning(
                f"Performance degradation detected: {metric_name} "
                f"below {threshold} in {np.sum(below_threshold)}/{len(recent_values)} recent samples"
            )
        
        return degradation
    
    def get_metric_trend(
        self,
        metric_name: str,
        window: int = 30
    ) -> str:
        """
        Get trend for a metric (improving, degrading, stable).
        
        Args:
            metric_name: Name of metric
            window: Number of recent samples to analyze
            
        Returns:
            One of: "improving", "degrading", "stable"
        """
        df = self.get_metrics_history(metric_name=metric_name, limit=window)
        
        if df.empty or metric_name not in df.columns or len(df) < 5:
            return "stable"
        
        values = df[metric_name].values
        
        # Simple linear regression
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # Determine trend based on slope
        if abs(slope) < 0.001:
            return "stable"
        elif slope > 0:
            return "improving"
        else:
            return "degrading"
    
    def calculate_statistics(
        self,
        metric_name: str,
        window: int = 30
    ) -> Dict[str, float]:
        """
        Calculate statistics for a metric.
        
        Args:
            metric_name: Name of metric
            window: Number of recent samples
            
        Returns:
            Dictionary with mean, std, min, max, median
        """
        df = self.get_metrics_history(metric_name=metric_name, limit=window)
        
        if df.empty or metric_name not in df.columns:
            return {}
        
        values = df[metric_name].values
        
        return {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "median": float(np.median(values)),
            "current": float(values[-1]) if len(values) > 0 else 0.0
        }
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Returns:
            Dictionary with performance summary
        """
        latest = self.get_latest_metrics()
        
        if not latest:
            return {"status": "no_data"}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "latest_metrics": latest,
            "trends": {},
            "statistics": {}
        }
        
        # Calculate trends and statistics for each metric
        for metric_name in latest.keys():
            report["trends"][metric_name] = self.get_metric_trend(metric_name)
            report["statistics"][metric_name] = self.calculate_statistics(metric_name)
        
        return report
    
    def alert_if_degraded(
        self,
        metric_thresholds: Dict[str, float]
    ) -> List[str]:
        """
        Check metrics against thresholds and return alerts.
        
        Args:
            metric_thresholds: Dictionary mapping metric names to minimum thresholds
            
        Returns:
            List of alert messages
        """
        alerts = []
        
        for metric_name, threshold in metric_thresholds.items():
            if self.check_performance_degradation(metric_name, threshold):
                stats = self.calculate_statistics(metric_name, window=10)
                current = stats.get("current", 0.0)
                
                alert_msg = (
                    f"⚠️ Performance Alert: {metric_name} = {current:.4f} "
                    f"(threshold: {threshold:.4f})"
                )
                alerts.append(alert_msg)
                logger.warning(alert_msg)
        
        return alerts
