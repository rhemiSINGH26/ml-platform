#!/bin/bash
# Setup script for ngrok + Streamlit Cloud deployment

set -e

echo "🚀 MLOps Platform - ngrok + Streamlit Cloud Setup"
echo "=================================================="
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📥 Installing ngrok..."
    
    # Download ngrok
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xvzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok-v3-stable-linux-amd64.tgz
    
    echo "✅ ngrok installed!"
    echo ""
else
    echo "✅ ngrok already installed"
    echo ""
fi

# Check ngrok auth
echo "🔑 Checking ngrok authentication..."
if ! ngrok config check &> /dev/null; then
    echo ""
    echo "⚠️  You need to authenticate ngrok!"
    echo ""
    echo "Steps:"
    echo "1. Go to https://dashboard.ngrok.com/signup (free account)"
    echo "2. Copy your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "3. Run: ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ ngrok is authenticated"
echo ""

# Start services
echo "🐳 Starting Docker services..."
sudo docker-compose up -d postgres mlflow api

echo ""
echo "⏳ Waiting for API to be healthy (30 seconds)..."
sleep 30

# Check if API is running
if ! curl -f http://localhost:8000/health &> /dev/null; then
    echo "❌ API is not responding. Check docker logs:"
    echo "   sudo docker logs mlops-api"
    exit 1
fi

echo "✅ API is healthy!"
echo ""

# Start ngrok
echo "🌐 Starting ngrok tunnel on port 8000..."
echo ""
echo "Starting ngrok in background..."
ngrok http 8000 --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

echo "⏳ Waiting for ngrok to start..."
sleep 5

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL. Check if ngrok is running:"
    echo "   curl http://localhost:4040/api/tunnels"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "✅ ngrok tunnel is running!"
echo ""
echo "=================================================="
echo "🎉 Your API is now publicly accessible!"
echo "=================================================="
echo ""
echo "📍 ngrok Public URL: $NGROK_URL"
echo "📍 Local API: http://localhost:8000"
echo "📍 ngrok Dashboard: http://localhost:4040"
echo ""
echo "=================================================="
echo "📋 Next Steps for Streamlit Cloud:"
echo "=================================================="
echo ""
echo "1. Go to https://share.streamlit.io/"
echo "2. Sign in with GitHub"
echo "3. Click 'New app'"
echo "4. Configure:"
echo "   - Repository: rhemiSINGH26/ml-platform"
echo "   - Branch: main"
echo "   - Main file: streamlit_app.py"
echo ""
echo "5. Click 'Advanced settings' and add this secret:"
echo ""
echo "   API_URL = \"$NGROK_URL\""
echo ""
echo "6. Click 'Deploy'!"
echo ""
echo "=================================================="
echo "⚠️  IMPORTANT:"
echo "=================================================="
echo ""
echo "• Keep this terminal open (ngrok tunnel running)"
echo "• ngrok PID: $NGROK_PID"
echo "• To stop: sudo docker-compose down && kill $NGROK_PID"
echo "• Free ngrok URLs change on restart"
echo "• Update Streamlit secrets if you restart ngrok"
echo ""
echo "Press Ctrl+C to stop ngrok and services"
echo ""

# Keep script running
trap "echo ''; echo 'Stopping services...'; sudo docker-compose down; kill $NGROK_PID 2>/dev/null; exit 0" INT TERM

# Follow ngrok logs
tail -f /tmp/ngrok.log
