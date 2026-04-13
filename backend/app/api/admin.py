"""
Admin Dashboard API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import UserResponse, SuccessResponse
from ..services.user_service import user_service
from ..services.april_security_service import april_security_service
from ..models import UserRole
from .auth import get_current_user

router = APIRouter()


def require_admin(current_user: UserResponse = Depends(get_current_user)):
    """
    Dependency to require admin role
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Get all users (Admin only)
    
    - Lists all users in the system
    - Supports pagination and filtering
    """
    users = user_service.get_all_users(db, skip, limit, is_active)
    return [UserResponse.from_orm(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Get user details (Admin only)
    
    - Returns complete user information
    """
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.post("/users/{user_id}/suspend", response_model=SuccessResponse)
async def suspend_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Suspend user account (Admin only)
    
    - Deactivates user account
    - User cannot login while suspended
    """
    # Prevent self-suspension
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot suspend your own account"
        )

    payload_json = request.headers.get("X-Security-Payload")
    signature_b64 = request.headers.get("X-Security-Signature")
    challenge_id = request.headers.get("X-OTP-Challenge-ID")
    positions_header = request.headers.get("X-OTP-Positions", "")
    positions = [int(p.strip()) for p in positions_header.split(",") if p.strip() != ""]
    if not (payload_json and signature_b64 and challenge_id and positions):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="High-risk verification headers required for admin suspend",
        )
    ok, msg = april_security_service.verify_high_risk_action(
        db, admin_user.id, "admin.user.suspend", payload_json, signature_b64, challenge_id, positions
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    
    success = user_service.suspend_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(
        message="User suspended successfully",
        data={"user_id": user_id, "is_active": False}
    )


@router.post("/users/{user_id}/reactivate", response_model=SuccessResponse)
async def reactivate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Reactivate user account (Admin only)
    
    - Re-enables suspended user account
    """
    payload_json = request.headers.get("X-Security-Payload")
    signature_b64 = request.headers.get("X-Security-Signature")
    challenge_id = request.headers.get("X-OTP-Challenge-ID")
    positions_header = request.headers.get("X-OTP-Positions", "")
    positions = [int(p.strip()) for p in positions_header.split(",") if p.strip() != ""]
    if not (payload_json and signature_b64 and challenge_id and positions):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="High-risk verification headers required for admin reactivate",
        )
    ok, msg = april_security_service.verify_high_risk_action(
        db, admin_user.id, "admin.user.reactivate", payload_json, signature_b64, challenge_id, positions
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    success = user_service.reactivate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(
        message="User reactivated successfully",
        data={"user_id": user_id, "is_active": True}
    )


@router.delete("/users/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Delete user account (Admin only)
    
    - Soft delete by suspending account
    - Prevents accidental data loss
    """
    # Prevent self-deletion
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    payload_json = request.headers.get("X-Security-Payload")
    signature_b64 = request.headers.get("X-Security-Signature")
    challenge_id = request.headers.get("X-OTP-Challenge-ID")
    positions_header = request.headers.get("X-OTP-Positions", "")
    positions = [int(p.strip()) for p in positions_header.split(",") if p.strip() != ""]
    if not (payload_json and signature_b64 and challenge_id and positions):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="High-risk verification headers required for admin delete",
        )
    ok, msg = april_security_service.verify_high_risk_action(
        db, admin_user.id, "admin.user.delete", payload_json, signature_b64, challenge_id, positions
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    
    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return SuccessResponse(
        message="User deleted successfully",
        data={"user_id": user_id, "deleted": True}
    )


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Get dashboard statistics (Admin only)
    
    - Returns overview of platform statistics
    """
    from ..models import User
    from sqlalchemy import func
    
    # Count users by status
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    verified_users = db.query(func.count(User.id)).filter(User.is_verified == True).scalar()
    
    # Count by role
    user_count = db.query(func.count(User.id)).filter(User.role == UserRole.USER).scalar()
    recruiter_count = db.query(func.count(User.id)).filter(User.role == UserRole.RECRUITER).scalar()
    admin_count = db.query(func.count(User.id)).filter(User.role == UserRole.ADMIN).scalar()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "verified_users": verified_users,
        "suspended_users": total_users - active_users,
        "users_by_role": {
            "users": user_count,
            "recruiters": recruiter_count,
            "admins": admin_count
        }
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 50,
    db: Session = Depends(get_db),
    admin_user: UserResponse = Depends(require_admin)
):
    """
    Get recent user activity (Admin only)
    
    - Returns recent user registrations and logins
    """
    from ..models import User
    from sqlalchemy import desc
    
    # Get recent registrations
    recent_users = db.query(User).order_by(desc(User.created_at)).limit(limit).all()
    
    return {
        "recent_registrations": [
            {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at,
                "is_verified": user.is_verified,
                "is_active": user.is_active
            }
            for user in recent_users
        ]
    }
