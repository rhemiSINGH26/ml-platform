# 🛠️ Technology Stack - Detailed Explanation

## Overview

This MLOps platform uses a carefully selected technology stack optimized for production ML deployments with autonomous remediation capabilities.

---

## 📊 Technology Stack by Layer

### **1. Data Layer**

#### **DVC (Data Version Control)** 
**Purpose**: Version control for datasets and models

**Why DVC?**
- ✅ Git-like semantics for large files
- ✅ Integrates seamlessly with MLflow
- ✅ Supports multiple storage backends (S3, GCS, Azure)
- ✅ Lightweight metadata in Git, actual data remote
- ✅ Reproducibility: Pin exact dataset versions
- ✅ Easy rollback to previous data versions

**Alternatives Considered**:
- ❌ Git LFS: Not designed for ML workflows, slower
- ❌ Pachyderm: Too heavyweight for this project
- ❌ Delta Lake: Requires Spark, overkill

**Usage**:
```bash
dvc add data/raw/heart_disease.csv
dvc push
git add data/raw/heart_disease.csv.dvc
git commit -m "Update dataset"
```

---

#### **Great Expectations**
**Purpose**: Data validation and quality assurance

**Why Great Expectations?**
- ✅ Industry-standard data testing framework
- ✅ Human-readable expectation suites
- ✅ Automatic HTML documentation of expectations
- ✅ Integration with Pandas, Spark, SQL
- ✅ Catches data issues before training
- ✅ Version-controlled expectations (JSON files)

**Alternatives Considered**:
- ❌ Custom validation: Reinventing the wheel
- ❌ Pandera: Less mature, smaller community
- ❌ TFDV (TensorFlow Data Validation): TensorFlow-specific

**Example Expectations**:
- Column names match schema
- No null values in critical fields
- Age between 0-120
- Categorical values in allowed set
- Statistical properties (mean, std within bounds)

**Usage**:
```python
from great_expectations.core.batch import RuntimeBatchRequest
validator = context.get_validator(batch_request=batch_request, expectation_suite_name="heart_disease_suite")
results = validator.validate()
```

---

### **2. ML Training & Experimentation**

#### **Scikit-learn**
**Purpose**: Core ML models (Logistic Regression, Random Forest)

**Why Scikit-learn?**
- ✅ Industry standard, battle-tested
- ✅ Clean, consistent API
- ✅ Excellent documentation
- ✅ Fast for small-to-medium datasets
- ✅ Easy to serialize (pickle/joblib)

---

#### **XGBoost / LightGBM**
**Purpose**: Gradient boosting models (often best for tabular data)

**Why Both?**
- ✅ XGBoost: Proven winner in Kaggle competitions
- ✅ LightGBM: Faster training, lower memory
- ✅ Both support GPU acceleration
- ✅ Handle missing values naturally
- ✅ Feature importance built-in

**When to Use**:
- XGBoost: Smaller datasets, need interpretability
- LightGBM: Larger datasets, speed priority

---

#### **MLflow**
**Purpose**: Experiment tracking, model registry, deployment

**Why MLflow?**
- ✅ Open-source, vendor-neutral
- ✅ Tracks parameters, metrics, artifacts
- ✅ Model registry with staging/production stages
- ✅ Supports model versioning and lineage
- ✅ REST API for programmatic access
- ✅ UI for visualization and comparison
- ✅ Integrates with deployment tools

**Alternatives Considered**:
- ❌ Weights & Biases: Commercial, vendor lock-in
- ❌ Neptune.ai: Commercial
- ❌ Comet.ml: Commercial
- ✅ Hugging Face Hub: Great for transformers, but MLflow more general

**Key Features Used**:
1. **Tracking**: Log parameters, metrics, models
2. **Registry**: Promote best model to "Production"
3. **Model Serving**: Load models by name/version
4. **Artifact Storage**: Store confusion matrices, plots

**Usage**:
```python
import mlflow
with mlflow.start_run():
    mlflow.log_param("max_depth", 10)
    mlflow.log_metric("f1_score", 0.87)
    mlflow.sklearn.log_model(model, "model")
```

---

### **3. Inference & API**

#### **FastAPI**
**Purpose**: REST API for model inference

