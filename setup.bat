@echo off
REM Complete MLOps Platform Setup Script (Windows)
REM Initializes the entire system for first-time use

echo ============================================
echo MLOps Platform Setup (Windows)
echo ============================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo [OK] Created .env file
    echo [WARNING] Please edit .env with your configuration before continuing
    echo.
    pause
)

REM Create required directories
echo Creating directories...
if not exist data\raw mkdir data\raw
if not exist data\processed mkdir data\processed
if not exist data\reference mkdir data\reference
if not exist models\production mkdir models\production
if not exist models\staging mkdir models\staging
if not exist models\archive mkdir models\archive
if not exist logs mkdir logs
if not exist audit\reports mkdir audit\reports
if not exist reports\drift mkdir reports\drift
echo [OK] Directories created
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Starting PostgreSQL and MLflow...
docker-compose up -d postgres mlflow
echo [OK] Core services started
echo.

REM Wait for PostgreSQL
echo Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak >nul
echo [OK] PostgreSQL ready
echo.

REM Initialize database
echo Initializing database...
python scripts\init_database.py
if errorlevel 1 (
    echo [WARNING] Could not initialize from host. Trying from container...
    docker-compose run --rm api python scripts/init_database.py
)
echo [OK] Database initialized
echo.

REM Download data
echo Downloading dataset...
python scripts\download_data.py
if errorlevel 1 (
    echo [WARNING] Could not download from host. Trying from container...
    docker-compose run --rm training python scripts/download_data.py
)
echo [OK] Dataset downloaded
echo.

REM Train initial model
echo Training initial model (this may take a few minutes)...
python training\train_pipeline.py
if errorlevel 1 (
    echo [WARNING] Could not train from host. Trying from container...
    docker-compose run --rm training python training/train_pipeline.py
)
echo [OK] Initial model trained
echo.

REM Start all services
echo Starting all services...
docker-compose up -d
echo [OK] All services started
echo.

REM Wait for services
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Health check
echo Running health checks...
curl -f http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [WARNING] API health check failed. Check logs: docker-compose logs api
) else (
    echo [OK] API is healthy
)
echo.

REM Show service URLs
echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Services are running at:
echo   - API:        http://localhost:8000
echo   - Dashboard:  http://localhost:8501
echo   - MLflow:     http://localhost:5000
echo   - Prometheus: http://localhost:9090
echo   - Grafana:    http://localhost:3000
echo.
echo API Documentation:
echo   - Swagger UI: http://localhost:8000/docs
echo   - ReDoc:      http://localhost:8000/redoc
echo.
echo Useful commands:
echo   - View logs:     docker-compose logs -f
echo   - Stop services: docker-compose down
echo   - Restart:       docker-compose restart
echo.
echo Next steps:
echo   1. Open dashboard: http://localhost:8501
echo   2. Make a test prediction (see README.md)
echo.
echo For help, see README.md or QUICK_START.md
echo.
pause
