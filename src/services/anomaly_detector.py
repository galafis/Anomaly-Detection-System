import os
import json
import pickle
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import sqlite3
import threading
import time

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import joblib

from src.models.data_models import AlgorithmType, AlertLevel, AnomalyResult, ModelMetrics
from src.services.database_manager import DatabaseManager
from src.services.alert_manager import AlertManager

logger = logging.getLogger(__name__)

class AdvancedAnomalyDetector:
    """Advanced anomaly detection with multiple algorithms"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_count = 1000
        self.db_manager = DatabaseManager()
        self.alert_manager = AlertManager()
        self.is_training = False
        self.training_progress = 0
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all detection models"""
        try:
            # Try to load existing models
            self._load_models()
        except Exception as e:
            logger.warning(f"Failed to load models: {e}. Creating new default models.")
            # Create new models if loading fails
            self._create_default_models()
    
    def _create_default_models(self):
        """Create default models with sample data"""
        logger.info("Creating default models...")
        
        # Generate sample training data
        np.random.seed(42)
        normal_data = np.random.randn(1000, self.feature_count)
        
        # Isolation Forest
        self.models[AlgorithmType.ISOLATION_FOREST.value] = IsolationForest(
            contamination=0.1, random_state=42, n_estimators=100
        )
        self.models[AlgorithmType.ISOLATION_FOREST.value].fit(normal_data)
        
        # One-Class SVM
        self.scalers[AlgorithmType.ONE_CLASS_SVM.value] = StandardScaler()
        scaled_data = self.scalers[AlgorithmType.ONE_CLASS_SVM.value].fit_transform(normal_data)
        self.models[AlgorithmType.ONE_CLASS_SVM.value] = OneClassSVM(gamma="scale", nu=0.1)
        self.models[AlgorithmType.ONE_CLASS_SVM.value].fit(scaled_data)
        
        # Save models
        self._save_models()
        logger.info("Default models created and saved")
    
    def _save_models(self):
        """Save models to disk"""
        os.makedirs("models", exist_ok=True)
        
        for algorithm, model in self.models.items():
            joblib.dump(model, f"models/{algorithm}_model.pkl")
        
        for algorithm, scaler in self.scalers.items():
            joblib.dump(scaler, f"models/{algorithm}_scaler.pkl")
    
    def _load_models(self):
        """Load models from disk"""
        model_files = {
            AlgorithmType.ISOLATION_FOREST.value: "models/isolation_forest_model.pkl",
            AlgorithmType.ONE_CLASS_SVM.value: "models/one_class_svm_model.pkl"
        }
        
        scaler_files = {
            AlgorithmType.ONE_CLASS_SVM.value: "models/one_class_svm_scaler.pkl"
        }
        
        for algorithm, file_path in model_files.items():
            if os.path.exists(file_path):
                self.models[algorithm] = joblib.load(file_path)
        
        for algorithm, file_path in scaler_files.items():
            if os.path.exists(file_path):
                self.scalers[algorithm] = joblib.load(file_path)
        
        logger.info("Models loaded successfully")
    
    def train_models(self, training_data: np.ndarray, algorithm: str = None):
        """Train models with new data"""
        self.is_training = True
        self.training_progress = 0
        
        try:
            algorithms_to_train = [algorithm] if algorithm else list(AlgorithmType)
            
            for i, algo in enumerate(algorithms_to_train):
                if isinstance(algo, AlgorithmType):
                    algo = algo.value
                
                start_time = time.time()
                
                if algo == AlgorithmType.ISOLATION_FOREST.value:
                    self.models[algo] = IsolationForest(
                        contamination=0.1, random_state=42, n_estimators=100
                    )
                    self.models[algo].fit(training_data)
                
                elif algo == AlgorithmType.ONE_CLASS_SVM.value:
                    self.scalers[algo] = StandardScaler()
                    scaled_data = self.scalers[algo].fit_transform(training_data)
                    self.models[algo] = OneClassSVM(gamma="scale", nu=0.1)
                    self.models[algo].fit(scaled_data)
                
                training_time = time.time() - start_time
                self.training_progress = ((i + 1) / len(algorithms_to_train)) * 100
                
                logger.info(f"Trained {algo} in {training_time:.2f} seconds")
            
            self._save_models()
            
        finally:
            self.is_training = False
            self.training_progress = 100
    
    def detect_anomaly(self, features: List[float], algorithm: str = None) -> AnomalyResult:
        """Detect anomaly using specified algorithm or ensemble"""
        if len(features) != self.feature_count:
            raise ValueError(f"Expected {self.feature_count} features, got {len(features)}")
        
        X = np.array(features).reshape(1, -1)
        
        if algorithm and algorithm in self.models:
            return self._detect_single_algorithm(X, algorithm, features)
        else:
            return self._detect_ensemble(X, features)
    
    def _detect_single_algorithm(self, X: np.ndarray, algorithm: str, features: List[float]) -> AnomalyResult:
        """Detect anomaly using single algorithm"""
        start_time = time.time()
        
        if algorithm == AlgorithmType.ISOLATION_FOREST.value:
            prediction = self.models[algorithm].predict(X)[0]
            score = self.models[algorithm].score_samples(X)[0]
            is_anomaly = prediction == -1
            confidence = abs(score)
        
        elif algorithm == AlgorithmType.ONE_CLASS_SVM.value:
            scaled_X = self.scalers[algorithm].transform(X)
            prediction = self.models[algorithm].predict(scaled_X)[0]
            score = self.models[algorithm].score_samples(scaled_X)[0]
            is_anomaly = prediction == -1
            confidence = abs(score)
        
        elif algorithm == AlgorithmType.STATISTICAL.value:
            # Statistical method using z-score
            mean_val = np.mean(features)
            std_val = np.std(features)
            z_scores = np.abs((np.array(features) - mean_val) / std_val)
            max_z_score = np.max(z_scores)
            is_anomaly = max_z_score > 3
            confidence = min(max_z_score / 3, 1.0)
            score = max_z_score
        
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        prediction_time = time.time() - start_time
        
        # Determine alert level
        alert_level = self._determine_alert_level(confidence, is_anomaly)
        
        # Create description
        description = self._generate_description(algorithm, confidence, is_anomaly)
        
        result = AnomalyResult(
            timestamp=datetime.now(),
            algorithm=algorithm,
            is_anomaly=is_anomaly,
            confidence=confidence,
            anomaly_score=score,
            features=features,
            alert_level=alert_level,
            description=description
        )
        
        # Save to database
        self.db_manager.save_anomaly(result)
        
        # Send alert if necessary
        self.alert_manager.send_alert(result)
        
        return result
    
    def _detect_ensemble(self, X: np.ndarray, features: List[float]) -> AnomalyResult:
        """Detect anomaly using ensemble of algorithms"""
        ensemble_predictions = []
        ensemble_scores = []
        
        for algo_type, model in self.models.items():
            if algo_type == AlgorithmType.ISOLATION_FOREST.value:
                prediction = model.predict(X)[0]
                score = model.score_samples(X)[0]
            elif algo_type == AlgorithmType.ONE_CLASS_SVM.value:
                scaled_X = self.scalers[algo_type].transform(X)
                prediction = model.predict(scaled_X)[0]
                score = model.score_samples(scaled_X)[0]
            else:
                continue # Skip statistical for ensemble for now
            
            ensemble_predictions.append(1 if prediction == -1 else 0) # 1 for anomaly, 0 for normal
            ensemble_scores.append(abs(score)) # Use absolute score for consistency
        
        # Simple majority vote for anomaly detection
        is_anomaly = sum(ensemble_predictions) >= len(ensemble_predictions) / 2
        
        # Average confidence and score
        confidence = np.mean(ensemble_scores) if ensemble_scores else 0.0
        anomaly_score = np.mean(ensemble_scores) if ensemble_scores else 0.0
        
        # Determine alert level
        alert_level = self._determine_alert_level(confidence, is_anomaly)
        
        # Create description
        description = self._generate_description("ensemble", confidence, is_anomaly)
        
        result = AnomalyResult(
            timestamp=datetime.now(),
            algorithm="ensemble",
            is_anomaly=is_anomaly,
            confidence=confidence,
            anomaly_score=anomaly_score,
            features=features,
            alert_level=alert_level,
            description=description
        )
        
        # Save to database
        self.db_manager.save_anomaly(result)
        
        # Send alert if necessary
        self.alert_manager.send_alert(result)
        
        return result
    
    def _determine_alert_level(self, confidence: float, is_anomaly: bool) -> AlertLevel:
        """Determine alert level based on confidence and anomaly status"""
        if not is_anomaly:
            return AlertLevel.LOW
        
        if confidence > 0.9:
            return AlertLevel.CRITICAL
        elif confidence > 0.7:
            return AlertLevel.HIGH
        elif confidence > 0.5:
            return AlertLevel.MEDIUM
        else:
            return AlertLevel.LOW
    
    def _generate_description(self, algorithm: str, confidence: float, is_anomaly: bool) -> str:
        """Generate human-readable description"""
        if is_anomaly:
            return f"{algorithm} detected anomaly with {confidence:.1%} confidence"
        else:
            return f"{algorithm} classified as normal with {confidence:.1%} confidence"
    
    def get_model_metrics(self) -> List[ModelMetrics]:
        """Get performance metrics for all models"""
        # This would typically use validation data
        # For demo purposes, we'll return mock metrics
        metrics = []
        
        for algorithm in self.models.keys():
            metrics.append(ModelMetrics(
                algorithm=algorithm,
                precision=np.random.uniform(0.85, 0.95),
                recall=np.random.uniform(0.80, 0.90),
                f1_score=np.random.uniform(0.82, 0.92),
                accuracy=np.random.uniform(0.88, 0.96),
                training_time=np.random.uniform(1.0, 5.0),
                prediction_time=np.random.uniform(0.001, 0.01),
                last_updated=datetime.now()
            ))
        
        return metrics

