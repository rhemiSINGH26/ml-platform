# Database Layer Documentation

## Overview

The database layer provides persistent storage for the MLOps platform using **SQLAlchemy ORM** with **PostgreSQL** in production and **SQLite** for development. It tracks model versions, predictions, drift reports, agent actions, performance metrics, and alerts.

## Architecture

```
database/
├── models.py          # SQLAlchemy models (7 tables)
├── connection.py      # Database connection & session management
├── crud.py           # CRUD operations for all models
├── migrations.py     # Alembic migration utilities
└── __init__.py       # Package exports

alembic/
├── env.py            # Alembic environment configuration
├── script.py.mako    # Migration template
└── versions/         # Migration files (auto-generated)
```

## Database Models

### 1. ModelVersion
Tracks ML model versions and metadata.

**Fields:**
- `id`, `model_name`, `version`, `algorithm`
- Metrics: `accuracy`, `f1_score`, `precision`, `recall`, `roc_auc`
- `hyperparameters` (JSON), `feature_names` (JSON)
- `status` (training/staging/production/archived)
- `is_active` (boolean - only one active model)
- `model_path`, `metadata_path`

**Relationships:**
- One-to-many with `Prediction`
- One-to-many with `DriftReport`

### 2. Prediction
Tracks individual predictions for monitoring.

**Fields:**
- `model_id` (FK to ModelVersion)
- `features` (JSON - input features)
- `prediction` (integer), `probability` (float)
- `latency_ms`, `created_at`
- `actual` (optional ground truth for validation)

### 3. DriftReport
Stores drift detection results.

**Fields:**
- `model_id` (FK to ModelVersion)
- `drift_detected` (boolean), `drift_score`
- `drifted_features` (JSON list), `n_drifted_features`
- `report_path`, `created_at`
- `reference_size`, `current_size`

### 4. AgentAction
Tracks autonomous agent actions and approvals.

**Fields:**
- `action_id` (unique), `action_type`, `description`
- `risk_level`, `requires_approval`
- `issue_id`, `issue_type`, `issue_severity`
- `status` (pending/approved/rejected/executed/failed)
- `reviewed_by`, `reviewed_at`, `review_comment`
- `executed_at`, `execution_result` (JSON)
- `parameters` (JSON)

### 5. PerformanceMetric
Time-series metrics for monitoring.

**Fields:**
- `metric_name`, `metric_value`
- `model_id` (optional FK)
- `created_at`, `metadata` (JSON)

### 6. Alert
System alerts for issues.

**Fields:**
- `alert_type`, `severity`, `title`, `message`
- `status` (active/acknowledged/resolved)
- `acknowledged_by`, `acknowledged_at`
- `resolved_by`, `resolved_at`, `resolution_notes`
- `created_at`, `related_data` (JSON)

## CRUD Operations

All CRUD operations are in `database/crud.py`:

### ModelVersion Operations
```python
from database import crud

# Create model version
model = crud.create_model_version(
    db=session,
    model_name="heart_disease_rf",
    version="1.0.0",
    algorithm="RandomForest",
    metrics={"accuracy": 0.85, "f1": 0.83},
    hyperparameters={"n_estimators": 100},
    feature_names=["age", "sex", ...],
    model_path="/path/to/model.pkl",
    metadata_path="/path/to/metadata.yaml",
    training_samples=1000,
)

# Get active model
active_model = crud.get_active_model(db=session)

# Set model as active (promotes to production)
crud.set_model_active(db=session, model_id=5)

# Get model versions
versions = crud.get_model_versions(db=session, model_name="heart_disease_rf", limit=10)
```

### Prediction Operations
```python
# Create prediction
pred = crud.create_prediction(
    db=session,
    model_id=1,
    features={"age": 55, "sex": 1, ...},
    prediction=1,
    probability=0.87,
    latency_ms=12.5,
)

# Get recent predictions
recent = crud.get_recent_predictions(db=session, model_id=1, hours=24)

# Update with ground truth
crud.update_prediction_actual(db=session, prediction_id=123, actual=1)
```

