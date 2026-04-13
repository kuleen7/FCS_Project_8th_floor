"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    RECRUITER = "recruiter"
    ADMIN = "admin"


# Health Check Schema
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    app: str
    version: str
    https: bool


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    mobile: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User registration schema"""
    password: str = Field(..., min_length=8, max_length=128)
    mobile: str = Field(..., min_length=10, max_length=15)
    role: Optional[UserRole] = Field(default=UserRole.USER)
    company_name: Optional[str] = Field(None, max_length=255)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserUpdate(BaseModel):
    """User profile update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    privacy_level: Optional[str] = Field(None, pattern="^(public|connections|private)$")


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str
    totp_code: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: UserRole
    is_verified: bool
    is_active: bool
    headline: Optional[str] = None
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    mobile: Optional[str] = None


# Token Schemas
class Token(BaseModel):
    """JWT token response with user information"""
    token: str
    user: dict
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    email: str
    role: UserRole


# OTP Schemas
class OTPRequest(BaseModel):
    """OTP request schema"""
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    otp_type: str = "verification"


class OTPVerify(BaseModel):
    """OTP verification schema"""
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    otp_code: str = Field(..., min_length=6, max_length=6)


class OTPResponse(BaseModel):
    """OTP response schema"""
    message: str
    expires_in: int


# Error Schemas
class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    message: Optional[str] = None


class ValidationError(BaseModel):
    """Validation error schema"""
    field: str
    message: str


# Success Schemas
class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    data: Optional[dict] = None


# Company Schemas
class CompanyBase(BaseModel):
    """Base company schema"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Company creation schema"""
    pass


class CompanyUpdate(BaseModel):
    """Company update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """Company response schema"""
    id: int
    is_verified: bool
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CompanyMemberBase(BaseModel):
    """Base company member schema"""
    role: str = Field(..., pattern="^(admin|recruiter|member)$")


class CompanyMemberCreate(CompanyMemberBase):
    """Company member creation schema"""
    company_id: int
    user_id: int


class CompanyMemberResponse(CompanyMemberBase):
    """Company member response schema"""
    id: int
    company_id: int
    user_id: int
    is_active: bool
    joined_at: datetime
    
    class Config:
        from_attributes = True


# Job Schemas
class JobType(str, Enum):
    """Job type enumeration"""
    REMOTE = "remote"
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    INTERNSHIP = "internship"
    FULL_TIME = "full_time"
    PART_TIME = "part_time"


class JobBase(BaseModel):
    """Base job schema"""
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=10)
    required_skills: Optional[str] = None  # JSON array string
    location: Optional[str] = None
    job_type: JobType = JobType.FULL_TIME
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    application_deadline: Optional[datetime] = None
    is_featured: bool = False
    
    @validator('salary_max')
    def validate_salary(cls, v, values):
        """Validate salary range"""
        if v is not None and 'salary_min' in values and values['salary_min'] is not None:
            if v < values['salary_min']:
                raise ValueError('Maximum salary must be greater than minimum salary')
        return v


class JobCreate(JobBase):
    """Job creation schema"""
    company_id: int


class JobUpdate(BaseModel):
    """Job update schema"""
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    required_skills: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    application_deadline: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class JobResponse(JobBase):
    """Job response schema"""
    id: int
    company_id: int
    posted_by: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    company: Optional[CompanyResponse] = None
    
    class Config:
        from_attributes = True


class JobSearchRequest(BaseModel):
    """Job search request schema"""
    keywords: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    is_featured: Optional[bool] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class JobSearchResponse(BaseModel):
    """Job search response schema"""
    jobs: list[JobResponse]
    total: int
    page: int
    limit: int
    total_pages: int


# Application Schemas
class ApplicationStatus(str, Enum):
    """Application status enumeration"""
    APPLIED = "Applied"
    REVIEWED = "Reviewed"
    INTERVIEWED = "Interviewed"
    REJECTED = "Rejected"
    OFFER = "Offer"


class ApplicationBase(BaseModel):
    """Base application schema"""
    cover_note: Optional[str] = Field(None, max_length=1000)


class ApplicationCreate(ApplicationBase):
    """Application creation schema"""
    job_id: int
    resume_id: Optional[int] = None


class ApplicationUpdate(BaseModel):
    """Application update schema (for recruiters)"""
    status: Optional[ApplicationStatus] = None
    recruiter_notes: Optional[str] = None
    is_shortlisted: Optional[bool] = None


class ApplicationResponse(ApplicationBase):
    """Application response schema"""
    id: int
    job_id: int
    applicant_id: int
    resume_id: Optional[int] = None
    status: ApplicationStatus
    recruiter_notes: Optional[str] = None
    is_shortlisted: bool
    applied_at: datetime
    updated_at: Optional[datetime] = None
    job: Optional[JobResponse] = None
    applicant: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


# Message Schemas
class ConversationType(str, Enum):
    """Conversation type enumeration"""
    ONE_TO_ONE = "one_to_one"
    GROUP = "group"


class ConversationBase(BaseModel):
    """Base conversation schema"""
    type: ConversationType = ConversationType.ONE_TO_ONE
    name: Optional[str] = Field(None, max_length=255)


class ConversationCreate(ConversationBase):
    """Conversation creation schema"""
    participant_ids: list[int] = Field(..., min_items=1)


class ConversationResponse(ConversationBase):
    """Conversation response schema"""
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base message schema"""
    content: str = Field(..., min_length=1, max_length=10000)
    message_type: str = Field("text", pattern="^(text|file|image)$")
    reply_to_id: Optional[int] = None


class MessageCreate(MessageBase):
    """Message creation schema"""
    conversation_id: int


class MessageResponse(BaseModel):
    """Message response schema"""
    id: int
    conversation_id: int
    sender_id: int
    content_encrypted: str
    content_hash: Optional[str] = None
    message_type: str
    reply_to_id: Optional[int] = None
    is_deleted: bool
    is_edited: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    sender: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class ConversationMessagesResponse(BaseModel):
    """Conversation messages response schema"""
    conversation: ConversationResponse
    messages: list[MessageResponse]
    total: int
    page: int
    limit: int
    total_pages: int
