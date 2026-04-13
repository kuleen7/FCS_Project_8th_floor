"""
Audit Logging Service with Tamper-Evident Hash Chaining
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
import hashlib
import json

from ..models import AuditLog, User


class AuditService:
    """Service for managing tamper-evident audit logs"""
    
    def log_action(
        self,
        db: Session,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Log an action with tamper-evident hash chaining"""
        
        # Get previous hash for chaining
        previous_log = (
            db.query(AuditLog)
            .order_by(desc(AuditLog.created_at))
            .first()
        )
        previous_hash = previous_log.current_hash if previous_log else None
        
        # Create log entry data
        log_data = {
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "previous_hash": previous_hash
        }
        
        # Generate current hash
        current_hash = self._generate_hash(log_data)
        
        # Create audit log entry
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address,
            user_agent=user_agent,
            previous_hash=previous_hash,
            current_hash=current_hash
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate SHA-256 hash for tamper evidence"""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def verify_log_integrity(self, db: Session, start_id: Optional[int] = None, end_id: Optional[int] = None) -> Dict[str, Any]:
        """Verify the integrity of audit logs using hash chaining"""
        query = db.query(AuditLog)
        
        if start_id:
            query = query.filter(AuditLog.id >= start_id)
        if end_id:
            query = query.filter(AuditLog.id <= end_id)
        
        logs = query.order_by(AuditLog.created_at).all()
        
        if not logs:
            return {"valid": True, "message": "No logs to verify"}
        
        violations = []
        previous_hash = None
        
        for log in logs:
            # Recreate hash to verify
            log_data = {
                "user_id": log.user_id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": json.loads(log.details) if log.details else {},
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "timestamp": log.created_at.isoformat(),
                "previous_hash": previous_hash
            }
            
            expected_hash = self._generate_hash(log_data)
            
            if log.current_hash != expected_hash:
                violations.append({
                    "log_id": log.id,
                    "expected_hash": expected_hash,
                    "actual_hash": log.current_hash,
                    "created_at": log.created_at
                })
            
            # Check hash chaining
            if previous_hash and log.previous_hash != previous_hash:
                violations.append({
                    "log_id": log.id,
                    "type": "chain_violation",
                    "expected_previous": previous_hash,
                    "actual_previous": log.previous_hash,
                    "created_at": log.created_at
                })
            
            previous_hash = log.current_hash
        
        return {
            "valid": len(violations) == 0,
            "total_logs": len(logs),
            "violations": violations,
            "message": f"Verified {len(logs)} logs, found {len(violations)} violations"
        }
    
    def get_audit_logs(
        self,
        db: Session,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 50
    ) -> tuple[list[AuditLog], int]:
        """Get audit logs with filtering"""
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        logs = (
            query
            .order_by(desc(AuditLog.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        return logs, total
    
    def get_user_activity_summary(
        self,
        db: Session,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get activity summary for a user"""
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total actions
        total_actions = (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .filter(AuditLog.created_at >= start_date)
            .count()
        )
        
        # Actions by type
        actions_by_type = (
            db.query(AuditLog.action, func.count(AuditLog.id))
            .filter(AuditLog.user_id == user_id)
            .filter(AuditLog.created_at >= start_date)
            .group_by(AuditLog.action)
            .all()
        )
        
        # Resources accessed
        resources_accessed = (
            db.query(AuditLog.resource_type, func.count(AuditLog.id))
            .filter(AuditLog.user_id == user_id)
            .filter(AuditLog.created_at >= start_date)
            .filter(AuditLog.resource_type.isnot(None))
            .group_by(AuditLog.resource_type)
            .all()
        )
        
        return {
            "user_id": user_id,
            "period_days": days,
            "total_actions": total_actions,
            "actions_by_type": dict(actions_by_type),
            "resources_accessed": dict(resources_accessed)
        }
    
    def get_system_activity_summary(
        self,
        db: Session,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get system-wide activity summary"""
        from sqlalchemy import func
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total actions
        total_actions = (
            db.query(AuditLog)
            .filter(AuditLog.created_at >= start_date)
            .count()
        )
        
        # Actions by type
        actions_by_type = (
            db.query(AuditLog.action, func.count(AuditLog.id))
            .filter(AuditLog.created_at >= start_date)
            .group_by(AuditLog.action)
            .all()
        )
        
        # Active users
        active_users = (
            db.query(func.count(func.distinct(AuditLog.user_id)))
            .filter(AuditLog.created_at >= start_date)
            .filter(AuditLog.user_id.isnot(None))
            .scalar()
        )
        
        # Top resource types
        top_resources = (
            db.query(AuditLog.resource_type, func.count(AuditLog.id))
            .filter(AuditLog.created_at >= start_date)
            .filter(AuditLog.resource_type.isnot(None))
            .group_by(AuditLog.resource_type)
            .order_by(desc(func.count(AuditLog.id)))
            .limit(10)
            .all()
        )
        
        return {
            "period_days": days,
            "total_actions": total_actions,
            "active_users": active_users,
            "actions_by_type": dict(actions_by_type),
            "top_resources": dict(top_resources)
        }


# Create singleton instance
audit_service = AuditService()
