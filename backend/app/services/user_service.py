"""
User Service for User Management Operations
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging

from ..models import User, UserRole
from ..schemas import UserCreate, UserUpdate
from ..security import PasswordHasher
from .email_service import EmailService

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> Optional[User]:
        """
        Create new user
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user or None if failed
        """
        try:
            logger.info(f"Creating user with data: {user_data}")
            
            # Validate required fields
            if not user_data.email or not user_data.email.strip():
                logger.error("Email is required and cannot be empty")
                raise ValueError("Email is required and cannot be empty")
            
            if not user_data.first_name or not user_data.first_name.strip():
                logger.error("First name is required and cannot be empty")
                raise ValueError("First name is required and cannot be empty")
            
            if not user_data.last_name or not user_data.last_name.strip():
                logger.error("Last name is required and cannot be empty")
                raise ValueError("Last name is required and cannot be empty")
            
            if not user_data.password or len(user_data.password) < 8:
                logger.error("Password must be at least 8 characters")
                raise ValueError("Password must be at least 8 characters")
            
            # Check if email already exists
            existing_user = db.query(User).filter(
                User.email == user_data.email
            ).first()
            
            if existing_user:
                logger.warning(f"User with email {user_data.email} already exists")
                return None
            
            # Check if mobile already exists (if provided and different from existing user)
            if user_data.mobile:
                existing_mobile = db.query(User).filter(
                    User.mobile == user_data.mobile,
                    User.email != user_data.email  # Exclude same user
                ).first()
                if existing_mobile:
                    logger.warning(f"User with mobile {user_data.mobile} already exists")
                    return None
            
            # Hash password
            hashed_password = PasswordHasher.hash_password(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                mobile=user_data.mobile,
                password_hash=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                role=user_data.role or UserRole.USER,
                company_name=getattr(user_data, 'company_name', None),
                is_verified=False,
                is_active=True
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created successfully: {user.email}")
            return user
            
        except ValueError as e:
            logger.error(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            logger.error(f"Error details: {type(e).__name__}: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_mobile(db: Session, mobile: str) -> Optional[User]:
        """Get user by mobile number"""
        return db.query(User).filter(User.mobile == mobile).first()
    
    @staticmethod
    def verify_user(db: Session, user_id: int) -> bool:
        """
        Mark user as verified
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_verified = True
                db.commit()
                logger.info(f"User {user_id} verified successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error verifying user: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def update_user_profile(
        db: Session,
        user_id: int,
        update_data: UserUpdate
    ) -> Optional[User]:
        """
        Update user profile
        
        Args:
            db: Database session
            user_id: User ID
            update_data: Update data
            
        Returns:
            Updated user or None if failed
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Update fields if provided
            if update_data.first_name is not None:
                user.first_name = update_data.first_name
            if update_data.last_name is not None:
                user.last_name = update_data.last_name
            if update_data.headline is not None:
                user.headline = update_data.headline
            if update_data.location is not None:
                user.location = update_data.location
            if update_data.bio is not None:
                user.bio = update_data.bio
            if update_data.mobile is not None:
                # Check if mobile already exists
                existing = db.query(User).filter(
                    User.mobile == update_data.mobile,
                    User.id != user_id
                ).first()
                if existing:
                    logger.warning(f"Mobile {update_data.mobile} already exists")
                    return None
                user.mobile = update_data.mobile
            
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            
            logger.info(f"User profile updated: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def update_last_login(db: Session, user_id: int) -> bool:
        """Update user's last login timestamp"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.utcnow()
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            db: Database session
            email: User email
            password: Plain password
            
        Returns:
            User if authenticated, None otherwise
        """
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {email}")
            return None
        
        if not PasswordHasher.verify_password(password, user.password_hash):
            logger.warning(f"Invalid password for user: {email}")
            return None
        
        logger.info(f"User authenticated successfully: {email}")
        return user
    
    @staticmethod
    def get_all_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        Get all users (for admin)
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            
        Returns:
            List of users
        """
        query = db.query(User)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def suspend_user(db: Session, user_id: int) -> bool:
        """Suspend user account"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = False
                db.commit()
                logger.info(f"User {user_id} suspended")
                return True
            return False
        except Exception as e:
            logger.error(f"Error suspending user: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def reactivate_user(db: Session, user_id: int) -> bool:
        """Reactivate suspended user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = True
                db.commit()
                logger.info(f"User {user_id} reactivated")
                return True
            return False
        except Exception as e:
            logger.error(f"Error reactivating user: {str(e)}")
            db.rollback()
            return False
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user (soft delete by deactivating)"""
        return UserService.suspend_user(db, user_id)
    
    @staticmethod
    async def send_welcome_email(user: User) -> bool:
        """Send welcome email to new user"""
        try:
            name = user.first_name or user.email.split('@')[0]
            return await EmailService.send_welcome_email(user.email, name)
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False


# Create singleton instance
user_service = UserService()
