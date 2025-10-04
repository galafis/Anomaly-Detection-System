import os
import logging
from datetime import datetime
from typing import List, Dict, Any

from flask import Flask, request, jsonify

from src.services.simple_anomaly_detector import AnomalyDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the anomaly detector
detector = AnomalyDetector()

@app.route("/predict", methods=["POST"])
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
                "error": "No JSON data provided",
                "status": "error"
            }), 400
        
        if "features" not in data:
            return jsonify({
                "error": "Missing \"features\" field in request",
                "status": "error"
            }), 400
        
        features = data["features"]
        
        # Make prediction
        result = detector.predict(features)
        result["status"] = "success"
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 400
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "status": "error"
        }), 500

@app.route("/api/status")
def status():
    """API health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "model_loaded": detector.model is not None,
        "timestamp": datetime.now().isoformat(),
        "author": "Gabriel Demetrios Lafis"
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "status": "error",
        "available_endpoints": ["/predict", "/api/status"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500

if __name__ == "__main__":
    logger.info("Starting Anomaly Detection System API")
    logger.info("Author: Gabriel Demetrios Lafis")
    app.run(debug=True, host="0.0.0.0", port=5000)

