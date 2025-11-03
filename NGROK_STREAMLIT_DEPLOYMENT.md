# ngrok + Streamlit Cloud Deployment Guide

## 🎯 Architecture

```
┌─────────────────┐     ngrok tunnel      ┌──────────────────┐
│  Your Local PC  │◄──────────────────────┤  Streamlit Cloud │
│                 │                        │     (Public)     │
│  ┌───────────┐  │   https://xyz.ngrok.io│                  │
│  │ API:8000  │  │                        │   Streamlit UI   │
│  │ MLflow    │  │                        │                  │
│  │ Agent     │  │                        └──────────────────┘
│  └───────────┘  │                              │
│                 │                              │
│  Docker Compose │◄─────────────────────────────┘
└─────────────────┘         API calls
```

## ⚡ Quick Start (After Jenkins Build Completes)

### Step 1: Run the Setup Script

```bash
cd /home/rhemi/IA3/mlops
./setup_ngrok_streamlit.sh
```

This script will:
1. ✅ Install ngrok (if not installed)
2. ✅ Check ngrok authentication
3. ✅ Start Docker services (postgres, mlflow, api)
4. ✅ Start ngrok tunnel
5. ✅ Display your public API URL

### Step 2: Get ngrok Account (First Time Only)

If you see "You need to authenticate ngrok!":

1. Go to https://dashboard.ngrok.com/signup (free account)
2. Copy your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
3. Run:
   ```bash
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```
4. Run the setup script again:
   ```bash
   ./setup_ngrok_streamlit.sh
   ```

### Step 3: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository:** `rhemiSINGH26/ml-platform`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`

5. Click **"Advanced settings"**
6. In the **Secrets** section, add:
   ```toml
   API_URL = "https://YOUR-NGROK-URL.ngrok.io"
   ```
   (Copy the URL from the setup script output)

7. Click **"Deploy"**!

### Step 4: Access Your App

- **Streamlit UI:** https://YOUR-APP-NAME.streamlit.app
- **Local API:** http://localhost:8000
- **ngrok Dashboard:** http://localhost:4040

---

## 🔄 Daily Usage

### Start Everything:
```bash
cd /home/rhemi/IA3/mlops
./setup_ngrok_streamlit.sh
```

Keep the terminal open! The script shows your ngrok URL.

### Stop Everything:
Press `Ctrl+C` in the terminal running the script

Or manually:
```bash
sudo docker-compose down
pkill ngrok
```

---

## 🔄 If ngrok URL Changes

ngrok free tier gives you a **new URL every time you restart**. When this happens:

1. Restart the setup script to get new URL
2. Go to your Streamlit Cloud app settings
3. Update the `API_URL` secret with the new ngrok URL
4. Click "Save" (app will restart automatically)

---

## 📊 Manual Setup (Alternative)

If you prefer manual control:

### 1. Start Docker Services:
```bash
sudo docker-compose up -d postgres mlflow api
```

### 2. Start ngrok:
```bash
ngrok http 8000
```

Copy the "Forwarding" URL (https://xxxxx.ngrok.io)

### 3. Update Streamlit Secrets:

Create `.streamlit/secrets.toml` locally (for testing):
```toml
API_URL = "https://YOUR-NGROK-URL.ngrok.io"
```

For Streamlit Cloud: Add in app settings → Secrets

### 4. Run Streamlit Locally (Optional):
```bash
cd /home/rhemi/IA3/mlops
streamlit run streamlit_app.py
```

---

## 🛠️ Troubleshooting

### ngrok tunnel not working
```bash
# Check if ngrok is running
curl http://localhost:4040/api/tunnels

# Restart ngrok
pkill ngrok
ngrok http 8000
```

### API not responding
```bash
# Check API health
curl http://localhost:8000/health

# Check logs
sudo docker logs mlops-api

# Restart API
sudo docker-compose restart api
```

### Streamlit can't connect to API
1. Check ngrok URL in Streamlit secrets
2. Make sure ngrok tunnel is running (check http://localhost:4040)
3. Test API manually: `curl YOUR-NGROK-URL/health`

### "This site can't be reached" on ngrok URL
- ngrok might have stopped - restart the setup script
- Free ngrok URLs expire after 2 hours of inactivity
- Check ngrok dashboard: http://localhost:4040

---

## 💡 Tips

1. **Keep ngrok running:** Don't close the terminal running the setup script
2. **Bookmark your Streamlit app:** https://YOUR-APP.streamlit.app
3. **Monitor ngrok:** Check http://localhost:4040 for request logs
4. **Free tier limits:** 
   - 1 tunnel at a time
   - URL changes on restart
   - 40 requests/minute

5. **For production:** Consider ngrok paid plan ($10/mo) for static URLs

---

## 🚀 CI/CD Integration

Your Jenkins pipeline already:
- ✅ Builds Docker images
- ✅ Pushes to Docker Hub
- ✅ Runs on every commit

After Jenkins builds successfully:
1. Pull latest images (or use locally built)
2. Run `./setup_ngrok_streamlit.sh`
3. Your Streamlit app updates automatically!

---

## 📝 File Structure

```
/home/rhemi/IA3/mlops/
├── setup_ngrok_streamlit.sh    # One-command setup
├── streamlit_app.py             # Streamlit entry point
├── .streamlit/
│   ├── config.toml             # UI configuration
│   └── secrets.toml            # API URL (local only)
├── services/ui/                # Streamlit pages
├── docker-compose.yml          # Docker services
└── Jenkinsfile                 # CI/CD pipeline
```

---

## ✅ You're All Set!

Run the script after Jenkins finishes building:

```bash
./setup_ngrok_streamlit.sh
```

Then deploy to Streamlit Cloud with the displayed ngrok URL! 🎉
