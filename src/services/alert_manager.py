import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.models.data_models import AnomalyResult, AlertLevel

logger = logging.getLogger(__name__)

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

