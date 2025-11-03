"""
Feature engineering for heart disease prediction.
Handles missing values, scaling, and transformations.
"""

import sys
from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.impute import SimpleImputer
import joblib
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from validation.schema_definitions import get_numeric_features, get_categorical_features


class FeatureEngineer:
    """Feature engineering and preprocessing."""
    
    def __init__(self, scaling_method: str = "standard"):
        """
        Initialize feature engineer.
        
        Args:
            scaling_method: Scaling method (standard, minmax, robust, none)
        """
        self.scaling_method = scaling_method
        self.numeric_features = get_numeric_features()
        self.categorical_features = get_categorical_features()
        
        # Initialize transformers
        self.imputer = SimpleImputer(strategy="median")
        
        if scaling_method == "standard":
            self.scaler = StandardScaler()
        elif scaling_method == "minmax":
            self.scaler = MinMaxScaler()
        elif scaling_method == "robust":
            self.scaler = RobustScaler()
        else:
            self.scaler = None
        
        self.is_fitted = False
    
    def fit(self, X: pd.DataFrame) -> "FeatureEngineer":
        """
        Fit transformers on training data.
        
        Args:
            X: Training features
            
        Returns:
            Self
        """
        logger.info("Fitting feature transformers...")
        
        # Fit imputer on all features
        self.imputer.fit(X)
        
        # Fit scaler on numeric features only
        if self.scaler is not None:
            X_imputed = pd.DataFrame(
                self.imputer.transform(X),
                columns=X.columns,
                index=X.index
            )
            self.scaler.fit(X_imputed[self.numeric_features])
        
        self.is_fitted = True
        logger.info("Feature transformers fitted")
        
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform features.
        
        Args:
            X: Features to transform
            
        Returns:
            Transformed features
        """
        if not self.is_fitted:
            raise RuntimeError("FeatureEngineer must be fitted before transform")
        
        # Handle missing values
        X_imputed = pd.DataFrame(
            self.imputer.transform(X),
            columns=X.columns,
            index=X.index
        )
        
        # Scale numeric features
        if self.scaler is not None:
            X_imputed[self.numeric_features] = self.scaler.transform(
                X_imputed[self.numeric_features]
            )
        
        return X_imputed
    
    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Fit and transform in one step.
        
        Args:
            X: Features to fit and transform
            
        Returns:
            Transformed features
        """
        return self.fit(X).transform(X)
    
    def save(self, path: Path):
        """
        Save feature engineer to disk.
        
        Args:
            path: Path to save to
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        logger.info(f"Saved feature engineer to {path}")
    
    @classmethod
    def load(cls, path: Path) -> "FeatureEngineer":
        """
        Load feature engineer from disk.
        
        Args:
            path: Path to load from
            
        Returns:
            Loaded FeatureEngineer
        """
        engineer = joblib.load(path)
        logger.info(f"Loaded feature engineer from {path}")
        return engineer
