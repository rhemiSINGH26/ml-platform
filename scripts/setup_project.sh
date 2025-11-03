#!/bin/bash

# MLOps Platform Setup Script
# This script sets up the entire MLOps platform

set -e  # Exit on error

echo "=================================="
echo "MLOps Platform Setup"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    print_error "Python 3.10+ required. Found: $python_version"
    exit 1
fi
print_success "Python $python_version found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel
print_success "Pip upgraded"

# Install dependencies
print_status "Installing core dependencies..."
pip install -r requirements.txt
print_success "Core dependencies installed"

print_status "Installing development dependencies..."
pip install -r requirements-dev.txt
print_success "Development dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created - PLEASE EDIT IT WITH YOUR SETTINGS"
else
    print_success ".env file already exists"
fi

# Create necessary directories
print_status "Creating directory structure..."
mkdir -p data/raw data/processed data/reference
mkdir -p models/production models/staging models/archive
mkdir -p logs
mkdir -p audit/reports
mkdir -p mlruns
print_success "Directories created"

# Download dataset
print_status "Downloading UCI Heart Disease dataset..."
python scripts/download_data.py
print_success "Dataset downloaded"

# Validate dataset
print_status "Validating dataset..."
python -m validation.data_validator data/raw/heart_disease.csv
print_success "Dataset validation complete"

# Initialize DVC
if [ ! -d ".dvc" ]; then
    print_status "Initializing DVC..."
    dvc init
    dvc remote add -d myremote ./dvc-storage
    dvc add data/raw/heart_disease.csv
    git add data/raw/heart_disease.csv.dvc .gitignore
    print_success "DVC initialized"
else
    print_success "DVC already initialized"
fi

# Initialize MLflow
print_status "MLflow tracking will use: sqlite:///mlflow.db"
print_success "MLflow configured"

# Create initial commit if this is a new git repo
if [ ! -d ".git" ]; then
    print_status "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: MLOps platform setup"
    print_success "Git repository initialized"
else
    print_success "Git repository already exists"
fi

echo ""
echo "=================================="
echo "Setup Complete! ✓"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run training: python -m training.train_pipeline"
echo "3. Start MLflow UI: mlflow ui"
echo "4. Start API: uvicorn services.api.main:app --reload"
echo "5. Start Streamlit: streamlit run services/ui/app.py"
echo ""
echo "Or start all services with Docker:"
echo "docker-compose up --build"
echo ""
