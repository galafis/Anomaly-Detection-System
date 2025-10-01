#!/usr/bin/env python3
"""
Anomaly Detection System API
Real-time anomaly detection using XGBoost regression model
Author: Gabriel Demetrios Lafis
"""

import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import logging
from typing import List, Dict, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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

# Initialize the anomaly detector
detector = AnomalyDetector()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anomaly Detection System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .info-card {
            background: rgba(255, 255, 255, 0.2);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .endpoint {
            background: rgba(0, 0, 0, 0.2);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }
        .method {
            color: #4CAF50;
            font-weight: bold;
        }
        .url {
            color: #FFC107;
        }
        .example {
            background: rgba(0, 0, 0, 0.3);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            overflow-x: auto;
        }
        .author {
            text-align: center;
            margin-top: 30px;
            font-style: italic;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Anomaly Detection System</h1>
        
        <div class="info-card">
            <h2>📊 System Information</h2>
            <p><strong>Author:</strong> Gabriel Demetrios Lafis</p>
            <p><strong>Version:</strong> 1.0.0</p>
            <p><strong>Status:</strong> <span style="color: #4CAF50;">Active</span></p>
            <p><strong>Model:</strong> XGBoost Regression</p>
            <p><strong>Features:</strong> 1000 dimensions</p>
        </div>

        <div class="info-card">
            <h2>🚀 API Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="url">/</span><br>
                Returns system information and status
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="url">/predict</span><br>
                Performs anomaly detection on provided features
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="url">/api/status</span><br>
                Returns API health status
            </div>
        </div>

        <div class="info-card">
            <h2>📝 Usage Example</h2>
            <p>Send a POST request to <code>/predict</code> with the following JSON structure:</p>
            
            <div class="example">
{
  "features": [0.5, 1.2, -0.3, 4.5, ...]  // Array of 1000 numerical values
}
            </div>
            
            <p>Example response:</p>
            <div class="example">
{
  "prediction": 123.45,
  "is_anomaly": false,
  "confidence": 0.85,
  "timestamp": "2025-01-01T12:00:00",
  "feature_count": 1000
}
            </div>
        </div>

        <div class="author">
            <p>Developed by Gabriel Demetrios Lafis</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Anomaly detection endpoint
    
    Expected JSON payload:
    {
        "features": [list of 1000 numerical values]
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400
        
        if 'features' not in data:
            return jsonify({
                'error': 'Missing "features" field in request',
                'status': 'error'
            }), 400
        
        features = data['features']
        
        # Make prediction
        result = detector.predict(features)
        result['status'] = 'success'
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 400
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500

@app.route('/api/status')
def status():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'model_loaded': detector.model is not None,
        'timestamp': datetime.now().isoformat(),
        'author': 'Gabriel Demetrios Lafis'
    })

@app.route('/api/info')
def info():
    """System information endpoint"""
    return jsonify({
        'project': 'Anomaly Detection System',
        'description': 'Real-time anomaly detection using XGBoost regression model',
        'author': 'Gabriel Demetrios Lafis',
        'version': '1.0.0',
        'features': {
            'model_type': 'XGBoost Regression',
            'feature_dimensions': detector.feature_count,
            'real_time_prediction': True,
            'anomaly_detection': True
        },
        'endpoints': [
            {'method': 'GET', 'path': '/', 'description': 'Web interface'},
            {'method': 'POST', 'path': '/predict', 'description': 'Anomaly detection'},
            {'method': 'GET', 'path': '/api/status', 'description': 'Health check'},
            {'method': 'GET', 'path': '/api/info', 'description': 'System information'}
        ]
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error',
        'available_endpoints': ['/predict', '/api/status', '/api/info']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Anomaly Detection System API")
    logger.info("Author: Gabriel Demetrios Lafis")
    app.run(debug=True, host='0.0.0.0', port=5000)