### Drift Report Operations
```python
# Create drift report
report = crud.create_drift_report(
    db=session,
    model_id=1,
    drift_detected=True,
    drift_score=0.65,
    drifted_features=["age", "chol"],
    report_path="/reports/drift_20240101.html",
    reference_size=1000,
    current_size=500,
)

# Get latest drift report
latest = crud.get_latest_drift_report(db=session, model_id=1)

# Get drift history
history = crud.get_drift_reports(db=session, days=30)
```

### Agent Action Operations
```python
# Create action
action = crud.create_agent_action(
    db=session,
    action_id="act_123",
    action_type="retrain_model",
    description="Retrain due to drift",
    risk_level="medium",
    requires_approval=True,
    issue_id="issue_456",
)

# Get pending approvals
pending = crud.get_pending_actions(db=session)

# Approve action
crud.approve_action(db=session, action_id="act_123", reviewer="admin", comment="Approved")

# Reject action
crud.reject_action(db=session, action_id="act_123", reviewer="admin", comment="Not needed")

# Mark as executed
crud.mark_action_executed(db=session, action_id="act_123", result={"status": "success"})
```

### Performance Metric Operations
```python
# Create metric
metric = crud.create_performance_metric(
    db=session,
    metric_name="api_latency",
    metric_value=25.3,
    model_id=1,
    metadata={"endpoint": "/predict"},
)

# Get time series
timeseries = crud.get_metrics_timeseries(
    db=session,
    metric_name="api_latency",
    days=7,
)
```

### Alert Operations
```python
# Create alert
alert = crud.create_alert(
    db=session,
    alert_type="performance_degradation",
    severity="high",
    title="Model F1 Score Dropped",
    message="F1 score dropped from 0.85 to 0.72",
    related_data={"model_id": 1},
)

# Get active alerts
active = crud.get_active_alerts(db=session)

# Acknowledge alert
crud.acknowledge_alert(db=session, alert_id=1, user="admin")

# Resolve alert
crud.resolve_alert(db=session, alert_id=1, user="admin", notes="Retrained model")
```

## Database Connection

### Using Context Manager (Recommended)
```python
from database import get_database

db = get_database()
with db.get_session() as session:
    # Session auto-commits on success, rolls back on error
    model = crud.get_active_model(db=session)
```

### Using FastAPI Dependency
```python
from fastapi import Depends
from database import get_db_session

@app.get("/models")
def get_models(db: Session = Depends(get_db_session)):
    return crud.get_model_versions(db, limit=10)
```

## Database Migrations (Alembic)

### Initialize Alembic (Already Done)
```bash
# Configuration is already set up in alembic.ini and alembic/env.py
```

### Create Migration
```bash
# After modifying models.py
python -m database.migrations create "add new column to predictions"
```

### Apply Migrations
```bash
# Upgrade to latest
python -m database.migrations upgrade

# Upgrade to specific revision
python -m database.migrations upgrade abc123

# Downgrade one revision
python -m database.migrations downgrade

# Downgrade to specific revision
python -m database.migrations downgrade abc123
```

### Check Status
```bash
# Show current revision
python -m database.migrations current

# Show migration history
python -m database.migrations history
```

## Setup Instructions

### 1. Configure Database URL

**Development (SQLite):**
```bash
# .env
DATABASE_URL=sqlite:///./mlops.db
```

**Production (PostgreSQL):**
```bash
# .env
DATABASE_URL=postgresql://mlops:mlops@postgres:5432/mlops
```

### 2. Initialize Database
```bash
# Create tables
python scripts/init_database.py

# Or use Python
python -c "from database import init_database; init_database()"
```

### 3. Run Migrations (Optional)
```bash
# Create initial migration
python -m database.migrations create "initial schema"

# Apply migration
python -m database.migrations upgrade
```

## Docker Integration

The `docker-compose.yml` includes a PostgreSQL service:

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: mlops
      POSTGRES_PASSWORD: mlops
      POSTGRES_DB: mlops
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

**Start PostgreSQL:**
```bash
docker-compose up -d postgres
```

