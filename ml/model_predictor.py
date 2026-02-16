"""
Production Model Predictor - COMPLETE VERSION
Complete inference pipeline: Risk → Performance → XGBoost → SHAP → Monte Carlo
"""

import pickle
import numpy as np
import sys
import os
from typing import Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.risk_engine import generate_risk, FEATURE_LIST
from ml.performance_layer import performance_from_risk, categorize_risk
from ml.shap_explainer import SHAPExplainer
from ml.monte_carlo_confidence import MonteCarloConfidence


class SDLCPredictor:
    """
    Production-ready SDLC risk prediction system.
    
    Complete pipeline:
    1. Validate 28 input features
    2. Calculate risk scores for all 6 SDLCs
    3. Calculate performance metrics
    4. XGBoost classification
    5. SHAP explainability
    6. Monte Carlo confidence
    """
    
    SDLC_MODELS = ['Waterfall', 'Agile', 'Spiral', 'V-Model', 'DevOps', 'Hybrid']
    
    def __init__(self, model_dir: str = 'models'):
        """
        Initialize predictor with trained models.
        
        Args:
            model_dir: Directory containing trained models
        """
        # Load XGBoost model
        with open(f'{model_dir}/xgboost_v1.pkl', 'rb') as f:
            self.model = pickle.load(f)
        
        # Load scaler
        with open(f'{model_dir}/scaler.pkl', 'rb') as f:
            self.scaler = pickle.load(f)
        
        # Load label encoder
        with open(f'{model_dir}/label_encoder.pkl', 'rb') as f:
            self.label_encoder = pickle.load(f)
        
        # Load metadata
        with open(f'{model_dir}/metadata.pkl', 'rb') as f:
            metadata = pickle.load(f)
            self.feature_names = metadata['feature_names']
            self.label_names = metadata['label_names']
        
        # Initialize SHAP explainer
        try:
            self.explainer = SHAPExplainer(
                f'{model_dir}/xgboost_v1.pkl',
                f'{model_dir}/scaler.pkl',
                f'{model_dir}/metadata.pkl'
            )
            print("[OK] SHAP Explainer initialized")
        except Exception as e:
            print(f"[WARN] SHAP initialization failed: {e}")
            self.explainer = None
        
        # Initialize Monte Carlo
        self.mc_confidence = MonteCarloConfidence(n_iterations=100, noise_std=0.05)
        
        print("[OK] SDLC Predictor initialized")
        print(f"   Model: XGBoost v1.0")
        print(f"   Features: {len(self.feature_names)}")
        print(f"   Classes: {len(self.label_names)}")
    
    def validate_features(self, features: Dict[str, float]) -> bool:
        """
        Validate input features.
        
        Args:
            features: Dictionary of 28 features
            
        Returns:
            True if valid
            
        Raises:
            ValueError if invalid
        """
        # Check all features present
        missing = set(FEATURE_LIST) - set(features.keys())
        if missing:
            raise ValueError(f"Missing features: {missing}")
        
        # Check all values in [0, 1]
        for feat, val in features.items():
            if feat in FEATURE_LIST and not (0 <= val <= 1):
                raise ValueError(f"Feature {feat} = {val} not in range [0, 1]")
        
        return True
    
    def predict(self, features: Dict[str, float], 
                include_shap: bool = True,
                include_confidence: bool = True) -> Dict:
        """
        Complete prediction pipeline.
        
        Args:
            features: Dictionary of 28 project features (all normalized 0-1)
            include_shap: Whether to include SHAP explanations
            include_confidence: Whether to calculate Monte Carlo confidence
            
        Returns:
            Complete prediction results with:
            - optimal_sdlc: Predicted best SDLC
            - probabilities: Probability for each SDLC
            - risk_scores: Risk score (0-1) for each SDLC
            - performance_metrics: Performance analysis
            - confidence: Prediction confidence (0-1)
            - top_features: SHAP feature importance
            - model_version: Model version info
        """
        # Validate inputs
        self.validate_features(features)
        
        # 1. CALCULATE RISK SCORES FOR ALL SDLCs
        risk_scores = {}
        performance_metrics = {}
        
        for sdlc in self.SDLC_MODELS:
            risk = generate_risk(features, sdlc)
            risk_scores[sdlc] = round(float(risk), 4)
            
            # Calculate performance for this SDLC
            perf = performance_from_risk(risk)
            performance_metrics[sdlc] = perf
        
        # Find optimal by risk
        optimal_by_risk = min(risk_scores, key=risk_scores.get)
        
        # 2. XGBOOST PREDICTION
        feature_array = np.array([[features[f] for f in self.feature_names]])
        feature_scaled = self.scaler.transform(feature_array)
        
        # Get probabilities
        proba = self.model.predict_proba(feature_scaled)[0]
        pred_class_idx = np.argmax(proba)
        optimal_sdlc = self.label_names[pred_class_idx]
        
        # Format probabilities
        probabilities = {
            self.label_names[i]: round(float(proba[i]), 4)
            for i in range(len(self.label_names))
        }
        
        # 3. SHAP EXPLANATION (COMPLETE REPLACEMENT)
        top_features = []
        try:
            if include_shap and self.explainer:
                shap_result = self.explainer.explain_prediction(features, top_k=5)
                top_features = shap_result['top_features']
            else:
                feature_array = np.array([[features[f] for f in self.feature_names]])
                feature_scaled = self.scaler.transform(feature_array)
                import shap
                explainer = shap.TreeExplainer(self.model)
                shap_values = explainer.shap_values(feature_scaled)
                pred_idx = np.argmax(self.model.predict_proba(feature_scaled)[0])
                class_shap = shap_values[pred_idx][0] if isinstance(shap_values, list) else shap_values[0]
                feat_importance = list(zip(self.feature_names, class_shap))
                top_features = [f"{f}:({v:+.3f})" for f,v in sorted(feat_importance, key=lambda x: abs(x[1]), reverse=True)[:3]]
        except Exception as e:
            print(f"[WARN] SHAP explanation failed: {e}")
            top_features = ["Analysis unavailable"]
        
        # 4. MONTE CARLO CONFIDENCE (if requested)
        confidence_score = None
        if include_confidence:
            try:
                mc_result = self.mc_confidence.calculate_confidence(
                    self.model, self.scaler, features,
                    self.feature_names, self.label_names
                )
                confidence_score = mc_result['confidence_score']
            except Exception as e:
                print(f"[WARN] Confidence calculation failed: {e}")
                confidence_score = round(float(proba[pred_class_idx]), 4)
        
        # 5. ASSEMBLE FINAL RESPONSE
        response = {
            # Primary prediction
            'optimal_sdlc': optimal_sdlc,
            'optimal_sdlc_by_risk': optimal_by_risk,
            
            # Probabilities and risks
            'probabilities': probabilities,
            'risk_scores': risk_scores,
            'risk_categories': {
                sdlc: categorize_risk(risk_scores[sdlc])
                for sdlc in self.SDLC_MODELS
            },
            
            # Performance analysis
            'performance_metrics': performance_metrics,
            
            # Explainability
            'confidence': confidence_score,
            'top_features': top_features,
            
            # Metadata
            'model_version': 'XGBoost_v1.0',
            'feature_count': len(self.feature_names),
            'prediction_method': 'ML + Physics-based Risk Engine'
        }
        
        return response
    
    def compare_sdlcs(self, features: Dict[str, float]) -> Dict:
        """
        Detailed comparison of all SDLCs for the given project.
        
        Args:
            features: Project features
            
        Returns:
            Comparison table with rankings
        """
        # Get full prediction
        prediction = self.predict(features, include_shap=False, include_confidence=False)
        
        # Build comparison table
        comparison = []
        for sdlc in self.SDLC_MODELS:
            comparison.append({
                'SDLC': sdlc,
                'Risk_Score': prediction['risk_scores'][sdlc],
                'Risk_Category': prediction['risk_categories'][sdlc],
                'ML_Probability': prediction['probabilities'].get(sdlc, 0.0),
                'Performance': prediction['performance_metrics'][sdlc]['performance_score'],
                'Success_Prob': prediction['performance_metrics'][sdlc]['success_probability'],
                'Cost_Overrun': prediction['performance_metrics'][sdlc]['cost_overrun_ratio']
            })
        
        # Sort by risk (ascending = better)
        comparison.sort(key=lambda x: x['Risk_Score'])
        
        # Add rank
        for i, item in enumerate(comparison, 1):
            item['Rank'] = i
        
        return {
            'comparison_table': comparison,
            'recommended': comparison[0]['SDLC'],
            'total_sdlcs': len(comparison)
        }


