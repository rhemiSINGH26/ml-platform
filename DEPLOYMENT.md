# MLOps Platform Deployment Guide

## 🚀 Overview

This guide covers deploying the MLOps platform to Render.com with automated CI/CD pipelines.

## 📋 Prerequisites

1. **GitHub Account** with repository access
2. **Render Account** (free tier available at https://render.com)
3. **Docker Hub Account** (for image registry)
4. **Optional:** Slack workspace for notifications
5. **Optional:** Email account (Gmail/SendGrid) for alerts

---

## 🔧 CI/CD Pipeline Setup

### GitHub Actions Workflows

The platform includes 3 automated workflows:

#### 1. **CI Pipeline** (`.github/workflows/ci.yml`)
**Triggers:** Every push/PR to `main` or `develop`

**What it does:**
- ✅ Lints code (ruff, black)
- ✅ Type checks (mypy)
- ✅ Runs unit & integration tests
- ✅ Builds Docker images
- ✅ Security scanning (Trivy)
- ✅ Coverage reports (Codecov)

#### 2. **CD Pipeline** (`.github/workflows/deploy.yml`)
**Triggers:** Push to `main` branch

**What it does:**
- 🚀 Builds & pushes Docker images to Docker Hub
- 🚀 Deploys to Render via API
- 🚀 Runs health checks
- 🚀 Sends Slack notifications

#### 3. **Scheduled Retraining** (`.github/workflows/retrain.yml`)
**Triggers:** Every Sunday at 2 AM UTC (or manual)

**What it does:**
- 🔄 Downloads latest data
- 🔄 Validates data quality
- 🔄 Trains new models
- 🔄 Checks performance thresholds
- 🔄 Auto-deploys if successful
- 🔄 Creates GitHub release

---

## 🔐 GitHub Secrets Configuration

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

### Required Secrets:

```bash
# Docker Hub (for image registry)
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-password-or-token

# Render (for deployment)
RENDER_API_KEY=rnd_xxxxxxxxxxxxxxxxxxxxx
RENDER_SERVICE_ID_API=srv-xxxxxxxxxxxxxxxxxxxxx
RENDER_SERVICE_ID_UI=srv-xxxxxxxxxxxxxxxxxxxxx
RENDER_SERVICE_ID_AGENT=srv-xxxxxxxxxxxxxxxxxxxxx

# API URL (after first deployment)
API_URL=https://mlops-api.onrender.com

# MLflow (after deployment)
MLFLOW_TRACKING_URI=https://mlops-mlflow.onrender.com
```

### Optional Secrets:

```bash
# Slack notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email notifications
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

---

## 🌐 Render Deployment

### Method 1: One-Click Deploy (Recommended)

1. **Push `render.yaml` to your repository**

2. **Go to Render Dashboard**
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository
   - Click "Apply"

3. **Render will automatically:**
   - Create PostgreSQL database
   - Deploy MLflow tracking server
   - Deploy API service
   - Deploy UI dashboard
   - Start autonomous agent worker

### Method 2: Manual Setup

#### Step 1: Create PostgreSQL Database

```bash
Name: mlops-postgres
Database: mlops
User: mlops
Plan: Starter ($7/month)
```

Copy the **Internal Database URL** for later.

#### Step 2: Deploy MLflow

```yaml
Name: mlops-mlflow
Type: Web Service
Environment: Docker
Dockerfile Path: ./Dockerfile.mlflow
Plan: Starter
Environment Variables:
  - MLFLOW_BACKEND_STORE_URI: <postgres-url>
  - MLFLOW_ARTIFACT_ROOT: /mlflow/artifacts
Disk:
  - Name: mlflow-artifacts
  - Mount Path: /mlflow/artifacts
  - Size: 20GB
```

#### Step 3: Deploy API Service

```yaml
Name: mlops-api
Type: Web Service
Environment: Docker
Dockerfile Path: ./Dockerfile.api
Plan: Starter
Environment Variables:
  - DATABASE_URL: <postgres-url>
  - MLFLOW_TRACKING_URI: <mlflow-url>
  - API_KEY: <generate-secure-key>
  - ENVIRONMENT: production
  - LOG_LEVEL: INFO
Health Check Path: /health
Auto-Deploy: Yes
```

#### Step 4: Deploy UI Dashboard

```yaml
Name: mlops-ui
Type: Web Service
Environment: Docker
Dockerfile Path: ./Dockerfile.ui
Plan: Starter
Environment Variables:
  - API_URL: <api-url>
  - MLFLOW_TRACKING_URI: <mlflow-url>
  - ENVIRONMENT: production
Health Check Path: /_stcore/health
Auto-Deploy: Yes
```

#### Step 5: Deploy Agent (Background Worker)

```yaml
Name: mlops-agent
Type: Background Worker
Environment: Docker
Dockerfile Path: ./Dockerfile.agent
Plan: Starter
Environment Variables:
  - DATABASE_URL: <postgres-url>
  - MLFLOW_TRACKING_URI: <mlflow-url>
  - API_URL: <api-url>
  - AGENT_ENABLED: true
  - ENVIRONMENT: production
Auto-Deploy: Yes
```

---

## 📧 Email Notifications Setup

### Option 1: Gmail

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "MLOps Platform"
   - Copy the 16-character password

3. **Add to GitHub Secrets:**
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=<16-char-app-password>
   SMTP_USE_TLS=true
   NOTIFICATION_EMAIL=alerts@yourcompany.com
   ```

4. **Update Render Environment Variables:**
   - Set `SMTP_ENABLED=true`
   - Add all SMTP_* variables

### Option 2: SendGrid (Recommended for Production)

1. **Sign up at https://sendgrid.com** (free tier: 100 emails/day)
2. **Create API Key** with "Mail Send" permissions
3. **Add to secrets:**
   ```bash
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USER=apikey
   SMTP_PASSWORD=<your-sendgrid-api-key>
   ```

---

## 💬 Slack Notifications Setup

1. **Create Incoming Webhook:**
   - Go to https://api.slack.com/messaging/webhooks
   - Click "Create New App" → "From scratch"
   - Enable "Incoming Webhooks"
   - Click "Add New Webhook to Workspace"
   - Select channel (e.g., #mlops-alerts)
   - Copy webhook URL

2. **Add to GitHub Secrets:**
   ```bash
   SLACK_WEBHOOK=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```

3. **Update Render Environment:**
   - Set `SLACK_ENABLED=true`
   - Set `SLACK_WEBHOOK_URL=<webhook-url>`
   - Set `SLACK_CHANNEL=#mlops-alerts`

---

## 🔑 Getting Render Service IDs

After deploying services on Render:

1. Go to each service dashboard
2. Copy the Service ID from the URL:
   ```
   https://dashboard.render.com/web/srv-xxxxxxxxxxxxxxxxxxxxx
                                      ^^^^^^^^^^^^^^^^^^^^^^^^
                                      This is your Service ID
   ```

3. Add to GitHub Secrets:
   ```bash
   RENDER_SERVICE_ID_API=srv-xxxxxxxxxxxxxxxxxxxxx
   RENDER_SERVICE_ID_UI=srv-xxxxxxxxxxxxxxxxxxxxx
   RENDER_SERVICE_ID_AGENT=srv-xxxxxxxxxxxxxxxxxxxxx
   ```

---

## 🔄 Deployment Workflow

### Automatic Deployment

```mermaid
graph LR
    A[Push to main] --> B[CI Tests]
    B --> C{Tests Pass?}
    C -->|Yes| D[Build Images]
    D --> E[Push to Docker Hub]
    E --> F[Deploy to Render]
    F --> G[Health Check]
    G --> H{Healthy?}
    H -->|Yes| I[Notify Success]
    H -->|No| J[Notify Failure]
    C -->|No| J
```

### Manual Deployment

```bash
# Trigger deployment via GitHub Actions
gh workflow run deploy.yml

# Or trigger via Render API
curl -X POST \
  "https://api.render.com/v1/services/${SERVICE_ID}/deploys" \
  -H "Authorization: Bearer ${RENDER_API_KEY}" \
  -H "Content-Type: application/json"
```

---

## 🧪 Testing the Deployment

### 1. Health Checks

```bash
# API Health
curl https://mlops-api.onrender.com/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-03T10:00:00Z"
}
```

### 2. Make Test Prediction

```bash
curl -X POST https://mlops-api.onrender.com/predict \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: your-api-key' \
  -d '{
    "age": 55,
    "sex": 1,
    "cp": 3,
    "trestbps": 140,
    "chol": 250,
    "fbs": 0,
    "restecg": 1,
    "thalach": 150,
    "exang": 1,
    "oldpeak": 2.5,
    "slope": 2,
    "ca": 0,
    "thal": 2
  }'
```

### 3. Access Services

- **API Documentation:** https://mlops-api.onrender.com/docs
- **Dashboard:** https://mlops-ui.onrender.com
- **MLflow UI:** https://mlops-mlflow.onrender.com

---

## 📊 Monitoring & Alerts

### What Gets Monitored:

- ✅ **API Health** - Automatic health checks every 30s
- ✅ **Model Performance** - Tracks accuracy, F1, ROC-AUC
- ✅ **Data Drift** - Detects distribution changes
- ✅ **Prediction Latency** - Response time tracking
- ✅ **Error Rates** - Failed predictions and exceptions
- ✅ **Resource Usage** - CPU, Memory, Disk

### Alert Triggers:

| Event | Threshold | Notification |
|-------|-----------|--------------|
| Model F1 Drop | < 0.75 | Email + Slack |
| Data Drift | > 0.7 | Email + Slack |
| API Errors | > 5% | Email + Slack |
| Response Time | > 2s | Slack |
| Disk Usage | > 80% | Email |

---

## 🔧 Troubleshooting

### Common Issues:

#### 1. Build Failures

```bash
# Check build logs in Render dashboard
# Common fixes:
- Increase build timeout in render.yaml
- Check Docker image size (should be < 5GB)
- Verify all dependencies in requirements.txt
```

#### 2. Database Connection Errors

```bash
# Verify DATABASE_URL format:
postgresql://user:password@host:port/database

# Check PostgreSQL logs in Render
# Ensure internal database URL is used (not external)
```

#### 3. MLflow Connection Issues

```bash
# Ensure MLFLOW_TRACKING_URI uses internal URL
# Format: http://mlflow:5000 (internal)
# Not: https://mlops-mlflow.onrender.com (external)
```

#### 4. Email Notifications Not Working

```bash
# Check SMTP settings
# For Gmail, verify app-specific password
# Check SMTP_ENABLED=true
# Review logs for SMTP errors
```

---

## 💰 Cost Estimation

### Render Pricing (Monthly):

| Service | Plan | Cost |
|---------|------|------|
| PostgreSQL | Starter | $7 |
| API | Starter | $7 |
| UI | Starter | $7 |
| MLflow | Starter | $7 |
| Agent | Starter | $7 |
| **Total** | | **$35/month** |

### Free Tier Option:

- Use **free tier** for testing (services sleep after inactivity)
- PostgreSQL requires paid plan ($7/month minimum)

---

## 🎯 Best Practices

1. **Use Environment-Specific Configs**
   - Development: Local Docker Compose
   - Staging: Render free tier
   - Production: Render paid plans

2. **Enable Auto-Deploy**
   - Only for `main` branch
   - Keep `develop` branch manual

3. **Monitor Costs**
   - Start with Starter plans
   - Upgrade to Standard if needed
   - Use disk snapshots for backups

4. **Security**
   - Rotate API keys regularly
   - Use strong database passwords
   - Enable 2FA on Render account
   - Keep dependencies updated

5. **Backup Strategy**
   - Weekly model snapshots
   - Daily database backups (Render automatic)
   - Store artifacts in S3/GCS for production

---

## 📚 Additional Resources

- **Render Documentation:** https://render.com/docs
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **MLflow Docs:** https://mlflow.org/docs/latest/index.html
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/

---

## 🆘 Support

If you encounter issues:

1. Check Render service logs
2. Review GitHub Actions workflow runs
3. Check database connectivity
4. Verify environment variables
5. Review this deployment guide

For questions, open an issue in the GitHub repository.

---

**Happy Deploying! 🚀**
