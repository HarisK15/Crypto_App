import os
import logging
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from typing import Optional, List
import requests
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class NotificationConfig:
    """Holds all the notification settings."""
    
    def __init__(self):
        self.email_enabled = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        self.webhook_enabled = os.getenv("WEBHOOK_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        self.sms_enabled = os.getenv("SMS_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        
        # Email settings
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL")
        
        # Webhook settings
        self.webhook_url = os.getenv("WEBHOOK_URL")
        self.webhook_headers = json.loads(os.getenv("WEBHOOK_HEADERS", "{}"))
        
        # SMS settings (Twilio)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
        
        # Check if everything looks right
        self._validate_config()
    
    def _validate_config(self):
        """Makes sure the config makes sense."""
        if self.email_enabled:
            if not all([self.email_username, self.email_password, self.sender_email]):
                logger.warning("Email notifications enabled but missing required configuration")
                self.email_enabled = False
                
        if self.webhook_enabled and not self.webhook_url:
            logger.warning("Webhook notifications enabled but missing webhook URL")
            self.webhook_enabled = False
            
        if self.sms_enabled:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
                logger.warning("SMS notifications enabled but missing required Twilio configuration")
                self.sms_enabled = False

class Notifier:
    """Main class that handles sending notifications."""
    
    def __init__(self):
        self.config = NotificationConfig()
        self.notification_history = []
    
    def send_notification(self, recipient: str, subject: str, body: str, 
                         notification_type: str = "email", priority: str = "normal") -> bool:
        """
        Sends a notification using the specified method.
        
        Args:
            recipient: Where to send it (email address, webhook URL, phone number)
            subject: What the notification is about
            body: The actual message
            notification_type: How to send it (email, webhook, sms)
            priority: How important it is (low, normal, high, urgent)
            
        Returns:
            True if it worked, False if something went wrong
        """
        timestamp = datetime.now()
        
        try:
            success = False
            
            if notification_type == "email" and self.config.email_enabled:
                success = self._send_email(recipient, subject, body)
            elif notification_type == "webhook" and self.config.webhook_enabled:
                success = self._send_webhook(recipient, subject, body)
            elif notification_type == "sms" and self.config.sms_enabled:
                success = self._send_sms(recipient, subject, body)
            else:
                logger.warning(f"Notification type {notification_type} not available or disabled")
                success = False
            
            # Keep track of what happened
            self._record_notification(
                timestamp, recipient, subject, notification_type, priority, success
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending {notification_type} notification: {e}")
            self._record_notification(
                timestamp, recipient, subject, notification_type, priority, False, str(e)
            )
            return False
    
    def _send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Actually sends the email."""
        try:
            # Build the email message
            msg = MIMEMultipart()
            msg['From'] = self.config.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Add the message body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send it
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.email_username, self.config.email_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {recipient}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("Email authentication failed. Check username and password.")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error(f"Invalid recipient email: {recipient}")
            return False
        except smtplib.SMTPServerDisconnected:
            logger.error("SMTP server disconnected unexpectedly")
            return False
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            return False
    
    def _send_webhook(self, recipient: str, subject: str, body: str) -> bool:
        """Sends a webhook notification."""
        try:
            payload = {
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                headers=self.config.webhook_headers,
                timeout=10
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Webhook notification sent successfully to {self.config.webhook_url}")
                return True
            else:
                logger.error(f"Webhook failed with status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook request error: {e}")
            return False
        except Exception as e:
            logger.error(f"Webhook sending error: {e}")
            return False
    
    def _send_sms(self, recipient: str, subject: str, body: str) -> bool:
        """Sends SMS notification using Twilio."""
        try:
            # TODO: This needs the twilio package to be installed
            logger.info("SMS notifications not yet implemented (needs twilio package)")
            return False
            
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return False
    
    def _record_notification(self, timestamp: datetime, recipient: str, subject: str,
                           notification_type: str, priority: str, success: bool, 
                           error_message: Optional[str] = None):
        """Keeps track of notification attempts."""
        record = {
            'timestamp': timestamp,
            'recipient': recipient,
            'subject': subject,
            'type': notification_type,
            'priority': priority,
            'success': success,
            'error': error_message
        }
        
        self.notification_history.append(record)
        
        # Keep only last 1000 notifications
        if len(self.notification_history) > 1000:
            self.notification_history = self.notification_history[-1000:]
    
    def get_notification_history(self, limit: int = 100) -> List[dict]:
        """Gets the history of notification attempts."""
        return self.notification_history[-limit:]
    
    def clear_notification_history(self):
        """Clears the notification history."""
        self.notification_history.clear()
        logger.info("Notification history cleared")

# Keep the old function for backward compatibility
def send_email_alert(recipient: str, subject: str, body: str) -> bool:
    """
    Old function that some code might still use.
    
    Args:
        recipient: Email address to send to
        subject: Email subject
        body: Email body
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        notifier = Notifier()
        return notifier.send_notification(recipient, subject, body, "email")
    except Exception as e:
        logger.error(f"Error in old send_email_alert function: {e}")
        return False

# Create a global notifier instance
notifier = Notifier()


