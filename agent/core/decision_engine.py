"""
Decision engine - recommends actions based on diagnosed issues.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from agent.core.diagnosis_engine import Issue


class Action:
    """Represents a recommended action."""
    
    def __init__(
        self,
        action_type: str,
        risk_level: str,
        description: str,
        parameters: Dict[str, Any],
        reason: str,
        related_issue: Optional[Issue] = None,
        estimated_impact: str = "Unknown",
        requires_approval: bool = False
    ):
        """
        Initialize action.
        
        Args:
            action_type: Type of action to take
            risk_level: Risk level (low, medium, high)
            description: Human-readable description
            parameters: Parameters for executing the action
            reason: Reason for this action
            related_issue: Issue that triggered this action
            estimated_impact: Estimated impact description
            requires_approval: Whether human approval is required
        """
        self.action_type = action_type
        self.risk_level = risk_level
        self.description = description
        self.parameters = parameters
        self.reason = reason
        self.related_issue = related_issue
        self.estimated_impact = estimated_impact
        self.requires_approval = requires_approval
        self.timestamp = datetime.now()
        self.action_id = f"ACT-{self.timestamp.strftime('%Y%m%d%H%M%S')}"
        self.status = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary."""
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "risk_level": self.risk_level,
            "description": self.description,
            "parameters": self.parameters,
            "reason": self.reason,
            "estimated_impact": self.estimated_impact,
            "requires_approval": self.requires_approval,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "related_issue_id": self.related_issue.issue_id if self.related_issue else None
        }
    
    def __repr__(self) -> str:
        return f"Action({self.action_id}, {self.action_type}, {self.risk_level})"


