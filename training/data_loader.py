"""
Data loader for ML training pipeline.
Handles loading, splitting, and preprocessing of data.
"""

import sys
from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from validation.schema_definitions import get_feature_names, get_target_name


class DataLoader:
    """Load and split data for training."""
    
    def __init__(self, data_path: Path = None, random_seed: int = None):
        """
        Initialize data loader.
        
        Args:
            data_path: Path to dataset CSV file
            random_seed: Random seed for reproducibility
        """
        self.data_path = data_path or (settings.data_dir / "raw" / "heart_disease.csv")
        self.random_seed = random_seed or settings.random_seed
        self.feature_names = get_feature_names()
        self.target_name = get_target_name()
    
    def load_data(self) -> pd.DataFrame:
        """
        Load dataset from file.
        
        Returns:
            DataFrame with loaded data
        """
        logger.info(f"Loading data from {self.data_path}")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")
        
        df = pd.read_csv(self.data_path)
        logger.info(f"Loaded {len(df)} samples with {len(df.columns)} columns")
        
        return df
    
    def split_data(
        self,
        df: pd.DataFrame,
        test_size: float = None,
        val_size: float = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            df: DataFrame to split
            test_size: Test set size (default from settings)
            val_size: Validation set size (default from settings)
            
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        test_size = test_size or settings.test_size
        val_size = val_size or settings.val_size
        
        # First split: separate test set
        train_val_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=self.random_seed,
            stratify=df[self.target_name]
        )
        
        # Second split: separate validation from training
        # Adjust val_size to account for already removed test set
        adjusted_val_size = val_size / (1 - test_size)
        
        train_df, val_df = train_test_split(
            train_val_df,
            test_size=adjusted_val_size,
            random_state=self.random_seed,
            stratify=train_val_df[self.target_name]
        )
        
        logger.info(f"Data split: train={len(train_df)}, val={len(val_df)}, test={len(test_df)}")
        logger.info(f"Train class distribution:\n{train_df[self.target_name].value_counts()}")
        
        return train_df, val_df, test_df
    
    def prepare_features_target(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Separate features and target.
        
        Args:
            df: DataFrame with features and target
            
        Returns:
            Tuple of (X, y)
        """
        X = df[self.feature_names].copy()
        y = df[self.target_name].copy()
        
        return X, y
    
    def load_and_split(
        self
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load data and split into train/val/test sets.
        
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        # Load data
        df = self.load_data()
        
        # Split into train/val/test
        train_df, val_df, test_df = self.split_data(df)
        
        # Save processed data
        self._save_processed_data(train_df, val_df, test_df)
        
        return train_df, val_df, test_df
    
    def _save_processed_data(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame
    ):
        """Save processed data splits."""
        processed_dir = settings.data_dir / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        train_df.to_csv(processed_dir / "train.csv", index=False)
        val_df.to_csv(processed_dir / "val.csv", index=False)
        test_df.to_csv(processed_dir / "test.csv", index=False)
        
        logger.info(f"Saved processed data to {processed_dir}")