**Why FastAPI?**
- ✅ Modern, async Python framework
- ✅ Automatic OpenAPI/Swagger docs
- ✅ Pydantic validation (type safety)
- ✅ High performance (comparable to Node.js)
- ✅ Native async/await support
- ✅ Easy dependency injection
- ✅ Built-in request validation

**Alternatives Considered**:
- ❌ Flask: Synchronous, older, less type-safe
- ❌ Django: Too heavyweight for API-only
- ❌ Tornado: Lower-level, more complex

**Endpoints**:
- `POST /predict`: Model inference
- `GET /health`: Health check for load balancers
- `GET /metrics`: Prometheus metrics
- `GET /model/info`: Current model metadata

**Example**:
```python
from fastapi import FastAPI
from pydantic import BaseModel

class PredictionRequest(BaseModel):
    age: int
    cholesterol: float
    # ... other features

@app.post("/predict")
async def predict(request: PredictionRequest):
    prediction = model.predict([request.dict()])
    return {"prediction": int(prediction[0])}
```

---

### **4. User Interface**

#### **Streamlit**
**Purpose**: Interactive dashboard for monitoring and approvals

**Why Streamlit?**
- ✅ Fastest way to build ML dashboards
- ✅ Pure Python (no HTML/CSS/JS required)
- ✅ Reactive programming model
- ✅ Built-in widgets (sliders, buttons, charts)
- ✅ Multi-page apps supported
- ✅ Integrates with Plotly, Matplotlib, Altair
- ✅ Session state for user interactions

**Alternatives Considered**:
- ❌ Dash (Plotly): More complex, React-based
- ❌ Gradio: Focused on demos, less customizable
- ❌ Panel: More flexible but steeper learning curve
- ❌ Custom React app: Too much overhead

**Dashboard Pages**:
1. **Model Performance**: Metrics, confusion matrix, ROC curve
2. **Drift Analysis**: Evidently reports visualization
3. **Approvals**: Human-in-the-loop approval interface
4. **Historical Trends**: Time-series metrics
5. **Agent Activity**: Audit log of agent actions

**Example**:
```python
import streamlit as st

st.title("Model Performance Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("Accuracy", "0.87", "+2%")
col2.metric("F1 Score", "0.85", "+1%")
col3.metric("AUC-ROC", "0.91", "+3%")
```

---

### **5. Monitoring & Observability**

#### **Evidently**
**Purpose**: ML-specific monitoring (data drift, model drift, data quality)

**Why Evidently?**
- ✅ Purpose-built for ML monitoring
- ✅ Pre-built dashboards and reports
- ✅ Statistical tests for drift detection
- ✅ Supports classification, regression, ranking
- ✅ HTML reports exportable to PDF
- ✅ JSON output for programmatic access
- ✅ Open-source with commercial support

**Alternatives Considered**:
- ❌ WhyLabs: Commercial, closed-source
- ❌ Arize AI: Commercial
- ❌ Custom drift detection: Time-consuming, error-prone

**Drift Metrics Tracked**:
1. **Data Drift**: Feature distribution changes (PSI, Wasserstein distance)
2. **Prediction Drift**: Output distribution shift
3. **Target Drift**: Actual label distribution (when available)
4. **Data Quality**: Missing values, new categories, out-of-range

**Usage**:
```python
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

report = Report(metrics=[DataDriftPreset()])
report.run(reference_data=reference_df, current_data=current_df)
report.save_html("drift_report.html")
```

---

#### **Prometheus**
**Purpose**: Metrics collection and alerting

**Why Prometheus?**
- ✅ Industry-standard monitoring system
- ✅ Time-series database optimized for metrics
- ✅ Powerful query language (PromQL)
- ✅ Pull-based model (scrapes endpoints)
- ✅ Alerting rules engine
- ✅ Integrates with Grafana for visualization
- ✅ Native Kubernetes support

**Alternatives Considered**:
- ❌ DataDog: Commercial, expensive
- ❌ New Relic: Commercial
- ❌ CloudWatch: AWS-specific

**Metrics Collected**:
- **Request metrics**: Rate, latency, errors (RED method)
- **Model metrics**: Inference time, prediction distribution
- **System metrics**: CPU, memory, disk
- **Business metrics**: Predictions per class, drift scores

