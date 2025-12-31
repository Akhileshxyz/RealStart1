"""
Email service for sending notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def get_renewal_reminder_template(
        developer_name: str,
        plan_name: str,
        end_date: str,
        days_left: int,
        plan_price: float
    ) -> tuple[str, str]:
        """
        Get renewal reminder email template
        
        Returns:
            tuple: (html_content, text_content)
        """
        
        text_content = f"""
Dear {developer_name},

This is a friendly reminder that your subscription is expiring soon.

Subscription Details:
- Plan: {plan_name}
- Expiry Date: {end_date}
- Days Remaining: {days_left} days
- Renewal Price: ₹{plan_price:,.2f}

To ensure uninterrupted service, please renew your subscription before it expires.

If you have any questions, please contact our support team.

Best regards,
RealStart Team
        """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #4F46E5;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f9fafb;
            padding: 30px;
            border: 1px solid #e5e7eb;
        }}
        .details {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .label {{
            font-weight: bold;
            color: #6b7280;
        }}
        .value {{
            color: #111827;
        }}
        .warning {{
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin: 20px 0;
            border-radius: 3px;
        }}
        .button {{
            display: inline-block;
            background-color: #4F46E5;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #6b7280;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Subscription Renewal Reminder</h1>
        </div>
        
        <div class="content">
            <p>Dear {developer_name},</p>
            
            <div class="warning">
                <strong>⚠️ Your subscription is expiring in {days_left} days!</strong>
            </div>
            
            <p>This is a friendly reminder that your subscription will expire soon. To ensure uninterrupted access to all features, please renew your subscription before it expires.</p>
            
            <div class="details">
                <h3>Subscription Details</h3>
                <div class="detail-row">
                    <span class="label">Plan:</span>
                    <span class="value">{plan_name}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Expiry Date:</span>
                    <span class="value">{end_date}</span>
                </div>
                <div class="detail-row">
                    <span class="label">Days Remaining:</span>
                    <span class="value">{days_left} days</span>
                </div>
                <div class="detail-row">
                    <span class="label">Renewal Price:</span>
                    <span class="value">₹{plan_price:,.2f}</span>
                </div>
            </div>
            
            <p style="text-align: center;">
                <a href="#" class="button">Renew Now</a>
            </p>
            
            <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
            
            <p>Best regards,<br>
            <strong>RealStart Team</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated reminder. Please do not reply to this email.</p>
            <p>&copy; 2025 RealStart. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content, text_content


email_service = EmailService()
