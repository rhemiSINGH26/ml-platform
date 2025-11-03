# MLOps Platform - Complete Folder Structure

```
mlops/
│
├── .github/                              # CI/CD workflows
│   └── workflows/
│       ├── ci.yml                        # Test, lint, build
│       ├── deploy.yml                    # Deploy to Render
│       └── retrain.yml                   # Scheduled retraining
│
├── data/                                 # Data storage (DVC tracked)
│   ├── raw/                              # Original datasets
│   │   └── heart_disease.csv
│   ├── processed/                        # Cleaned & feature-engineered
│   │   ├── train.csv
│   │   ├── val.csv
│   │   └── test.csv
│   ├── reference/                        # Reference data for drift detection
│   │   └── reference.csv
│   └── .gitignore                        # Ignore actual data files
│
├── models/                               # Trained model artifacts (DVC tracked)
│   ├── production/                       # Current production model
│   │   ├── model.pkl
│   │   ├── metadata.json
│   │   └── feature_names.json
│   ├── staging/                          # Candidate models
│   └── archive/                          # Historical models
│
├── training/                             # ML training pipeline
│   ├── __init__.py
│   ├── dataset_selector.py               # Auto-select best dataset
│   ├── data_loader.py                    # Load & split data
│   ├── feature_engineering.py            # Feature transformations
│   ├── model_factory.py                  # Create model instances
│   ├── train_pipeline.py                 # Main training orchestrator
│   ├── model_evaluator.py                # Metrics & comparison
│   ├── model_selector.py                 # Select best model logic
│   └── utils.py                          # Helper functions
│
├── validation/                           # Data validation
│   ├── __init__.py
│   ├── great_expectations/               # GX configs
│   │   ├── great_expectations.yml
│   │   ├── expectations/                 # Expectation suites
│   │   │   ├── heart_disease_suite.json
│   │   │   └── prediction_suite.json
│   │   ├── checkpoints/                  # Validation checkpoints
│   │   │   └── training_checkpoint.yml
│   │   └── uncommitted/                  # Local GX data (ignored)
│   ├── data_validator.py                 # Main validation script
│   └── schema_definitions.py             # Expected schemas
│
├── monitoring/                           # Drift & performance monitoring
│   ├── __init__.py
│   ├── drift_detector.py                 # Evidently drift checks
│   ├── performance_monitor.py            # Model quality tracking
│   ├── data_quality_monitor.py           # Input data monitoring
│   ├── alert_rules.py                    # Alert threshold definitions
│   └── prometheus_metrics.py             # Custom Prometheus metrics
│
├── services/                             # Microservices
│   │
│   ├── api/                              # FastAPI inference service
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py                 # Health check endpoints
│   │   │   ├── predict.py                # Prediction endpoint
│   │   │   ├── metrics.py                # Prometheus metrics endpoint
│   │   │   └── model_info.py             # Model metadata endpoint
│   │   ├── models/                       # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── request.py                # Request schemas
│   │   │   └── response.py               # Response schemas
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py                # Request logging
│   │   │   ├── auth.py                   # API key validation
│   │   │   └── monitoring.py             # Request metrics
│   │   ├── dependencies/
│   │   │   ├── __init__.py
│   │   │   └── model_loader.py           # Load ML model
│   │   └── config.py                     # API configuration
│   │
│   ├── ui/                               # Streamlit dashboard
│   │   ├── __init__.py
│   │   ├── app.py                        # Main Streamlit app
│   │   ├── pages/
│   │   │   ├── 1_📊_Model_Performance.py
│   │   │   ├── 2_🔍_Drift_Analysis.py
│   │   │   ├── 3_⚙️_Approvals.py
│   │   │   ├── 4_📈_Historical_Trends.py
│   │   │   └── 5_🤖_Agent_Activity.py
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── metrics_cards.py
│   │   │   ├── drift_charts.py
│   │   │   ├── approval_buttons.py
│   │   │   └── model_comparison.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── data_fetcher.py           # Fetch from MLflow/DB
│   │   │   └── formatters.py             # Display formatting
│   │   └── config.py                     # UI configuration
│   │
│   ├── agent/                            # Autonomous remediation agent
│   │   ├── __init__.py
│   │   ├── agent_service.py              # Main agent FastAPI app
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── listener.py               # Webhook listener
│   │   │   ├── diagnosis.py              # Diagnose alerts
│   │   │   ├── decision.py               # Decision engine
│   │   │   ├── executor.py               # Execute actions
│   │   │   └── approval_manager.py       # Manage approval requests
│   │   ├── actions/
│   │   │   ├── __init__.py
│   │   │   ├── retrain.py                # Trigger retraining
│   │   │   ├── rollback.py               # Rollback to previous model
│   │   │   ├── scale.py                  # Scale services
│   │   │   ├── cache.py                  # Clear caches
│   │   │   └── alert.py                  # Send notifications
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── alert.py                  # Alert data models
│   │   │   ├── action.py                 # Action data models
│   │   │   └── approval.py               # Approval request models
│   │   └── config.py                     # Agent configuration
│   │
│   └── mlflow_server/                    # MLflow tracking server
│       ├── __init__.py
│       ├── run_server.py                 # MLflow server launcher
│       └── config.py                     # MLflow configuration
│
├── reporting/                            # Report generation
│   ├── __init__.py
│   ├── report_generator.py               # Main report orchestrator
│   ├── templates/                        # Jinja2 templates
│   │   ├── deployment_report.html
│   │   ├── drift_report.html
│   │   ├── incident_report.html
│   │   └── weekly_summary.html
│   ├── pdf_generator.py                  # HTML to PDF converter
│   └── email_sender.py                   # Email notifications
│
├── notifications/                        # Notification services
│   ├── __init__.py
│   ├── email_notifier.py                 # SMTP email sender
│   ├── slack_notifier.py                 # Slack webhook
│   └── notification_manager.py           # Unified notification interface
│
├── database/                             # Database schemas & migrations
│   ├── __init__.py
│   ├── models.py                         # SQLAlchemy models
│   ├── schemas.py                        # Pydantic schemas
│   ├── crud.py                           # CRUD operations
│   ├── connection.py                     # DB connection manager
│   └── migrations/                       # Alembic migrations
│       └── versions/
│
├── config/                               # Configuration files
│   ├── __init__.py
│   ├── settings.py                       # Global settings (Pydantic)
│   ├── logging_config.py                 # Logging configuration
│   ├── mlflow_config.py                  # MLflow settings
│   ├── prometheus_config.yml             # Prometheus config
│   ├── alertmanager_config.yml           # Alert manager config
│   └── model_config.yml                  # Model hyperparameters
│
├── tests/                                # Test suite
│   ├── __init__.py
│   ├── conftest.py                       # Pytest fixtures
│   ├── unit/
│   │   ├── test_training.py
│   │   ├── test_validation.py
│   │   ├── test_monitoring.py
│   │   ├── test_agent.py
│   │   └── test_api.py
│   ├── integration/
│   │   ├── test_training_pipeline.py
│   │   ├── test_deployment.py
│   │   └── test_agent_flow.py
│   └── e2e/
│       └── test_full_workflow.py
│
├── scripts/                              # Utility scripts
│   ├── setup_project.sh                  # Initial setup script
│   ├── download_data.py                  # Download dataset
│   ├── init_dvc.sh                       # Initialize DVC
│   ├── init_mlflow.sh                    # Initialize MLflow
│   ├── run_training.sh                   # Run training pipeline
│   ├── run_validation.sh                 # Run data validation
│   ├── deploy_local.sh                   # Local Docker deployment
│   ├── seed_database.py                  # Seed initial data
│   └── generate_report.py                # Manual report generation
│
├── docker/                               # Docker configurations
│   ├── Dockerfile.api                    # FastAPI service
│   ├── Dockerfile.ui                     # Streamlit UI
│   ├── Dockerfile.agent                  # Autonomous agent
│   ├── Dockerfile.mlflow                 # MLflow server
│   ├── Dockerfile.prometheus             # Prometheus
│   └── docker-compose.yml                # Multi-service orchestration
│
├── docs/                                 # Documentation
│   ├── ARCHITECTURE.md                   # System architecture (already created)
│   ├── SETUP.md                          # Setup instructions
│   ├── API.md                            # API documentation
│   ├── DEPLOYMENT.md                     # Deployment guide
│   ├── MONITORING.md                     # Monitoring guide
│   ├── AGENT.md                          # Agent behavior & config
│   ├── TROUBLESHOOTING.md                # Common issues
│   └── CONTRIBUTING.md                   # Contribution guidelines
│
├── .dvc/                                 # DVC configuration (auto-generated)
│   ├── config
│   └── .gitignore
│
├── .vscode/                              # VS Code settings (optional)
│   ├── settings.json
│   ├── launch.json
│   └── extensions.json
│
├── mlruns/                               # MLflow runs (local, ignored)
│   └── .gitignore
│
├── logs/                                 # Application logs (ignored)
│   ├── api.log
│   ├── agent.log
│   ├── training.log
│   └── .gitignore
│
├── audit/                                # Audit logs & reports
│   ├── actions.db                        # SQLite audit database
│   ├── reports/                          # Generated reports
│   │   └── .gitignore
│   └── .gitignore
│
├── .env.example                          # Example environment variables
├── .env                                  # Actual secrets (not committed)
├── .gitignore                            # Git ignore rules
├── .dockerignore                         # Docker ignore rules
├── .dvcignore                            # DVC ignore rules
│
├── requirements.txt                      # Core dependencies
├── requirements-dev.txt                  # Development dependencies
├── pyproject.toml                        # Project metadata & tools config
├── setup.py                              # Package installation
│
├── README.md                             # Main project documentation
├── LICENSE                               # License file
└── CHANGELOG.md                          # Version history

```

