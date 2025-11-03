"""
Pydantic models for API responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class PredictionResponse(BaseModel):
    """Response schema for single prediction."""
    
    prediction: int = Field(..., description="Predicted class (0=no disease, 1=disease)")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability of disease")
    model_name: str = Field(..., description="Name of the model used")
    model_version: str = Field(..., description="Version of the model")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Prediction timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction": 1,
                "probability": 0.85,
                "model_name": "random_forest",
                "model_version": "v1.0.0",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class BatchPredictionResponse(BaseModel):
    """Response schema for batch prediction."""
    
    predictions: list[PredictionResponse] = Field(..., description="List of predictions")
    total: int = Field(..., description="Total number of predictions")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Batch timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "predictions": [
                    {
                        "prediction": 1,
                        "probability": 0.85,
                        "model_name": "random_forest",
                        "model_version": "v1.0.0",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 1,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class HealthResponse(BaseModel):
    """Response schema for health check."""
    
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_name: Optional[str] = Field(None, description="Loaded model name")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "model_name": "random_forest",
                "uptime_seconds": 3600.5,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class MetricsResponse(BaseModel):
    """Response schema for Prometheus metrics."""
    
    metrics: Dict[str, Any] = Field(..., description="Collected metrics")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metrics": {
                    "predictions_total": 1000,
                    "predictions_success": 995,
                    "predictions_error": 5,
                    "avg_inference_time_ms": 15.3,
                    "model_name": "random_forest"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "detail": "Age must be between 1 and 120",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
