"""
Audit Log API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.schemas import SuccessResponse
from ..services.audit_service import audit_service
from .auth import get_current_user
from app.schemas import UserResponse

router = APIRouter()


@router.get("/logs", response_model=dict)
async def get_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[int] = Query(None, description="Filter by resource ID"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with filtering
    
    - Only admins can view all logs
    - Users can only view their own logs
    """
    try:
        # Check permissions
        if current_user.role != "admin":
            # Non-admin users can only view their own logs
            if user_id and user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Users can only view their own audit logs"
                )
            user_id = current_user.id
        
        logs, total = audit_service.get_audit_logs(
            db, user_id, action, resource_type, resource_id,
            start_date, end_date, page, limit
        )
        
        # Convert logs to dict format
        log_list = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "previous_hash": log.previous_hash,
                "current_hash": log.current_hash,
                "created_at": log.created_at
            }
            log_list.append(log_dict)
        
        return {
            "logs": log_list,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


@router.get("/integrity", response_model=dict)
async def verify_log_integrity(
    start_id: Optional[int] = Query(None, description="Start log ID"),
    end_id: Optional[int] = Query(None, description="End log ID"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify the integrity of audit logs using hash chaining
    
    - Only admins can verify log integrity
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can verify log integrity"
        )
    
    try:
        result = audit_service.verify_log_integrity(db, start_id, end_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify log integrity"
        )


@router.get("/summary/user/{user_id}", response_model=dict)
async def get_user_activity_summary(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get activity summary for a specific user
    
    - Admins can view any user's summary
    - Users can only view their own summary
    """
    try:
        # Check permissions
        if current_user.role != "admin" and user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users can only view their own activity summary"
            )
        
        summary = audit_service.get_user_activity_summary(db, user_id, days)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user activity summary"
        )


@router.get("/summary/system", response_model=dict)
async def get_system_activity_summary(
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system-wide activity summary
    
    - Only admins can view system summary
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view system activity summary"
        )
    
    try:
        summary = audit_service.get_system_activity_summary(db, days)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system activity summary"
        )


@router.get("/actions", response_model=List[str])
async def get_available_actions(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of available action types for filtering
    
    - Only admins can view all actions
    - Users can view common actions
    """
    try:
        from sqlalchemy import func
        
        query = db.query(audit_service.models.AuditLog.action, func.count(audit_service.models.AuditLog.id))
        
        if current_user.role != "admin":
            # Non-admins only see their own actions
            query = query.filter(audit_service.models.AuditLog.user_id == current_user.id)
        
        actions = query.group_by(audit_service.models.AuditLog.action).all()
        return [action[0] for action in actions]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available actions"
        )


@router.get("/resources", response_model=List[str])
async def get_available_resources(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of available resource types for filtering
    
    - Only admins can view all resources
    - Users can view resources they've accessed
    """
    try:
        from sqlalchemy import func
        
        query = db.query(audit_service.models.AuditLog.resource_type, func.count(audit_service.models.AuditLog.id))
        
        if current_user.role != "admin":
            # Non-admins only see their own resources
            query = query.filter(audit_service.models.AuditLog.user_id == current_user.id)
        
        resources = query.filter(audit_service.models.AuditLog.resource_type.isnot(None)).group_by(audit_service.models.AuditLog.resource_type).all()
        return [resource[0] for resource in resources if resource[0]]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available resources"
        )