**Initialize database in container:**
```bash
docker-compose exec api python scripts/init_database.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `postgresql://mlops:mlops@localhost:5432/mlops` |
| `database_echo` | Log all SQL queries | `False` |
| `database_pool_size` | Connection pool size | `5` |

## Best Practices

### 1. Always Use Sessions Properly
```python
# ✓ Good - auto-cleanup
with db.get_session() as session:
    result = crud.get_model_version(session, 1)

# ✗ Bad - manual cleanup required
session = db.SessionLocal()
result = crud.get_model_version(session, 1)
session.close()  # Easy to forget!
```

### 2. Handle Transactions
```python
from database import get_database

db = get_database()
with db.get_session() as session:
    try:
        # Multiple operations in transaction
        model = crud.create_model_version(session, ...)
        crud.set_model_active(session, model.id)
        # Auto-commits here
    except Exception as e:
        # Auto-rollback on error
        logger.error(f"Transaction failed: {e}")
        raise
```

### 3. Use Indexes for Queries
All frequently queried columns have indexes:
- `model_name`, `created_at`, `status`
- `action_id`, `metric_name`
- Foreign keys

### 4. Clean Up Old Data
```python
from datetime import datetime, timedelta

# Delete old predictions (> 90 days)
cutoff = datetime.utcnow() - timedelta(days=90)
session.query(Prediction).filter(Prediction.created_at < cutoff).delete()
session.commit()
```

## Testing

```python
import pytest
from database import get_database, crud

@pytest.fixture
def db_session():
    """Create test database session."""
    db = get_database("sqlite:///:memory:")  # In-memory DB
    db.create_tables()
    with db.get_session() as session:
        yield session
    db.drop_tables()

def test_create_model_version(db_session):
    model = crud.create_model_version(
        db=db_session,
        model_name="test_model",
        version="1.0.0",
        algorithm="RandomForest",
        metrics={"f1": 0.85},
        hyperparameters={},
        feature_names=[],
        model_path="/test",
        metadata_path="/test",
        training_samples=100,
    )
    assert model.id is not None
    assert model.model_name == "test_model"
```

## Troubleshooting

### Connection Issues
```bash
# Test database connection
psql -h localhost -U mlops -d mlops

# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres
```

### Migration Issues
```bash
# Reset migrations (development only!)
rm -rf alembic/versions/*.py
python -m database.migrations create "initial schema"
python -m database.migrations upgrade
```

### Performance Issues
```python
# Enable SQL logging
from config import settings
settings.database_echo = True

# Check query performance
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    print(f"SQL: {statement}")
```

## Integration Examples

### With Training Pipeline
```python
from database import get_database, crud

# After training
db = get_database()
with db.get_session() as session:
    model = crud.create_model_version(
        db=session,
        model_name=best_model.name,
        version=run_id,
        algorithm=best_model.algorithm,
        metrics=best_model.metrics,
        hyperparameters=best_model.params,
        feature_names=feature_names,
        model_path=model_path,
        metadata_path=metadata_path,
        training_samples=len(X_train),
    )
    crud.set_model_active(session, model.id)
```

### With API
```python
from fastapi import FastAPI, Depends
from database import get_db_session, crud

app = FastAPI()

@app.post("/predict")
def predict(data: dict, db: Session = Depends(get_db_session)):
    # Make prediction
    pred = model.predict(data)
    
    # Store prediction
    crud.create_prediction(
        db=db,
        model_id=current_model.id,
        features=data,
        prediction=int(pred),
        probability=float(proba),
        latency_ms=latency,
    )
    return {"prediction": pred}
```

### With Agent
```python
from database import get_database, crud

# Create action for approval
db = get_database()
with db.get_session() as session:
    action = crud.create_agent_action(
        db=session,
        action_id=action.id,
        action_type=action.type,
        description=action.description,
        risk_level=action.risk,
        requires_approval=True,
    )
```

## Next Steps

1. ✅ Database layer complete
2. 🔄 Integrate with API service
3. 🔄 Integrate with training pipeline
4. 🔄 Integrate with autonomous agent
5. 🔄 Add reporting queries
6. 🔄 Create admin UI for database management
