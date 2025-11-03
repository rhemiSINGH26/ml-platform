"""
Drift detector using Evidently AI.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from loguru import logger

try:
    from evidently import ColumnMapping
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset, DataQualityPreset
    from evidently.test_suite import TestSuite
    from evidently.tests import TestColumnDrift, TestShareOfDriftedColumns
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False
    logger.warning("Evidently not installed. Install with: pip install evidently")

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import settings


class DriftDetector:
    """Detect data and prediction drift using Evidently."""
    
    def __init__(self, drift_threshold: float = 0.1):
        """
        Initialize drift detector.
        
        Args:
            drift_threshold: Threshold for drift detection (0.0 - 1.0)
        """
        if not EVIDENTLY_AVAILABLE:
            raise ImportError("Evidently is required for drift detection")
        
        self.drift_threshold = drift_threshold
        self.reference_data = None
        self.column_mapping = None
        
    def set_reference_data(self, reference_df: pd.DataFrame, target_col: str = "target"):
        """
        Set reference data for drift comparison.
        
        Args:
            reference_df: Reference dataset (typically training data)
            target_col: Name of target column
        """
        self.reference_data = reference_df.copy()
        
        # Setup column mapping
        numerical_features = reference_df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numerical_features:
            numerical_features.remove(target_col)
        
        categorical_features = reference_df.select_dtypes(exclude=[np.number]).columns.tolist()
        
        self.column_mapping = ColumnMapping(
            target=target_col,
            numerical_features=numerical_features,
            categorical_features=categorical_features if categorical_features else None
        )
        
        logger.info(
            f"Reference data set: {len(reference_df)} samples, "
            f"{len(numerical_features)} numerical features, "
            f"{len(categorical_features) if categorical_features else 0} categorical features"
        )
    
    def detect_drift(
        self,
        current_df: pd.DataFrame,
        save_report: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Detect drift between reference and current data.
        
        Args:
            current_df: Current dataset to check for drift
            save_report: Whether to save HTML report
            
        Returns:
            Tuple of (drift_detected, drift_report)
        """
        if self.reference_data is None:
            raise ValueError("Reference data not set. Call set_reference_data() first.")
        
        logger.info(f"Detecting drift on {len(current_df)} samples...")
        
        # Create report
        report = Report(metrics=[
            DataDriftPreset(drift_share=self.drift_threshold),
            DataQualityPreset()
        ])
        
        # Run report
        report.run(
            reference_data=self.reference_data,
            current_data=current_df,
            column_mapping=self.column_mapping
        )
        
        # Extract results
        result = report.as_dict()
        
        # Check for dataset drift
        drift_detected = False
        drifted_features = []
        
        try:
            # Navigate the result dictionary
            for metric in result.get("metrics", []):
                if metric.get("metric") == "DatasetDriftMetric":
                    drift_detected = metric["result"]["dataset_drift"]
                    drifted_features = [
                        feat for feat, info in metric["result"]["drift_by_columns"].items()
                        if info.get("drift_detected", False)
                    ]
                    break
        except (KeyError, TypeError) as e:
            logger.warning(f"Could not parse drift results: {e}")
        
        logger.info(
            f"Drift detection complete: "
            f"{'DRIFT DETECTED' if drift_detected else 'NO DRIFT'}"
        )
        
        if drifted_features:
            logger.warning(f"Drifted features: {', '.join(drifted_features)}")
        
        # Save report
        if save_report:
            reports_dir = settings.reports_dir / "drift"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = reports_dir / f"drift_report_{timestamp}.html"
            
            report.save_html(str(report_path))
            logger.info(f"Drift report saved to {report_path}")
        
        # Build summary
        drift_summary = {
            "drift_detected": drift_detected,
            "drifted_features": drifted_features,
            "n_drifted_features": len(drifted_features),
            "drift_share": len(drifted_features) / len(self.column_mapping.numerical_features or [])
            if self.column_mapping.numerical_features else 0,
            "threshold": self.drift_threshold,
            "timestamp": datetime.now().isoformat(),
            "reference_size": len(self.reference_data),
            "current_size": len(current_df)
        }
        
        return drift_detected, drift_summary
    
    def test_drift(self, current_df: pd.DataFrame) -> bool:
        """
        Run drift tests (pass/fail).
        
        Args:
            current_df: Current dataset
            
        Returns:
            True if tests pass, False if drift detected
        """
        if self.reference_data is None:
            raise ValueError("Reference data not set. Call set_reference_data() first.")
        
        # Create test suite
        tests = TestSuite(tests=[
            TestShareOfDriftedColumns(lt=self.drift_threshold),
        ])
        
        # Run tests
        tests.run(
            reference_data=self.reference_data,
            current_data=current_df,
            column_mapping=self.column_mapping
        )
        
        # Check if all tests passed
        result = tests.as_dict()
        all_passed = result.get("summary", {}).get("all_passed", False)
        
        logger.info(f"Drift tests: {'PASSED' if all_passed else 'FAILED'}")
        
        return all_passed
    
    def get_feature_drift_scores(
        self,
        current_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Get drift scores for individual features.
        
        Args:
            current_df: Current dataset
            
        Returns:
            Dictionary mapping feature names to drift scores
        """
        if self.reference_data is None:
            raise ValueError("Reference data not set. Call set_reference_data() first.")
        
        report = Report(metrics=[DataDriftPreset()])
        
        report.run(
            reference_data=self.reference_data,
            current_data=current_df,
            column_mapping=self.column_mapping
        )
        
        result = report.as_dict()
        
        # Extract drift scores
        drift_scores = {}
        
        try:
            for metric in result.get("metrics", []):
                if metric.get("metric") == "DatasetDriftMetric":
                    for feat, info in metric["result"]["drift_by_columns"].items():
                        # Get drift score (could be p-value, distance, etc.)
                        drift_scores[feat] = info.get("drift_score", 0.0)
                    break
        except (KeyError, TypeError) as e:
            logger.warning(f"Could not extract drift scores: {e}")
        
        return drift_scores


def load_reference_data() -> pd.DataFrame:
    """
    Load reference data (training data).
    
    Returns:
        Reference DataFrame
    """
    train_data_path = settings.processed_data_dir / "train.csv"
    
    if not train_data_path.exists():
        raise FileNotFoundError(f"Training data not found: {train_data_path}")
    
    logger.info(f"Loading reference data from {train_data_path}")
    df = pd.read_csv(train_data_path)
    
    return df