---

## 📂 Folder Structure Explanation

### **Root Level**
- **`.github/workflows/`**: CI/CD pipelines for automated testing, building, and deployment
- **`data/`**: All datasets (DVC-tracked, not stored in Git)
- **`models/`**: Trained model artifacts (DVC-tracked)

### **Training & Validation**
- **`training/`**: Complete ML training pipeline with modular components
- **`validation/`**: Great Expectations integration for data quality

### **Monitoring**
- **`monitoring/`**: Drift detection, performance tracking, and alerting logic

### **Services (Microservices)**
- **`services/api/`**: FastAPI REST API for model inference
- **`services/ui/`**: Streamlit dashboard with multiple pages
- **`services/agent/`**: Autonomous remediation agent (FastAPI app)
- **`services/mlflow_server/`**: MLflow tracking server

### **Supporting Components**
- **`reporting/`**: PDF and email report generation
- **`notifications/`**: Email and Slack notification handlers
- **`database/`**: SQLAlchemy models and audit log storage

### **Configuration**
- **`config/`**: Centralized configuration files (YAML + Python)

### **Testing**
- **`tests/`**: Comprehensive test suite (unit, integration, E2E)

### **Infrastructure**
- **`docker/`**: Dockerfiles and Docker Compose for containerization
- **`scripts/`**: Automation scripts for setup and deployment

