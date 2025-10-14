import os
import logging
from datetime import datetime
from dataclasses import asdict
import threading  # Adicionado para a função train_models
import io

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from src.services.anomaly_detector import AdvancedAnomalyDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize the advanced detector
detector = AdvancedAnomalyDetector()

# Flask application
app = Flask(__name__)
CORS(app)


@app.route("/api/detect", methods=["POST"])
def detect_anomaly():
    """Advanced anomaly detection endpoint"""
    try:
        data = request.get_json()

        if not data or "features" not in data:
            return (
                jsonify({"error": "Missing features in request", "status": "error"}),
                400,
            )

        features = data["features"]
        algorithm = data.get("algorithm")

        # Detect anomaly
        result = detector.detect_anomaly(features, algorithm)

        return jsonify(
            {
                "status": "success",
                "timestamp": result.timestamp.isoformat(),
                "algorithm": result.algorithm,
                "is_anomaly": result.is_anomaly,
                "confidence": result.confidence,
                "anomaly_score": result.anomaly_score,
                "alert_level": result.alert_level.value,
                "description": result.description,
            }
        )

    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/api/batch-detect", methods=["POST"])
def batch_detect():
    """Batch anomaly detection for file uploads"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Read file content
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.filename.endswith(".json"):
            df = pd.read_json(file)
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        # Process each row
        results = []
        for _, row in df.iterrows():
            features = row.values.tolist()
            if len(features) == detector.feature_count:
                result = detector.detect_anomaly(features)
                results.append(asdict(result))

        return jsonify(
            {
                "status": "success",
                "total_processed": len(results),
                "anomalies_found": sum(1 for r in results if r["is_anomaly"]),
                "results": results,
            }
        )

    except Exception as e:
        logger.error(f"Batch detection error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/train", methods=["POST"])
def train_models():
    """Train models with new data"""
    try:
        data = request.get_json()

        if not data or "training_data" not in data:
            return jsonify({"error": "Missing training data"}), 400

        training_data = np.array(data["training_data"])
        algorithm = data.get("algorithm")

        # Start training in background thread
        def train_async():
            detector.train_models(training_data, algorithm)

        thread = threading.Thread(target=train_async)
        thread.start()

        return jsonify(
            {
                "status": "success",
                "message": "Training started",
                "training_samples": len(training_data),
            }
        )

    except Exception as e:
        logger.error(f"Training error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/training-progress")
def get_training_progress():
    """Get training progress"""
    return jsonify(
        {"is_training": detector.is_training, "progress": detector.training_progress}
    )


@app.route("/api/metrics")
def get_metrics():
    """Get model performance metrics"""
    try:
        metrics = detector.get_model_metrics()
        return jsonify([asdict(m) for m in metrics])
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/history")
def get_history():
    """Get anomaly detection history"""
    try:
        limit = request.args.get("limit", 100, type=int)
        algorithm = request.args.get("algorithm")

        history = detector.db_manager.get_anomalies(limit, algorithm)

        return jsonify({"status": "success", "total": len(history), "history": history})

    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/export-report", methods=["POST"])
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
        title = Paragraph("Anomaly Detection System Report", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 12))

        # Summary
        summary_text = f"""
        Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Total anomalies analyzed: {len(anomalies)}
        Anomalies detected: {sum(1 for a in anomalies if a['is_anomaly'])}
        Detection rate: {(sum(1 for a in anomalies if a['is_anomaly']) / len(anomalies) * 100):.1f}%
        """

        summary = Paragraph(summary_text, styles["Normal"])
        story.append(summary)
        story.append(Spacer(1, 12))

        # Metrics table
        if metrics:
            metrics_data = [
                ["Algorithm", "Precision", "Recall", "F1-Score", "Accuracy"]
            ]
            for m in metrics:
                metrics_data.append(
                    [
                        m.algorithm,
                        f"{m.precision:.3f}",
                        f"{m.recall:.3f}",
                        f"{m.f1_score:.3f}",
                        f"{m.accuracy:.3f}",
                    ]
                )

            metrics_table = Table(metrics_data)
            metrics_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 14),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )

            story.append(Paragraph("Model Performance Metrics", styles["Heading2"]))
            story.append(metrics_table)
            story.append(Spacer(1, 12))

        # Recent anomalies
        if anomalies:
            story.append(Paragraph("Recent Anomaly Detections", styles["Heading2"]))

            anomaly_data = [
                ["Timestamp", "Algorithm", "Status", "Confidence", "Alert Level"]
            ]
            for a in anomalies[:20]:  # Show only first 20
                status = "Anomaly" if a["is_anomaly"] else "Normal"
                anomaly_data.append(
                    [
                        a["timestamp"][:19],  # Remove microseconds
                        a["algorithm"],
                        status,
                        f"{a['confidence']:.3f}",
                        a["alert_level"],
                    ]
                )

            anomaly_table = Table(anomaly_data)
            anomaly_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )

            story.append(anomaly_table)

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'anomaly_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype="application/pdf",
        )

    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Submit feedback for anomaly detection"""
    try:
        data = request.get_json()

        if not data or "anomaly_id" not in data or "feedback_type" not in data:
            return jsonify({"error": "Missing required fields"}), 400

        # Save feedback to database
        detector.db_manager.save_feedback(
            data["anomaly_id"], data["feedback_type"], data.get("comment", "")
        )

        return jsonify(
            {"status": "success", "message": "Feedback submitted successfully"}
        )

    except Exception as e:
        logger.error(f"Feedback error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/status")
def status():
    """Enhanced API status endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "version": "2.0.0",
            "algorithms_available": list(detector.models.keys()),
            "features_expected": detector.feature_count,
            "is_training": detector.is_training,
            "training_progress": detector.training_progress,
            "database_connected": os.path.exists(detector.db_manager.db_path),
            "total_detections": len(detector.db_manager.get_anomalies(1000)),
            "author": "Gabriel Demetrios Lafis",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.errorhandler(404)
def not_found(error):
    """Enhanced 404 error handler"""
    return (
        jsonify(
            {
                "error": "Endpoint not found",
                "status": "error",
                "available_endpoints": [
                    "/api/detect",
                    "/api/batch-detect",
                    "/api/train",
                    "/api/training-progress",
                    "/api/metrics",
                    "/api/history",
                    "/api/export-report",
                    "/api/feedback",
                    "/api/status",
                ],
            }
        ),
        404,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
