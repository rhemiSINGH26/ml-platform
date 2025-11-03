# Jenkins CI/CD Quick Start Guide

## ✅ Jenkins is Running!

**Access:** http://localhost:9090  
**Initial Password:** `2e705d4dc65e4cb1ab34b7428c78327e`

---

## 🚀 5-Minute Setup

### Step 1: Unlock Jenkins (2 minutes)
1. Open http://localhost:9090 in your browser
2. Paste password: `2e705d4dc65e4cb1ab34b7428c78327e`
3. Click **"Install suggested plugins"** (wait for installation)
4. Create admin user:
   - Username: `admin` (or your choice)
   - Password: (choose a password)
   - Full name: Your name
   - Email: rhemanthjeyanezsingh@karunya.edu.in
5. Click **Save and Continue** → **Save and Finish** → **Start using Jenkins**

### Step 2: Add Docker Hub Credentials (1 minute)
1. Go to: **Manage Jenkins** (left sidebar) → **Credentials**
2. Click **System** → **Global credentials (unrestricted)**
3. Click **+ Add Credentials** (left sidebar)
4. Fill in:
   - **Kind:** Username with password
   - **Username:** Your Docker Hub username
   - **Password:** Your Docker Hub password or [access token](https://hub.docker.com/settings/security)
   - **ID:** `dockerhub-creds` ⚠️ **Must be exactly this!**
   - **Description:** Docker Hub Credentials
5. Click **Create**

### Step 3: Add GitHub Token (Optional - 1 minute)
Only needed if your repo is private:
1. Create GitHub token at https://github.com/settings/tokens
   - Click **Generate new token (classic)**
   - Select scope: `repo` (full access to repositories)
   - Generate and copy the token
2. Back in Jenkins: **Manage Jenkins** → **Credentials** → **System** → **Global credentials**
3. Click **+ Add Credentials**
4. Fill in:
   - **Kind:** Secret text
   - **Secret:** Paste your GitHub token
   - **ID:** `github-token`
   - **Description:** GitHub Access Token
5. Click **Create**

### Step 4: Create Pipeline Job (1 minute)
1. Click **Dashboard** (top left) → **New Item** (left sidebar)
2. Enter name: `mlops-pipeline`
3. Select **Pipeline**, click **OK**
4. Scroll down to **Pipeline** section
5. Configure:
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/rhemiSINGH26/ml-platform.git`
   - **Credentials:** (leave as none if public repo, or select github-token if private)
   - **Branch Specifier:** `*/main`
   - **Script Path:** `Jenkinsfile`
6. Click **Save**

### Step 5: Run the Pipeline! (30 seconds)
1. Click **Build Now** (left sidebar)
2. Watch the progress:
   - Click on the build number (e.g., **#1**) under "Build History"
   - Click **Console Output** to see logs
   - Or click **Open Blue Ocean** for visual pipeline view

---

## 📊 What the Pipeline Does

### Stages:
1. ✅ **Checkout** - Pulls code from GitHub
2. ✅ **Environment Setup** - Creates Python venv
3. ✅ **Lint & Tests** - Runs flake8 and pytest
4. ✅ **Build Docker Images** - Builds 5 images in parallel:
   - mlops-api
   - mlops-ui
   - mlops-agent
   - mlops-mlflow
   - mlops-training
5. ✅ **Push Docker Images** - Pushes to Docker Hub with tags `latest` and `build-#`
6. ✅ **Trigger Streamlit Deploy** - Creates git tag to trigger Streamlit Cloud

### Expected Duration: ~15-20 minutes (first build)
- Subsequent builds: ~5-10 minutes (with Docker cache)

---

## 🔧 Troubleshooting

### Build Fails at "Push Docker Images"
- **Cause:** Docker Hub credentials not configured or incorrect ID
- **Fix:** Check credential ID is exactly `dockerhub-creds` (Step 2)

### Build Fails at "Checkout"
- **Cause:** GitHub repo is private but no token configured
- **Fix:** Add github-token credential (Step 3)

### Docker build timeouts
- **Cause:** Network issues downloading packages
- **Fix:** Pipeline already has 300s timeout and retries configured

### Permission denied running Docker
- **Cause:** Jenkins user not in docker group
- **Fix:** Already handled! We ran `usermod -aG docker jenkins`
- If still fails, restart Jenkins:
  ```bash
  sudo docker restart jenkins
  ```

---

## 🎯 After First Successful Build

### View Docker Images:
```bash
# On Docker Hub (replace YOUR_USERNAME):
# https://hub.docker.com/r/YOUR_USERNAME/mlops-api
# https://hub.docker.com/r/YOUR_USERNAME/mlops-ui
# https://hub.docker.com/r/YOUR_USERNAME/mlops-agent
# https://hub.docker.com/r/YOUR_USERNAME/mlops-mlflow
# https://hub.docker.com/r/YOUR_USERNAME/mlops-training
```

### Trigger Builds:
- **Manual:** Click "Build Now" in Jenkins
- **Automatic:** Push to main branch (configure webhook in GitHub repo settings)

### Configure Webhooks (Optional):
1. Go to your GitHub repo: https://github.com/rhemiSINGH26/ml-platform/settings/hooks
2. Add webhook:
   - Payload URL: `http://YOUR_IP:9090/github-webhook/`
   - Content type: `application/json`
   - Events: Just the push event
   - Active: ✓
3. Now every push to main triggers a build!

---

## 📱 Next: Deploy Streamlit UI

After Jenkins builds successfully:
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click **New app**
4. Select:
   - Repository: `rhemiSINGH26/ml-platform`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
5. Click **Deploy**
6. Your app will be live at: `https://YOUR_APP_NAME.streamlit.app/`

Streamlit Cloud auto-deploys on every push to main!

---

## 🛑 Stop Jenkins

When done testing:
```bash
sudo docker stop jenkins
```

Restart anytime:
```bash
sudo docker start jenkins
```

Remove completely:
```bash
sudo docker rm -f jenkins
sudo docker volume rm jenkins_home
```

---

## ✨ You're Ready!

Open http://localhost:9090 and follow Steps 1-5 above. Your CI/CD pipeline will be running in 5 minutes!
