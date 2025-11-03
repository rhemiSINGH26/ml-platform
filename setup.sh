#!/bin/bash
#
# Complete MLOps Platform Setup Script
# Initializes the entire system for first-time use
#

set -e  # Exit on error

echo "============================================"
echo "MLOps Platform Setup"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠ Please edit .env with your configuration before continuing${NC}"
    echo ""
    read -p "Press Enter when .env is configured..."
fi

# Create required directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p data/raw data/processed data/reference
mkdir -p models/production models/staging models/archive
mkdir -p logs
mkdir -p audit/reports
mkdir -p reports/drift
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting PostgreSQL and MLflow...${NC}"
docker-compose up -d postgres mlflow
echo -e "${GREEN}✓ Core services started${NC}"
echo ""

# Wait for PostgreSQL
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
sleep 5
echo -e "${GREEN}✓ PostgreSQL ready${NC}"
echo ""

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python scripts/init_database.py || {
    echo -e "${YELLOW}⚠ Could not initialize database from host. Trying from container...${NC}"
    docker-compose run --rm api python scripts/init_database.py
}
echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

# Download data
echo -e "${YELLOW}Downloading dataset...${NC}"
python scripts/download_data.py || {
    echo -e "${YELLOW}⚠ Could not download from host. Trying from container...${NC}"
    docker-compose run --rm training python scripts/download_data.py
}
echo -e "${GREEN}✓ Dataset downloaded${NC}"
echo ""

# Train initial model
echo -e "${YELLOW}Training initial model (this may take a few minutes)...${NC}"
python training/train_pipeline.py || {
    echo -e "${YELLOW}⚠ Could not train from host. Trying from container...${NC}"
    docker-compose run --rm training python training/train_pipeline.py
}
echo -e "${GREEN}✓ Initial model trained${NC}"
echo ""

# Start all services
echo -e "${YELLOW}Starting all services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ All services started${NC}"
echo ""

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Health check
echo -e "${YELLOW}Running health checks...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${YELLOW}⚠ API health check failed. Check logs: docker-compose logs api${NC}"
fi
echo ""

# Show service URLs
echo ""
echo "============================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "============================================"
echo ""
echo "Services are running at:"
echo "  - API:        http://localhost:8000"
echo "  - Dashboard:  http://localhost:8501"
echo "  - MLflow:     http://localhost:5000"
echo "  - Prometheus: http://localhost:9090"
echo "  - Grafana:    http://localhost:3000"
echo ""
echo "API Documentation:"
echo "  - Swagger UI: http://localhost:8000/docs"
echo "  - ReDoc:      http://localhost:8000/redoc"
echo ""
echo "Useful commands:"
echo "  - View logs:     docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart:       docker-compose restart"
echo ""
echo "Next steps:"
echo "  1. Open dashboard: http://localhost:8501"
echo "  2. Make a test prediction:"
echo "     curl -X POST http://localhost:8000/predict \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -H 'X-API-Key: your-api-key' \\"
echo "       -d '{\"age\": 55, \"sex\": 1, \"cp\": 3, ...}'"
echo ""
echo "For help, see README.md or QUICK_START.md"
echo ""
