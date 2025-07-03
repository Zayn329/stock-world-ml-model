from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime

from app.models.schemas import (
    ExplainabilityResult, 
    APIResponse
)
from app.services.explainability_service import ExplainabilityService
from app.core.config import settings

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/prediction/{prediction_id}", response_model=ExplainabilityResult)
async def explain_prediction(
    prediction_id: str,
    explainability_service: ExplainabilityService = Depends()
):
    """
    Get detailed explanation for a specific prediction
    """
    try:
        logger.info("Explaining prediction", prediction_id=prediction_id)
        
        explanation = await explainability_service.explain_prediction(prediction_id)
        
        if not explanation:
            raise HTTPException(status_code=404, detail="Prediction explanation not found")
        
        return explanation
        
    except Exception as e:
        logger.error("Error explaining prediction", prediction_id=prediction_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{symbol}/explain-features", response_model=Dict[str, Any])
async def explain_feature_importance(
    symbol: str,
    features: Dict[str, float],
    model_type: str = Query("price_prediction", regex="^(price_prediction|sentiment_analysis|technical_analysis)$"),
    explainability_service: ExplainabilityService = Depends()
):
    """
    Explain the importance of specific features for a stock prediction
    """
    try:
        logger.info("Explaining feature importance", symbol=symbol, model_type=model_type)
        
        explanation = await explainability_service.explain_feature_importance(
            symbol=symbol,
            features=features,
            model_type=model_type
        )
        
        return explanation
        
    except Exception as e:
        logger.error("Error explaining feature importance", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/{model_name}/global-importance", response_model=Dict[str, Any])
async def get_global_feature_importance(
    model_name: str,
    top_n: int = Query(20, ge=5, le=100),
    explainability_service: ExplainabilityService = Depends()
):
    """
    Get global feature importance for a specific model
    """
    try:
        logger.info("Getting global feature importance", model_name=model_name, top_n=top_n)
        
        importance = await explainability_service.get_global_feature_importance(
            model_name=model_name,
            top_n=top_n
        )
        
        return importance
        
    except Exception as e:
        logger.error("Error getting global feature importance", model_name=model_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{symbol}/shap-analysis", response_model=Dict[str, Any])
async def generate_shap_analysis(
    symbol: str,
    prediction_data: Dict[str, Any],
    model_type: str = Query("price_prediction"),
    explainability_service: ExplainabilityService = Depends()
):
    """
    Generate SHAP analysis for a specific prediction
    """
    try:
        logger.info("Generating SHAP analysis", symbol=symbol, model_type=model_type)
        
        shap_analysis = await explainability_service.generate_shap_analysis(
            symbol=symbol,
            prediction_data=prediction_data,
            model_type=model_type
        )
        
        return shap_analysis
        
    except Exception as e:
        logger.error("Error generating SHAP analysis", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{symbol}/lime-explanation", response_model=Dict[str, Any])
async def generate_lime_explanation(
    symbol: str,
    instance_data: Dict[str, Any],
    model_type: str = Query("price_prediction"),
    num_features: int = Query(10, ge=5, le=50),
    explainability_service: ExplainabilityService = Depends()
):
    """
    Generate LIME explanation for a specific instance
    """
    try:
        logger.info("Generating LIME explanation", symbol=symbol, model_type=model_type)
        
        lime_explanation = await explainability_service.generate_lime_explanation(
            symbol=symbol,
            instance_data=instance_data,
            model_type=model_type,
            num_features=num_features
        )
        
        return lime_explanation
        
    except Exception as e:
        logger.error("Error generating LIME explanation", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/{model_name}/interpretability-report", response_model=Dict[str, Any])
async def get_model_interpretability_report(
    model_name: str,
    explainability_service: ExplainabilityService = Depends()
):
    """
    Get comprehensive interpretability report for a model
    """
    try:
        logger.info("Getting model interpretability report", model_name=model_name)
        
        report = await explainability_service.generate_interpretability_report(model_name)
        
        return report
        
    except Exception as e:
        logger.error("Error getting interpretability report", model_name=model_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/decision-path", response_model=Dict[str, Any])
async def get_prediction_decision_path(
    symbol: str,
    prediction_id: str,
    explainability_service: ExplainabilityService = Depends()
):
    """
    Get the decision path for a specific prediction
    """
    try:
        logger.info("Getting prediction decision path", symbol=symbol, prediction_id=prediction_id)
        
        decision_path = await explainability_service.get_decision_path(symbol, prediction_id)
        
        return decision_path
        
    except Exception as e:
        logger.error("Error getting decision path", symbol=symbol, prediction_id=prediction_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feature-interactions/{model_name}", response_model=Dict[str, Any])
async def get_feature_interactions(
    model_name: str,
    top_n: int = Query(10, ge=5, le=50),
    explainability_service: ExplainabilityService = Depends()
):
    """
    Get important feature interactions for a model
    """
    try:
        logger.info("Getting feature interactions", model_name=model_name, top_n=top_n)
        
        interactions = await explainability_service.analyze_feature_interactions(
            model_name=model_name,
            top_n=top_n
        )
        
        return interactions
        
    except Exception as e:
        logger.error("Error getting feature interactions", model_name=model_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/counterfactual/{symbol}", response_model=Dict[str, Any])
async def generate_counterfactual_explanation(
    symbol: str,
    original_features: Dict[str, float],
    desired_outcome: float,
    model_type: str = Query("price_prediction"),
    explainability_service: ExplainabilityService = Depends()
):
    """
    Generate counterfactual explanations showing what would need to change for different outcomes
    """
    try:
        logger.info("Generating counterfactual explanation", symbol=symbol, model_type=model_type)
        
        counterfactual = await explainability_service.generate_counterfactual_explanation(
            symbol=symbol,
            original_features=original_features,
            desired_outcome=desired_outcome,
            model_type=model_type
        )
        
        return counterfactual
        
    except Exception as e:
        logger.error("Error generating counterfactual explanation", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bias-analysis/{model_name}", response_model=Dict[str, Any])
async def analyze_model_bias(
    model_name: str,
    explainability_service: ExplainabilityService = Depends()
):
    """
    Analyze potential bias in model predictions
    """
    try:
        logger.info("Analyzing model bias", model_name=model_name)
        
        bias_analysis = await explainability_service.analyze_model_bias(model_name)
        
        return bias_analysis
        
    except Exception as e:
        logger.error("Error analyzing model bias", model_name=model_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))