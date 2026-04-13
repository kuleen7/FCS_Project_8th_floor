"""
Database Models for Secure Job Platform
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    RECRUITER = "recruiter"
    ADMIN = "admin"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    mobile = Column(String(20), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    headline = Column(String(255))
    location = Column(String(255))
    bio = Column(Text)
    profile_picture = Column(String(500))
    company_name = Column(String(255))  # For recruiters
    
    # Account status
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    privacy_level = Column(String(20), default='public')  # public, connections, private
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships (to be added in later milestones)
    # otp_verifications = relationship("OTPVerification", back_populates="user")
    # audit_logs = relationship("AuditLog", back_populates="user")


class OTPVerification(Base):
    """OTP verification model"""
    __tablename__ = "otp_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    otp_code = Column(String(6), nullable=False)
    otp_type = Column(String(20), nullable=False)  # email, mobile, password_reset, etc.
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    # user = relationship("User", back_populates="otp_verifications")


class AuditLog(Base):
    """Audit log model with hash chaining"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Action details
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(Text)
    
    # Request metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Hash chaining for tamper-evidence
    previous_hash = Column(String(64))
    current_hash = Column(String(64), nullable=False, index=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    # user = relationship("User", back_populates="audit_logs")


class Session(Base):
    """User session model"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True)
    
    # Session metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), onupdate=func.now())


class ApplicationStatus(str, enum.Enum):
    """Application status enumeration"""
    APPLIED = "Applied"
    REVIEWED = "Reviewed"
    INTERVIEWED = "Interviewed"
    REJECTED = "Rejected"
    OFFER = "Offer"


class JobType(str, enum.Enum):
    """Job type enumeration"""
    REMOTE = "remote"
    ON_SITE = "on_site"
    HYBRID = "hybrid"
    INTERNSHIP = "internship"
    FULL_TIME = "full_time"
    PART_TIME = "part_time"


class ConversationType(str, enum.Enum):
    """Conversation type enumeration"""
    ONE_TO_ONE = "one_to_one"
    GROUP = "group"


class Company(Base):
    """Company model"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    location = Column(String(255))
    website = Column(String(500))
    logo_url = Column(String(500))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    jobs = relationship("Job", back_populates="company")
    company_members = relationship("CompanyMember", back_populates="company")


class CompanyMember(Base):
    """Company member model"""
    __tablename__ = "company_members"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")  # admin, recruiter, member
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="company_members")
    user = relationship("User")


class Job(Base):
    """Job model"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    required_skills = Column(Text)  # JSON array of skills
    location = Column(String(255))
    job_type = Column(Enum(JobType), default=JobType.FULL_TIME)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    application_deadline = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # Relationships
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")


class Application(Base):
    """Application model"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer)  # Reference to uploaded resume
    cover_note = Column(Text)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    
    # Recruiter notes
    recruiter_notes = Column(Text)
    is_shortlisted = Column(Boolean, default=False)
    
    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    applicant = relationship("User")


class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ConversationType), default=ConversationType.ONE_TO_ONE)
    name = Column(String(255))  # For group conversations
    is_active = Column(Boolean, default=True)
    
    # Relationships
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="conversation")
    participants = relationship("ConversationParticipant", back_populates="conversation")


class ConversationParticipant(Base):
    """Conversation participant model"""
    __tablename__ = "conversation_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="participant")  # admin, participant
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_read_at = Column(DateTime(timezone=True))
    
    # Relationships
    conversation = relationship("Conversation", back_populates="participants")
    user = relationship("User")


class Message(Base):
    """Message model with encryption"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Encrypted content
    content_encrypted = Column(Text, nullable=False)
    encryption_key_id = Column(String(255))  # Reference to encryption key
    content_hash = Column(String(64))  # SHA-256 hash for integrity
    
    # Message metadata
    message_type = Column(String(20), default="text")  # text, file, image
    reply_to_id = Column(Integer, ForeignKey("messages.id"))
    is_deleted = Column(Boolean, default=False)
    is_edited = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User")
    reply_to = relationship("Message", remote_side=[id])


class UserSigningKey(Base):
    """Stores user public keys for digital signature verification"""
    __tablename__ = "user_signing_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    public_key_pem = Column(Text, nullable=False)
    key_fingerprint = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    rotated_at = Column(DateTime(timezone=True))


class SecurityEvent(Base):
    """Tracks suspicious activity and security-relevant events"""
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="low")
    source_ip = Column(String(45))
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class AuditBlock(Base):
    """Simple blockchain-inspired audit blocks"""
    __tablename__ = "audit_blocks"

    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, nullable=False, unique=True, index=True)
    previous_hash = Column(String(64))
    block_hash = Column(String(64), nullable=False, index=True)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class UserTwoFactorAuth(Base):
    """Stores optional TOTP settings per user."""
    __tablename__ = "user_two_factor_auth"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    totp_secret = Column(String(64), nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ConnectionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"


class Connection(Base):
    """Professional connection request/relationship."""
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProfileViewerSetting(Base):
    """Per-user toggle for exposing identity in recent viewers list."""
    __tablename__ = "profile_viewer_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    show_identity = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProfileView(Base):
    """Tracks profile views for viewer count and recent viewers."""
    __tablename__ = "profile_views"

    id = Column(Integer, primary_key=True, index=True)
    profile_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    viewer_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


# Additional models to be added in future milestones:
# - Profile (extended user profile)
# - Connection (professional connections)
# - Resume (detailed resume management)
# - AuditLog (already defined above)
# - Session (already defined above)
# - OTPVerification (already defined above)