def main():
    """Example usage of production predictor"""
    print("\n" + "="*60)
    print("[DEMO] SDLC RISK PREDICTION SYSTEM - PRODUCTION DEMO")
    print("="*60)
    
    # Initialize predictor
    predictor = SDLCPredictor(model_dir='models')
    
    # Example project: High volatility, low automation
    print("\n[PROJECT] Example: E-commerce Platform Migration")
    features = {feat: 0.5 for feat in FEATURE_LIST}
    features['requirements_volatility'] = 0.85
    features['automation_maturity_score'] = 0.25
    features['stakeholder_alignment_score'] = 0.40
    features['technical_complexity_index'] = 0.75
    
    # Get prediction
    result = predictor.predict(features)
    
    # Display results
    print(f"\n[RESULT] RECOMMENDED SDLC: {result['optimal_sdlc']}")
    print(f"   Confidence: {result['confidence']:.2%}")
    print(f"   Risk Score: {result['risk_scores'][result['optimal_sdlc']]}")
    
    print(f"\n[PROBS] All SDLC Probabilities:")
    for sdlc, prob in sorted(result['probabilities'].items(), 
                             key=lambda x: x[1], reverse=True):
        print(f"   {sdlc:12s}: {prob:.2%}")
    
    print(f"\n[FEATURES] Top Risk Drivers:")
    for feat in result['top_features'][:3]:
        print(f"   * {feat}")
    
    # Comparison
    comparison = predictor.compare_sdlcs(features)
    print(f"\n[RANKING] SDLC Ranking (by risk):")
    for item in comparison['comparison_table'][:3]:
        print(f"   {item['Rank']}. {item['SDLC']:12s} - Risk: {item['Risk_Score']:.3f} ({item['Risk_Category']})")
    
    print("\n" + "="*60)
    print("[OK] PREDICTION COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
