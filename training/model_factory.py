"""
Model factory - creates and configures ML models.
"""

import sys
from pathlib import Path
from typing import Any, Dict
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


class ModelFactory:
    """Factory for creating ML models."""
    
    def __init__(self, config_path: Path = None):
        """
        Initialize model factory.
        
        Args:
            config_path: Path to model config YAML
        """
        self.config_path = config_path or (settings.base_dir / "config" / "model_config.yml")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from YAML."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
        return config
    
    def create_logistic_regression(self) -> LogisticRegression:
        """Create Logistic Regression model."""
        params = self.config["models"]["logistic_regression"]["hyperparameters"]
        return LogisticRegression(**params)
    
    def create_random_forest(self) -> RandomForestClassifier:
        """Create Random Forest model."""
        params = self.config["models"]["random_forest"]["hyperparameters"]
        return RandomForestClassifier(**params)
    
    def create_xgboost(self) -> XGBClassifier:
        """Create XGBoost model."""
        params = self.config["models"]["xgboost"]["hyperparameters"]
        return XGBClassifier(**params)
    
    def create_lightgbm(self) -> LGBMClassifier:
        """Create LightGBM model."""
        params = self.config["models"]["lightgbm"]["hyperparameters"]
        return LGBMClassifier(**params)
    
    def create_all_models(self) -> Dict[str, Any]:
        """
        Create all enabled models.
        
        Returns:
            Dictionary of model_name -> model_instance
        """
        models = {}
        
        for model_name, model_config in self.config["models"].items():
            if not model_config.get("enabled", True):
                logger.info(f"Skipping disabled model: {model_name}")
                continue
            
            logger.info(f"Creating model: {model_name}")
            
            if model_name == "logistic_regression":
                models[model_name] = self.create_logistic_regression()
            elif model_name == "random_forest":
                models[model_name] = self.create_random_forest()
            elif model_name == "xgboost":
                models[model_name] = self.create_xgboost()
            elif model_name == "lightgbm":
                models[model_name] = self.create_lightgbm()
            else:
                logger.warning(f"Unknown model type: {model_name}")
        
        logger.info(f"Created {len(models)} models")
        return models
    
    def get_model_description(self, model_name: str) -> str:
        """Get model description."""
        return self.config["models"][model_name].get("description", "")
    
    def get_selection_metric(self) -> str:
        """Get metric for model selection."""
        return self.config["selection"]["primary_metric"]
    
    def get_minimum_threshold(self) -> float:
        """Get minimum threshold for model selection."""
        return self.config["selection"]["minimum_threshold"]
