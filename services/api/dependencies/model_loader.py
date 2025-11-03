"""
Model loader dependency - singleton pattern for loading ML model.
"""

import sys
from pathlib import Path
import joblib
import yaml
from typing import Any, Dict, Optional
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from config.settings import settings


class ModelLoader:
    """Singleton class for loading and caching the ML model."""
    
    _instance = None
    _model = None
    _preprocessor = None
    _metadata = None
    _model_name = None
    
    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self, model_name: str = None) -> tuple[Any, Any, Dict]:
        """
        Load the model, preprocessor, and metadata.
        
        Args:
            model_name: Name of the model to load (optional, searches for latest)
            
        Returns:
            Tuple of (model, preprocessor, metadata)
        """
        if self._model is not None and self._model_name == model_name:
            logger.info(f"Using cached model: {self._model_name}")
            return self._model, self._preprocessor, self._metadata
        
        # Find model file
        if model_name:
            model_path = settings.production_model_dir / f"{model_name}.joblib"
            metadata_path = settings.production_model_dir / f"{model_name}_metadata.yaml"
        else:
            # Find the latest model
            model_files = list(settings.production_model_dir.glob("*.joblib"))
            if not model_files:
                raise FileNotFoundError(f"No models found in {settings.production_model_dir}")
            
            # Sort by modification time (most recent first)
            model_path = max(model_files, key=lambda p: p.stat().st_mtime)
            model_name = model_path.stem
            metadata_path = settings.production_model_dir / f"{model_name}_metadata.yaml"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        logger.info(f"Loading model from {model_path}")
        
        # Load model
        self._model = joblib.load(model_path)
        self._model_name = model_name
        
        # Load preprocessor
        preprocessor_path = settings.models_dir / "preprocessor.joblib"
        if preprocessor_path.exists():
            logger.info(f"Loading preprocessor from {preprocessor_path}")
            self._preprocessor = joblib.load(preprocessor_path)
        else:
            logger.warning(f"Preprocessor not found at {preprocessor_path}")
            self._preprocessor = None
        
        # Load metadata
        if metadata_path.exists():
            logger.info(f"Loading metadata from {metadata_path}")
            with open(metadata_path, "r") as f:
                self._metadata = yaml.safe_load(f)
        else:
            logger.warning(f"Metadata not found at {metadata_path}")
            self._metadata = {"model_name": model_name}
        
        logger.info(f"Model loaded successfully: {self._model_name}")
        
        return self._model, self._preprocessor, self._metadata
    
    def get_model(self) -> Any:
        """Get the loaded model."""
        if self._model is None:
            self.load_model()
        return self._model
    
    def get_preprocessor(self) -> Any:
        """Get the loaded preprocessor."""
        if self._preprocessor is None:
            self.load_model()
        return self._preprocessor
    
    def get_metadata(self) -> Dict:
        """Get the model metadata."""
        if self._metadata is None:
            self.load_model()
        return self._metadata
    
    def get_model_name(self) -> str:
        """Get the name of the loaded model."""
        if self._model_name is None:
            self.load_model()
        return self._model_name
    
    def reload_model(self, model_name: str = None):
        """
        Reload the model (for hot-swapping).
        
        Args:
            model_name: Name of the model to load
        """
        logger.info("Reloading model...")
        self._model = None
        self._preprocessor = None
        self._metadata = None
        self._model_name = None
        return self.load_model(model_name)


# Global instance
model_loader = ModelLoader()


def get_model_loader() -> ModelLoader:
    """Dependency injection for model loader."""
    return model_loader
