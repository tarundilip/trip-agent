"""
Universal email notification service - works with ANY recipient email
"""
import os
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

class NotificationService:
    """Universal email service - works with ANY recipient"""
    
    def __init__(self):
        self.email_enabled = bool(SENDER_EMAIL and SENDER_PASSWORD)
        
        if self.email_enabled:
            logger.info(f"✅ Email service ready - Sender: {SENDER_EMAIL}")
        else:
            logger.warning("⚠️ Email not configured - set SENDER_EMAIL and SENDER_PASSWORD in .env")
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = "") -> bool:
        """
        Send email to ANY recipient address
        
        Args:
            to_email: Recipient email (can be ANYTHING - mail.tm, Gmail, etc.)
            subject: Email subject
            html_body: HTML content
            text_body: Plain text fallback
            
        Returns:
            bool: True if sent successfully
        """
        if not self.email_enabled:
            logger.warning("❌ Cannot send - email service not configured")
            return False
        
        # ✅ Validate recipient email format (basic check)
        if not to_email or '@' not in to_email or '.' not in to_email:
            logger.error(f"❌ Invalid recipient email: {to_email}")
            return False
        
        try:
            logger.info(f"📧 Sending email from {SENDER_EMAIL} to {to_email}")
            
            msg = MIMEMultipart('alternative')
            msg['From'] = SENDER_EMAIL
            msg['To'] = to_email  # ✅ Can be ANY email address!
            msg['Subject'] = subject
            
            # Add text version (for email clients that don't support HTML)
            if text_body:
                msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
            
            # Add HTML version (preferred)
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # Connect to Gmail SMTP and send
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Authentication failed - check SENDER_EMAIL and SENDER_PASSWORD in .env")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error(f"❌ Recipient email rejected: {to_email}")
            return False
        except Exception as e:
            logger.error(f"❌ Email send failed: {e}")
            return False
    
    def send_booking_email(self, user_email: str, user_name: str, booking_type: str, 
                          booking_details: Dict[str, Any], booking_id: str) -> bool:
        """Send booking confirmation to ANY user email"""
        
        subject = f"✅ Booking Confirmed - {booking_id}"
        
        html_body = self._generate_email_html(user_name, booking_type, booking_details, booking_id)
        text_body = self._generate_email_text(user_name, booking_type, booking_details, booking_id)
        
        return self.send_email(user_email, subject, html_body, text_body)
    
    def _generate_email_html(self, user_name: str, booking_type: str, 
                            details: Dict, booking_id: str) -> str:
        """Generate beautiful HTML email"""
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .content {{ padding: 30px; }}
        .booking-id {{ background: #667eea; color: white; padding: 12px 20px; border-radius: 8px; display: inline-block; margin: 15px 0; font-weight: bold; font-size: 16px; }}
        .booking-info {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .booking-info h3 {{ margin: 0 0 15px 0; color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
        .info-row {{ padding: 10px 0; border-bottom: 1px solid #e0e0e0; display: flex; justify-content: space-between; }}
        .info-row:last-child {{ border-bottom: none; }}
        .label {{ font-weight: 600; color: #667eea; }}
        .value {{ color: #333; text-align: right; }}
        .footer {{ text-align: center; padding: 20px; color: #888; font-size: 12px; background: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎫 Booking Confirmed</h1>
            <p>Trip Planner Agent</p>
        </div>
        <div class="content">
            <p style="font-size: 18px; font-weight: 600; color: #667eea;">Dear {user_name},</p>
            <p>Your <strong>{booking_type}</strong> booking has been successfully confirmed!</p>
            
            <div style="text-align: center;">
                <div class="booking-id">Booking ID: {booking_id}</div>
            </div>
            
            <div class="booking-info">
                <h3>📋 Booking Details</h3>
"""
        
        # Add ONLY provided booking details
        for key, value in details.items():
            if key in ['booking_id', 'user_id', 'created_at']:
                continue
            if value is None or value == "" or value == 0:
                continue
            
            label = key.replace('_', ' ').title()
            
            if isinstance(value, (int, float)) and any(x in key.lower() for x in ['price', 'fee', 'cost', 'total']):
                formatted_value = f"₹{value:,.2f}"
            else:
                formatted_value = str(value)
            
            html += f"""
                <div class="info-row">
                    <span class="label">{label}</span>
                    <span class="value">{formatted_value}</span>
                </div>
"""
        
        html += """
            </div>
            <p style="margin-top: 20px; font-size: 14px; color: #888; text-align: center;">
                Thank you for using Trip Planner Agent! ✨
            </p>
        </div>
        <div class="footer">
            <p>This is an automated confirmation.</p>
            <p>© 2025 Trip Planner Agent</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_email_text(self, user_name: str, booking_type: str, 
                            details: Dict, booking_id: str) -> str:
        """Generate plain text email"""
        
        text = f"""
═══════════════════════════════════════════════
BOOKING CONFIRMATION
═══════════════════════════════════════════════

Dear {user_name},

Your {booking_type} booking has been confirmed!

Booking ID: {booking_id}

BOOKING DETAILS:
───────────────────────────────────────────────
"""
        
        for key, value in details.items():
            if key in ['booking_id', 'user_id', 'created_at']:
                continue
            if value is None or value == "" or value == 0:
                continue
            
            label = key.replace('_', ' ').title()
            
            if isinstance(value, (int, float)) and any(x in key.lower() for x in ['price', 'fee', 'cost', 'total']):
                formatted_value = f"₹{value:,.2f}"
            else:
                formatted_value = str(value)
            
            text += f"{label}: {formatted_value}\n"
        
        text += """
───────────────────────────────────────────────

Thank you for using Trip Planner Agent!

This is an automated confirmation.
© 2025 Trip Planner Agent
═══════════════════════════════════════════════
"""
        return text
    
    async def send_booking_notification(self, user_email: Optional[str], 
                                       user_name: str, booking_type: str, 
                                       booking_details: Dict, booking_id: str) -> Dict[str, bool]:
        """
        Send booking notification to ANY email address
        
        Works with:
        - mail.tm addresses (abc@pjfwi.com)
        - 10minutemail addresses
        - Gmail addresses
        - ANY valid email address
        """
        
        results = {"email_sent": False, "email_address": user_email}
        
        if not user_email:
            logger.warning("⚠️ No email provided - skipping notification")
            return results
        
        results["email_sent"] = self.send_booking_email(
            user_email, user_name, booking_type, booking_details, booking_id
        )
        
        return results


# ✅ Global instance (create once, use everywhere)
notification_service = NotificationService()