"""
SMS Service for Mobile OTP Verification
"""
from typing import Optional
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from ..config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS messages via Twilio"""
    
    def __init__(self):
        """Initialize Twilio client"""
        self.client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
    
    async def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send SMS message
        
        Args:
            to_number: Recipient phone number (E.164 format)
            message: Message content
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            logger.error("Twilio client not initialized")
            return False
        
        if not settings.TWILIO_PHONE_NUMBER:
            logger.error("Twilio phone number not configured")
            return False
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully to {to_number}, SID: {message.sid}")
            return True
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {to_number}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            return False
    
    async def send_otp_sms(self, mobile: str, otp: str) -> bool:
        """
        Send OTP verification SMS
        
        Args:
            mobile: Recipient mobile number
            otp: OTP code
            
        Returns:
            True if sent successfully
        """
        message = f"""Your {settings.APP_NAME} verification code is: {otp}

This code will expire in {settings.OTP_EXPIRE_MINUTES} minutes.

Do not share this code with anyone."""
        
        return await self.send_sms(mobile, message)
    
    @staticmethod
    def format_phone_number(phone: str, country_code: str = "+1") -> str:
        """
        Format phone number to E.164 format
        
        Args:
            phone: Phone number
            country_code: Country code (default +1 for US)
            
        Returns:
            Formatted phone number
        """
        # Remove any non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present
        if not phone.startswith('+'):
            return f"{country_code}{digits}"
        
        return f"+{digits}"
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate phone number format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - should have at least 10 digits
        digits = ''.join(filter(str.isdigit, phone))
        return len(digits) >= 10


# Create singleton instance
sms_service = SMSService()
