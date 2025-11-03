"""
FastAPI application entry point.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.logging_config import setup_logging
from services.api.middleware import LoggingMiddleware, setup_cors
from services.api.routes import health, predict, metrics
from services.api.dependencies import model_loader


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    Args:
        app: FastAPI application
    """
    # Startup
    logger.info("Starting up MLOps API service...")
    
    # Setup logging
    setup_logging()
    
    # Load model on startup
    try:
        model_loader.load_model()
        logger.info("Model loaded successfully on startup")
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")
        logger.warning("Service will start but predictions will fail until model is loaded")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MLOps API service...")


# Create FastAPI app
app = FastAPI(
    title="MLOps Heart Disease Prediction API",
    description="Production-ready API for heart disease prediction with monitoring and drift detection",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Setup middleware
app.add_middleware(LoggingMiddleware)
setup_cors(app)

# Register routes
app.include_router(health.router)
app.include_router(predict.router)
app.include_router(metrics.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An internal server error occurred",
            "detail": str(exc) if app.debug else None
        }
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MLOps Heart Disease Prediction API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "services.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None  # Use our custom logging
    )