### **Documentation**
- **`docs/`**: Detailed markdown documentation for all aspects

### **Generated/Ignored**
- **`mlruns/`**: MLflow experiment tracking (local only)
- **`logs/`**: Application logs (not committed)
- **`audit/`**: Audit database and generated reports

---

## 🎯 Key Design Decisions

1. **Modular Services**: Each service (API, UI, Agent, MLflow) is independent and containerized
2. **Clear Separation**: Training logic separated from inference and monitoring
3. **DVC for Data**: Large files (data, models) tracked with DVC, not Git
4. **Config-Driven**: All settings in `config/` for easy modification
5. **Multi-Page UI**: Streamlit pages for different concerns (metrics, drift, approvals)
6. **Testable**: Each component has corresponding test files
7. **Production-Ready**: Docker, CI/CD, monitoring, and logging built-in

---

## 📋 File Count Summary

| Category | Files | Description |
|----------|-------|-------------|
| Python modules | ~80 | Core application code |
| Config files | ~15 | YAML, JSON, environment |
| Docker files | ~6 | Containers & orchestration |
| CI/CD workflows | ~3 | GitHub Actions |
| Tests | ~10 | Unit, integration, E2E |
| Documentation | ~8 | Markdown guides |
| Scripts | ~10 | Automation & utilities |
| Templates | ~4 | Report templates |
| **Total** | **~136** | **Complete project** |

---

This structure follows industry best practices for MLOps projects and supports the full lifecycle from development to production deployment.
