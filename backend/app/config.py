"""
Configuration Management for Secure Job Platform
"""
from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Secure Job Search Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://jobplatform:password@localhost/secure_job_platform"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OTP Configuration
    OTP_SECRET_KEY: str = secrets.token_urlsafe(32)
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@securejobplatform.com"
    
    # SMS Configuration (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_RESUME_EXTENSIONS: list = [".pdf", ".docx"]
    UPLOAD_DIR: str = "./uploads"
    
    # Encryption
    ENCRYPTION_KEY: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: list = [
        "https://localhost",
        "https://localhost:3000",
        "http://localhost:3000"
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # HTTPS/SSL
    SSL_CERT_PATH: str = "../ssl/cert.pem"
    SSL_KEY_PATH: str = "../ssl/key.pem"
    USE_SSL: bool = True
    
    # Frontend
    FRONTEND_URL: str = "https://localhost"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
