"""
OTP Service
Handles OTP generation, sending, and verification
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import asyncio

from app.models import OTPVerification
from app.security import OTPGenerator
from app.config import settings
from app.services.email_service import email_service


class OTPService:

    async def generate_and_send_otp(
        self,
        db: Session,
        user_id: int,
        otp_type: str,
        email: Optional[str] = None,
        mobile: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Generate OTP and attempt to send via email or mobile.
        Always prints OTP to terminal for development.
        """

        # Generate OTP
        otp_code = OTPGenerator.generate_otp()

        # ALWAYS PRINT OTP (for demo/dev)
        print("\n========== OTP GENERATED ==========")
        print(f"User ID: {user_id}")
        print(f"OTP Code: {otp_code}")
        print("===================================\n")

        # Store OTP in DB
        otp_entry = OTPVerification(
            user_id=user_id,
            otp_code=otp_code,
            otp_type=otp_type,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
            is_used=False
        )

        db.add(otp_entry)
        db.commit()

        # Try sending email if provided
        if email:
            try:
                sent = await asyncio.wait_for(email_service.send_otp_email(email, otp_code), timeout=8)
                if sent:
                    return True, "OTP sent successfully"
                if settings.OTP_REQUIRE_DELIVERY:
                    return False, "Failed to deliver OTP email"
                return True, "OTP generated. Email delivery failed; use fallback OTP flow."
            except asyncio.TimeoutError:
                print("⚠ Email sending timed out")
                if settings.OTP_REQUIRE_DELIVERY:
                    return False, "OTP email delivery timed out"
                return True, "OTP generated. Email timed out; use fallback OTP flow."
            except Exception as e:
                print(f"⚠ Email sending failed: {str(e)}")
                if settings.OTP_REQUIRE_DELIVERY:
                    return False, "Failed to deliver OTP email"
                return True, "OTP generated. Email delivery failed; use fallback OTP flow."

        # Mobile sending can be added here later
        return True, "OTP generated successfully"

    def verify_otp(
        self,
        db: Session,
        user_id: int,
        otp_code: str,
        otp_type: str
    ) -> Tuple[bool, str]:
        """
        Verify OTP for user
        """

        otp_entry = db.query(OTPVerification).filter(
            OTPVerification.user_id == user_id,
            OTPVerification.otp_code == otp_code,
            OTPVerification.otp_type == otp_type,
            OTPVerification.is_used == False
        ).first()

        if not otp_entry:
            return False, "Invalid OTP"

        if otp_entry.expires_at < datetime.now(timezone.utc):
            return False, "OTP expired"

        # Mark OTP as used
        otp_entry.is_used = True
        db.commit()

        return True, "OTP verified successfully"

    async def resend_otp(
        self,
        db: Session,
        user_id: int,
        otp_type: str,
        email: Optional[str] = None,
        mobile: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Resend OTP (generate new one)
        """

        return await self.generate_and_send_otp(
            db=db,
            user_id=user_id,
            otp_type=otp_type,
            email=email,
            mobile=mobile
        )


# Singleton instance
otp_service = OTPService()
