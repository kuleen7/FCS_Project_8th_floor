"""
Authentication API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    OTPRequest, OTPVerify, OTPResponse, SuccessResponse
)
from ..services.user_service import user_service
from ..services.otp_service import otp_service
from ..security import JWTHandler, PasswordHasher, validate_password_strength, OTPGenerator
from ..models import UserTwoFactorAuth
from ..config import settings

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - Creates user account with role-specific data
    - Sends OTP to email for verification
    - Password must meet security requirements
    """
    # Check if user already exists
    existing_user = user_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or mobile already registered"
        )
    
    # Create user with role and company data
    user = user_service.create_user(db, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please check your details."
        )
    
    # Generate and send email OTP
    success, message = await otp_service.generate_and_send_otp(
        db, user.id, "email", email=user.email
    )
    
    if not success:
        # User created but OTP failed - still return success
        return SuccessResponse(
            message="Registration successful. Please contact support for verification.",
            data={"user_id": user.id, "email": user.email}
        )
    
    return SuccessResponse(
        message="Registration successful. Please check your email for verification code.",
        data={"user_id": user.id, "email": user.email, "role": user.role.value}
    )


@router.post("/verify-email", response_model=SuccessResponse)
async def verify_email(otp_data: OTPVerify, db: Session = Depends(get_db)):
    """
    Verify email with OTP
    
    - Verifies the OTP code sent to email
    - Marks user as verified
    """
    # Get user by email
    user = user_service.get_user_by_email(db, otp_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify OTP
    success, message = otp_service.verify_otp(
        db, user.id, otp_data.otp_code, "email"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Mark user as verified
    user_service.verify_user(db, user.id)
    
    # Send welcome email
    await user_service.send_welcome_email(user)
    
    return SuccessResponse(
        message="Email verified successfully",
        data={"verified": True}
    )


@router.post("/verify-mobile", response_model=SuccessResponse)
async def verify_mobile(otp_data: OTPVerify, db: Session = Depends(get_db)):
    """
    Verify mobile number with OTP
    
    - Verifies the OTP code sent to mobile
    """
    # Get user by mobile
    user = user_service.get_user_by_mobile(db, otp_data.mobile)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify OTP
    success, message = otp_service.verify_otp(
        db, user.id, otp_data.otp_code, "mobile"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return SuccessResponse(
        message="Mobile verified successfully",
        data={"verified": True}
    )


@router.post("/resend-otp", response_model=OTPResponse)
async def resend_otp(otp_request: OTPRequest, db: Session = Depends(get_db)):
    """
    Resend OTP code
    
    - Generates new OTP and sends to email or mobile
    """
    # Get user
    user = None
    if otp_request.email:
        user = user_service.get_user_by_email(db, otp_request.email)
    elif otp_request.mobile:
        user = user_service.get_user_by_mobile(db, otp_request.mobile)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Resend OTP
    success, message = await otp_service.resend_otp(
        db, user.id, otp_request.otp_type,
        email=otp_request.email,
        mobile=otp_request.mobile
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return OTPResponse(
        message=message,
        expires_in=settings.OTP_EXPIRE_MINUTES * 60
    )


@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(payload: dict, db: Session = Depends(get_db)):
    """
    Reset password using email OTP.

    Required payload:
    - email
    - otp_code
    - new_password
    """
    email = (payload.get("email") or "").strip().lower()
    otp_code = (payload.get("otp_code") or "").strip()
    new_password = payload.get("new_password") or ""

    if not email or not otp_code or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email, otp_code and new_password are required",
        )

    user = user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    strong, errors = validate_password_strength(new_password)
    if not strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(errors),
        )

    success, message = otp_service.verify_otp(db, user.id, otp_code, "password_reset")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    user.password_hash = PasswordHasher.hash_password(new_password)
    db.commit()

    return SuccessResponse(
        message="Password reset successful",
        data={"email": user.email}
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    User login
    
    - Authenticates user with email and password
    - Returns JWT access token
    - User must be verified and active
    """
    # Authenticate user
    user = user_service.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )

    # Optional TOTP verification if enabled for this user
    two_factor = db.query(UserTwoFactorAuth).filter(UserTwoFactorAuth.user_id == user.id).first()
    if two_factor and two_factor.is_enabled:
        if not credentials.totp_code:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="TOTP code required for this account",
            )
        if not OTPGenerator.verify_totp(two_factor.totp_secret, credentials.totp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TOTP code",
            )
    
    # Update last login
    user_service.update_last_login(db, user.id)
    
    # Generate JWT token
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value
    }
    access_token = JWTHandler.create_access_token(token_data)
    
    # Create user response data
    user_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role.value,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat()
    }
    
    return Token(
        token=access_token,
        user=user_data,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Dependency to get current authenticated user
    """
    token = credentials.credentials
    payload = JWTHandler.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("user_id")
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return UserResponse.from_orm(user)


@router.post("/2fa/setup", response_model=SuccessResponse)
async def setup_totp_2fa(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a TOTP secret and provisioning URI for optional 2FA setup."""
    secret = OTPGenerator.generate_totp_secret()
    provisioning_uri = OTPGenerator.get_totp_provisioning_uri(secret, current_user.email)

    config = db.query(UserTwoFactorAuth).filter(UserTwoFactorAuth.user_id == current_user.id).first()
    if not config:
        config = UserTwoFactorAuth(user_id=current_user.id, totp_secret=secret, is_enabled=False)
        db.add(config)
    else:
        config.totp_secret = secret
        config.is_enabled = False
    db.commit()

    return SuccessResponse(
        message="2FA setup secret generated. Verify one TOTP code to enable.",
        data={
            "totp_secret": secret,
            "provisioning_uri": provisioning_uri,
            "enabled": False,
        },
    )


@router.post("/2fa/enable", response_model=SuccessResponse)
async def enable_totp_2fa(
    payload: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enable TOTP 2FA after verifying a current authenticator code."""
    token = str(payload.get("totp_code", "")).strip()
    if not token:
        raise HTTPException(status_code=400, detail="totp_code is required")

    config = db.query(UserTwoFactorAuth).filter(UserTwoFactorAuth.user_id == current_user.id).first()
    if not config:
        raise HTTPException(status_code=404, detail="2FA setup not initialized. Call /auth/2fa/setup first.")

    if not OTPGenerator.verify_totp(config.totp_secret, token):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    config.is_enabled = True
    db.commit()
    return SuccessResponse(message="2FA enabled successfully", data={"enabled": True})


@router.post("/2fa/disable", response_model=SuccessResponse)
async def disable_totp_2fa(
    payload: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Disable TOTP 2FA after verifying a current authenticator code."""
    token = str(payload.get("totp_code", "")).strip()
    if not token:
        raise HTTPException(status_code=400, detail="totp_code is required")

    config = db.query(UserTwoFactorAuth).filter(UserTwoFactorAuth.user_id == current_user.id).first()
    if not config or not config.is_enabled:
        raise HTTPException(status_code=400, detail="2FA is not enabled")

    if not OTPGenerator.verify_totp(config.totp_secret, token):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    config.is_enabled = False
    db.commit()
    return SuccessResponse(message="2FA disabled successfully", data={"enabled": False})


@router.post("/logout", response_model=SuccessResponse)
async def logout():
    """
    User logout
    
    - In a stateless JWT system, logout is handled client-side
    - Client should delete the token
    - For added security, implement token blacklisting in production
    """
    return SuccessResponse(
        message="Logged out successfully",
        data={"logged_out": True}
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current user information
    
    - Returns authenticated user's profile
    """
    return current_user
