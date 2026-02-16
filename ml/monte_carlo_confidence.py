"""
Monte Carlo Confidence Scoring
Estimates prediction stability through input perturbation
"""

import numpy as np
from typing import Dict, List  # FIXED: Added missing import


class MonteCarloConfidence:
    """Estimate prediction confidence using Monte Carlo simulation"""
    
    def __init__(self, n_iterations: int = 100, noise_std: float = 0.05):
        """
        Initialize Monte Carlo confidence estimator.
        
        Args:
            n_iterations: Number of Monte Carlo iterations
            noise_std: Standard deviation of Gaussian noise (default 5%)
        """
        self.n_iterations = n_iterations
        self.noise_std = noise_std
    
    def calculate_confidence(self, model, scaler, features: Dict[str, float],
                            feature_names: List[str], label_names: List[str]) -> Dict:
        """
        Calculate prediction confidence using Monte Carlo sampling.
        
        Process:
        1. Perturb input features ±5% noise
        2. Predict 100 times
        3. Measure variance in predictions
        4. Convert to confidence score (0-1)
        
        Args:
            model: Trained classifier
            scaler: Fitted feature scaler
            features: Input feature dictionary
            feature_names: Ordered list of feature names
            label_names: List of SDLC class names
            
        Returns:
            Dictionary with confidence score and prediction statistics
        """
        # Convert features to array
        base_features = np.array([[features[f] for f in feature_names]])
        
        # Storage for predictions
        predictions = []
        probabilities = []
        
        # Monte Carlo iterations
        for _ in range(self.n_iterations):
            # Add Gaussian noise to features
            noise = np.random.normal(0, self.noise_std, base_features.shape)
            perturbed = base_features + noise
            
            # Clip to [0, 1] range
            perturbed = np.clip(perturbed, 0, 1)
            
            # Scale and predict
            scaled = scaler.transform(perturbed)
            proba = model.predict_proba(scaled)[0]
            pred = model.predict(scaled)[0]
            
            predictions.append(pred)
            probabilities.append(proba)
        
        # Analyze prediction stability
        predictions = np.array(predictions)
        probabilities = np.array(probabilities)
        
        # Most common prediction
        unique, counts = np.unique(predictions, return_counts=True)
        mode_idx = np.argmax(counts)
        most_common_pred = unique[mode_idx]
        prediction_frequency = counts[mode_idx] / self.n_iterations
        
        # Probability statistics
        mean_probs = probabilities.mean(axis=0)
        std_probs = probabilities.std(axis=0)
        
        # Confidence score calculation
        variance_score = 1.0 - np.mean(std_probs)
        agreement_score = prediction_frequency
        
        confidence = 0.6 * agreement_score + 0.4 * variance_score
        confidence = np.clip(confidence, 0.0, 1.0)
        
        return {
            'confidence_score': round(float(confidence), 4),
            'prediction_agreement': round(float(prediction_frequency), 4),
            'probability_variance': round(float(np.mean(std_probs)), 4),
            'predicted_class': label_names[most_common_pred],
            'mean_probabilities': {
                label_names[i]: round(float(mean_probs[i]), 4)
                for i in range(len(label_names))
            }
        }