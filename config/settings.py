"""
Global settings and configuration for the MLOps platform.
Uses Pydantic Settings for type-safe configuration from environment variables.
"""

from pathlib import Path
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Project paths
    project_name: str = "MLOps Platform"
    version: str = "1.0.0"
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    models_dir: Path = base_dir / "models"
    logs_dir: Path = base_dir / "logs"
    audit_dir: Path = base_dir / "audit"
    reports_dir: Path = audit_dir / "reports"
    production_model_dir: Path = models_dir / "production"
    staging_model_dir: Path = models_dir / "staging"
    
    # Dataset configuration
    dataset_name: str = Field(default="heart_disease", description="Dataset to use")
    dataset_url: str = Field(
        default="https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
        description="URL to download dataset"
    )
    test_size: float = Field(default=0.2, ge=0.1, le=0.5)
    val_size: float = Field(default=0.1, ge=0.05, le=0.3)
    random_seed: int = Field(default=42)
    
    # MLflow configuration
    mlflow_tracking_uri: str = Field(default="http://localhost:5000")
    mlflow_backend_store_uri: str = Field(default="sqlite:///mlflow.db")
    mlflow_artifact_root: str = Field(default="./mlruns")
    mlflow_experiment_name: str = Field(default="heart_disease_classification")
    mlflow_registry_uri: Optional[str] = None
    
    # DVC configuration
    dvc_remote_name: str = Field(default="myremote")
    dvc_remote_url: str = Field(default="./dvc-storage")
    
    # Model training configuration
    model_selection_metric: str = Field(default="f1")  # sklearn metric name
    model_min_threshold: float = Field(default=0.75)
    enable_cross_validation: bool = Field(default=True)
    cv_folds: int = Field(default=5)
    
    # API configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_key: str = Field(default="change-me-in-production")
    api_rate_limit: int = Field(default=100, description="Requests per minute")
    api_workers: int = Field(default=4)
    
    # Streamlit configuration
    streamlit_host: str = Field(default="0.0.0.0")
    streamlit_port: int = Field(default=8501)
    
    # Agent configuration
    agent_host: str = Field(default="0.0.0.0")
    agent_port: int = Field(default=8001)
    agent_enabled: bool = Field(default=True)
    agent_auto_execute_safe: bool = Field(default=True)
    agent_require_approval_threshold: float = Field(default=0.7)
    
    # Database configuration
    DATABASE_URL: str = Field(default="postgresql://mlops:mlops@localhost:5432/mlops")
    database_url: str = Field(default="postgresql://mlops:mlops@localhost:5432/mlops")  # Alias
    database_echo: bool = Field(default=False)
    database_pool_size: int = Field(default=5)
    
    # Monitoring configuration
    drift_detection_enabled: bool = Field(default=True)
    drift_threshold: float = Field(default=0.5)
    drift_critical_threshold: float = Field(default=0.7)
    drift_check_interval: int = Field(default=1000, description="Check every N predictions")
    performance_degradation_threshold: float = Field(default=0.1, description="10% degradation")
    
    # Prometheus configuration
    prometheus_enabled: bool = Field(default=True)
    prometheus_port: int = Field(default=9090)
    
    # Email configuration
    smtp_enabled: bool = Field(default=False)
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_use_tls: bool = Field(default=True)
    notification_email: str = Field(default="alerts@example.com")
    notification_from: str = Field(default="mlops@example.com")
    
    # Slack configuration
    slack_enabled: bool = Field(default=False)
    slack_webhook_url: str = Field(default="")
    slack_channel: str = Field(default="#mlops-alerts")
    
    # Reporting configuration
    reports_enabled: bool = Field(default=True)
    report_generation_on_deploy: bool = Field(default=True)
    report_generation_on_drift: bool = Field(default=True)
    weekly_summary_enabled: bool = Field(default=True)
    
    # Logging configuration
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")
    log_to_file: bool = Field(default=True)
    log_rotation: str = Field(default="1 day")
    log_retention: str = Field(default="30 days")
    
    # Security configuration
    enable_api_auth: bool = Field(default=True)
    webhook_secret: str = Field(default="change-me-in-production")
    cors_origins: List[str] = Field(default=["*"])
    
    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of allowed values."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @field_validator("model_selection_metric")
    @classmethod
    def validate_metric(cls, v: str) -> str:
        """Validate model selection metric."""
        allowed = ["accuracy", "f1", "roc_auc", "precision", "recall"]
        if v not in allowed:
            raise ValueError(f"Metric must be one of {allowed}")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"
    
    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.data_dir / "raw",
            self.data_dir / "processed",
            self.data_dir / "reference",
            self.models_dir / "production",
            self.models_dir / "staging",
            self.models_dir / "archive",
            self.logs_dir,
            self.audit_dir / "reports",
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Create directories on import
settings.create_directories()
