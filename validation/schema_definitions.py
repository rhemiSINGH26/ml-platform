"""
Schema definitions for the heart disease dataset.
Defines expected data types, ranges, and validation rules.
"""

from typing import Dict, List, Any
from enum import Enum


class FeatureType(Enum):
    """Feature types for validation."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BINARY = "binary"


# Schema definition for heart disease dataset
HEART_DISEASE_SCHEMA: Dict[str, Any] = {
    "age": {
        "type": FeatureType.NUMERIC,
        "dtype": "int64",
        "min": 0,
        "max": 120,
        "nullable": False,
        "description": "Age in years"
    },
    "sex": {
        "type": FeatureType.BINARY,
        "dtype": "int64",
        "allowed_values": [0, 1],
        "nullable": False,
        "description": "Sex (1 = male; 0 = female)"
    },
    "cp": {
        "type": FeatureType.CATEGORICAL,
        "dtype": "int64",
        "allowed_values": [0, 1, 2, 3],
        "nullable": False,
        "description": "Chest pain type"
    },
    "trestbps": {
        "type": FeatureType.NUMERIC,
        "dtype": "int64",
        "min": 80,
        "max": 220,
        "nullable": False,
        "description": "Resting blood pressure (mm Hg)"
    },
    "chol": {
        "type": FeatureType.NUMERIC,
        "dtype": "int64",
        "min": 100,
        "max": 600,
        "nullable": False,
        "description": "Serum cholesterol (mg/dl)"
    },
    "fbs": {
        "type": FeatureType.BINARY,
        "dtype": "int64",
        "allowed_values": [0, 1],
        "nullable": False,
        "description": "Fasting blood sugar > 120 mg/dl"
    },
    "restecg": {
        "type": FeatureType.CATEGORICAL,
        "dtype": "int64",
        "allowed_values": [0, 1, 2],
        "nullable": False,
        "description": "Resting electrocardiographic results"
    },
    "thalach": {
        "type": FeatureType.NUMERIC,
        "dtype": "int64",
        "min": 60,
        "max": 220,
        "nullable": False,
        "description": "Maximum heart rate achieved"
    },
    "exang": {
        "type": FeatureType.BINARY,
        "dtype": "int64",
        "allowed_values": [0, 1],
        "nullable": False,
        "description": "Exercise induced angina"
    },
    "oldpeak": {
        "type": FeatureType.NUMERIC,
        "dtype": "float64",
        "min": 0,
        "max": 10,
        "nullable": False,
        "description": "ST depression induced by exercise"
    },
    "slope": {
        "type": FeatureType.CATEGORICAL,
        "dtype": "int64",
        "allowed_values": [0, 1, 2],
        "nullable": False,
        "description": "Slope of the peak exercise ST segment"
    },
    "ca": {
        "type": FeatureType.CATEGORICAL,
        "dtype": "float64",  # Can be float due to missing values
        "allowed_values": [0.0, 1.0, 2.0, 3.0],
        "nullable": True,  # This field can have missing values
        "description": "Number of major vessels colored by fluoroscopy"
    },
    "thal": {
        "type": FeatureType.CATEGORICAL,
        "dtype": "float64",  # Can be float due to missing values
        "allowed_values": [1.0, 2.0, 3.0],
        "nullable": True,  # This field can have missing values
        "description": "Thalassemia"
    },
    "target": {
        "type": FeatureType.BINARY,
        "dtype": "int64",
        "allowed_values": [0, 1],
        "nullable": False,
        "description": "Diagnosis of heart disease (0 = no, 1 = yes)"
    }
}


# Expected column order
EXPECTED_COLUMNS: List[str] = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"
]


# Feature columns (excluding target)
FEATURE_COLUMNS: List[str] = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]


# Target column
TARGET_COLUMN: str = "target"


# Numeric features
NUMERIC_FEATURES: List[str] = [
    col for col, props in HEART_DISEASE_SCHEMA.items()
    if props["type"] == FeatureType.NUMERIC and col != TARGET_COLUMN
]


# Categorical features
CATEGORICAL_FEATURES: List[str] = [
    col for col, props in HEART_DISEASE_SCHEMA.items()
    if props["type"] in [FeatureType.CATEGORICAL, FeatureType.BINARY]
    and col != TARGET_COLUMN
]


# Validation rules
VALIDATION_RULES: Dict[str, Any] = {
    "max_missing_percentage": 0.05,  # Max 5% missing values allowed
    "min_samples": 100,  # Minimum number of samples required
    "min_class_ratio": 0.1,  # Minimum ratio for minority class
    "max_class_ratio": 0.9,  # Maximum ratio for majority class
}


def get_feature_names() -> List[str]:
    """Get list of feature names (excluding target)."""
    return FEATURE_COLUMNS


def get_target_name() -> str:
    """Get target column name."""
    return TARGET_COLUMN


def get_all_columns() -> List[str]:
    """Get all column names."""
    return EXPECTED_COLUMNS


def get_numeric_features() -> List[str]:
    """Get list of numeric feature names."""
    return NUMERIC_FEATURES


def get_categorical_features() -> List[str]:
    """Get list of categorical feature names."""
    return CATEGORICAL_FEATURES


def get_schema() -> Dict[str, Any]:
    """Get the complete schema definition."""
    return HEART_DISEASE_SCHEMA


def get_validation_rules() -> Dict[str, Any]:
    """Get validation rules."""
    return VALIDATION_RULES
