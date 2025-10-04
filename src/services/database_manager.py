import sqlite3
import json
import logging
from typing import List, Dict
from datetime import datetime

from src.models.data_models import AnomalyResult, ModelMetrics

logger = logging.getLogger(__name__)

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
                result["features"] = json.loads(result["features"])
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

    def save_feedback(self, anomaly_id: int, feedback_type: str, user_comment: str = '') -> None:
        """Save user feedback to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (anomaly_id, feedback_type, user_comment)
                VALUES (?, ?, ?)
            """, (
                anomaly_id,
                feedback_type,
                user_comment
            ))
            conn.commit()

