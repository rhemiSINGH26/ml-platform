# Jenkins CI/CD + Streamlit Cloud Deployment Guide

This guide shows you how to run Jenkins locally for CI/CD and deploy your Streamlit UI to Streamlit Cloud.

---

## 🚀 Quick Start

### Step 1: Start Jenkins Locally

Run Jenkins in Docker with access to Docker socket:

```bash
sudo docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -u root \
  jenkins/jenkins:lts
```

**Why `-u root`?** Allows Jenkins to run Docker commands. For production, use proper Docker-in-Docker setup.

### Step 2: Get Initial Admin Password

```bash
sudo docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Copy the password, then visit http://localhost:8080

### Step 3: Install Jenkins Plugins

1. Choose "Install suggested plugins"
2. After installation, also install:
   - **Docker Pipeline** plugin
   - **GitHub** plugin
   - **Credentials Binding** plugin

### Step 4: Create Jenkins Credentials

Navigate to: **Dashboard → Manage Jenkins → Credentials → System → Global credentials → Add Credentials**

#### A. Docker Hub Credentials
- **Kind**: Username with password
- **ID**: `dockerhub-creds`
- **Username**: Your Docker Hub username
- **Password**: Your Docker Hub password or access token
- **Description**: Docker Hub credentials

#### B. GitHub Token
- **Kind**: Secret text
- **ID**: `github-token`
- **Secret**: Your GitHub Personal Access Token
- **Description**: GitHub token for pushing tags

**How to create GitHub token:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Copy and save the token

### Step 5: Create Jenkins Pipeline Job

1. **Dashboard → New Item**
2. Enter name: `mlops-pipeline`
3. Select: **Pipeline**
4. Click **OK**

#### Configure the Pipeline:

**General:**
- ✅ GitHub project
- Project URL: `https://github.com/rhemiSINGH26/ml-platform`

**Build Triggers:**
- ✅ GitHub hook trigger for GITScm polling (if you set up webhooks)
- OR: ✅ Poll SCM: `H/15 * * * *` (check every 15 min)

**Pipeline:**
- **Definition**: Pipeline script from SCM
- **SCM**: Git
- **Repository URL**: `https://github.com/rhemiSINGH26/ml-platform.git`
- **Credentials**: Add your GitHub credentials
- **Branch**: `*/main`
- **Script Path**: `Jenkinsfile`

Click **Save**.

### Step 6: Run Your First Build

1. Click **Build Now**
2. Watch the pipeline stages execute
3. Check **Console Output** for logs

---

## 📊 Deploy Streamlit UI to Streamlit Cloud

### Step 1: Sign Up for Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Authorize Streamlit to access your repositories

### Step 2: Deploy the App

1. Click **New app**
2. Select repository: `rhemiSINGH26/ml-platform`
3. Branch: `main`
4. Main file path: `streamlit_app.py`
5. Click **Deploy!**

### Step 3: Configure Environment Variables (If Needed)

In Streamlit Cloud app settings, add:

```
API_URL=https://your-api-service.onrender.com
MLFLOW_TRACKING_URI=https://your-mlflow-service.onrender.com
```

**Note:** For local testing, you can run the API and MLflow services locally or on another server.

### Step 4: Auto-Deploy on Push

Streamlit Cloud automatically redeploys when you push to the `main` branch!

---

## 🔧 Jenkins Pipeline Stages

The `Jenkinsfile` includes these stages:

1. **Checkout** - Pull code from GitHub
2. **Environment Setup** - Create Python venv
3. **Lint & Tests** - Run flake8 and pytest
4. **Build Docker Images** - Build 5 images in parallel:
   - API
   - UI
   - Agent
   - MLflow
   - Training
5. **Push Docker Images** - Push to Docker Hub with build number and `latest` tags
6. **Trigger Streamlit Deploy** - Push git tag to trigger Streamlit Cloud redeploy

---

## 🛠️ Local Development Workflow

### Test Streamlit App Locally

```bash
cd /home/rhemi/IA3/mlops
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501
```

Visit http://localhost:8501

### Run Jenkins Pipeline Manually

```bash
# Trigger from command line (requires Jenkins CLI)
java -jar jenkins-cli.jar -s http://localhost:8080/ build mlops-pipeline
```

Or just click **Build Now** in Jenkins UI.

---

## 📦 Docker Image Tags

Each build creates images with two tags:

- `${DOCKERHUB_USERNAME}/mlops-api:123` (build number)
- `${DOCKERHUB_USERNAME}/mlops-api:latest`

You can deploy specific builds by using the build number tag.

---

## 🔐 Security Best Practices

1. **Never commit credentials** - Always use Jenkins credentials store
2. **Use Docker Hub access tokens** instead of passwords
3. **Limit GitHub token scope** to only `repo` access
4. **Run Jenkins with proper user permissions** (not root in production)
5. **Use secrets management** for production (HashiCorp Vault, AWS Secrets Manager)

---

## 🐛 Troubleshooting

### Jenkins can't run Docker commands

**Error:** `docker: command not found`

**Fix:** Install Docker inside Jenkins container:

```bash
sudo docker exec -u root jenkins bash -c "
  apt-get update && 
  apt-get install -y docker.io &&
  usermod -aG docker jenkins
"
sudo docker restart jenkins
```

### Streamlit Cloud app won't start

**Check:**
1. `streamlit_app.py` exists at repo root ✓
2. `requirements.txt` includes `streamlit` ✓
3. No import errors in logs
4. Environment variables set correctly

### Build fails on "Push Docker Images"

**Check:**
1. Docker Hub credentials in Jenkins are correct
2. You have permission to push to the repository
3. Repository name matches your Docker Hub username

---

## 📚 Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Docker Hub](https://hub.docker.com/)

---

## 🎯 Next Steps

1. ✅ Start Jenkins container
2. ✅ Configure credentials
3. ✅ Create pipeline job
4. ✅ Run first build
5. ✅ Deploy Streamlit app
6. 🔄 Push code changes → Jenkins builds → Streamlit auto-deploys

**Your CI/CD pipeline is now complete!** 🚀
