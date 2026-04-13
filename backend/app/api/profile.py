"""
Profile API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import User, UserRole, Connection, ConnectionStatus, ProfileView, ProfileViewerSetting
from ..schemas import UserUpdate
from ..security import get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("/me")
async def get_current_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "mobile": current_user.mobile,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "headline": getattr(current_user, 'headline', ''),
        "location": getattr(current_user, 'location', ''),
        "bio": getattr(current_user, 'bio', ''),
        "profile_picture": getattr(current_user, 'profile_picture', ''),
        "company_name": getattr(current_user, 'company_name', ''),
        "role": current_user.role.value,
        "is_verified": current_user.is_verified,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }

@router.put("/me")
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    
    try:
        # Update fields if provided
        if profile_data.first_name is not None:
            current_user.first_name = profile_data.first_name
        
        if profile_data.last_name is not None:
            current_user.last_name = profile_data.last_name
        
        if profile_data.headline is not None:
            current_user.headline = profile_data.headline
        
        if profile_data.location is not None:
            current_user.location = profile_data.location
        
        if profile_data.bio is not None:
            current_user.bio = profile_data.bio
        
        if profile_data.profile_picture is not None:
            current_user.profile_picture = profile_data.profile_picture
        
        if profile_data.privacy_level is not None:
            current_user.privacy_level = profile_data.privacy_level
        
        # Commit changes
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Profile updated successfully",
            "data": {
                "id": current_user.id,
                "email": current_user.email,
                "mobile": current_user.mobile,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "headline": current_user.headline,
                "location": current_user.location,
                "bio": current_user.bio,
                "profile_picture": current_user.profile_picture,
                "company_name": current_user.company_name,
                "role": current_user.role.value,
                "is_verified": current_user.is_verified,
                "is_active": current_user.is_active
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )

@router.post("/upload-picture")
async def upload_profile_picture(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture"""
    return {
        "message": "Profile picture upload not implemented yet",
        "status": "not_implemented"
    }

@router.get("/view/{user_id}")
async def view_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """View another user's profile with privacy controls"""
    
    profile_user = db.query(User).filter(User.id == user_id).first()
    if not profile_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check privacy settings
    privacy_level = getattr(profile_user, 'privacy_level', 'public')
    
    # If private, only owner can view
    if privacy_level == 'private' and profile_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This profile is private"
        )
    
    # If connections-only, enforce accepted connection relationship.
    if privacy_level == 'connections' and profile_user.id != current_user.id:
        connection = db.query(Connection).filter(
            Connection.status == ConnectionStatus.ACCEPTED,
            (
                ((Connection.requester_id == current_user.id) & (Connection.recipient_id == profile_user.id)) |
                ((Connection.requester_id == profile_user.id) & (Connection.recipient_id == current_user.id))
            )
        ).first()
        if not connection:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This profile is visible to connections only"
            )

    # Track viewer event (skip self-views).
    if profile_user.id != current_user.id:
        db.add(ProfileView(profile_user_id=profile_user.id, viewer_user_id=current_user.id))
        db.commit()

    # Viewer stats for owner profile view.
    viewer_count = None
    recent_viewers = None
    if profile_user.id == current_user.id:
        viewer_count = db.query(ProfileView).filter(ProfileView.profile_user_id == current_user.id).count()
        recent_rows = (
            db.query(ProfileView, User, ProfileViewerSetting)
            .join(User, User.id == ProfileView.viewer_user_id)
            .outerjoin(ProfileViewerSetting, ProfileViewerSetting.user_id == ProfileView.viewer_user_id)
            .filter(ProfileView.profile_user_id == current_user.id)
            .order_by(ProfileView.created_at.desc())
            .limit(10)
            .all()
        )
        recent_viewers = []
        for view, viewer, setting in recent_rows:
            show_identity = True if not setting else setting.show_identity
            recent_viewers.append({
                "viewed_at": view.created_at,
                "viewer_id": viewer.id if show_identity else None,
                "viewer_name": f"{viewer.first_name or ''} {viewer.last_name or ''}".strip() if show_identity else "Anonymous viewer",
                "viewer_email": viewer.email if show_identity else None,
            })
    
    return {
        "id": profile_user.id,
        "first_name": profile_user.first_name,
        "last_name": profile_user.last_name,
        "headline": profile_user.headline,
        "location": profile_user.location,
        "bio": profile_user.bio,
        "profile_picture": profile_user.profile_picture,
        "role": profile_user.role.value,
        "created_at": profile_user.created_at,
        "viewer_count": viewer_count,
        "recent_viewers": recent_viewers,
    }
