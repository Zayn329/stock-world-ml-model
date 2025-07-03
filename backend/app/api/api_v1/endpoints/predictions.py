from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import structlog
from datetime import datetime

from app.models.schemas import (
    PredictionResult, 
    PredictionRequest,
    ExplainabilityResult,
    APIResponse
)
from app.services.prediction_service import PredictionService
from app.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/{symbol}", response_model=PredictionResult)
async def create_prediction(
    symbol: str,
    request: PredictionRequest,
    prediction_service: PredictionService = Depends()
):
    """
    Create a new AI-powered stock prediction
    """
    try:
        logger.info("Creating prediction", symbol=symbol, request=request.dict())
        
        prediction = await prediction_service.create_prediction(
            symbol=symbol,
            prediction_type=request.prediction_type,
            time_horizon=request.time_horizon,
            include_explainability=request.include_explainability
        )
        
        return prediction
        
    except Exception as e:
        logger.error("Error creating prediction", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}", response_model=List[PredictionResult])
async def get_predictions(
    symbol: str,
    prediction_type: Optional[str] = Query(None),
    time_horizon: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    prediction_service: PredictionService = Depends()
):
    """
    Get historical predictions for a stock symbol
    """
    try:
        logger.info("Getting predictions", symbol=symbol, prediction_type=prediction_type)
        
        predictions = await prediction_service.get_predictions(
            symbol=symbol,
            prediction_type=prediction_type,
            time_horizon=time_horizon,
            limit=limit
        )
        
        return predictions
        
    except Exception as e:
        logger.error("Error getting predictions", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/latest", response_model=PredictionResult)
async def get_latest_prediction(
    symbol: str,
    prediction_type: str = "price",
    prediction_service: PredictionService = Depends()
):
    """
    Get the latest prediction for a stock symbol
    """
    try:
        logger.info("Getting latest prediction", symbol=symbol, prediction_type=prediction_type)
        
        prediction = await prediction_service.get_latest_prediction(
            symbol=symbol,
            prediction_type=prediction_type
        )
        
        if not prediction:
            raise HTTPException(status_code=404, detail="No predictions found")
        
        return prediction
        
    except Exception as e:
        logger.error("Error getting latest prediction", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explain/{prediction_id}", response_model=ExplainabilityResult)
async def get_prediction_explanation(
    prediction_id: str,
    prediction_service: PredictionService = Depends()
):
    """
    Get explainability results for a specific prediction
    """
    try:
        logger.info("Getting prediction explanation", prediction_id=prediction_id)
        
        explanation = await prediction_service.explain_prediction(prediction_id)
        
        if not explanation:
            raise HTTPException(status_code=404, detail="Explanation not found")
        
        return explanation
        
    except Exception as e:
        logger.error("Error getting prediction explanation", prediction_id=prediction_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk", response_model=List[PredictionResult])
async def bulk_predictions(
    symbols: List[str],
    prediction_type: str = "price",
    time_horizon: str = "1d",
    prediction_service: PredictionService = Depends()
):
    """
    Create predictions for multiple stock symbols
    """
    try:
        logger.info("Bulk predictions", symbols=symbols, prediction_type=prediction_type)
        
        if len(symbols) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 symbols allowed for bulk predictions")
        
        predictions = await prediction_service.bulk_predictions(
            symbols=symbols,
            prediction_type=prediction_type,
            time_horizon=time_horizon
        )
        
        return predictions
        
    except Exception as e:
        logger.error("Error in bulk predictions", symbols=symbols, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/{symbol}", response_model=dict)
async def get_prediction_performance(
    symbol: str,
    days_back: int = Query(30, ge=1, le=365),
    prediction_service: PredictionService = Depends()
):
    """
    Get prediction performance metrics for a stock symbol
    """
    try:
        logger.info("Getting prediction performance", symbol=symbol, days_back=days_back)
        
        performance = await prediction_service.get_prediction_performance(
            symbol=symbol,
            days_back=days_back
        )
        
        return performance
        
    except Exception as e:
        logger.error("Error getting prediction performance", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/status", response_model=dict)
async def get_model_status(
    prediction_service: PredictionService = Depends()
):
    """
    Get status and performance of prediction models
    """
    try:
        logger.info("Getting model status")
        
        status = await prediction_service.get_model_status()
        
        return status
        
    except Exception as e:
        logger.error("Error getting model status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain/{model_name}")
async def retrain_model(
    model_name: str,
    prediction_service: PredictionService = Depends()
):
    """
    Trigger model retraining
    """
    try:
        logger.info("Retraining model", model_name=model_name)
        
        result = await prediction_service.retrain_model(model_name)
        
        return {"message": f"Model {model_name} retraining initiated", "job_id": result}
        
    except Exception as e:
        logger.error("Error retraining model", model_name=model_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))