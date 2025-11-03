"""
Diagnosis engine - detects issues in the ML system.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config.settings import settings
from monitoring.drift_detector import DriftDetector, load_reference_data
from monitoring.performance_monitor import PerformanceMonitor


class Issue:
    """Represents a detected issue."""
    
    def __init__(
        self,
        issue_type: str,
        severity: str,
        description: str,
        details: Dict[str, Any],
        timestamp: datetime = None
    ):
        """
        Initialize issue.
        
        Args:
            issue_type: Type of issue (drift, performance, data_quality, etc.)
            severity: Severity level (low, medium, high, critical)
            description: Human-readable description
            details: Additional details about the issue
            timestamp: When the issue was detected
        """
        self.issue_type = issue_type
        self.severity = severity
        self.description = description
        self.details = details
        self.timestamp = timestamp or datetime.now()
        self.issue_id = f"ISSUE-{self.timestamp.strftime('%Y%m%d%H%M%S')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "issue_id": self.issue_id,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "description": self.description,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"Issue({self.issue_id}, {self.severity}, {self.issue_type})"


class DiagnosisEngine:
    """Diagnose issues in the ML system."""
    
    def __init__(self):
        """Initialize diagnosis engine."""
        self.drift_detector = None
        self.performance_monitor = PerformanceMonitor()
        self.detected_issues = []
        
    def initialize_drift_detector(self):
        """Initialize drift detector with reference data."""
        try:
            if self.drift_detector is None:
                self.drift_detector = DriftDetector(drift_threshold=0.1)
                reference_data = load_reference_data()
                self.drift_detector.set_reference_data(reference_data, target_col="target")
                logger.info("Drift detector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize drift detector: {e}")
    
    def check_data_drift(self, current_data) -> List[Issue]:
        """
        Check for data drift.
        
        Args:
            current_data: Current dataset to check
            
        Returns:
            List of drift-related issues
        """
        issues = []
        
        try:
            self.initialize_drift_detector()
            
            drift_detected, drift_summary = self.drift_detector.detect_drift(
                current_data,
                save_report=True
            )
            
            if drift_detected:
                # Determine severity based on number of drifted features
                n_drifted = drift_summary.get("n_drifted_features", 0)
                if n_drifted >= 5:
                    severity = "high"
                elif n_drifted >= 3:
                    severity = "medium"
                else:
                    severity = "low"
                
                issue = Issue(
                    issue_type="data_drift",
                    severity=severity,
                    description=f"Data drift detected on {n_drifted} features",
                    details=drift_summary
                )
                issues.append(issue)
                logger.warning(f"Detected data drift: {issue}")
        
        except Exception as e:
            logger.error(f"Error checking data drift: {e}")
        
        return issues
    
    def check_performance_degradation(
        self,
        metric_thresholds: Dict[str, float] = None
    ) -> List[Issue]:
        """
        Check for performance degradation.
        
        Args:
            metric_thresholds: Dictionary of metric name to minimum threshold
            
        Returns:
            List of performance-related issues
        """
        issues = []
        
        # Default thresholds
        if metric_thresholds is None:
            metric_thresholds = {
                "f1_score": 0.75,
                "accuracy": 0.75,
                "precision": 0.70,
                "recall": 0.70
            }
        
        try:
            # Check each metric
            for metric_name, threshold in metric_thresholds.items():
                if self.performance_monitor.check_performance_degradation(
                    metric_name,
                    threshold,
                    window=10
                ):
                    stats = self.performance_monitor.calculate_statistics(
                        metric_name,
                        window=10
                    )
                    
                    current = stats.get("current", 0.0)
                    severity = "critical" if current < threshold - 0.1 else "high"
                    
                    issue = Issue(
                        issue_type="performance_degradation",
                        severity=severity,
                        description=f"{metric_name} below threshold: {current:.4f} < {threshold:.4f}",
                        details={
                            "metric": metric_name,
                            "current": current,
                            "threshold": threshold,
                            "statistics": stats
                        }
                    )
                    issues.append(issue)
                    logger.warning(f"Detected performance degradation: {issue}")
        
        except Exception as e:
            logger.error(f"Error checking performance: {e}")
        
        return issues
    
    def check_prediction_anomalies(
        self,
        predictions: List[int],
        probabilities: List[float] = None
    ) -> List[Issue]:
        """
        Check for prediction anomalies.
        
        Args:
            predictions: List of predictions
            probabilities: List of prediction probabilities
            
        Returns:
            List of anomaly-related issues
        """
        issues = []
        
        try:
            import numpy as np
            
            # Check class distribution
            unique, counts = np.unique(predictions, return_counts=True)
            class_dist = dict(zip(unique, counts))
            
            # Check for extreme class imbalance in predictions
            if len(class_dist) == 2:
                ratio = min(counts) / max(counts)
                if ratio < 0.05:  # Less than 5% minority class
                    issue = Issue(
                        issue_type="prediction_anomaly",
                        severity="medium",
                        description=f"Extreme class imbalance in predictions: {ratio:.2%}",
                        details={"class_distribution": class_dist, "ratio": ratio}
                    )
                    issues.append(issue)
                    logger.warning(f"Detected prediction anomaly: {issue}")
            
            # Check probability confidence
            if probabilities:
                low_confidence = sum(1 for p in probabilities if 0.4 < p < 0.6)
                low_conf_ratio = low_confidence / len(probabilities)
                
                if low_conf_ratio > 0.3:  # More than 30% low confidence
                    issue = Issue(
                        issue_type="low_confidence",
                        severity="medium",
                        description=f"High proportion of low-confidence predictions: {low_conf_ratio:.2%}",
                        details={
                            "low_confidence_count": low_confidence,
                            "total": len(probabilities),
                            "ratio": low_conf_ratio
                        }
                    )
                    issues.append(issue)
                    logger.warning(f"Detected low confidence: {issue}")
        
        except Exception as e:
            logger.error(f"Error checking prediction anomalies: {e}")
        
        return issues
    
    def check_data_quality(self, data) -> List[Issue]:
        """
        Check data quality issues.
        
        Args:
            data: DataFrame to check
            
        Returns:
            List of data quality issues
        """
        issues = []
        
        try:
            import pandas as pd
            
            # Check missing values
            missing_pct = data.isnull().sum() / len(data)
            high_missing = missing_pct[missing_pct > 0.1]
            
            if len(high_missing) > 0:
                issue = Issue(
                    issue_type="data_quality",
                    severity="medium",
                    description=f"{len(high_missing)} features with >10% missing values",
                    details={"features": high_missing.to_dict()}
                )
                issues.append(issue)
                logger.warning(f"Detected data quality issue: {issue}")
            
            # Check for duplicates
            duplicates = data.duplicated().sum()
            if duplicates > len(data) * 0.05:  # More than 5% duplicates
                issue = Issue(
                    issue_type="data_quality",
                    severity="low",
                    description=f"{duplicates} duplicate rows ({duplicates/len(data):.2%})",
                    details={"duplicates": int(duplicates), "total": len(data)}
                )
                issues.append(issue)
                logger.warning(f"Detected duplicates: {issue}")
        
        except Exception as e:
            logger.error(f"Error checking data quality: {e}")
        
        return issues
    
    def run_full_diagnosis(
        self,
        current_data=None,
        predictions=None,
        probabilities=None
    ) -> List[Issue]:
        """
        Run full system diagnosis.
        
        Args:
            current_data: Current dataset (for drift detection)
            predictions: Recent predictions (for anomaly detection)
            probabilities: Prediction probabilities
            
        Returns:
            List of all detected issues
        """
        logger.info("Running full system diagnosis...")
        
        all_issues = []
        
        # Check performance
        perf_issues = self.check_performance_degradation()
        all_issues.extend(perf_issues)
        
        # Check data drift if data provided
        if current_data is not None:
            drift_issues = self.check_data_drift(current_data)
            all_issues.extend(drift_issues)
            
            # Check data quality
            quality_issues = self.check_data_quality(current_data)
            all_issues.extend(quality_issues)
        
        # Check prediction anomalies if predictions provided
        if predictions is not None:
            anomaly_issues = self.check_prediction_anomalies(predictions, probabilities)
            all_issues.extend(anomaly_issues)
        
        # Store detected issues
        self.detected_issues = all_issues
        
        logger.info(f"Diagnosis complete: {len(all_issues)} issues detected")
        
        # Log summary by severity
        severity_counts = {}
        for issue in all_issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        for severity, count in severity_counts.items():
            logger.info(f"  - {severity}: {count} issues")
        
        return all_issues
    
    def get_issues_by_severity(self, severity: str) -> List[Issue]:
        """Get issues filtered by severity."""
        return [issue for issue in self.detected_issues if issue.severity == severity]
    
    def get_critical_issues(self) -> List[Issue]:
        """Get all critical and high severity issues."""
        return [
            issue for issue in self.detected_issues
            if issue.severity in ["critical", "high"]
        ]
