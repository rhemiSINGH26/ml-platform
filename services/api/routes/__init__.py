"""Routes package."""

from services.api.routes import health, predict, metrics

__all__ = ["health", "predict", "metrics"]
