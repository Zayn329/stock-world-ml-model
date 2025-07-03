import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Any, Optional, Tuple
import structlog
import asyncio
from datetime import datetime

from app.core.config import settings

logger = structlog.get_logger(__name__)


class FinBERTSentimentModel:
    """
    FinBERT model for financial sentiment analysis
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.SENTIMENT_MODEL_NAME
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = 512
        self.batch_size = settings.BATCH_SIZE
        
        # Sentiment labels mapping
        self.label_mapping = {
            0: "negative",
            1: "neutral", 
            2: "positive"
        }
        
        self.confidence_threshold = 0.6
        self.is_loaded = False
    
    async def load_model(self):
        """Load the FinBERT model and tokenizer"""
        try:
            logger.info("Loading FinBERT model", model_name=self.model_name)
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=settings.HUGGINGFACE_CACHE_DIR
            )
            
            # Load model
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                cache_dir=settings.HUGGINGFACE_CACHE_DIR
            )
            
            # Move model to device
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            logger.info("FinBERT model loaded successfully", device=str(self.device))
            
        except Exception as e:
            logger.error("Error loading FinBERT model", error=str(e))
            raise
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Basic text cleaning
        text = text.strip()
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long (keep within token limits)
        if len(text) > 2000:  # Rough character limit
            text = text[:2000] + "..."
        
        return text
    
    async def predict_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Predict sentiment for a single text
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(text)
            
            # Tokenize
            inputs = self.tokenizer(
                processed_text,
                max_length=self.max_length,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
            
            # Map to sentiment labels
            sentiment_label = self.label_mapping[predicted_class]
            
            # Calculate compound score (similar to VADER)
            compound_score = self._calculate_compound_score(probabilities[0])
            
            result = {
                "label": sentiment_label,
                "score": confidence,
                "compound_score": compound_score,
                "probabilities": {
                    "negative": probabilities[0][0].item(),
                    "neutral": probabilities[0][1].item(),
                    "positive": probabilities[0][2].item()
                },
                "model": "finbert",
                "processed_at": datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error("Error predicting sentiment", error=str(e))
            raise
    
    async def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Predict sentiment for a batch of texts
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            results = []
            
            # Process in batches
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                batch_results = await self._process_batch(batch_texts)
                results.extend(batch_results)
            
            return results
            
        except Exception as e:
            logger.error("Error predicting batch sentiment", error=str(e))
            raise
    
    async def _process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Process a single batch of texts"""
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Tokenize batch
        inputs = self.tokenizer(
            processed_texts,
            max_length=self.max_length,
            padding=True,
            truncation=True,
            return_tensors="pt"
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_classes = torch.argmax(probabilities, dim=-1)
        
        # Process results
        results = []
        for i, text in enumerate(texts):
            predicted_class = predicted_classes[i].item()
            confidence = probabilities[i][predicted_class].item()
            sentiment_label = self.label_mapping[predicted_class]
            compound_score = self._calculate_compound_score(probabilities[i])
            
            result = {
                "text": text,
                "label": sentiment_label,
                "score": confidence,
                "compound_score": compound_score,
                "probabilities": {
                    "negative": probabilities[i][0].item(),
                    "neutral": probabilities[i][1].item(),
                    "positive": probabilities[i][2].item()
                },
                "model": "finbert",
                "processed_at": datetime.utcnow()
            }
            results.append(result)
        
        return results
    
    def _calculate_compound_score(self, probabilities: torch.Tensor) -> float:
        """Calculate compound sentiment score similar to VADER"""
        neg_prob = probabilities[0].item()
        neu_prob = probabilities[1].item()
        pos_prob = probabilities[2].item()
        
        # Calculate compound score
        compound = pos_prob - neg_prob
        
        # Normalize to [-1, 1] range
        if compound >= 0:
            compound = compound / (1 + neu_prob)
        else:
            compound = compound / (1 + neu_prob)
        
        return compound
    
    def get_sentiment_category(self, compound_score: float) -> str:
        """Categorize sentiment based on compound score"""
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    async def health_check(self) -> bool:
        """Check if the model is healthy and working"""
        try:
            if not self.is_loaded:
                return False
            
            # Test with a simple sentence
            test_result = await self.predict_sentiment("The market is performing well today.")
            return test_result is not None and "label" in test_result
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and statistics"""
        return {
            "model_name": self.model_name,
            "device": str(self.device),
            "max_length": self.max_length,
            "batch_size": self.batch_size,
            "is_loaded": self.is_loaded,
            "labels": list(self.label_mapping.values()),
            "confidence_threshold": self.confidence_threshold
        }