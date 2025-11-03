"""
CRUD operations for database models.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from database.models import (
    ModelVersion,
    Prediction,
    DriftReport,
    AgentAction,
    PerformanceMetric,
    Alert,
)


# ============================================================================
# ModelVersion CRUD
# ============================================================================

def create_model_version(
    db: Session,
    model_name: str,
    version: str,
    algorithm: str,
    metrics: Dict[str, float],
    hyperparameters: Dict[str, Any],
    feature_names: List[str],
    model_path: str,
    metadata_path: str,
    training_samples: int,
) -> ModelVersion:
    """Create a new model version."""
    model = ModelVersion(
        model_name=model_name,
        version=version,
        algorithm=algorithm,
        accuracy=metrics.get("accuracy"),
        f1_score=metrics.get("f1"),
        precision=metrics.get("precision"),
        recall=metrics.get("recall"),
        roc_auc=metrics.get("roc_auc"),
        hyperparameters=hyperparameters,
        feature_names=feature_names,
        model_path=model_path,
        metadata_path=metadata_path,
        training_samples=training_samples,
        status="staging",
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


def get_model_version(db: Session, model_id: int) -> Optional[ModelVersion]:
    """Get a model version by ID."""
    return db.query(ModelVersion).filter(ModelVersion.id == model_id).first()


def get_active_model(db: Session) -> Optional[ModelVersion]:
    """Get the currently active (production) model."""
    return db.query(ModelVersion).filter(
        ModelVersion.is_active == True
    ).first()


def get_model_versions(
    db: Session,
    model_name: str = None,
    limit: int = 10,
) -> List[ModelVersion]:
    """Get model versions."""
    query = db.query(ModelVersion)
    if model_name:
        query = query.filter(ModelVersion.model_name == model_name)
    return query.order_by(desc(ModelVersion.created_at)).limit(limit).all()


def set_model_active(db: Session, model_id: int) -> ModelVersion:
    """Set a model as active (deactivate others)."""
    # Deactivate all models
    db.query(ModelVersion).update({"is_active": False, "status": "archived"})
    
    # Activate target model
    model = get_model_version(db, model_id)
    if model:
        model.is_active = True
        model.status = "production"
        db.commit()
        db.refresh(model)
    return model


# ============================================================================
# Prediction CRUD
# ============================================================================

def create_prediction(
    db: Session,
    model_id: int,
    features: Dict[str, Any],
    prediction: int,
    probability: float,
    latency_ms: float,
) -> Prediction:
    """Create a prediction record."""
    pred = Prediction(
        model_id=model_id,
        features=features,
        prediction=prediction,
        probability=probability,
        latency_ms=latency_ms,
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred


def get_recent_predictions(
    db: Session,
    model_id: int = None,
    hours: int = 24,
    limit: int = 1000,
) -> List[Prediction]:
    """Get recent predictions."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    query = db.query(Prediction).filter(Prediction.created_at >= cutoff)
    if model_id:
        query = query.filter(Prediction.model_id == model_id)
    return query.order_by(desc(Prediction.created_at)).limit(limit).all()


def update_prediction_actual(
    db: Session,
    prediction_id: int,
    actual: int,
) -> Optional[Prediction]:
    """Update prediction with actual value (ground truth)."""
    pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if pred:
        pred.actual = actual
        db.commit()
        db.refresh(pred)
    return pred


# ============================================================================
# DriftReport CRUD
# ============================================================================

