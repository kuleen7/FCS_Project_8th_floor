"""
Email Service for OTP and Notifications
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.error("SMTP credentials not configured")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = settings.SMTP_FROM_EMAIL
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add plain text body
            message.attach(MIMEText(body, "plain"))
            
            # Add HTML body if provided
            if html_body:
                message.attach(MIMEText(html_body, "html"))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_SERVER,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                start_tls=settings.SMTP_STARTTLS,
                use_tls=settings.SMTP_USE_TLS,
                timeout=settings.SMTP_TIMEOUT_SECONDS,
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    async def send_otp_email(email: str, otp: str, purpose: str = "verification") -> bool:
        """
        Send OTP verification email
        
        Args:
            email: Recipient email
            otp: OTP code
            purpose: Purpose of OTP (verification, password_reset, etc.)
            
        Returns:
            True if sent successfully
        """
        subject = f"Your {settings.APP_NAME} Verification Code"
        
        body = f"""
Hello,

Your verification code for {settings.APP_NAME} is: {otp}

This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.

If you did not request this code, please ignore this email.

Best regards,
{settings.APP_NAME} Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 20px; text-align: center; border-radius: 5px; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 20px; }}
        .otp-code {{ font-size: 32px; font-weight: bold; color: #667eea; 
                     text-align: center; padding: 20px; background: white; 
                     border-radius: 5px; letter-spacing: 5px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 {settings.APP_NAME}</h1>
        </div>
        <div class="content">
            <h2>Verification Code</h2>
            <p>Your verification code is:</p>
            <div class="otp-code">{otp}</div>
            <p>This code will expire in <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>.</p>
            <p>If you did not request this code, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>© 2025 {settings.APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return await EmailService.send_email(email, subject, body, html_body)
    
    @staticmethod
    async def send_welcome_email(email: str, name: str) -> bool:
        """Send welcome email after successful registration"""
        subject = f"Welcome to {settings.APP_NAME}!"
        
        body = f"""
Hello {name},

Welcome to {settings.APP_NAME}! Your account has been successfully created.

You can now:
- Create and manage your professional profile
- Upload your resume securely
- Search and apply for jobs
- Connect with recruiters

Visit {settings.FRONTEND_URL} to get started.

Best regards,
{settings.APP_NAME} Team
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 20px; text-align: center; border-radius: 5px; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 5px; margin-top: 20px; }}
        .button {{ display: inline-block; padding: 12px 30px; background: #667eea; 
                   color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to {settings.APP_NAME}!</h1>
        </div>
        <div class="content">
            <h2>Hello {name},</h2>
            <p>Your account has been successfully created!</p>
            <p>You can now:</p>
            <ul>
                <li>Create and manage your professional profile</li>
                <li>Upload your resume securely</li>
                <li>Search and apply for jobs</li>
                <li>Connect with recruiters</li>
            </ul>
            <a href="{settings.FRONTEND_URL}" class="button">Get Started</a>
        </div>
        <div class="footer">
            <p>© 2025 {settings.APP_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
        """
        
        return await EmailService.send_email(email, subject, body, html_body)
email_service = EmailService()
