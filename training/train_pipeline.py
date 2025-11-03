"""
Main training pipeline - orchestrates the entire training process with MLflow.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import cross_val_score
from loguru import logger
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings
from training.data_loader import DataLoader
from training.feature_engineering import FeatureEngineer
from training.model_factory import ModelFactory
from training.model_evaluator import ModelEvaluator
from training.model_selector import ModelSelector


class TrainingPipeline:
    """Complete training pipeline with MLflow integration."""
    
    def __init__(
        self,
        experiment_name: str = None,
        run_name: str = None
    ):
        """
        Initialize training pipeline.
        
        Args:
            experiment_name: MLflow experiment name (default: from settings)
            run_name: MLflow run name (optional)
        """
        self.experiment_name = experiment_name or settings.mlflow_experiment_name
        self.run_name = run_name
        
        # Initialize components
        self.data_loader = DataLoader()
        self.feature_engineer = FeatureEngineer()
        self.model_factory = ModelFactory()
        self.evaluator = ModelEvaluator()
        self.selector = ModelSelector()
        
        # Data holders
        self.train_data = None
        self.val_data = None
        self.test_data = None
        self.X_train = None
        self.y_train = None
        self.X_val = None
        self.y_val = None
        self.X_test = None
        self.y_test = None
        self.feature_names = None
        
        # Setup MLflow
        self._setup_mlflow()
    
    def _setup_mlflow(self):
        """Setup MLflow tracking."""
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(self.experiment_name)
        logger.info(f"MLflow experiment: {self.experiment_name}")
        logger.info(f"MLflow tracking URI: {settings.mlflow_tracking_uri}")
    
    def load_data(self):
        """Load and split data."""
        logger.info("Loading and splitting data...")
        
        self.train_data, self.val_data, self.test_data = self.data_loader.load_and_split()
        
        # Prepare features and target
        self.X_train, self.y_train = self.data_loader.prepare_features_target(self.train_data)
        self.X_val, self.y_val = self.data_loader.prepare_features_target(self.val_data)
        self.X_test, self.y_test = self.data_loader.prepare_features_target(self.test_data)
        
        self.feature_names = list(self.X_train.columns)
        
        logger.info(f"Training samples: {len(self.X_train)}")
        logger.info(f"Validation samples: {len(self.X_val)}")
        logger.info(f"Test samples: {len(self.X_test)}")
        logger.info(f"Features: {len(self.feature_names)}")
    
    def preprocess_data(self):
        """Preprocess features."""
        logger.info("Preprocessing features...")
        
        # Fit on training data
        self.X_train = self.feature_engineer.fit_transform(self.X_train)
        
        # Transform validation and test data
        self.X_val = self.feature_engineer.transform(self.X_val)
        self.X_test = self.feature_engineer.transform(self.X_test)
        
        # Save preprocessor
        preprocessor_path = settings.models_dir / "preprocessor.joblib"
        self.feature_engineer.save(preprocessor_path)
        logger.info(f"Saved preprocessor to {preprocessor_path}")
    
    def train_model(
        self,
        model_name: str,
        model: Any,
        use_cross_validation: bool = True
    ) -> Dict[str, float]:
        """
        Train a single model and log to MLflow.
        
        Args:
            model_name: Name of the model
            model: Model instance
            use_cross_validation: Whether to perform cross-validation
            
        Returns:
            Dictionary of evaluation metrics
        """
        with mlflow.start_run(run_name=f"{self.run_name}_{model_name}" if self.run_name else model_name, nested=True):
            logger.info(f"Training {model_name}...")
            
            # Log parameters
            if hasattr(model, "get_params"):
                params = model.get_params()
                mlflow.log_params({f"{model_name}_{k}": v for k, v in params.items()})
            
            # Cross-validation on training data
            if use_cross_validation:
                logger.info("Performing cross-validation...")
                cv_scores = cross_val_score(
                    model,
                    self.X_train,
                    self.y_train,
                    cv=5,
                    scoring=settings.model_selection_metric,
                    n_jobs=-1
                )
                cv_mean = cv_scores.mean()
                cv_std = cv_scores.std()
                logger.info(f"CV {settings.model_selection_metric}: {cv_mean:.4f} (+/- {cv_std:.4f})")
                mlflow.log_metric("cv_score_mean", cv_mean)
                mlflow.log_metric("cv_score_std", cv_std)
            
            # Train on full training set
            model.fit(self.X_train, self.y_train)
            
            # Evaluate on validation set
            y_val_pred = model.predict(self.X_val)
            y_val_proba = None
            if hasattr(model, "predict_proba"):
                y_val_proba = model.predict_proba(self.X_val)[:, 1]
            
            metrics = self.evaluator.evaluate(self.y_val, y_val_pred, y_val_proba)
            
            # Log metrics
            for metric_name, value in metrics.items():
                mlflow.log_metric(f"val_{metric_name}", value)
            
            # Generate and log plots
            plots_dir = settings.reports_dir / "plots" / model_name
            plot_paths = self.evaluator.generate_all_plots(
                model,
                self.y_val,
                y_val_pred,
                y_val_proba,
                self.feature_names,
                plots_dir
            )
            
            # Log plots as artifacts
            for plot_name, plot_path in plot_paths.items():
                mlflow.log_artifact(str(plot_path))
            
            # Log model
            mlflow.sklearn.log_model(model, f"model_{model_name}")
            
            logger.info(f"Completed training {model_name}")
            self.evaluator.print_metrics()
            
            return metrics
    
    def train_all_models(self) -> Dict[str, Dict[str, float]]:
        """
        Train all enabled models.
        
        Returns:
            Dictionary mapping model names to their metrics
        """
        logger.info("Training all models...")
        
        models = self.model_factory.create_all_models()
        all_metrics = {}
        
        with mlflow.start_run(run_name=self.run_name):
            # Log dataset info
            mlflow.log_param("train_samples", len(self.X_train))
            mlflow.log_param("val_samples", len(self.X_val))
            mlflow.log_param("test_samples", len(self.X_test))
            mlflow.log_param("n_features", len(self.feature_names))
            mlflow.log_param("selection_metric", settings.model_selection_metric)
            
            for model_name, model in models.items():
                metrics = self.train_model(model_name, model)
                all_metrics[model_name] = metrics
                
                # Add to selector
                self.selector.add_model_result(model_name, model, metrics)
        
        return all_metrics
    
    def select_best_model(self) -> tuple:
        """
        Select the best model.
        
        Returns:
            Tuple of (model_name, model, metrics)
        """
        logger.info("Selecting best model...")
        
        best_name, best_model, best_metrics = self.selector.select_best_model()
        
        # Print comparison
        self.selector.print_comparison()
        
        # Save comparison
        comparison_path = settings.reports_dir / "model_comparison.csv"
        self.selector.save_comparison(comparison_path)
        
        return best_name, best_model, best_metrics
    
    def evaluate_on_test_set(
        self,
        model_name: str,
        model: Any
    ) -> Dict[str, float]:
        """
        Evaluate the best model on test set.
        
        Args:
            model_name: Name of the model
            model: Trained model
            
        Returns:
            Test set metrics
        """
        logger.info(f"Evaluating {model_name} on test set...")
        
        with mlflow.start_run(run_name=f"{self.run_name}_test_evaluation" if self.run_name else "test_evaluation"):
            # Predict
            y_test_pred = model.predict(self.X_test)
            y_test_proba = None
            if hasattr(model, "predict_proba"):
                y_test_proba = model.predict_proba(self.X_test)[:, 1]
            
            # Evaluate
            test_metrics = self.evaluator.evaluate(self.y_test, y_test_pred, y_test_proba)
            
            # Log metrics
            for metric_name, value in test_metrics.items():
                mlflow.log_metric(f"test_{metric_name}", value)
            
            # Generate plots
            test_plots_dir = settings.reports_dir / "plots" / f"{model_name}_test"
            plot_paths = self.evaluator.generate_all_plots(
                model,
                self.y_test,
                y_test_pred,
                y_test_proba,
                self.feature_names,
                test_plots_dir
            )
            
            # Log plots
            for plot_name, plot_path in plot_paths.items():
                mlflow.log_artifact(str(plot_path))
            
            logger.info("Test set evaluation:")
            self.evaluator.print_metrics()
            
            return test_metrics
    
    def save_best_model(
        self,
        model_name: str,
        model: Any,
        metrics: Dict[str, float]
    ):
        """
        Save the best model to production.
        
        Args:
            model_name: Name of the model
            model: Trained model
            metrics: Model metrics
        """
        logger.info(f"Saving best model '{model_name}' to production...")
        
        # Save model
        import joblib
        model_path = settings.production_model_dir / f"{model_name}.joblib"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, model_path)
        logger.info(f"Saved model to {model_path}")
        
        # Save metadata
        metadata = {
            "model_name": model_name,
            "metrics": metrics,
            "feature_names": self.feature_names,
            "training_samples": len(self.X_train),
            "selection_metric": settings.model_selection_metric
        }
        
        metadata_path = settings.production_model_dir / f"{model_name}_metadata.yaml"
        with open(metadata_path, "w") as f:
            yaml.dump(metadata, f, default_flow_style=False)
        logger.info(f"Saved metadata to {metadata_path}")
        
        # Register in MLflow Model Registry
        try:
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model_{model_name}"
            mlflow.register_model(model_uri, model_name)
            logger.info(f"Registered model in MLflow registry: {model_name}")
        except Exception as e:
            logger.warning(f"Could not register model in MLflow registry: {e}")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete training pipeline.
        
        Returns:
            Dictionary with pipeline results
        """
        logger.info("=" * 80)
        logger.info("Starting Training Pipeline")
        logger.info("=" * 80)
        
        # Load data
        self.load_data()
        
        # Preprocess
        self.preprocess_data()
        
        # Train all models
        all_metrics = self.train_all_models()
        
        # Select best model
        best_name, best_model, best_metrics = self.select_best_model()
        
        if best_model is None:
            logger.error("No best model selected, aborting pipeline")
            return {"status": "failed", "reason": "No best model"}
        
        # Evaluate on test set
        test_metrics = self.evaluate_on_test_set(best_name, best_model)
        
        # Check if meets minimum threshold
        meets_threshold = self.selector.meets_minimum_threshold(
            threshold=0.75,  # Can be made configurable
            metric=settings.model_selection_metric
        )
        
        if not meets_threshold:
            logger.warning(
                f"Best model does not meet minimum threshold, "
                f"but saving anyway for reference"
            )
        
        # Save best model
        self.save_best_model(best_name, best_model, best_metrics)
        
        logger.info("=" * 80)
        logger.info("Training Pipeline Completed Successfully")
        logger.info("=" * 80)
        
        return {
            "status": "success",
            "best_model": best_name,
            "validation_metrics": best_metrics,
            "test_metrics": test_metrics,
            "all_metrics": all_metrics,
            "meets_threshold": meets_threshold
        }


def main():
    """Main entry point for training pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train ML models")
    parser.add_argument(
        "--experiment-name",
        type=str,
        default=None,
        help="MLflow experiment name"
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="MLflow run name"
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = TrainingPipeline(
        experiment_name=args.experiment_name,
        run_name=args.run_name
    )
    
    results = pipeline.run()
    
    logger.info(f"Pipeline results: {results}")


if __name__ == "__main__":
    main()
