"""
Metrics routes for Prometheus.
"""

from fastapi import APIRouter
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response


router = APIRouter(prefix="/metrics", tags=["metrics"])

# Define Prometheus metrics
prediction_counter = Counter(
    "predictions_total",
    "Total number of predictions",
    ["model_name", "status"]
)

prediction_duration = Histogram(
    "prediction_duration_seconds",
    "Time spent making predictions",
    ["model_name"]
)

model_info = Gauge(
    "model_info",
    "Information about the loaded model",
    ["model_name", "version"]
)


@router.get("")
async def metrics():
    """
    Expose Prometheus metrics.
    
    Returns metrics in Prometheus format.
    """
    return Response(
        content=generate_latest(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )
