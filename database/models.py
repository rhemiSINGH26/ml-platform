"""
SQLAlchemy database models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ModelVersion(Base):
    """Track model versions and metadata."""
    
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    algorithm = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Metrics
    accuracy = Column(Float)
    f1_score = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    roc_auc = Column(Float)
    
    # Metadata
    training_samples = Column(Integer)
    feature_names = Column(JSON)
    hyperparameters = Column(JSON)
    
    # Status
    status = Column(String(20), default="training")  # training, staging, production, archived
    is_active = Column(Boolean, default=False)
    
    # File paths
    model_path = Column(String(500))
    metadata_path = Column(String(500))
    
    # Relationships
    predictions = relationship("Prediction", back_populates="model")
    drift_reports = relationship("DriftReport", back_populates="model")


class Prediction(Base):
    """Track individual predictions."""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("model_versions.id"))
    
    # Input features (stored as JSON)
    features = Column(JSON, nullable=False)
    
    # Prediction
    prediction = Column(Integer, nullable=False)
    probability = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    latency_ms = Column(Float)
    
    # Optional ground truth (for monitoring)
    actual = Column(Integer, nullable=True)
    
    # Relationship
    model = relationship("ModelVersion", back_populates="predictions")


class DriftReport(Base):
    """Track drift detection reports."""
    
    __tablename__ = "drift_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("model_versions.id"))
    
    # Drift metrics
    drift_detected = Column(Boolean, nullable=False)
    drift_score = Column(Float)
    drifted_features = Column(JSON)
    n_drifted_features = Column(Integer)
    
    # Report metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    report_path = Column(String(500))
    
    # Sample sizes
    reference_size = Column(Integer)
    current_size = Column(Integer)
    
    # Relationship
    model = relationship("ModelVersion", back_populates="drift_reports")


class AgentAction(Base):
    """Track autonomous agent actions."""
    
    __tablename__ = "agent_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(String(50), unique=True, index=True)
    
    # Action details
    action_type = Column(String(50), nullable=False)
    description = Column(Text)
    risk_level = Column(String(20))
    
    # Related issue
    issue_id = Column(String(50), nullable=True)
    issue_type = Column(String(50), nullable=True)
    issue_severity = Column(String(20), nullable=True)
    
    # Execution
    status = Column(String(20), default="pending")  # pending, approved, rejected, executed, failed
    requires_approval = Column(Boolean, default=False)
    
    # Approval info
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_comment = Column(Text, nullable=True)
    
    # Execution info
    executed_at = Column(DateTime, nullable=True)
    execution_result = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Parameters
    parameters = Column(JSON)


class PerformanceMetric(Base):
    """Track performance metrics over time."""
    
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("model_versions.id"), nullable=True)
    
    # Metrics
    metric_name = Column(String(50), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    
    # Metadata (renamed to avoid SQLAlchemy conflict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    metric_metadata = Column(JSON)


class Alert(Base):
    """Track system alerts."""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    
    # Acknowledgment
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Resolution
    resolved_by = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Related data
    related_data = Column(JSON)
