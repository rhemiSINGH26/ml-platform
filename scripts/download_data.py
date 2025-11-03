"""
Download and prepare the UCI Heart Disease dataset.
This script automatically downloads the dataset and saves it to the data/raw directory.
"""

import sys
from pathlib import Path
import pandas as pd
import requests
from typing import Optional
from loguru import logger

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


# Column names for the UCI Heart Disease dataset
COLUMN_NAMES = [
    "age",          # Age in years
    "sex",          # Sex (1 = male; 0 = female)
    "cp",           # Chest pain type (0-3)
    "trestbps",     # Resting blood pressure (mm Hg)
    "chol",         # Serum cholesterol (mg/dl)
    "fbs",          # Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)
    "restecg",      # Resting electrocardiographic results (0-2)
    "thalach",      # Maximum heart rate achieved
    "exang",        # Exercise induced angina (1 = yes; 0 = no)
    "oldpeak",      # ST depression induced by exercise
    "slope",        # Slope of the peak exercise ST segment (0-2)
    "ca",           # Number of major vessels colored by fluoroscopy (0-3)
    "thal",         # Thalassemia (1 = normal; 2 = fixed defect; 3 = reversible defect)
    "target",       # Diagnosis of heart disease (0 = no disease, 1-4 = disease)
]


def download_dataset(url: str, output_path: Path, force: bool = False) -> bool:
    """
    Download dataset from URL.
    
    Args:
        url: URL to download from
        output_path: Path to save the downloaded file
        force: If True, re-download even if file exists
        
    Returns:
        True if downloaded successfully, False otherwise
    """
    if output_path.exists() and not force:
        logger.info(f"Dataset already exists at {output_path}, skipping download")
        return True
    
    try:
        logger.info(f"Downloading dataset from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the file
        output_path.write_bytes(response.content)
        logger.info(f"Dataset downloaded successfully to {output_path}")
        return True
        
    except requests.RequestException as e:
        logger.error(f"Failed to download dataset: {e}")
        return False


def load_and_prepare_data(file_path: Path) -> Optional[pd.DataFrame]:
    """
    Load and prepare the heart disease dataset.
    
    Args:
        file_path: Path to the downloaded dataset
        
    Returns:
        Prepared DataFrame or None if loading fails
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, names=COLUMN_NAMES, na_values="?")
        
        logger.info(f"Loaded dataset with shape: {df.shape}")
        logger.info(f"Missing values:\n{df.isnull().sum()}")
        
        # Convert target to binary (0 = no disease, 1 = disease)
        df['target'] = (df['target'] > 0).astype(int)
        
        # Display class distribution
        class_distribution = df['target'].value_counts()
        logger.info(f"Class distribution:\n{class_distribution}")
        logger.info(f"Class balance: {class_distribution[1] / len(df):.2%} positive cases")
        
        # Basic statistics
        logger.info(f"Dataset statistics:\n{df.describe()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        return None


def save_dataset(df: pd.DataFrame, output_path: Path) -> bool:
    """
    Save the prepared dataset.
    
    Args:
        df: DataFrame to save
        output_path: Path to save to
        
    Returns:
        True if saved successfully
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Dataset saved to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save dataset: {e}")
        return False


def main(force_download: bool = False):
    """
    Main function to download and prepare the dataset.
    
    Args:
        force_download: If True, re-download even if file exists
    """
    logger.info("Starting dataset download and preparation")
    
    # Define paths
    raw_data_path = settings.data_dir / "raw" / "heart_disease.csv"
    temp_download_path = settings.data_dir / "raw" / "heart_disease_raw.data"
    
    # Download the dataset
    success = download_dataset(
        settings.dataset_url,
        temp_download_path,
        force=force_download
    )
    
    if not success:
        logger.error("Dataset download failed")
        return False
    
    # Load and prepare the data
    df = load_and_prepare_data(temp_download_path)
    
    if df is None:
        logger.error("Data loading failed")
        return False
    
    # Save the prepared dataset
    success = save_dataset(df, raw_data_path)
    
    if success:
        logger.info("Dataset preparation completed successfully")
        logger.info(f"Dataset saved to: {raw_data_path}")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Features: {list(df.columns)}")
        
        # Clean up temporary file
        if temp_download_path.exists():
            temp_download_path.unlink()
            
        return True
    else:
        logger.error("Dataset preparation failed")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download UCI Heart Disease dataset")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if file exists"
    )
    
    args = parser.parse_args()
    
    success = main(force_download=args.force)
    sys.exit(0 if success else 1)
