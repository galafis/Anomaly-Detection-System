import os
import pickle
import numpy as np
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """
    Anomaly Detection System using XGBoost regression model
    """
    
    def __init__(self, model_path: str = 'regressor_model.pkl'):
        self.model = None
        self.model_path = model_path
        self.feature_count = 1000  # Expected number of features
        self.load_model()
    
    def load_model(self):
        """Load the pre-trained XGBoost model"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Model loaded successfully from {self.model_path}")
            else:
                logger.warning(f"Model file {self.model_path} not found. Creating mock model.")
                self.create_mock_model()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.create_mock_model()
    
    def create_mock_model(self):
        """Create a mock model for demonstration purposes"""
        from sklearn.ensemble import RandomForestRegressor
        
        # Create a simple mock model
        self.model = RandomForestRegressor(n_estimators=10, random_state=42)
        
        # Generate some dummy training data
        X_dummy = np.random.randn(100, self.feature_count)
        y_dummy = np.random.randn(100)
        
        # Train the mock model
        self.model.fit(X_dummy, y_dummy)
        
        # Save the mock model
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        logger.info("Mock model created and saved successfully")
    
    def validate_features(self, features: List[float]) -> bool:
        """Validate input features"""
        if not isinstance(features, list):
            return False
        
        if len(features) != self.feature_count:
            return False
        
        # Check if all features are numeric
        try:
            [float(f) for f in features]
            return True
        except (ValueError, TypeError):
            return False
    
    def predict(self, features: List[float]) -> Dict[str, Any]:
        """
        Make prediction using the loaded model
        
        Args:
            features: List of numerical features
            
        Returns:
            Dictionary containing prediction and metadata
        """
        if not self.validate_features(features):
            raise ValueError(f"Invalid features. Expected {self.feature_count} numerical values.")
        
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        try:
            # Convert to numpy array and reshape for prediction
            X = np.array(features).reshape(1, -1)
            
            # Make prediction
            prediction = self.model.predict(X)[0]
            
            # Calculate confidence (simplified approach)
            confidence = min(abs(prediction) / 100.0, 1.0)
            
            # Determine if it's an anomaly (simplified threshold)
            is_anomaly = abs(prediction) > 50.0
            
            return {
                'prediction': float(prediction),
                'is_anomaly': is_anomaly,
                'confidence': float(confidence),
                'timestamp': datetime.now().isoformat(),
                'feature_count': len(features)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise RuntimeError(f"Prediction failed: {str(e)}")