**Example Metrics**:
```python
from prometheus_client import Counter, Histogram

prediction_counter = Counter('predictions_total', 'Total predictions', ['model_version', 'prediction_class'])
inference_duration = Histogram('inference_duration_seconds', 'Inference time')

with inference_duration.time():
    prediction = model.predict(X)
prediction_counter.labels(model_version='v1.2', prediction_class=str(prediction[0])).inc()
```

---

### **6. Containerization & Orchestration**

#### **Docker**
**Purpose**: Application containerization

**Why Docker?**
- ✅ Industry standard for containerization
- ✅ Reproducible environments
- ✅ Isolated dependencies
- ✅ Easy deployment to cloud platforms
- ✅ Efficient layer caching
- ✅ Multi-stage builds for smaller images

**Containers**:
1. **API**: FastAPI + model
2. **UI**: Streamlit dashboard
3. **Agent**: Autonomous remediation service
4. **MLflow**: Tracking server
5. **Prometheus**: Metrics collector

---

#### **Docker Compose**
**Purpose**: Local multi-container orchestration

**Why Docker Compose?**
- ✅ Simple YAML configuration
- ✅ Easy local development
- ✅ Network isolation between services
- ✅ Volume management
- ✅ Environment variable injection
- ✅ One-command startup (`docker-compose up`)

**Future**: Migrate to Kubernetes for production scale

---

### **7. CI/CD & Deployment**

#### **GitHub Actions**
**Purpose**: Automated testing, building, and deployment

**Why GitHub Actions?**
- ✅ Native GitHub integration
- ✅ Free for public repos (generous limits for private)
- ✅ Matrix builds (test multiple Python versions)
- ✅ Secrets management
- ✅ Marketplace with thousands of actions
- ✅ Workflow triggers (push, PR, schedule, manual)

**Workflows**:
1. **CI**: Run tests, lint, type-check on every push
2. **Deploy**: Build Docker images, push to registry, deploy to Render
3. **Retrain**: Scheduled weekly retraining (cron)

**Alternatives Considered**:
- ❌ Jenkins: Self-hosted, more maintenance
- ❌ CircleCI: Commercial
- ❌ GitLab CI: Would require GitLab migration

---

#### **Render**
**Purpose**: Cloud deployment platform

**Why Render?**
- ✅ Simple, modern alternative to Heroku
- ✅ Native Docker support
- ✅ Auto-scaling
- ✅ Free tier for experimentation
- ✅ Easy environment variable management
- ✅ Automatic HTTPS
- ✅ Health check monitoring
- ✅ GitHub integration (auto-deploy on push)

**Alternatives Considered**:
- ❌ AWS ECS/Fargate: More complex, higher cost
- ❌ Google Cloud Run: GCP-specific
- ❌ Heroku: Removed free tier, more expensive
- ❌ Railway: Less mature

**Services Deployed**:
- FastAPI (web service)
- Streamlit (web service)
- Agent (background worker)
- MLflow (web service)
- PostgreSQL (managed database)

---

### **8. Reporting & Notifications**

#### **Jinja2**
**Purpose**: HTML template engine for reports

**Why Jinja2?**
- ✅ Python's most popular template engine
- ✅ Clean syntax (similar to Django templates)
- ✅ Powerful filters and control structures
- ✅ Template inheritance
- ✅ Auto-escaping for security

---

#### **WeasyPrint**
**Purpose**: HTML to PDF conversion

**Why WeasyPrint?**
- ✅ Pure Python (easy to install)
- ✅ Supports modern CSS (Flexbox, Grid)
- ✅ No external dependencies (unlike wkhtmltopdf)
- ✅ Accurate rendering

**Alternatives Considered**:
- ❌ ReportLab: Low-level, more code required
- ❌ wkhtmltopdf: External binary, harder to deploy
- ❌ Playwright PDF: Requires browser, heavy

---

#### **SMTP (Email)**
**Purpose**: Email notifications

**Why SMTP?**
- ✅ Universal email protocol
- ✅ Works with any provider (Gmail, SendGrid, Mailgun)
- ✅ Python's built-in `smtplib`

**Providers**:
- Development: Mailtrap (email testing)
- Production: SendGrid (99% deliverability, generous free tier)

---

#### **Slack Webhooks**
**Purpose**: Real-time team notifications

**Why Slack?**
- ✅ Most popular team communication tool
- ✅ Simple webhook API
- ✅ Rich message formatting (blocks, attachments)
- ✅ No auth required for incoming webhooks

