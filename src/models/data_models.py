import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


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
