import shap
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import structlog
import joblib
import pickle
from datetime import datetime

logger = structlog.get_logger(__name__)


class SHAPExplainer:
    """
    SHAP-based explainability service for ML models
    """
    
    def __init__(self):
        self.explainers = {}
        self.feature_names = {}
        self.background_data = {}
        self.is_initialized = False
    
    async def initialize_explainer(self, model_name: str, model: Any, X_background: np.ndarray, feature_names: List[str]):
        """Initialize SHAP explainer for a specific model"""
        try:
            logger.info("Initializing SHAP explainer", model_name=model_name)
            
            # Determine explainer type based on model
            if hasattr(model, 'predict_proba'):
                # Tree-based or sklearn models
                explainer = shap.Explainer(model, X_background)
            elif hasattr(model, 'predict'):
                # General ML models
                explainer = shap.Explainer(model.predict, X_background)
            else:
                # Neural networks or other models
                explainer = shap.KernelExplainer(model, X_background)
            
            self.explainers[model_name] = explainer
            self.feature_names[model_name] = feature_names
            self.background_data[model_name] = X_background
            
            logger.info("SHAP explainer initialized successfully", model_name=model_name)
            
        except Exception as e:
            logger.error("Error initializing SHAP explainer", model_name=model_name, error=str(e))
            raise
    
    async def explain_prediction(self, model_name: str, X_instance: np.ndarray, max_evals: int = 1000) -> Dict[str, Any]:
        """Generate SHAP explanation for a single prediction"""
        try:
            if model_name not in self.explainers:
                raise ValueError(f"No explainer found for model {model_name}")
            
            explainer = self.explainers[model_name]
            feature_names = self.feature_names[model_name]
            
            # Calculate SHAP values
            shap_values = explainer(X_instance, max_evals=max_evals)
            
            # Convert to proper format
            if hasattr(shap_values, 'values'):
                values = shap_values.values
                base_value = shap_values.base_values
            else:
                values = shap_values
                base_value = explainer.expected_value
            
            # Handle multi-output models
            if len(values.shape) > 2:
                values = values[0]  # Take first output for simplicity
            
            if len(values.shape) == 2:
                values = values[0]  # Take first instance
            
            # Create feature importance dictionary
            feature_importance = {}
            for i, feature_name in enumerate(feature_names):
                if i < len(values):
                    feature_importance[feature_name] = float(values[i])
            
            # Sort by absolute importance
            sorted_features = sorted(
                feature_importance.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            )
            
            # Get top contributing factors
            top_factors = []
            for feature, importance in sorted_features[:10]:
                direction = "increases" if importance > 0 else "decreases"
                top_factors.append({
                    'feature': feature,
                    'importance': importance,
                    'direction': direction,
                    'abs_importance': abs(importance)
                })
            
            result = {
                'model_name': model_name,
                'base_value': float(base_value) if isinstance(base_value, (int, float)) else float(base_value[0]),
                'feature_importance': feature_importance,
                'top_factors': top_factors,
                'explanation_text': self._generate_explanation_text(top_factors),
                'generated_at': datetime.utcnow()
            }
            
            return result
            
        except Exception as e:
            logger.error("Error generating SHAP explanation", model_name=model_name, error=str(e))
            raise
    
    async def explain_batch(self, model_name: str, X_batch: np.ndarray, max_evals: int = 100) -> List[Dict[str, Any]]:
        """Generate SHAP explanations for a batch of predictions"""
        try:
            if model_name not in self.explainers:
                raise ValueError(f"No explainer found for model {model_name}")
            
            results = []
            
            # Process each instance in the batch
            for i in range(X_batch.shape[0]):
                X_instance = X_batch[i:i+1]  # Keep 2D shape
                explanation = await self.explain_prediction(model_name, X_instance, max_evals)
                explanation['instance_index'] = i
                results.append(explanation)
            
            return results
            
        except Exception as e:
            logger.error("Error generating batch SHAP explanations", model_name=model_name, error=str(e))
            raise
    
    async def get_global_feature_importance(self, model_name: str, X_sample: np.ndarray, sample_size: int = 100) -> Dict[str, Any]:
        """Calculate global feature importance using SHAP"""
        try:
            if model_name not in self.explainers:
                raise ValueError(f"No explainer found for model {model_name}")
            
            explainer = self.explainers[model_name]
            feature_names = self.feature_names[model_name]
            
            # Sample data if too large
            if X_sample.shape[0] > sample_size:
                indices = np.random.choice(X_sample.shape[0], sample_size, replace=False)
                X_sample = X_sample[indices]
            
            # Calculate SHAP values for sample
            shap_values = explainer(X_sample)
            
            # Convert to proper format
            if hasattr(shap_values, 'values'):
                values = shap_values.values
            else:
                values = shap_values
            
            # Handle multi-output models
            if len(values.shape) > 2:
                values = values[:, :, 0]  # Take first output
            
            # Calculate mean absolute SHAP values
            mean_shap_values = np.mean(np.abs(values), axis=0)
            
            # Create global importance dictionary
            global_importance = {}
            for i, feature_name in enumerate(feature_names):
                if i < len(mean_shap_values):
                    global_importance[feature_name] = float(mean_shap_values[i])
            
            # Sort by importance
            sorted_importance = sorted(
                global_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return {
                'model_name': model_name,
                'global_importance': global_importance,
                'top_features': sorted_importance[:20],
                'sample_size': X_sample.shape[0],
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error calculating global feature importance", model_name=model_name, error=str(e))
            raise
    
    async def analyze_feature_interactions(self, model_name: str, X_sample: np.ndarray, max_interactions: int = 10) -> Dict[str, Any]:
        """Analyze feature interactions using SHAP interaction values"""
        try:
            if model_name not in self.explainers:
                raise ValueError(f"No explainer found for model {model_name}")
            
            explainer = self.explainers[model_name]
            feature_names = self.feature_names[model_name]
            
            # Sample data if too large
            if X_sample.shape[0] > 50:
                indices = np.random.choice(X_sample.shape[0], 50, replace=False)
                X_sample = X_sample[indices]
            
            # Calculate interaction values (if supported)
            try:
                interaction_values = explainer.shap_interaction_values(X_sample)
                
                # Calculate mean absolute interaction values
                mean_interactions = np.mean(np.abs(interaction_values), axis=0)
                
                # Find top interactions
                interactions = []
                for i in range(len(feature_names)):
                    for j in range(i+1, len(feature_names)):
                        if i < mean_interactions.shape[0] and j < mean_interactions.shape[1]:
                            interaction_strength = mean_interactions[i, j]
                            interactions.append({
                                'feature_1': feature_names[i],
                                'feature_2': feature_names[j],
                                'interaction_strength': float(interaction_strength)
                            })
                
                # Sort by interaction strength
                interactions = sorted(interactions, key=lambda x: x['interaction_strength'], reverse=True)
                
                return {
                    'model_name': model_name,
                    'top_interactions': interactions[:max_interactions],
                    'sample_size': X_sample.shape[0],
                    'generated_at': datetime.utcnow()
                }
                
            except Exception:
                # Fallback: use correlation-based interaction estimation
                correlations = np.corrcoef(X_sample.T)
                interactions = []
                
                for i in range(len(feature_names)):
                    for j in range(i+1, len(feature_names)):
                        if i < correlations.shape[0] and j < correlations.shape[1]:
                            correlation = abs(correlations[i, j])
                            interactions.append({
                                'feature_1': feature_names[i],
                                'feature_2': feature_names[j],
                                'interaction_strength': float(correlation)
                            })
                
                interactions = sorted(interactions, key=lambda x: x['interaction_strength'], reverse=True)
                
                return {
                    'model_name': model_name,
                    'top_interactions': interactions[:max_interactions],
                    'method': 'correlation_based',
                    'sample_size': X_sample.shape[0],
                    'generated_at': datetime.utcnow()
                }
            
        except Exception as e:
            logger.error("Error analyzing feature interactions", model_name=model_name, error=str(e))
            raise
    
    def _generate_explanation_text(self, top_factors: List[Dict[str, Any]]) -> str:
        """Generate human-readable explanation text"""
        try:
            if not top_factors:
                return "No significant factors identified."
            
            explanation = "The prediction is primarily influenced by:\n\n"
            
            for i, factor in enumerate(top_factors[:5], 1):
                feature = factor['feature']
                direction = factor['direction']
                importance = abs(factor['importance'])
                
                # Create more readable feature names
                readable_feature = feature.replace('_', ' ').title()
                
                explanation += f"{i}. {readable_feature} - {direction} prediction "
                
                if importance > 0.1:
                    explanation += "significantly"
                elif importance > 0.05:
                    explanation += "moderately"
                else:
                    explanation += "slightly"
                
                explanation += f" (impact: {importance:.3f})\n"
            
            return explanation.strip()
            
        except Exception as e:
            logger.error("Error generating explanation text", error=str(e))
            return "Unable to generate explanation text."
    
    async def generate_counterfactual_explanation(self, model_name: str, X_instance: np.ndarray, 
                                                target_change: float = 0.1) -> Dict[str, Any]:
        """Generate counterfactual explanations"""
        try:
            if model_name not in self.explainers:
                raise ValueError(f"No explainer found for model {model_name}")
            
            explainer = self.explainers[model_name]
            feature_names = self.feature_names[model_name]
            
            # Get SHAP values for the instance
            shap_values = explainer(X_instance)
            
            if hasattr(shap_values, 'values'):
                values = shap_values.values[0]
            else:
                values = shap_values[0]
            
            # Find features with highest impact
            feature_impacts = [(i, abs(val)) for i, val in enumerate(values)]
            feature_impacts = sorted(feature_impacts, key=lambda x: x[1], reverse=True)
            
            # Generate counterfactual suggestions
            suggestions = []
            for i, (feature_idx, impact) in enumerate(feature_impacts[:5]):
                if feature_idx < len(feature_names):
                    feature_name = feature_names[feature_idx]
                    current_value = X_instance[0, feature_idx]
                    shap_value = values[feature_idx]
                    
                    # Suggest change direction
                    if shap_value > 0:
                        suggested_change = "decrease"
                        direction = -1
                    else:
                        suggested_change = "increase"
                        direction = 1
                    
                    # Estimate magnitude of change needed
                    change_magnitude = abs(target_change / (shap_value + 1e-8))
                    suggested_value = current_value + (direction * change_magnitude * current_value * 0.1)
                    
                    suggestions.append({
                        'feature': feature_name,
                        'current_value': float(current_value),
                        'suggested_value': float(suggested_value),
                        'change_direction': suggested_change,
                        'impact_if_changed': float(shap_value),
                        'priority': i + 1
                    })
            
            return {
                'model_name': model_name,
                'target_change': target_change,
                'counterfactual_suggestions': suggestions,
                'explanation': f"To change the prediction by {target_change:.3f}, consider modifying these features:",
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error("Error generating counterfactual explanation", model_name=model_name, error=str(e))
            raise
    
    def get_explainer_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific explainer"""
        if model_name not in self.explainers:
            return {'error': f'No explainer found for model {model_name}'}
        
        return {
            'model_name': model_name,
            'explainer_type': type(self.explainers[model_name]).__name__,
            'num_features': len(self.feature_names[model_name]),
            'feature_names': self.feature_names[model_name],
            'background_data_shape': self.background_data[model_name].shape,
            'is_available': True
        }