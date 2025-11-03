"""
Health check routes.
"""

import time
from fastapi import APIRouter, Depends
from services.api.models.response import HealthResponse
from services.api.dependencies import get_model_loader

router = APIRouter(tags=["health"])

# Track service start time
SERVICE_START_TIME = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check(loader = Depends(get_model_loader)):
    """
    Health check endpoint.
    
    Returns service health status and model loading status.
    """
    try:
        model_name = loader.get_model_name()
        model_loaded = loader._model is not None
    except Exception:
        model_name = None
        model_loaded = False
    
    uptime = time.time() - SERVICE_START_TIME
    
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        model_name=model_name,
        uptime_seconds=uptime
    )


@router.get("/ready")
async def readiness_check(loader = Depends(get_model_loader)):
    """
    Readiness check endpoint (for Kubernetes).
    
    Returns 200 if service is ready to accept traffic.
    """
    try:
        loader.get_model()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}, 503


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint (for Kubernetes).
    
    Returns 200 if service is alive.
    """
    return {"status": "alive"}
