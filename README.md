# 🚀 MLOps Platform with Autonomous Remediation

> **Production-grade MLOps system with automated model training, deployment, monitoring, and intelligent self-healing capabilities.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MLflow](https://img.shields.io/badge/MLflow-2.8+-orange.svg)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-24+-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Detailed Setup](#-detailed-setup)
- [Usage Guide](#-usage-guide)
- [Deployment](#-deployment)
- [Monitoring & Alerts](#-monitoring--alerts)
- [Autonomous Agent](#-autonomous-agent)
- [Project Structure](#-project-structure)
- [Technologies](#-technologies)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

This MLOps platform provides a complete end-to-end solution for:

1. **Automated ML Pipeline**: Train multiple models, track experiments, select best performer
2. **Data Quality**: Validate datasets with Great Expectations before training
3. **Version Control**: DVC for data/model versioning, MLflow for experiment tracking
4. **Production Deployment**: Dockerized FastAPI service deployed to Render
5. **Real-time Monitoring**: Track drift, performance, and system health with Evidently & Prometheus
6. **Autonomous Remediation**: AI agent that diagnoses issues and takes corrective actions
7. **Human Oversight**: Approval workflow for risky actions via Streamlit dashboard
8. **Comprehensive Reporting**: Automated PDF reports and email notifications

### 🎯 System Goals

✅ **Fully Automated**: Minimal manual intervention required  
✅ **Self-Healing**: Autonomous agent handles common issues  
✅ **Observable**: Complete visibility into model and system performance  
✅ **Governed**: Audit logs and human approvals for safety  
✅ **Production-Ready**: Dockerized, tested, with CI/CD  

---

## ✨ Features

### **ML Training & Model Management**
- 🤖 Trains multiple models (Logistic Regression, Random Forest, XGBoost, LightGBM)
- 📊 Automatic model comparison and best-model selection
- 🏷️ MLflow experiment tracking and model registry
- 🔄 DVC for dataset and model versioning
- 🎯 Automated hyperparameter logging

### **Data Quality & Validation**
- ✅ Great Expectations for schema validation
- 🔍 Data quality checks before every training run
- 📈 Statistical validation (ranges, distributions, null checks)
- 🚨 Alerts on data quality issues

### **Deployment & Serving**
- ⚡ FastAPI REST API for real-time predictions
- 🐳 Docker containerization for consistency
- 🌐 Deployed on Render with auto-scaling
- 🔐 API authentication and rate limiting
- 📡 Health checks and readiness probes

### **Monitoring & Observability**
- 📉 Evidently for data drift and model drift detection
- 📊 Prometheus metrics (latency, throughput, errors)
- 📝 Structured logging with correlation IDs
- 📧 Email and Slack notifications
- 📄 Automated PDF drift reports

### **Autonomous Remediation**
- 🤖 AI agent that listens to alerts
- 🧠 Diagnoses issues (drift, errors, performance degradation)
- 🛠️ Takes safe actions automatically (logging, scaling)
- ⚠️ Requests human approval for risky actions (retrain, rollback)
- 📋 Maintains audit log of all actions

### **User Interface**
- 🖥️ Streamlit dashboard with multiple pages:
  - **Model Performance**: Metrics, confusion matrix, ROC curves
  - **Drift Analysis**: Visualize data and prediction drift
  - **Approvals**: Review and approve agent actions
  - **Historical Trends**: Time-series performance metrics
  - **Agent Activity**: Audit log of autonomous actions

### **CI/CD & DevOps**
- 🔄 GitHub Actions for automated testing and deployment
- 🧪 Comprehensive test suite (unit, integration, E2E)
- 📦 Multi-stage Docker builds for optimization
- 🚀 One-click deployment to Render

---

## 🏗️ Architecture

### High-Level System Diagram

```
┌─────────────┐
│   Dataset   │
│  (UCI/CSV)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Great Expectations  │  ◄─── Data Validation
│   (Schema Check)    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Training Pipeline  │
│  - Log Regression   │
│  - Random Forest    │
│  - XGBoost/LightGBM │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  MLflow Tracking    │  ◄─── Experiment Tracking
│  (Log all runs)     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Model Selector     │  ◄─── Best Model Selection
│  (Best by F1)       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ MLflow Registry     │  ◄─── Model Versioning
│  (Production Tag)   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│           Docker Deployment              │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ FastAPI  │  │Streamlit │  │ Agent  ││
│  │   API    │  │    UI    │  │Service ││
│  └──────────┘  └──────────┘  └────────┘│
└─────────────────────────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌─────────────────────────────────────────┐
│          Monitoring & Alerts             │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Evidently │  │Prometheus│  │  Logs  ││
│  │  Drift   │  │ Metrics  │  │        ││
│  └──────────┘  └──────────┘  └────────┘│
└───────────────────┬─────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │ Alert Manager │
            └───────┬───────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
  ┌──────────────┐    ┌──────────────┐
  │Autonomous    │    │ Human via    │
  │Agent         │    │ Streamlit    │
  │(Auto-fix)    │    │ (Approval)   │
  └──────────────┘    └──────────────┘
```

**📖 For detailed architecture diagrams and explanations, see [ARCHITECTURE.md](ARCHITECTURE.md)**

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Git
- 4GB RAM minimum (8GB recommended)

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/mlops-platform.git
cd mlops-platform
```

### 2️⃣ Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### 3️⃣ Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or your preferred editor
```

**Required variables:**
```env
# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_BACKEND_STORE_URI=sqlite:///mlflow.db
MLFLOW_ARTIFACT_ROOT=./mlruns

# DVC
DVC_REMOTE_NAME=myremote
DVC_REMOTE_URL=s3://my-bucket/dvc-storage  # Or local path

# Database
DATABASE_URL=sqlite:///./audit.db  # Use PostgreSQL in production

# Email (optional for local dev)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
NOTIFICATION_EMAIL=alerts@yourcompany.com

# Slack (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# API
API_KEY=your-secret-api-key-change-in-production
```

### 4️⃣ Initialize Project

```bash
# Run setup script
bash scripts/setup_project.sh
```

This script will:
- Download the dataset (UCI Heart Disease)
- Initialize DVC
- Initialize MLflow
- Create necessary directories
- Set up Great Expectations
- Seed the database

### 5️⃣ Run First Training

```bash
# Validate data
python -m validation.data_validator

# Train models
python -m training.train_pipeline

# Check MLflow UI to see results
mlflow ui --host 0.0.0.0 --port 5000
# Open http://localhost:5000 in browser
```

### 6️⃣ Launch Services Locally

```bash
# Start all services with Docker Compose
docker-compose up --build

# Services will be available at:
# - FastAPI: http://localhost:8000
# - Streamlit: http://localhost:8501
# - MLflow: http://localhost:5000
# - Prometheus: http://localhost:9090
```

### 7️⃣ Test Prediction API

```bash
# Test prediction endpoint
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-change-in-production" \
  -d '{
    "age": 54,
    "sex": 1,
    "cp": 0,
    "trestbps": 140,
    "chol": 239,
    "fbs": 0,
    "restecg": 1,
    "thalach": 160,
    "exang": 0,
    "oldpeak": 1.2,
    "slope": 2,
    "ca": 0,
    "thal": 2
  }'

# Expected response:
# {
#   "prediction": 0,
#   "probability": 0.73,
#   "model_version": "1",
#   "timestamp": "2025-11-03T12:34:56Z"
# }
```

### 8️⃣ Open Streamlit Dashboard

```bash
# Navigate to http://localhost:8501
# Explore different pages:
# - Model Performance
# - Drift Analysis
# - Approvals (for agent actions)
# - Historical Trends
```

---

## 📚 Detailed Setup

### Dataset Selection

The system automatically selects the **UCI Heart Disease** dataset because:
- ✅ Tabular data (ideal for MLOps)
- ✅ Binary classification (clear success metrics)
- ✅ Small enough for frequent retraining
- ✅ Well-documented and widely used
- ✅ Contains realistic data quality issues to handle

**Alternative datasets** (can be configured in `config/settings.py`):
- Adult Census Income
- Credit Card Fraud Detection
- Diabetes Prediction

### Model Training Configuration

Edit `config/model_config.yml` to customize:

```yaml
models:
  logistic_regression:
    enabled: true
    hyperparameters:
      C: 1.0
      max_iter: 1000
      class_weight: balanced
  
  random_forest:
    enabled: true
    hyperparameters:
      n_estimators: 100
      max_depth: 10
      class_weight: balanced
  
  xgboost:
    enabled: true
    hyperparameters:
      n_estimators: 100
      max_depth: 6
      learning_rate: 0.1

selection:
  metric: f1_score  # Options: accuracy, f1_score, roc_auc, precision, recall
  minimum_threshold: 0.75  # Minimum acceptable score
```

### Data Validation Configuration

Great Expectations suites are defined in `validation/great_expectations/expectations/`.

To create or modify expectations:

```bash
# Launch Great Expectations UI
great_expectations --v3-api docs build

# Or edit JSON files directly
nano validation/great_expectations/expectations/heart_disease_suite.json
```

### DVC Configuration

Initialize DVC with remote storage:

```bash
# Initialize DVC
dvc init

# Add remote storage (S3 example)
dvc remote add -d myremote s3://my-bucket/dvc-storage
dvc remote modify myremote region us-west-2

# Or use local remote for testing
dvc remote add -d myremote /tmp/dvc-storage

# Configure credentials
dvc remote modify myremote --local access_key_id YOUR_ACCESS_KEY
dvc remote modify myremote --local secret_access_key YOUR_SECRET_KEY

# Track data
dvc add data/raw/heart_disease.csv
git add data/raw/heart_disease.csv.dvc .gitignore
git commit -m "Track dataset with DVC"
dvc push
```

---

## 📖 Usage Guide

### Training a New Model

```bash
# Option 1: Run directly
python -m training.train_pipeline

# Option 2: Use script
bash scripts/run_training.sh

# Option 3: Trigger via API
curl -X POST "http://localhost:8000/trigger-training" \
  -H "X-API-Key: your-api-key"
```

### Monitoring Drift

```bash
# Run drift detection manually
python -m monitoring.drift_detector \
  --reference-data data/reference/reference.csv \
  --current-data data/incoming/latest.csv \
  --output-report reports/drift_report.html

# Drift reports are automatically generated when:
# - New predictions are made (every 1000 predictions)
# - Scheduled job runs (daily via cron)
# - Manually triggered via Streamlit UI
```

### Viewing Experiment Results

```bash
# Start MLflow UI
mlflow ui --host 0.0.0.0 --port 5000

# Compare runs, view metrics, download artifacts
# Navigate to http://localhost:5000
```

### Deploying to Production

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

**Quick deploy to Render:**

1. Push code to GitHub
2. Connect repository to Render
3. Configure environment variables in Render dashboard
4. Deploy automatically via GitHub Actions

```bash
# Manual deployment
git push origin main
# GitHub Actions will automatically build and deploy
```

### Generating Reports

```bash
# Generate deployment report
python scripts/generate_report.py \
  --type deployment \
  --output reports/deployment_report.pdf

# Generate drift report
python scripts/generate_report.py \
  --type drift \
  --output reports/drift_report.pdf

# Reports are also auto-generated and emailed:
# - After each deployment
# - When drift is detected
# - Weekly summary (scheduled)
```

---

## 🐳 Deployment

### Local Deployment (Docker Compose)

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Production Deployment (Render)

**Prerequisites:**
- GitHub repository
- Render account (free tier available)
- Docker Hub account (optional, for custom images)

**Steps:**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Configure Render Services**
   
   Create the following services in Render:
   
   - **FastAPI Service**
     - Type: Web Service
     - Build Command: `docker build -f docker/Dockerfile.api -t api .`
     - Start Command: `uvicorn services.api.main:app --host 0.0.0.0 --port $PORT`
     - Plan: Starter (or higher)
   
   - **Streamlit UI**
     - Type: Web Service
     - Build Command: `docker build -f docker/Dockerfile.ui -t ui .`
     - Start Command: `streamlit run services/ui/app.py --server.port $PORT`
   
   - **Agent Service**
     - Type: Background Worker
     - Build Command: `docker build -f docker/Dockerfile.agent -t agent .`
     - Start Command: `python -m services.agent.agent_service`
   
   - **PostgreSQL**
     - Type: PostgreSQL (managed)
     - Plan: Starter
   
   - **Redis** (optional, for caching)
     - Type: Redis (managed)

3. **Set Environment Variables** (in Render dashboard)
   - Copy all values from `.env.example`
   - Update `DATABASE_URL` to PostgreSQL connection string
   - Add production API keys and secrets

4. **Deploy**
   - Render will auto-deploy on every push to `main`
   - Or manually deploy via dashboard

**GitHub Actions will handle:**
- Running tests
- Building Docker images
- Pushing to registry
- Triggering Render deployment

---

## 📊 Monitoring & Alerts

### Metrics Collected

**Model Metrics:**
- Accuracy, Precision, Recall, F1 Score, AUC-ROC
- Confusion Matrix
- Feature Importance
- Inference Time

**Drift Metrics:**
- Data Drift Score (per feature)
- Prediction Drift Score
- Target Drift (when labels available)

**System Metrics:**
- Request Rate (requests/second)
- Latency (p50, p95, p99)
- Error Rate
- CPU & Memory Usage

### Alert Rules

**Configured in `config/alertmanager_config.yml`:**

```yaml
alerts:
  - name: high_data_drift
    condition: drift_score > 0.7
    severity: warning
    action: notify_agent
    
  - name: critical_data_drift
    condition: drift_score > 0.9
    severity: critical
    action: request_retrain_approval
    
  - name: model_performance_degradation
    condition: f1_score < 0.7
    severity: critical
    action: request_rollback_approval
    
  - name: high_error_rate
    condition: error_rate > 0.05
    severity: critical
    action: escalate_human
```

### Notification Channels

- **Email**: Sent to `NOTIFICATION_EMAIL` for all critical alerts
- **Slack**: Posted to configured channel for all alerts
- **Streamlit**: Badge notifications in approval page
- **Audit Log**: All alerts logged to database

---

## 🤖 Autonomous Agent

### How It Works

1. **Listens** for alerts from Prometheus/Evidently via webhooks
2. **Diagnoses** the issue by analyzing alert context
3. **Decides** appropriate action based on severity and type
4. **Executes** safe actions automatically
5. **Requests approval** for risky actions
6. **Logs** all actions to audit database

### Decision Logic

```python
# Simplified decision tree
if drift_score > 0.9:
    action = "retrain_model"
    requires_approval = True
elif drift_score > 0.7:
    action = "log_warning"
    requires_approval = False
elif error_rate > 0.1:
    action = "rollback_model"
    requires_approval = True
elif latency > 2.0:
    action = "scale_service"
    requires_approval = False
```

### Safe vs. Risky Actions

**Safe (Auto-Executed):**
- ✅ Log warnings
- ✅ Send notifications
- ✅ Clear caches
- ✅ Scale services (within limits)

**Risky (Require Approval):**
- ⚠️ Retrain model
- ⚠️ Deploy new model
- ⚠️ Rollback to previous version
- ⚠️ Modify configuration

### Approving Agent Actions

1. Navigate to Streamlit dashboard
2. Go to **"Approvals"** page
3. Review pending requests with context
4. Click **"Approve"** or **"Reject"**
5. Agent proceeds accordingly

**See [docs/AGENT.md](docs/AGENT.md) for detailed agent documentation.**

---

## 📁 Project Structure

```
mlops/
├── .github/workflows/     # CI/CD pipelines
├── config/                # Configuration files
├── data/                  # Datasets (DVC tracked)
├── models/                # Model artifacts
├── training/              # ML training pipeline
├── validation/            # Data validation (Great Expectations)
├── monitoring/            # Drift & performance monitoring
├── services/              # Microservices
│   ├── api/               # FastAPI inference service
│   ├── ui/                # Streamlit dashboard
│   ├── agent/             # Autonomous agent
│   └── mlflow_server/     # MLflow tracking
├── reporting/             # Report generation
├── notifications/         # Email & Slack
├── database/              # DB models & migrations
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docker/                # Dockerfiles
└── docs/                  # Documentation
```

**See [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) for complete structure.**

---

## 🛠️ Technologies

| Component | Technology |
|-----------|-----------|
| ML Framework | Scikit-learn, XGBoost, LightGBM |
| Experiment Tracking | MLflow |
| Data Versioning | DVC |
| Data Validation | Great Expectations |
| Drift Monitoring | Evidently |
| API Framework | FastAPI |
| UI Dashboard | Streamlit |
| Metrics | Prometheus |
| Database | SQLite → PostgreSQL |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Render |
| Reporting | Jinja2, WeasyPrint |
| Notifications | SMTP, Slack |

**See [TECH_STACK.md](TECH_STACK.md) for detailed technology explanations.**

---

## 📋 Setup Checklist

### Initial Setup

- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Copy `.env.example` to `.env`
- [ ] Configure environment variables
- [ ] Run `setup_project.sh`
- [ ] Download dataset
- [ ] Initialize DVC
- [ ] Initialize MLflow
- [ ] Set up Great Expectations

### First Training Run

- [ ] Validate data with Great Expectations
- [ ] Run training pipeline
- [ ] Check MLflow for logged runs
- [ ] Verify best model selected
- [ ] Promote model to production in MLflow Registry

### Local Deployment

- [ ] Build Docker images
- [ ] Start Docker Compose
- [ ] Verify all services running
- [ ] Test prediction API
- [ ] Open Streamlit dashboard
- [ ] Check Prometheus metrics

### Production Deployment

- [ ] Push code to GitHub
- [ ] Configure Render services
- [ ] Set production environment variables
- [ ] Deploy via GitHub Actions
- [ ] Run smoke tests
- [ ] Verify monitoring and alerts
- [ ] Test autonomous agent
- [ ] Configure email/Slack notifications

### Ongoing Operations

- [ ] Monitor drift reports (daily)
- [ ] Review agent audit logs (weekly)
- [ ] Approve pending agent actions (as needed)
- [ ] Review model performance trends (weekly)
- [ ] Update model when needed (via approval)
- [ ] Backup database regularly
- [ ] Update dependencies (monthly)

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_training.py
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/mlops-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/mlops-platform/discussions)

---

## 🙏 Acknowledgments

- UCI Machine Learning Repository for datasets
- MLflow, DVC, Evidently teams for excellent tools
- FastAPI and Streamlit communities
- Open-source contributors

---

## 🗺️ Roadmap

### Current Version (v1.0)
- ✅ Basic training pipeline
- ✅ MLflow tracking
- ✅ FastAPI inference
- ✅ Streamlit dashboard
- ✅ Docker deployment
- ✅ Autonomous agent (basic)

### Next Version (v1.1)
- [ ] Advanced agent with LLM reasoning
- [ ] Feature store (Feast)
- [ ] A/B testing framework
- [ ] Multi-model ensembles
- [ ] Advanced visualizations (Grafana)

### Future (v2.0+)
- [ ] Kubernetes deployment
- [ ] Distributed training (Ray)
- [ ] Real-time streaming (Kafka)
- [ ] Advanced AutoML
- [ ] Multi-cloud support

---

**Built with ❤️ for production ML systems**
