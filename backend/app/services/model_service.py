import asyncio
import structlog
from typing import Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datetime import datetime
import joblib
import os

from app.core.config import settings
from app.ml.sentiment.finbert_model import FinBERTSentimentModel
from app.ml.technical.technical_analyzer import TechnicalAnalyzer
from app.ml.explainability.shap_explainer import SHAPExplainer

logger = structlog.get_logger(__name__)


class ModelService:
    """Service for managing all ML models and their lifecycle"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict] = {}
        self.initialized = False
    
    async def initialize_models(self):
        """Initialize all ML models"""
        try:
            logger.info("Initializing ML models")
            
            # Initialize sentiment analysis models
            await self._initialize_sentiment_models()
            
            # Initialize technical analysis models
            await self._initialize_technical_models()
            
            # Initialize prediction models
            await self._initialize_prediction_models()
            
            # Initialize explainability models
            await self._initialize_explainability_models()
            
            self.initialized = True
            logger.info("All ML models initialized successfully")
            
        except Exception as e:
            logger.error("Error initializing models", error=str(e))
            raise
    
    async def _initialize_sentiment_models(self):
        """Initialize sentiment analysis models"""
        try:
            logger.info("Initializing sentiment models")
            
            # Initialize FinBERT model
            finbert_model = FinBERTSentimentModel()
            await finbert_model.load_model()
            self.models["finbert"] = finbert_model
            
            self.model_metadata["finbert"] = {
                "type": "sentiment",
                "name": "FinBERT",
                "description": "Financial sentiment analysis using BERT",
                "initialized_at": datetime.utcnow(),
                "version": "1.0.0"
            }
            
            logger.info("Sentiment models initialized")
            
        except Exception as e:
            logger.error("Error initializing sentiment models", error=str(e))
            raise
    
    async def _initialize_technical_models(self):
        """Initialize technical analysis models"""
        try:
            logger.info("Initializing technical models")
            
            # Initialize technical analyzer
            technical_analyzer = TechnicalAnalyzer()
            self.models["technical_analyzer"] = technical_analyzer
            
            self.model_metadata["technical_analyzer"] = {
                "type": "technical",
                "name": "Technical Analyzer",
                "description": "Technical analysis indicators and patterns",
                "initialized_at": datetime.utcnow(),
                "version": "1.0.0"
            }
            
            logger.info("Technical models initialized")
            
        except Exception as e:
            logger.error("Error initializing technical models", error=str(e))
            raise
    
    async def _initialize_prediction_models(self):
        """Initialize prediction models"""
        try:
            logger.info("Initializing prediction models")
            
            # Load pre-trained models if they exist
            model_path = settings.MODEL_PATH
            
            # Price prediction model
            if os.path.exists(f"{model_path}/price_predictor.joblib"):
                price_model = joblib.load(f"{model_path}/price_predictor.joblib")
                self.models["price_predictor"] = price_model
                
                self.model_metadata["price_predictor"] = {
                    "type": "prediction",
                    "name": "Price Predictor",
                    "description": "Stock price prediction model",
                    "initialized_at": datetime.utcnow(),
                    "version": "1.0.0"
                }
            
            # Direction prediction model
            if os.path.exists(f"{model_path}/direction_predictor.joblib"):
                direction_model = joblib.load(f"{model_path}/direction_predictor.joblib")
                self.models["direction_predictor"] = direction_model
                
                self.model_metadata["direction_predictor"] = {
                    "type": "prediction",
                    "name": "Direction Predictor",
                    "description": "Stock direction prediction model",
                    "initialized_at": datetime.utcnow(),
                    "version": "1.0.0"
                }
            
            logger.info("Prediction models initialized")
            
        except Exception as e:
            logger.error("Error initializing prediction models", error=str(e))
            raise
    
    async def _initialize_explainability_models(self):
        """Initialize explainability models"""
        try:
            logger.info("Initializing explainability models")
            
            # Initialize SHAP explainer
            shap_explainer = SHAPExplainer()
            self.models["shap_explainer"] = shap_explainer
            
            self.model_metadata["shap_explainer"] = {
                "type": "explainability",
                "name": "SHAP Explainer",
                "description": "SHAP-based model explainability",
                "initialized_at": datetime.utcnow(),
                "version": "1.0.0"
            }
            
            logger.info("Explainability models initialized")
            
        except Exception as e:
            logger.error("Error initializing explainability models", error=str(e))
            raise
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get a specific model by name"""
        if not self.initialized:
            raise RuntimeError("Models not initialized. Call initialize_models() first.")
        
        return self.models.get(model_name)
    
    def get_model_metadata(self, model_name: str) -> Optional[Dict]:
        """Get metadata for a specific model"""
        return self.model_metadata.get(model_name)
    
    def list_models(self) -> Dict[str, Dict]:
        """List all available models with their metadata"""
        return self.model_metadata
    
    async def reload_model(self, model_name: str) -> bool:
        """Reload a specific model"""
        try:
            logger.info("Reloading model", model_name=model_name)
            
            if model_name == "finbert":
                await self._initialize_sentiment_models()
            elif model_name == "technical_analyzer":
                await self._initialize_technical_models()
            elif model_name in ["price_predictor", "direction_predictor"]:
                await self._initialize_prediction_models()
            elif model_name == "shap_explainer":
                await self._initialize_explainability_models()
            else:
                logger.warning("Unknown model name", model_name=model_name)
                return False
            
            logger.info("Model reloaded successfully", model_name=model_name)
            return True
            
        except Exception as e:
            logger.error("Error reloading model", model_name=model_name, error=str(e))
            return False
    
    async def check_model_health(self) -> Dict[str, bool]:
        """Check health status of all models"""
        health_status = {}
        
        for model_name, model in self.models.items():
            try:
                # Perform a simple health check on each model
                if hasattr(model, 'health_check'):
                    health_status[model_name] = await model.health_check()
                else:
                    health_status[model_name] = model is not None
            except Exception as e:
                logger.error("Health check failed", model_name=model_name, error=str(e))
                health_status[model_name] = False
        
        return health_status
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded models"""
        stats = {
            "total_models": len(self.models),
            "models_by_type": {},
            "initialized": self.initialized,
            "memory_usage": self._estimate_memory_usage()
        }
        
        # Count models by type
        for metadata in self.model_metadata.values():
            model_type = metadata.get("type", "unknown")
            stats["models_by_type"][model_type] = stats["models_by_type"].get(model_type, 0) + 1
        
        return stats
    
    def _estimate_memory_usage(self) -> Dict[str, str]:
        """Estimate memory usage of loaded models"""
        memory_usage = {}
        
        for model_name, model in self.models.items():
            try:
                if hasattr(model, 'model') and hasattr(model.model, 'get_memory_footprint'):
                    # For transformer models
                    memory_usage[model_name] = f"{model.model.get_memory_footprint() / 1024 / 1024:.2f} MB"
                elif hasattr(model, '__sizeof__'):
                    # For other models
                    memory_usage[model_name] = f"{model.__sizeof__() / 1024 / 1024:.2f} MB"
                else:
                    memory_usage[model_name] = "Unknown"
            except Exception:
                memory_usage[model_name] = "Error calculating"
        
        return memory_usage