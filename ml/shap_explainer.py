"""
SHAP Explainability Module - COMPLETE VERSION
Provides feature importance and interaction analysis using SHAP
"""

import numpy as np
import pickle
from typing import Dict, List

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("[WARN] SHAP not installed. Install with: pip install shap")


class SHAPExplainer:
    """SHAP-based model explainability"""
    
    def __init__(self, model_path: str = 'models/xgboost_v1.pkl',
                 scaler_path: str = 'models/scaler.pkl',
                 metadata_path: str = 'models/metadata.pkl'):
        """
        Initialize SHAP explainer.
        
        Args:
            model_path: Path to trained XGBoost model
            scaler_path: Path to fitted scaler
            metadata_path: Path to feature metadata
        """
        # Load model
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        # Load scaler
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
            self.feature_names = metadata['feature_names']
            self.label_names = metadata['label_names']
        
        # Initialize SHAP explainer if available
        if SHAP_AVAILABLE:
            self.explainer = shap.TreeExplainer(self.model)
            self.shap_enabled = True
        else:
            self.explainer = None
            self.shap_enabled = False
    
    def explain_prediction(self, features: Dict[str, float], 
                          top_k: int = 5) -> Dict:
        """
        Explain a single prediction using SHAP values.
        
        Args:
            features: Dictionary of 28 project features
            top_k: Number of top features to return
            
        Returns:
            Dictionary with SHAP explanation
        """
        # Convert to array and scale
        feature_array = np.array([[features[f] for f in self.feature_names]])
        feature_scaled = self.scaler.transform(feature_array)
        
        # Get prediction
        pred_proba = self.model.predict_proba(feature_scaled)[0]
        pred_class_idx = np.argmax(pred_proba)
        pred_class = self.label_names[pred_class_idx]
        
        if self.shap_enabled:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(feature_scaled)
            
            # Get SHAP values for predicted class
            if isinstance(shap_values, list):
                # Multi-class: one array per class
                class_shap = shap_values[pred_class_idx][0]
            else:
                # Binary or single output
                class_shap = shap_values[0]
            
            # Get top features by absolute SHAP value
            feature_impacts = []
            for i, feat_name in enumerate(self.feature_names):
                feature_impacts.append({
                    'feature': feat_name,
                    'value': features[feat_name],
                    'shap_value': float(class_shap[i]),
                    'impact': 'positive' if class_shap[i] > 0 else 'negative'
                })
            
            # Sort by absolute SHAP value
            feature_impacts.sort(key=lambda x: abs(x['shap_value']), reverse=True)
            
            # Format top features
            top_features = []
            for feat in feature_impacts[:top_k]:
                sign = '+' if feat['shap_value'] > 0 else ''
                top_features.append(
                    f"{feat['feature']}({sign}{feat['shap_value']:.3f})"
                )
        else:
            # Fallback: use feature values as proxy
            feature_impacts = []
            for i, feat_name in enumerate(self.feature_names):
                value = features[feat_name]
                impact = value if value > 0.5 else -(1 - value)
                feature_impacts.append({
                    'feature': feat_name,
                    'value': value,
                    'shap_value': impact,
                    'impact': 'positive' if impact > 0 else 'negative'
                })
            
            feature_impacts.sort(key=lambda x: abs(x['shap_value']), reverse=True)
            
            top_features = []
            for feat in feature_impacts[:top_k]:
                sign = '+' if feat['shap_value'] > 0 else ''
                top_features.append(
                    f"{feat['feature']}({sign}{abs(feat['shap_value']):.3f})"
                )
        
        return {
            'predicted_sdlc': pred_class,
            'confidence': float(pred_proba[pred_class_idx]),
            'top_features': top_features,
            'all_feature_impacts': feature_impacts[:top_k],
            'shap_enabled': self.shap_enabled
        }
    
    def get_feature_interactions(self, features: Dict[str, float]) -> List[Dict]:
        """
        Identify top feature interactions using SHAP interaction values.
        
        Args:
            features: Dictionary of project features
            
        Returns:
            List of top feature interactions
        """
        if not self.shap_enabled:
            return []
        
        # Convert to array and scale
        feature_array = np.array([[features[f] for f in self.feature_names]])
        feature_scaled = self.scaler.transform(feature_array)
        
        try:
            # Calculate SHAP interaction values
            shap_interaction = self.explainer.shap_interaction_values(feature_scaled)
            
            # Extract top interactions
            if isinstance(shap_interaction, list):
                # Use first class for simplicity
                interaction_matrix = shap_interaction[0][0]
            else:
                interaction_matrix = shap_interaction[0]
            
            # Find top interactions (off-diagonal elements)
            interactions = []
            n = len(self.feature_names)
            for i in range(n):
                for j in range(i+1, n):
                    interactions.append({
                        'feature1': self.feature_names[i],
                        'feature2': self.feature_names[j],
                        'interaction_strength': float(abs(interaction_matrix[i, j]))
                    })
            
            # Sort by strength
            interactions.sort(key=lambda x: x['interaction_strength'], reverse=True)
            
            return interactions[:5]  # Top 5 interactions
        except Exception as e:
            print(f"[WARN] Could not calculate interactions: {e}")
            return []