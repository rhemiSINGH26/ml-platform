"""
Data validation using Great Expectations.
Validates data quality, schema, and statistical properties.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.schema_definitions import (
    HEART_DISEASE_SCHEMA,
    EXPECTED_COLUMNS,
    VALIDATION_RULES,
    FeatureType
)


class DataValidator:
    """Validates data quality and schema compliance."""
    
    def __init__(self, schema: Dict[str, Any] = None):
        """
        Initialize validator.
        
        Args:
            schema: Schema definition (defaults to HEART_DISEASE_SCHEMA)
        """
        self.schema = schema or HEART_DISEASE_SCHEMA
        self.validation_results: List[Dict[str, Any]] = []
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """
        Validate DataFrame schema.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if schema is valid
        """
        logger.info("Validating schema...")
        is_valid = True
        
        # Check columns
        expected_cols = set(EXPECTED_COLUMNS)
        actual_cols = set(df.columns)
        
        missing_cols = expected_cols - actual_cols
        extra_cols = actual_cols - expected_cols
        
        if missing_cols:
            self._add_result("schema", False, f"Missing columns: {missing_cols}")
            is_valid = False
        
        if extra_cols:
            self._add_result("schema", False, f"Extra columns: {extra_cols}")
            is_valid = False
        
        if is_valid:
            self._add_result("schema", True, "All expected columns present")
        
        return is_valid
    
    def validate_data_types(self, df: pd.DataFrame) -> bool:
        """
        Validate data types.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if data types are valid
        """
        logger.info("Validating data types...")
        is_valid = True
        
        for col, props in self.schema.items():
            if col not in df.columns:
                continue
            
            expected_dtype = props["dtype"]
            actual_dtype = str(df[col].dtype)
            
            # Allow compatible types
            compatible = (
                (expected_dtype == "int64" and actual_dtype in ["int32", "int64"]) or
                (expected_dtype == "float64" and actual_dtype in ["float32", "float64"]) or
                expected_dtype == actual_dtype
            )
            
            if not compatible:
                self._add_result(
                    "data_types",
                    False,
                    f"Column '{col}': expected {expected_dtype}, got {actual_dtype}"
                )
                is_valid = False
        
        if is_valid:
            self._add_result("data_types", True, "All data types valid")
        
        return is_valid
    
    def validate_ranges(self, df: pd.DataFrame) -> bool:
        """
        Validate numeric ranges.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if ranges are valid
        """
        logger.info("Validating numeric ranges...")
        is_valid = True
        
        for col, props in self.schema.items():
            if col not in df.columns:
                continue
            
            if props["type"] != FeatureType.NUMERIC:
                continue
            
            # Get non-null values
            values = df[col].dropna()
            
            if len(values) == 0:
                continue
            
            min_val = values.min()
            max_val = values.max()
            expected_min = props.get("min")
            expected_max = props.get("max")
            
            if expected_min is not None and min_val < expected_min:
                self._add_result(
                    "ranges",
                    False,
                    f"Column '{col}': min {min_val} < expected {expected_min}"
                )
                is_valid = False
            
            if expected_max is not None and max_val > expected_max:
                self._add_result(
                    "ranges",
                    False,
                    f"Column '{col}': max {max_val} > expected {expected_max}"
                )
                is_valid = False
        
        if is_valid:
            self._add_result("ranges", True, "All numeric ranges valid")
        
        return is_valid
    
    def validate_categorical_values(self, df: pd.DataFrame) -> bool:
        """
        Validate categorical values.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if categorical values are valid
        """
        logger.info("Validating categorical values...")
        is_valid = True
        
        for col, props in self.schema.items():
            if col not in df.columns:
                continue
            
            if "allowed_values" not in props:
                continue
            
            allowed = set(props["allowed_values"])
            actual = set(df[col].dropna().unique())
            
            invalid = actual - allowed
            
            if invalid:
                self._add_result(
                    "categorical",
                    False,
                    f"Column '{col}': invalid values {invalid}"
                )
                is_valid = False
        
        if is_valid:
            self._add_result("categorical", True, "All categorical values valid")
        
        return is_valid
    
    def validate_missing_values(self, df: pd.DataFrame) -> bool:
        """
        Validate missing values.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if missing values are acceptable
        """
        logger.info("Validating missing values...")
        is_valid = True
        max_missing_pct = VALIDATION_RULES["max_missing_percentage"]
        
        for col, props in self.schema.items():
            if col not in df.columns:
                continue
            
            missing_count = df[col].isnull().sum()
            missing_pct = missing_count / len(df)
            
            # Check if column allows nulls
            if not props.get("nullable", False) and missing_count > 0:
                self._add_result(
                    "missing_values",
                    False,
                    f"Column '{col}': has {missing_count} nulls but nulls not allowed"
                )
                is_valid = False
            
            # Check if missing percentage exceeds threshold
            if missing_pct > max_missing_pct:
                self._add_result(
                    "missing_values",
                    False,
                    f"Column '{col}': {missing_pct:.1%} missing (max allowed: {max_missing_pct:.1%})"
                )
                is_valid = False
        
        if is_valid:
            self._add_result("missing_values", True, "Missing values within acceptable limits")
        
        return is_valid
    
    def validate_sample_size(self, df: pd.DataFrame) -> bool:
        """
        Validate sample size.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if sample size is sufficient
        """
        logger.info("Validating sample size...")
        min_samples = VALIDATION_RULES["min_samples"]
        n_samples = len(df)
        
        if n_samples < min_samples:
            self._add_result(
                "sample_size",
                False,
                f"Only {n_samples} samples (minimum: {min_samples})"
            )
            return False
        
        self._add_result(
            "sample_size",
            True,
            f"{n_samples} samples (minimum: {min_samples})"
        )
        return True
    
    def validate_class_balance(self, df: pd.DataFrame, target_col: str = "target") -> bool:
        """
        Validate class balance.
        
        Args:
            df: DataFrame to validate
            target_col: Target column name
            
        Returns:
            True if class balance is acceptable
        """
        logger.info("Validating class balance...")
        
        if target_col not in df.columns:
            self._add_result("class_balance", False, f"Target column '{target_col}' not found")
            return False
        
        class_counts = df[target_col].value_counts()
        class_ratio = class_counts.min() / class_counts.sum()
        
        min_ratio = VALIDATION_RULES["min_class_ratio"]
        max_ratio = VALIDATION_RULES["max_class_ratio"]
        
        if class_ratio < min_ratio:
            self._add_result(
                "class_balance",
                False,
                f"Class imbalance: minority class is {class_ratio:.1%} (min: {min_ratio:.1%})"
            )
            return False
        
        self._add_result(
            "class_balance",
            True,
            f"Class balance acceptable: minority class is {class_ratio:.1%}"
        )
        return True
    
    def validate_all(self, df: pd.DataFrame) -> bool:
        """
        Run all validations.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if all validations pass
        """
        logger.info(f"Starting validation for DataFrame with shape {df.shape}")
        self.validation_results = []
        
        validations = [
            self.validate_schema(df),
            self.validate_data_types(df),
            self.validate_ranges(df),
            self.validate_categorical_values(df),
            self.validate_missing_values(df),
            self.validate_sample_size(df),
            self.validate_class_balance(df),
        ]
        
        all_valid = all(validations)
        
        # Log summary
        self._log_summary()
        
        return all_valid
    
    def _add_result(self, category: str, passed: bool, message: str):
        """Add validation result."""
        self.validation_results.append({
            "category": category,
            "passed": passed,
            "message": message
        })
        
        if passed:
            logger.info(f"✓ {category}: {message}")
        else:
            logger.warning(f"✗ {category}: {message}")
    
    def _log_summary(self):
        """Log validation summary."""
        total = len(self.validation_results)
        passed = sum(1 for r in self.validation_results if r["passed"])
        failed = total - passed
        
        logger.info("=" * 60)
        logger.info(f"Validation Summary: {passed}/{total} checks passed")
        
        if failed > 0:
            logger.warning(f"{failed} validation(s) failed:")
            for result in self.validation_results:
                if not result["passed"]:
                    logger.warning(f"  - {result['category']}: {result['message']}")
        else:
            logger.info("All validations passed! ✓")
        
        logger.info("=" * 60)
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get validation results."""
        return self.validation_results


def validate_dataset(file_path: Path) -> bool:
    """
    Validate a dataset file.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        True if validation passes
    """
    try:
        df = pd.read_csv(file_path)
        validator = DataValidator()
        return validator.validate_all(df)
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate heart disease dataset")
    parser.add_argument("file", type=str, help="Path to CSV file")
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    success = validate_dataset(file_path)
    sys.exit(0 if success else 1)
