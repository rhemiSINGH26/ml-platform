"""
Prediction routes.
"""

import sys
from pathlib import Path
import time
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
from services.api.models.request import HeartDiseaseInput, BatchPredictionInput
from services.api.models.response import PredictionResponse, BatchPredictionResponse
from services.api.dependencies import get_model_loader

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/", response_model=PredictionResponse)
async def predict(
    input_data: HeartDiseaseInput,
    loader = Depends(get_model_loader)
):
    """
    Make a prediction for a single sample.
    
    Args:
        input_data: Heart disease input features
        loader: Model loader dependency
        
    Returns:
        Prediction response with class and probability
    """
    try:
        # Get model and preprocessor
        model = loader.get_model()
        preprocessor = loader.get_preprocessor()
        metadata = loader.get_metadata()
        
        # Convert input to DataFrame
        input_dict = input_data.model_dump()
        df = pd.DataFrame([input_dict])
        
        # Preprocess if preprocessor available
        if preprocessor is not None:
            df = preprocessor.transform(df)
        
        # Make prediction
        prediction = int(model.predict(df)[0])
        
        # Get probability if available
        if hasattr(model, "predict_proba"):
            probability = float(model.predict_proba(df)[0][1])
        else:
            # For models without predict_proba, use decision function or default
            if hasattr(model, "decision_function"):
                # Normalize decision function to [0, 1]
                decision = model.decision_function(df)[0]
                probability = float(1 / (1 + np.exp(-decision)))  # Sigmoid
            else:
                probability = float(prediction)  # 0.0 or 1.0
        
        return PredictionResponse(
            prediction=prediction,
            probability=probability,
            model_name=metadata.get("model_name", "unknown"),
            model_version="v1.0.0"  # TODO: Add versioning
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    input_data: BatchPredictionInput,
    loader = Depends(get_model_loader)
):
    """
    Make predictions for a batch of samples.
    
    Args:
        input_data: Batch of heart disease inputs
        loader: Model loader dependency
        
    Returns:
        Batch prediction response
    """
    try:
        # Get model and preprocessor
        model = loader.get_model()
        preprocessor = loader.get_preprocessor()
        metadata = loader.get_metadata()
        
        # Convert inputs to DataFrame
        input_dicts = [sample.model_dump() for sample in input_data.samples]
        df = pd.DataFrame(input_dicts)
        
        # Preprocess if preprocessor available
        if preprocessor is not None:
            df = preprocessor.transform(df)
        
        # Make predictions
        predictions = model.predict(df)
        
        # Get probabilities if available
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(df)[:, 1]
        else:
            # Fallback
            if hasattr(model, "decision_function"):
                decisions = model.decision_function(df)
                probabilities = 1 / (1 + np.exp(-decisions))  # Sigmoid
            else:
                probabilities = predictions.astype(float)
        
        # Build response
        responses = []
        for pred, prob in zip(predictions, probabilities):
            responses.append(
                PredictionResponse(
                    prediction=int(pred),
                    probability=float(prob),
                    model_name=metadata.get("model_name", "unknown"),
                    model_version="v1.0.0"
                )
            )
        
        return BatchPredictionResponse(
            predictions=responses,
            total=len(responses)
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")