class DecisionEngine:
    """Decide what actions to take based on issues."""
    
    def __init__(self, auto_approve_low_risk: bool = True):
        """
        Initialize decision engine.
        
        Args:
            auto_approve_low_risk: Whether to auto-approve low risk actions
        """
        self.auto_approve_low_risk = auto_approve_low_risk
        self.recommended_actions = []
        
        # Define action templates
        self.action_templates = self._define_action_templates()
    
    def _define_action_templates(self) -> Dict[str, Dict[str, Any]]:
        """Define templates for different action types."""
        return {
            "retrain_model": {
                "risk_level": "medium",
                "requires_approval": True,
                "estimated_impact": "Training time: 15-30 minutes, Resources: 2 CPU cores"
            },
            "rollback_model": {
                "risk_level": "high",
                "requires_approval": True,
                "estimated_impact": "Service downtime: 2-5 minutes"
            },
            "send_alert": {
                "risk_level": "low",
                "requires_approval": False,
                "estimated_impact": "Email/Slack notification sent to team"
            },
            "adjust_threshold": {
                "risk_level": "low",
                "requires_approval": False,
                "estimated_impact": "Minimal - threshold configuration update"
            },
            "collect_diagnostics": {
                "risk_level": "low",
                "requires_approval": False,
                "estimated_impact": "System diagnostics collected for analysis"
            },
            "validate_data": {
                "risk_level": "low",
                "requires_approval": False,
                "estimated_impact": "Data validation check, no changes made"
            },
            "generate_report": {
                "risk_level": "low",
                "requires_approval": False,
                "estimated_impact": "Performance report generated and emailed"
            }
        }
    
    def decide_action_for_issue(self, issue: Issue) -> List[Action]:
        """
        Decide what action(s) to take for a specific issue.
        
        Args:
            issue: Detected issue
            
        Returns:
            List of recommended actions
        """
        actions = []
        
        if issue.issue_type == "data_drift":
            actions.extend(self._handle_data_drift(issue))
        
        elif issue.issue_type == "performance_degradation":
            actions.extend(self._handle_performance_degradation(issue))
        
        elif issue.issue_type == "prediction_anomaly":
            actions.extend(self._handle_prediction_anomaly(issue))
        
        elif issue.issue_type == "low_confidence":
            actions.extend(self._handle_low_confidence(issue))
        
        elif issue.issue_type == "data_quality":
            actions.extend(self._handle_data_quality(issue))
        
        else:
            # Default: send alert and collect diagnostics
            actions.append(self._create_alert_action(issue))
            actions.append(self._create_diagnostics_action(issue))
        
        return actions
    
    def _handle_data_drift(self, issue: Issue) -> List[Action]:
        """Handle data drift issue."""
        actions = []
        
        severity = issue.severity
        n_drifted = issue.details.get("n_drifted_features", 0)
        
        # Always send alert
        actions.append(self._create_alert_action(
            issue,
            message=f"Data drift detected on {n_drifted} features"
        ))
        
        # If severe drift, recommend retraining
        if severity in ["high", "critical"] or n_drifted >= 5:
            template = self.action_templates["retrain_model"]
            action = Action(
                action_type="retrain_model",
                risk_level=template["risk_level"],
                description=f"Retrain model due to drift on {n_drifted} features",
                parameters={
                    "trigger": "data_drift",
                    "drifted_features": issue.details.get("drifted_features", []),
                    "use_latest_data": True
                },
                reason=f"Significant data drift detected ({n_drifted} features)",
                related_issue=issue,
                estimated_impact=template["estimated_impact"],
                requires_approval=template["requires_approval"]
            )
            actions.append(action)
        
        # Generate drift report
        actions.append(self._create_report_action(
            issue,
            report_type="drift_analysis"
        ))
        
        return actions
    
    def _handle_performance_degradation(self, issue: Issue) -> List[Action]:
        """Handle performance degradation issue."""
        actions = []
        
        metric = issue.details.get("metric", "unknown")
        current = issue.details.get("current", 0.0)
        threshold = issue.details.get("threshold", 0.0)
        
        # Send critical alert
        actions.append(self._create_alert_action(
            issue,
            message=f"Performance degradation: {metric} = {current:.4f} (threshold: {threshold:.4f})",
            priority="high"
        ))
        
        # Collect diagnostics
        actions.append(self._create_diagnostics_action(issue))
        
        # If critical, consider rollback
        if issue.severity == "critical":
            template = self.action_templates["rollback_model"]
            action = Action(
                action_type="rollback_model",
                risk_level=template["risk_level"],
                description="Rollback to previous model version",
                parameters={
                    "trigger": "performance_degradation",
                    "metric": metric,
                    "current_value": current,
                    "rollback_to": "previous_production"
                },
                reason=f"Critical performance drop: {metric} below threshold",
                related_issue=issue,
                estimated_impact=template["estimated_impact"],
                requires_approval=True
            )
            actions.append(action)
        else:
            # Otherwise, retrain
            template = self.action_templates["retrain_model"]
            action = Action(
                action_type="retrain_model",
                risk_level=template["risk_level"],
                description="Retrain model to recover performance",
                parameters={
                    "trigger": "performance_degradation",
                    "metric": metric,
                    "use_latest_data": True
                },
                reason=f"Performance below acceptable threshold: {metric}",
                related_issue=issue,
                estimated_impact=template["estimated_impact"],
                requires_approval=template["requires_approval"]
            )
            actions.append(action)
        
        return actions
    
    def _handle_prediction_anomaly(self, issue: Issue) -> List[Action]:
        """Handle prediction anomaly."""
        actions = []
        
        # Send alert
        actions.append(self._create_alert_action(issue))
        
        # Collect diagnostics
        actions.append(self._create_diagnostics_action(issue))
        
        # Validate recent data
        template = self.action_templates["validate_data"]
        action = Action(
            action_type="validate_data",
            risk_level=template["risk_level"],
            description="Validate recent input data for anomalies",
            parameters={"validation_type": "schema_and_distribution"},
            reason="Unusual prediction patterns detected",
            related_issue=issue,
            estimated_impact=template["estimated_impact"],
            requires_approval=template["requires_approval"]
        )
        actions.append(action)
        
        return actions
    
    def _handle_low_confidence(self, issue: Issue) -> List[Action]:
        """Handle low confidence predictions."""
        actions = []
        
        # Send alert
        actions.append(self._create_alert_action(issue))
        
        # Consider retraining if persistent
        ratio = issue.details.get("ratio", 0.0)
        if ratio > 0.4:  # More than 40% low confidence
            template = self.action_templates["retrain_model"]
            action = Action(
                action_type="retrain_model",
                risk_level=template["risk_level"],
                description="Retrain model to improve confidence",
                parameters={
                    "trigger": "low_confidence",
                    "low_confidence_ratio": ratio
                },
                reason=f"High proportion of low-confidence predictions: {ratio:.2%}",
                related_issue=issue,
                estimated_impact=template["estimated_impact"],
                requires_approval=template["requires_approval"]
            )
            actions.append(action)
        
        return actions
    
    def _handle_data_quality(self, issue: Issue) -> List[Action]:
        """Handle data quality issues."""
        actions = []
        
        # Send alert
        actions.append(self._create_alert_action(issue))
        
        # Validate data
        template = self.action_templates["validate_data"]
        action = Action(
            action_type="validate_data",
            risk_level=template["risk_level"],
            description="Run comprehensive data quality validation",
            parameters={"validation_type": "full"},
            reason="Data quality issues detected",
            related_issue=issue,
            estimated_impact=template["estimated_impact"],
            requires_approval=template["requires_approval"]
        )
        actions.append(action)
        
        return actions
    
    def _create_alert_action(
        self,
        issue: Issue,
        message: str = None,
        priority: str = "normal"
    ) -> Action:
        """Create an alert action."""
        template = self.action_templates["send_alert"]
        
        return Action(
            action_type="send_alert",
            risk_level=template["risk_level"],
            description=message or f"Alert: {issue.description}",
            parameters={
                "channels": ["email", "slack"],
                "priority": priority,
                "issue_details": issue.to_dict()
            },
            reason=f"Notify team about {issue.issue_type}",
            related_issue=issue,
            estimated_impact=template["estimated_impact"],
            requires_approval=template["requires_approval"]
        )
    
    def _create_diagnostics_action(self, issue: Issue) -> Action:
        """Create a diagnostics collection action."""
        template = self.action_templates["collect_diagnostics"]
        
        return Action(
            action_type="collect_diagnostics",
            risk_level=template["risk_level"],
            description="Collect system diagnostics for analysis",
            parameters={"issue_type": issue.issue_type},
            reason="Gather information for troubleshooting",
            related_issue=issue,
            estimated_impact=template["estimated_impact"],
            requires_approval=template["requires_approval"]
        )
    
    def _create_report_action(
        self,
        issue: Issue,
        report_type: str = "general"
    ) -> Action:
        """Create a report generation action."""
        template = self.action_templates["generate_report"]
        
        return Action(
            action_type="generate_report",
            risk_level=template["risk_level"],
            description=f"Generate {report_type} report",
            parameters={"report_type": report_type, "issue_id": issue.issue_id},
            reason=f"Document {issue.issue_type} for records",
            related_issue=issue,
            estimated_impact=template["estimated_impact"],
            requires_approval=template["requires_approval"]
        )
    
    def recommend_actions(self, issues: List[Issue]) -> List[Action]:
        """
        Recommend actions for all issues.
        
        Args:
            issues: List of detected issues
            
        Returns:
            List of recommended actions
        """
        logger.info(f"Recommending actions for {len(issues)} issues...")
        
        all_actions = []
        
        for issue in issues:
            actions = self.decide_action_for_issue(issue)
            all_actions.extend(actions)
            
            logger.info(
                f"Issue {issue.issue_id} ({issue.severity}): "
                f"{len(actions)} actions recommended"
            )
        
        # Apply auto-approval logic
        for action in all_actions:
            if self.auto_approve_low_risk and action.risk_level == "low":
                action.requires_approval = False
                logger.info(f"Action {action.action_id} auto-approved (low risk)")
        
        self.recommended_actions = all_actions
        
        # Summary
        needs_approval = sum(1 for a in all_actions if a.requires_approval)
        auto_execute = len(all_actions) - needs_approval
        
        logger.info(f"Total actions: {len(all_actions)}")
        logger.info(f"  - Auto-execute: {auto_execute}")
        logger.info(f"  - Requires approval: {needs_approval}")
        
        return all_actions
    
    def get_actions_by_approval_status(self, requires_approval: bool) -> List[Action]:
        """Get actions filtered by approval requirement."""
        return [
            action for action in self.recommended_actions
            if action.requires_approval == requires_approval
        ]
    
    def get_high_priority_actions(self) -> List[Action]:
        """Get high and critical risk actions."""
        return [
            action for action in self.recommended_actions
            if action.risk_level in ["high", "critical"]
        ]
