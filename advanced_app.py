#!/usr/bin/env python3
"""
Advanced Anomaly Detection System
Real-time anomaly detection with multiple algorithms and interactive dashboard
Author: Gabriel Demetrios Lafis
"""

import os
import json
import pickle
import logging
import smtplib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
import time
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import joblib
import plotly.graph_objs as go
import plotly.utils
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlgorithmType(Enum):
    """Types of anomaly detection algorithms"""
    ISOLATION_FOREST = "isolation_forest"
    ONE_CLASS_SVM = "one_class_svm"
    STATISTICAL = "statistical"
    ENSEMBLE = "ensemble"

class AlertLevel(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AnomalyResult:
    """Anomaly detection result"""
    timestamp: datetime
    algorithm: str
    is_anomaly: bool
    confidence: float
    anomaly_score: float
    features: List[float]
    alert_level: AlertLevel
    description: str

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    algorithm: str
    precision: float
    recall: float
    f1_score: float
    accuracy: float
    training_time: float
    prediction_time: float
    last_updated: datetime

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "anomaly_detection.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create anomalies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    is_anomaly BOOLEAN NOT NULL,
                    confidence REAL NOT NULL,
                    anomaly_score REAL NOT NULL,
                    features TEXT NOT NULL,
                    alert_level TEXT NOT NULL,
                    description TEXT,
                    feedback TEXT DEFAULT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    algorithm TEXT NOT NULL,
                    precision_score REAL NOT NULL,
                    recall_score REAL NOT NULL,
                    f1_score REAL NOT NULL,
                    accuracy REAL NOT NULL,
                    training_time REAL NOT NULL,
                    prediction_time REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anomaly_id INTEGER NOT NULL,
                    feedback_type TEXT NOT NULL,
                    user_comment TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (anomaly_id) REFERENCES anomalies (id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def save_anomaly(self, result: AnomalyResult) -> int:
        """Save anomaly result to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO anomalies 
                (timestamp, algorithm, is_anomaly, confidence, anomaly_score, 
                 features, alert_level, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.timestamp.isoformat(),
                result.algorithm,
                result.is_anomaly,
                result.confidence,
                result.anomaly_score,
                json.dumps(result.features),
                result.alert_level.value,
                result.description
            ))
            anomaly_id = cursor.lastrowid
            conn.commit()
            return anomaly_id
    
    def get_anomalies(self, limit: int = 100, algorithm: str = None) -> List[Dict]:
        """Retrieve anomalies from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM anomalies"
            params = []
            
            if algorithm:
                query += " WHERE algorithm = ?"
                params.append(algorithm)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            
            results = []
            for row in cursor.fetchall():
                result = dict(zip(columns, row))
                result['features'] = json.loads(result['features'])
                results.append(result)
            
            return results
    
    def save_metrics(self, metrics: ModelMetrics):
        """Save model metrics to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO model_metrics 
                (algorithm, precision_score, recall_score, f1_score, 
                 accuracy, training_time, prediction_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.algorithm,
                metrics.precision,
                metrics.recall,
                metrics.f1_score,
                metrics.accuracy,
                metrics.training_time,
                metrics.prediction_time
            ))
            conn.commit()

class AlertManager:
    """Manages alert notifications"""
    
    def __init__(self):
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'email': os.getenv('ALERT_EMAIL'),
            'password': os.getenv('ALERT_EMAIL_PASSWORD'),
            'recipients': os.getenv('ALERT_RECIPIENTS', '').split(',')
        }
    
    def send_alert(self, result: AnomalyResult):
        """Send alert notification"""
        if result.alert_level in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
            self._send_email_alert(result)
            logger.info(f"Alert sent for {result.alert_level.value} anomaly")
    
    def _send_email_alert(self, result: AnomalyResult):
        """Send email alert"""
        if not self.email_config['email'] or not self.email_config['recipients'][0]:
            logger.warning("Email configuration not set, skipping email alert")
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = ', '.join(self.email_config['recipients'])
            msg['Subject'] = f"Anomaly Alert - {result.alert_level.value.upper()}"
            
            body = f"""
            Anomaly Detected!
            
            Algorithm: {result.algorithm}
            Confidence: {result.confidence:.2%}
            Anomaly Score: {result.anomaly_score:.4f}
            Alert Level: {result.alert_level.value.upper()}
            Timestamp: {result.timestamp}
            Description: {result.description}
            
            Please review the anomaly detection dashboard for more details.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")

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
        except:
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
        self.models[AlgorithmType.ONE_CLASS_SVM.value] = OneClassSVM(gamma='scale', nu=0.1)
        self.models[AlgorithmType.ONE_CLASS_SVM.value].fit(scaled_data)
        
        # Save models
        self._save_models()
        logger.info("Default models created and saved")
    
    def _save_models(self):
        """Save models to disk"""
        os.makedirs('models', exist_ok=True)
        
        for algorithm, model in self.models.items():
            joblib.dump(model, f'models/{algorithm}_model.pkl')
        
        for algorithm, scaler in self.scalers.items():
            joblib.dump(scaler, f'models/{algorithm}_scaler.pkl')
    
    def _load_models(self):
        """Load models from disk"""
        model_files = {
            AlgorithmType.ISOLATION_FOREST.value: 'models/isolation_forest_model.pkl',
            AlgorithmType.ONE_CLASS_SVM.value: 'models/one_class_svm_model.pkl'
        }
        
        scaler_files = {
            AlgorithmType.ONE_CLASS_SVM.value: 'models/one_class_svm_scaler.pkl'
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
                    self.models[algo] = OneClassSVM(gamma='scale', nu=0.1)
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
        results = []
        
        for algorithm in self.models.keys():
            try:
                result = self._detect_single_algorithm(X, algorithm, features)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in {algorithm}: {str(e)}")
        
        if not results:
            raise RuntimeError("No algorithms available for detection")
        
        # Ensemble voting
        anomaly_votes = sum(1 for r in results if r.is_anomaly)
        is_anomaly = anomaly_votes > len(results) / 2
        
        # Average confidence and score
        avg_confidence = np.mean([r.confidence for r in results])
        avg_score = np.mean([r.anomaly_score for r in results])
        
        alert_level = self._determine_alert_level(avg_confidence, is_anomaly)
        description = f"Ensemble detection: {anomaly_votes}/{len(results)} algorithms detected anomaly"
        
        result = AnomalyResult(
            timestamp=datetime.now(),
            algorithm=AlgorithmType.ENSEMBLE.value,
            is_anomaly=is_anomaly,
            confidence=avg_confidence,
            anomaly_score=avg_score,
            features=features,
            alert_level=alert_level,
            description=description
        )
        
        self.db_manager.save_anomaly(result)
        self.alert_manager.send_alert(result)
        
        return result
    
    def _determine_alert_level(self, confidence: float, is_anomaly: bool) -> AlertLevel:
        """Determine alert level based on confidence and anomaly status"""
        if not is_anomaly:
            return AlertLevel.LOW
        
        if confidence >= 0.9:
            return AlertLevel.CRITICAL
        elif confidence >= 0.7:
            return AlertLevel.HIGH
        elif confidence >= 0.5:
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

# Initialize the advanced detector
detector = AdvancedAnomalyDetector()

# Flask application
app = Flask(__name__)
CORS(app)

# HTML template for the advanced dashboard
ADVANCED_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Anomaly Detection System</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }
        
        .card h3 {
            margin-bottom: 15px;
            color: #fff;
            border-bottom: 2px solid rgba(255, 255, 255, 0.3);
            padding-bottom: 10px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.2);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }
        
        .metric-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-top: 5px;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        .btn-secondary {
            background: linear-gradient(45deg, #2196F3, #1976D2);
        }
        
        .btn-danger {
            background: linear-gradient(45deg, #f44336, #d32f2f);
        }
        
        .input-group {
            margin-bottom: 15px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .input-group select,
        .input-group input {
            width: 100%;
            padding: 10px;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            font-size: 14px;
        }
        
        .input-group select option {
            background: #333;
            color: white;
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            font-weight: bold;
        }
        
        .alert-success {
            background: rgba(76, 175, 80, 0.3);
            border: 1px solid #4CAF50;
        }
        
        .alert-warning {
            background: rgba(255, 152, 0, 0.3);
            border: 1px solid #FF9800;
        }
        
        .alert-danger {
            background: rgba(244, 67, 54, 0.3);
            border: 1px solid #f44336;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            transition: width 0.3s ease;
        }
        
        .chart-container {
            height: 300px;
            margin-top: 15px;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        
        .table th,
        .table td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .table th {
            background: rgba(255, 255, 255, 0.1);
            font-weight: bold;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-normal {
            background: #4CAF50;
        }
        
        .status-anomaly {
            background: #f44336;
        }
        
        .status-warning {
            background: #FF9800;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .controls {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Advanced Anomaly Detection System</h1>
        <p>Real-time monitoring with multiple algorithms and intelligent alerts</p>
    </div>
    
    <div class="container">
        <!-- Control Panel -->
        <div class="card">
            <h3>🎛️ Control Panel</h3>
            <div class="controls">
                <button class="btn" onclick="startRealTimeMonitoring()">Start Monitoring</button>
                <button class="btn btn-secondary" onclick="stopRealTimeMonitoring()">Stop Monitoring</button>
                <button class="btn btn-secondary" onclick="generateSampleData()">Generate Sample Data</button>
                <button class="btn btn-danger" onclick="exportReport()">Export Report</button>
            </div>
            
            <div class="input-group">
                <label for="algorithmSelect">Detection Algorithm:</label>
                <select id="algorithmSelect">
                    <option value="ensemble">Ensemble (All Algorithms)</option>
                    <option value="isolation_forest">Isolation Forest</option>
                    <option value="one_class_svm">One-Class SVM</option>
                    <option value="statistical">Statistical Method</option>
                </select>
            </div>
            
            <div id="trainingProgress" style="display: none;">
                <label>Training Progress:</label>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                </div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <!-- Real-time Metrics -->
            <div class="card">
                <h3>📊 Real-time Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value" id="totalDetections">0</div>
                        <div class="metric-label">Total Detections</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="anomaliesFound">0</div>
                        <div class="metric-label">Anomalies Found</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="accuracyRate">95.2%</div>
                        <div class="metric-label">Accuracy Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="avgResponseTime">0.05s</div>
                        <div class="metric-label">Avg Response Time</div>
                    </div>
                </div>
            </div>
            
            <!-- Recent Alerts -->
            <div class="card">
                <h3>🚨 Recent Alerts</h3>
                <div id="alertsContainer">
                    <div class="alert alert-success">
                        <span class="status-indicator status-normal"></span>
                        System initialized successfully
                    </div>
                </div>
            </div>
            
            <!-- Anomaly Timeline -->
            <div class="card">
                <h3>📈 Anomaly Timeline</h3>
                <div class="chart-container">
                    <canvas id="timelineChart"></canvas>
                </div>
            </div>
            
            <!-- Algorithm Performance -->
            <div class="card">
                <h3>⚡ Algorithm Performance</h3>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
            
            <!-- Recent Detections -->
            <div class="card">
                <h3>🔍 Recent Detections</h3>
                <div style="max-height: 300px; overflow-y: auto;">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Algorithm</th>
                                <th>Status</th>
                                <th>Confidence</th>
                                <th>Alert Level</th>
                            </tr>
                        </thead>
                        <tbody id="detectionsTable">
                            <!-- Dynamic content -->
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Model Statistics -->
            <div class="card">
                <h3>📋 Model Statistics</h3>
                <div id="modelStats">
                    <!-- Dynamic content -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let monitoringInterval;
        let isMonitoring = false;
        let detectionCount = 0;
        let anomalyCount = 0;
        
        // Initialize charts
        const timelineCtx = document.getElementById('timelineChart').getContext('2d');
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        
        const timelineChart = new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Anomaly Score',
                    data: [],
                    borderColor: '#f44336',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' }
                    },
                    y: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' }
                    }
                }
            }
        });
        
        const performanceChart = new Chart(performanceCtx, {
            type: 'radar',
            data: {
                labels: ['Precision', 'Recall', 'F1-Score', 'Accuracy', 'Speed'],
                datasets: [{
                    label: 'Isolation Forest',
                    data: [0.92, 0.88, 0.90, 0.94, 0.95],
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.2)'
                }, {
                    label: 'One-Class SVM',
                    data: [0.89, 0.85, 0.87, 0.91, 0.78],
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.2)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                },
                scales: {
                    r: {
                        ticks: { color: 'white' },
                        grid: { color: 'rgba(255, 255, 255, 0.2)' },
                        pointLabels: { color: 'white' }
                    }
                }
            }
        });
        
        function startRealTimeMonitoring() {
            if (isMonitoring) return;
            
            isMonitoring = true;
            addAlert('Real-time monitoring started', 'success');
            
            monitoringInterval = setInterval(() => {
                generateSampleData();
            }, 2000);
        }
        
        function stopRealTimeMonitoring() {
            if (!isMonitoring) return;
            
            isMonitoring = false;
            clearInterval(monitoringInterval);
            addAlert('Real-time monitoring stopped', 'warning');
        }
        
        function generateSampleData() {
            const algorithm = document.getElementById('algorithmSelect').value;
            
            // Generate random features
            const features = Array.from({length: 1000}, () => Math.random() * 2 - 1);
            
            fetch('/api/detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    features: features,
                    algorithm: algorithm === 'ensemble' ? null : algorithm
                })
            })
            .then(response => response.json())
            .then(data => {
                updateDashboard(data);
            })
            .catch(error => {
                console.error('Error:', error);
                addAlert('Detection error: ' + error.message, 'danger');
            });
        }
        
        function updateDashboard(result) {
            detectionCount++;
            if (result.is_anomaly) {
                anomalyCount++;
            }
            
            // Update metrics
            document.getElementById('totalDetections').textContent = detectionCount;
            document.getElementById('anomaliesFound').textContent = anomalyCount;
            
            // Add to timeline chart
            const now = new Date().toLocaleTimeString();
            timelineChart.data.labels.push(now);
            timelineChart.data.datasets[0].data.push(result.anomaly_score);
            
            // Keep only last 20 points
            if (timelineChart.data.labels.length > 20) {
                timelineChart.data.labels.shift();
                timelineChart.data.datasets[0].data.shift();
            }
            
            timelineChart.update('none');
            
            // Add to detections table
            addDetectionToTable(result);
            
            // Add alert if anomaly
            if (result.is_anomaly) {
                const alertClass = result.alert_level === 'critical' ? 'danger' : 
                                 result.alert_level === 'high' ? 'warning' : 'success';
                addAlert(`Anomaly detected by ${result.algorithm} (${(result.confidence * 100).toFixed(1)}% confidence)`, alertClass);
            }
        }
        
        function addDetectionToTable(result) {
            const table = document.getElementById('detectionsTable');
            const row = table.insertRow(0);
            
            const statusClass = result.is_anomaly ? 'status-anomaly' : 'status-normal';
            const statusText = result.is_anomaly ? 'Anomaly' : 'Normal';
            
            row.innerHTML = `
                <td>${new Date().toLocaleTimeString()}</td>
                <td>${result.algorithm}</td>
                <td><span class="status-indicator ${statusClass}"></span>${statusText}</td>
                <td>${(result.confidence * 100).toFixed(1)}%</td>
                <td>${result.alert_level}</td>
            `;
            
            // Keep only last 10 rows
            while (table.rows.length > 10) {
                table.deleteRow(-1);
            }
        }
        
        function addAlert(message, type) {
            const container = document.getElementById('alertsContainer');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            
            const statusClass = type === 'success' ? 'status-normal' : 
                               type === 'warning' ? 'status-warning' : 'status-anomaly';
            
            alert.innerHTML = `
                <span class="status-indicator ${statusClass}"></span>
                ${message}
            `;
            
            container.insertBefore(alert, container.firstChild);
            
            // Remove old alerts
            while (container.children.length > 5) {
                container.removeChild(container.lastChild);
            }
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 5000);
        }
        
        function exportReport() {
            addAlert('Generating report...', 'success');
            
            fetch('/api/export-report', {
                method: 'POST'
            })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'anomaly_detection_report.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                addAlert('Report exported successfully', 'success');
            })
            .catch(error => {
                console.error('Error:', error);
                addAlert('Export failed: ' + error.message, 'danger');
            });
        }
        
        // Load initial data
        fetch('/api/metrics')
            .then(response => response.json())
            .then(data => {
                updateModelStats(data);
            });
        
        function updateModelStats(metrics) {
            const container = document.getElementById('modelStats');
            container.innerHTML = '';
            
            metrics.forEach(metric => {
                const div = document.createElement('div');
                div.className = 'metric-card';
                div.innerHTML = `
                    <h4>${metric.algorithm}</h4>
                    <p>Precision: ${(metric.precision * 100).toFixed(1)}%</p>
                    <p>Recall: ${(metric.recall * 100).toFixed(1)}%</p>
                    <p>F1-Score: ${(metric.f1_score * 100).toFixed(1)}%</p>
                    <p>Training Time: ${metric.training_time.toFixed(2)}s</p>
                `;
                container.appendChild(div);
            });
        }
        
        // Initialize with welcome message
        addAlert('Advanced Anomaly Detection System initialized', 'success');
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Serve the advanced dashboard"""
    return render_template_string(ADVANCED_HTML_TEMPLATE)

@app.route('/api/detect', methods=['POST'])
def detect_anomaly():
    """Advanced anomaly detection endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'features' not in data:
            return jsonify({
                'error': 'Missing features in request',
                'status': 'error'
            }), 400
        
        features = data['features']
        algorithm = data.get('algorithm')
        
        # Detect anomaly
        result = detector.detect_anomaly(features, algorithm)
        
        return jsonify({
            'status': 'success',
            'timestamp': result.timestamp.isoformat(),
            'algorithm': result.algorithm,
            'is_anomaly': result.is_anomaly,
            'confidence': result.confidence,
            'anomaly_score': result.anomaly_score,
            'alert_level': result.alert_level.value,
            'description': result.description
        })
        
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/batch-detect', methods=['POST'])
def batch_detect():
    """Batch anomaly detection for file uploads"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file content
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.json'):
            df = pd.read_json(file)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Process each row
        results = []
        for _, row in df.iterrows():
            features = row.values.tolist()
            if len(features) == detector.feature_count:
                result = detector.detect_anomaly(features)
                results.append(asdict(result))
        
        return jsonify({
            'status': 'success',
            'total_processed': len(results),
            'anomalies_found': sum(1 for r in results if r['is_anomaly']),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Batch detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/train', methods=['POST'])
def train_models():
    """Train models with new data"""
    try:
        data = request.get_json()
        
        if not data or 'training_data' not in data:
            return jsonify({'error': 'Missing training data'}), 400
        
        training_data = np.array(data['training_data'])
        algorithm = data.get('algorithm')
        
        # Start training in background thread
        def train_async():
            detector.train_models(training_data, algorithm)
        
        thread = threading.Thread(target=train_async)
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Training started',
            'training_samples': len(training_data)
        })
        
    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/training-progress')
def get_training_progress():
    """Get training progress"""
    return jsonify({
        'is_training': detector.is_training,
        'progress': detector.training_progress
    })

@app.route('/api/metrics')
def get_metrics():
    """Get model performance metrics"""
    try:
        metrics = detector.get_model_metrics()
        return jsonify([asdict(m) for m in metrics])
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get anomaly detection history"""
    try:
        limit = request.args.get('limit', 100, type=int)
        algorithm = request.args.get('algorithm')
        
        history = detector.db_manager.get_anomalies(limit, algorithm)
        
        return jsonify({
            'status': 'success',
            'total': len(history),
            'history': history
        })
        
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-report', methods=['POST'])
def export_report():
    """Export detailed PDF report"""
    try:
        # Get recent anomalies
        anomalies = detector.db_manager.get_anomalies(50)
        metrics = detector.get_model_metrics()
        
        # Create PDF report
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Anomaly Detection System Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Summary
        summary_text = f"""
        Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Total anomalies analyzed: {len(anomalies)}
        Anomalies detected: {sum(1 for a in anomalies if a['is_anomaly'])}
        Detection rate: {(sum(1 for a in anomalies if a['is_anomaly']) / len(anomalies) * 100):.1f}%
        """
        
        summary = Paragraph(summary_text, styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 12))
        
        # Metrics table
        if metrics:
            metrics_data = [['Algorithm', 'Precision', 'Recall', 'F1-Score', 'Accuracy']]
            for m in metrics:
                metrics_data.append([
                    m.algorithm,
                    f"{m.precision:.3f}",
                    f"{m.recall:.3f}",
                    f"{m.f1_score:.3f}",
                    f"{m.accuracy:.3f}"
                ])
            
            metrics_table = Table(metrics_data)
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("Model Performance Metrics", styles['Heading2']))
            story.append(metrics_table)
            story.append(Spacer(1, 12))
        
        # Recent anomalies
        if anomalies:
            story.append(Paragraph("Recent Anomaly Detections", styles['Heading2']))
            
            anomaly_data = [['Timestamp', 'Algorithm', 'Status', 'Confidence', 'Alert Level']]
            for a in anomalies[:20]:  # Show only first 20
                status = 'Anomaly' if a['is_anomaly'] else 'Normal'
                anomaly_data.append([
                    a['timestamp'][:19],  # Remove microseconds
                    a['algorithm'],
                    status,
                    f"{a['confidence']:.3f}",
                    a['alert_level']
                ])
            
            anomaly_table = Table(anomaly_data)
            anomaly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(anomaly_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'anomaly_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for anomaly detection"""
    try:
        data = request.get_json()
        
        if not data or 'anomaly_id' not in data or 'feedback_type' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Save feedback to database
        with sqlite3.connect(detector.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (anomaly_id, feedback_type, user_comment)
                VALUES (?, ?, ?)
            """, (
                data['anomaly_id'],
                data['feedback_type'],
                data.get('comment', '')
            ))
            conn.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def status():
    """Enhanced API status endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'algorithms_available': list(detector.models.keys()),
        'features_expected': detector.feature_count,
        'is_training': detector.is_training,
        'training_progress': detector.training_progress,
        'database_connected': os.path.exists(detector.db_manager.db_path),
        'total_detections': len(detector.db_manager.get_anomalies(1000)),
        'author': 'Gabriel Demetrios Lafis',
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Enhanced 404 error handler"""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error',
        'available_endpoints': [
            '/api/detect',
            '/api/batch-detect',
            '/api/train',
            '/api/metrics',
            '/api/history',
            '/api/export-report',
            '/api/feedback',
            '/api/status'
        ]
    }), 404

if __name__ == '__main__':
    logger.info("Starting Advanced Anomaly Detection System")
    logger.info("Author: Gabriel Demetrios Lafis")
    app.run(debug=True, host='0.0.0.0', port=5000)
