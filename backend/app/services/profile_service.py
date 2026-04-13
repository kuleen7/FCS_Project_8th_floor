"""
Profile Service for Profile Management
"""
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ..models import User
from ..schemas import UserUpdate

logger = logging.getLogger(__name__)

class ProfileService:
    """Service for profile management"""
    
    @staticmethod
    def update_profile(db: Session, user_id: int, profile_data: UserUpdate) -> Optional[User]:
        """
        Update user profile
        
        Args:
            db: Database session
            user_id: User ID to update
            profile_data: Profile update data
            
        Returns:
            Updated user or None if failed
        """
        try:
            logger.info(f"Updating profile for user {user_id} with data: {profile_data}")
            
            # Get existing user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return None
            
            # Update fields if provided
            if profile_data.first_name is not None:
                user.first_name = profile_data.first_name
            
            if profile_data.last_name is not None:
                user.last_name = profile_data.last_name
            
            if profile_data.headline is not None:
                user.headline = profile_data.headline
            
            if profile_data.location is not None:
                user.location = profile_data.location
            
            if profile_data.bio is not None:
                user.bio = profile_data.bio
            
            if profile_data.profile_picture is not None:
                user.profile_picture = profile_data.profile_picture
            
            if profile_data.privacy_level is not None:
                user.privacy_level = profile_data.privacy_level
            
            # Commit changes
            db.commit()
            db.refresh(user)
            
            logger.info(f"Profile updated successfully for user {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def get_profile_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user profile by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def search_profiles(db: Session, query: str, limit: int = 10) -> list[User]:
        """Search profiles by name or headline"""
        try:
            search_pattern = f"%{query}%"
            return db.query(User).filter(
                (User.first_name.ilike(search_pattern) | 
                 User.last_name.ilike(search_pattern) | 
                 User.headline.ilike(search_pattern))
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Error searching profiles: {str(e)}")
            return []
