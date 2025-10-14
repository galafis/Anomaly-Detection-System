#!/usr/bin/env python3
"""
Unit tests for Anomaly Detection System
Author: Gabriel Demetrios Lafis
"""

import unittest
import json
import os
import sys
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.api.simple_app import app, AnomalyDetector  # noqa: E402


class TestAnomalyDetector(unittest.TestCase):
    """Test cases for AnomalyDetector class"""

    def setUp(self):
        """Set up test fixtures"""
        self.detector = AnomalyDetector()

    def test_validate_features_valid_input(self):
        """Test feature validation with valid input"""
        features = [float(i) for i in range(1000)]
        self.assertTrue(self.detector.validate_features(features))

    def test_validate_features_invalid_length(self):
        """Test feature validation with invalid length"""
        features = [1.0, 2.0, 3.0]  # Too few features
        self.assertFalse(self.detector.validate_features(features))

    def test_validate_features_invalid_type(self):
        """Test feature validation with invalid type"""
        features = "not a list"
        self.assertFalse(self.detector.validate_features(features))

    def test_validate_features_non_numeric(self):
        """Test feature validation with non-numeric values"""
        features = ["string"] * 1000
        self.assertFalse(self.detector.validate_features(features))

    def test_predict_valid_features(self):
        """Test prediction with valid features"""
        features = [float(i) for i in range(1000)]
        result = self.detector.predict(features)

        self.assertIsInstance(result, dict)
        self.assertIn("prediction", result)
        self.assertIn("is_anomaly", result)
        self.assertIn("confidence", result)
        self.assertIn("timestamp", result)
        self.assertIn("feature_count", result)

        self.assertIsInstance(result["prediction"], float)
        self.assertIsInstance(result["is_anomaly"], bool)
        self.assertIsInstance(result["confidence"], float)
        self.assertEqual(result["feature_count"], 1000)

    def test_predict_invalid_features(self):
        """Test prediction with invalid features"""
        features = [1.0, 2.0, 3.0]  # Too few features

        with self.assertRaises(ValueError):
            self.detector.predict(features)

    def test_model_loading(self):
        """Test model loading functionality"""
        # Test that model is loaded or created
        self.assertIsNotNone(self.detector.model)


class TestFlaskAPI(unittest.TestCase):
    """Test cases for Flask API endpoints"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_endpoint(self):
        """Test the index endpoint"""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.content_type)

    def test_status_endpoint(self):
        """Test the status endpoint"""
        response = self.app.get("/api/status")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["version"], "1.0.0")
        self.assertIn("model_loaded", data)
        self.assertIn("timestamp", data)
        self.assertEqual(data["author"], "Gabriel Demetrios Lafis")

    def test_info_endpoint(self):
        """Test the info endpoint"""
        response = self.app.get("/api/info")
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["project"], "Anomaly Detection System")
        self.assertEqual(data["author"], "Gabriel Demetrios Lafis")
        self.assertIn("endpoints", data)
        self.assertIn("features", data)

    def test_predict_endpoint_valid_request(self):
        """Test predict endpoint with valid request"""
        features = [float(i) for i in range(1000)]
        payload = {"features": features}

        response = self.app.post(
            "/predict", data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("prediction", data)
        self.assertIn("is_anomaly", data)
        self.assertIn("confidence", data)

    def test_predict_endpoint_missing_features(self):
        """Test predict endpoint with missing features"""
        payload = {}

        response = self.app.post(
            "/predict", data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("error", data)

    def test_predict_endpoint_invalid_features(self):
        """Test predict endpoint with invalid features"""
        payload = {"features": [1.0, 2.0, 3.0]}  # Too few features

        response = self.app.post(
            "/predict", data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")

    def test_predict_endpoint_no_json(self):
        """Test predict endpoint with no JSON data"""
        response = self.app.post("/predict")

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")

    def test_404_error_handler(self):
        """Test 404 error handler"""
        response = self.app.get("/nonexistent")
        self.assertEqual(response.status_code, 404)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("available_endpoints", data)


class TestIntegration(unittest.TestCase):
    """Integration tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True

    def test_full_prediction_workflow(self):
        """Test complete prediction workflow"""
        # Generate test features
        np.random.seed(42)  # For reproducible results
        features = np.random.randn(1000).tolist()

        # Make prediction request
        payload = {"features": features}
        response = self.app.post(
            "/predict", data=json.dumps(payload), content_type="application/json"
        )

        # Verify response
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIsInstance(data["prediction"], (int, float))
        self.assertIsInstance(data["is_anomaly"], bool)
        self.assertIsInstance(data["confidence"], (int, float))
        self.assertEqual(data["feature_count"], 1000)

        # Verify confidence is within valid range
        self.assertGreaterEqual(data["confidence"], 0.0)
        self.assertLessEqual(data["confidence"], 1.0)


class TestPerformance(unittest.TestCase):
    """Performance tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True

    def test_prediction_performance(self):
        """Test prediction performance"""
        import time

        features = [float(i) for i in range(1000)]
        payload = {"features": features}

        start_time = time.time()

        # Make multiple requests
        for _ in range(10):
            response = self.app.post(
                "/predict", data=json.dumps(payload), content_type="application/json"
            )
            self.assertEqual(response.status_code, 200)

        end_time = time.time()
        avg_time = (end_time - start_time) / 10

        # Prediction should be fast (less than 1 second per request)
        self.assertLess(avg_time, 1.0)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAnomalyDetector))
    test_suite.addTest(unittest.makeSuite(TestFlaskAPI))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    test_suite.addTest(unittest.makeSuite(TestPerformance))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