def create_drift_report(
    db: Session,
    model_id: int,
    drift_detected: bool,
    drift_score: float,
    drifted_features: List[str],
    report_path: str,
    reference_size: int,
    current_size: int,
) -> DriftReport:
    """Create a drift report."""
    report = DriftReport(
        model_id=model_id,
        drift_detected=drift_detected,
        drift_score=drift_score,
        drifted_features=drifted_features,
        n_drifted_features=len(drifted_features),
        report_path=report_path,
        reference_size=reference_size,
        current_size=current_size,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_latest_drift_report(
    db: Session,
    model_id: int = None,
) -> Optional[DriftReport]:
    """Get the latest drift report."""
    query = db.query(DriftReport)
    if model_id:
        query = query.filter(DriftReport.model_id == model_id)
    return query.order_by(desc(DriftReport.created_at)).first()


def get_drift_reports(
    db: Session,
    model_id: int = None,
    days: int = 30,
    limit: int = 100,
) -> List[DriftReport]:
    """Get drift reports."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = db.query(DriftReport).filter(DriftReport.created_at >= cutoff)
    if model_id:
        query = query.filter(DriftReport.model_id == model_id)
    return query.order_by(desc(DriftReport.created_at)).limit(limit).all()


# ============================================================================
# AgentAction CRUD
# ============================================================================

def create_agent_action(
    db: Session,
    action_id: str,
    action_type: str,
    description: str,
    risk_level: str,
    requires_approval: bool,
    parameters: Dict[str, Any] = None,
    issue_id: str = None,
    issue_type: str = None,
    issue_severity: str = None,
) -> AgentAction:
    """Create an agent action."""
    action = AgentAction(
        action_id=action_id,
        action_type=action_type,
        description=description,
        risk_level=risk_level,
        requires_approval=requires_approval,
        parameters=parameters or {},
        issue_id=issue_id,
        issue_type=issue_type,
        issue_severity=issue_severity,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


def get_agent_action(db: Session, action_id: str) -> Optional[AgentAction]:
    """Get an agent action by ID."""
    return db.query(AgentAction).filter(
        AgentAction.action_id == action_id
    ).first()


def get_pending_actions(db: Session) -> List[AgentAction]:
    """Get actions pending approval."""
    return db.query(AgentAction).filter(
        and_(
            AgentAction.status == "pending",
            AgentAction.requires_approval == True,
        )
    ).order_by(AgentAction.created_at).all()


def approve_action(
    db: Session,
    action_id: str,
    reviewer: str,
    comment: str = None,
) -> Optional[AgentAction]:
    """Approve an agent action."""
    action = get_agent_action(db, action_id)
    if action:
        action.status = "approved"
        action.reviewed_by = reviewer
        action.reviewed_at = datetime.utcnow()
        action.review_comment = comment
        db.commit()
        db.refresh(action)
    return action


def reject_action(
    db: Session,
    action_id: str,
    reviewer: str,
    comment: str = None,
) -> Optional[AgentAction]:
    """Reject an agent action."""
    action = get_agent_action(db, action_id)
    if action:
        action.status = "rejected"
        action.reviewed_by = reviewer
        action.reviewed_at = datetime.utcnow()
        action.review_comment = comment
        db.commit()
        db.refresh(action)
    return action


def mark_action_executed(
    db: Session,
    action_id: str,
    result: Dict[str, Any],
) -> Optional[AgentAction]:
    """Mark an action as executed."""
    action = get_agent_action(db, action_id)
    if action:
        action.status = "executed"
        action.executed_at = datetime.utcnow()
        action.execution_result = result
        db.commit()
        db.refresh(action)
    return action


def get_agent_actions(
    db: Session,
    action_type: str = None,
    status: str = None,
    days: int = 30,
    limit: int = 100,
) -> List[AgentAction]:
    """Get agent actions."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = db.query(AgentAction).filter(AgentAction.created_at >= cutoff)
    if action_type:
        query = query.filter(AgentAction.action_type == action_type)
    if status:
        query = query.filter(AgentAction.status == status)
    return query.order_by(desc(AgentAction.created_at)).limit(limit).all()


# ============================================================================
# PerformanceMetric CRUD
# ============================================================================

def create_performance_metric(
    db: Session,
    metric_name: str,
    metric_value: float,
    model_id: int = None,
    metadata: Dict[str, Any] = None,
) -> PerformanceMetric:
    """Create a performance metric."""
    metric = PerformanceMetric(
        metric_name=metric_name,
        metric_value=metric_value,
        model_id=model_id,
        metric_metadata=metadata or {},
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def get_metrics_timeseries(
    db: Session,
    metric_name: str,
    model_id: int = None,
    days: int = 30,
) -> List[PerformanceMetric]:
    """Get time series of a metric."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = db.query(PerformanceMetric).filter(
        and_(
            PerformanceMetric.metric_name == metric_name,
            PerformanceMetric.created_at >= cutoff,
        )
    )
    if model_id:
        query = query.filter(PerformanceMetric.model_id == model_id)
    return query.order_by(PerformanceMetric.created_at).all()


# ============================================================================
# Alert CRUD
# ============================================================================

def create_alert(
    db: Session,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    related_data: Dict[str, Any] = None,
) -> Alert:
    """Create an alert."""
    alert = Alert(
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        related_data=related_data or {},
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_active_alerts(db: Session) -> List[Alert]:
    """Get active alerts."""
    return db.query(Alert).filter(
        Alert.status == "active"
    ).order_by(desc(Alert.created_at)).all()


def acknowledge_alert(
    db: Session,
    alert_id: int,
    user: str,
) -> Optional[Alert]:
    """Acknowledge an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.status = "acknowledged"
        alert.acknowledged_by = user
        alert.acknowledged_at = datetime.utcnow()
        db.commit()
        db.refresh(alert)
    return alert


def resolve_alert(
    db: Session,
    alert_id: int,
    user: str,
    notes: str = None,
) -> Optional[Alert]:
    """Resolve an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.status = "resolved"
        alert.resolved_by = user
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = notes
        db.commit()
        db.refresh(alert)
    return alert


def get_alerts(
    db: Session,
    alert_type: str = None,
    severity: str = None,
    status: str = None,
    days: int = 30,
    limit: int = 100,
) -> List[Alert]:
    """Get alerts."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = db.query(Alert).filter(Alert.created_at >= cutoff)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(desc(Alert.created_at)).limit(limit).all()