---

### **9. Database & Storage**

#### **SQLite → PostgreSQL**
**Purpose**: Audit logs, metadata, approval queue

**Why SQLite for Development?**
- ✅ Zero configuration
- ✅ File-based (easy backups)
- ✅ Perfect for development/testing

**Why PostgreSQL for Production?**
- ✅ Production-grade reliability
- ✅ ACID compliance
- ✅ Better concurrency
- ✅ Managed services available (Render, AWS RDS)
- ✅ JSON/JSONB support (store complex data)

---

#### **SQLAlchemy**
**Purpose**: ORM for database interactions

**Why SQLAlchemy?**
- ✅ Most mature Python ORM
- ✅ Database-agnostic (same code for SQLite/Postgres)
- ✅ Type hints support
- ✅ Migration support (Alembic)
- ✅ Connection pooling

---

### **10. Autonomous Agent**

#### **Custom Python Logic**
**Purpose**: Decision engine for autonomous remediation

**Why Custom?**
- ✅ Full control over decision logic
- ✅ Transparent, auditable
- ✅ No vendor lock-in
- ✅ Easy to customize rules

**Components**:
1. **Listener**: FastAPI webhook endpoint
2. **Diagnosis**: Parse alerts, extract context
3. **Decision Engine**: Rule-based decision tree
4. **Executor**: Trigger actions (retrain, rollback, etc.)
5. **Approval Manager**: Queue risky actions for human review

**Decision Tree Example**:
```
Alert: Data drift detected (score=0.8)
├─ If drift_score > 0.9 → Request approval for retrain
├─ If drift_score > 0.7 → Log warning, monitor
└─ If drift_score > 0.5 → Auto-retrain (safe threshold)
```

---

## 📦 Complete Dependency List

### **Core ML & Data**
```
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
xgboost>=2.0.0
lightgbm>=4.0.0
imbalanced-learn>=0.11.0  # For handling class imbalance
```

### **MLOps Tools**
```
mlflow>=2.8.0
dvc>=3.0.0
dvc-s3>=3.0.0  # For S3 remote storage
great-expectations>=0.18.0
evidently>=0.4.0
```

### **API & Web**
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
streamlit>=1.28.0
pydantic>=2.4.0
pydantic-settings>=2.0.0
python-multipart>=0.0.6  # For file uploads
```

### **Monitoring**
```
prometheus-client>=0.18.0
prometheus-fastapi-instrumentator>=6.1.0
```

### **Database**
```
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0  # PostgreSQL adapter
```

### **Reporting & Notifications**
```
jinja2>=3.1.2
weasyprint>=60.0
matplotlib>=3.8.0
seaborn>=0.13.0
plotly>=5.17.0
python-dotenv>=1.0.0
requests>=2.31.0  # For Slack webhooks
```

### **Testing & Quality**
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
black>=23.11.0
ruff>=0.1.0
mypy>=1.7.0
```

### **Utilities**
```
python-dateutil>=2.8.2
pyyaml>=6.0.1
click>=8.1.0  # For CLI tools
rich>=13.6.0  # For beautiful terminal output
loguru>=0.7.0  # Better logging
```

---

## 🎯 Technology Selection Principles

1. **Open Source First**: Avoid vendor lock-in
2. **Battle-Tested**: Prefer mature, widely-used tools
3. **Python-Native**: Minimize language switching
4. **Cloud-Agnostic**: Can deploy anywhere
5. **Community Support**: Large communities, good docs
6. **Scalability Path**: Can grow from MVP to enterprise
7. **Developer Experience**: Fast iteration, good debugging

---

## 🔄 Technology Upgrade Path

### **Current (MVP)**
- SQLite → **PostgreSQL**
- Local storage → **S3/GCS**
- Docker Compose → **Kubernetes**
- Manual alerts → **PagerDuty**
- Basic agent → **LangChain-powered agent**

### **Future Enhancements**
- Add **Ray** for distributed training
- Add **Feast** for feature store
- Add **Airflow** for complex orchestration
- Add **Grafana** for visualization
- Add **OpenTelemetry** for distributed tracing

---

This technology stack provides a solid foundation for a production-grade MLOps platform while remaining accessible and maintainable.
