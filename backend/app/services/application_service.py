"""
Application Management Service
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime

from ..models import Application, Job, User, ApplicationStatus
from ..schemas import ApplicationCreate, ApplicationUpdate


class ApplicationService:
    """Service for managing job applications"""
    
    def create_application(self, db: Session, application_data: ApplicationCreate, applicant_id: int) -> Optional[Application]:
        """Create a new job application"""
        # Check if user can apply to this job
        from .job_service import job_service
        if not job_service.can_user_apply(db, application_data.job_id, applicant_id):
            raise PermissionError("User cannot apply to this job")
        
        try:
            application = Application(
                **application_data.dict(),
                applicant_id=applicant_id,
                status=ApplicationStatus.APPLIED
            )
            db.add(application)
            db.commit()
            db.refresh(application)
            return application
        except Exception as e:
            db.rollback()
            raise e
    
    def get_application_by_id(self, db: Session, application_id: int) -> Optional[Application]:
        """Get application by ID"""
        return db.query(Application).filter(Application.id == application_id).first()
    
    def update_application(self, db: Session, application_id: int, update_data: ApplicationUpdate, user_id: int) -> Optional[Application]:
        """Update application status and notes (for recruiters)"""
        application = self.get_application_by_id(db, application_id)
        if not application:
            return None
        
        # Check if user has permission to update this application
        if not self._can_update_application(db, application, user_id):
            raise PermissionError("User does not have permission to update this application")
        
        try:
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(application, field, value)
            
            application.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(application)
            return application
        except Exception as e:
            db.rollback()
            raise e
    
    def withdraw_application(self, db: Session, application_id: int, applicant_id: int) -> bool:
        """Withdraw an application (applicant only)"""
        application = self.get_application_by_id(db, application_id)
        if not application:
            return False
        
        if application.applicant_id != applicant_id:
            raise PermissionError("Only the applicant can withdraw their application")
        
        # Can only withdraw if not already rejected or offered
        if application.status in [ApplicationStatus.REJECTED, ApplicationStatus.OFFER]:
            raise PermissionError("Cannot withdraw application in current status")
        
        try:
            application.status = ApplicationStatus.REJECTED
            application.recruiter_notes = "Withdrawn by applicant"
            application.updated_at = datetime.utcnow()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def get_applications_by_job(self, db: Session, job_id: int, user_id: int, page: int = 1, limit: int = 20) -> Tuple[List[Application], int]:
        """Get applications for a job (recruiters only)"""
        # Check if user has permission to view applications for this job
        from .job_service import job_service
        job = job_service.get_job_by_id(db, job_id)
        if not job:
            return [], 0
        
        from .company_service import company_service
        if not company_service._has_company_permission(db, job.company_id, user_id, ["admin", "recruiter"]):
            raise PermissionError("User does not have permission to view applications for this job")
        
        query = (
            db.query(Application)
            .filter(Application.job_id == job_id)
            .join(User)
            .join(Job)
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        applications = (
            query
            .order_by(desc(Application.is_shortlisted), desc(Application.applied_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        return applications, total
    
    def get_applications_by_applicant(self, db: Session, applicant_id: int, page: int = 1, limit: int = 20) -> Tuple[List[Application], int]:
        """Get applications submitted by a user"""
        query = (
            db.query(Application)
            .filter(Application.applicant_id == applicant_id)
            .join(Job)
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        applications = (
            query
            .order_by(desc(Application.applied_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        return applications, total
    
    def get_shortlisted_applications(self, db: Session, user_id: int, page: int = 1, limit: int = 20) -> Tuple[List[Application], int]:
        """Get shortlisted applications for recruiters"""
        # Get companies where user has permission
        from .company_service import company_service
        user_companies = company_service.get_companies_by_user(db, user_id)
        company_ids = [company.id for company in user_companies]
        
        if not company_ids:
            return [], 0
        
        query = (
            db.query(Application)
            .filter(Application.is_shortlisted == True)
            .join(Job)
            .filter(Job.company_id.in_(company_ids))
            .join(User)
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        applications = (
            query
            .order_by(desc(Application.updated_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        return applications, total
    
    def get_application_statistics(self, db: Session, job_id: Optional[int] = None, company_id: Optional[int] = None) -> dict:
        """Get application statistics"""
        query = db.query(Application).join(Job)
        
        if job_id:
            query = query.filter(Application.job_id == job_id)
        elif company_id:
            query = query.filter(Job.company_id == company_id)
        
        # Total applications
        total_applications = query.count()
        
        # Applications by status
        status_distribution = (
            query
            .with_entities(Application.status, func.count(Application.id))
            .group_by(Application.status)
            .all()
        )
        
        # Shortlisted applications
        shortlisted_count = query.filter(Application.is_shortlisted == True).count()
        
        return {
            "total_applications": total_applications,
            "shortlisted_count": shortlisted_count,
            "status_distribution": dict(status_distribution)
        }
    
    def bulk_update_status(self, db: Session, application_ids: List[int], new_status: ApplicationStatus, user_id: int) -> int:
        """Bulk update application status (for recruiters)"""
        if not application_ids:
            return 0
        
        # Verify user has permission for all applications
        applications = (
            db.query(Application)
            .filter(Application.id.in_(application_ids))
            .join(Job)
            .all()
        )
        
        from .company_service import company_service
        for application in applications:
            if not self._can_update_application(db, application, user_id):
                raise PermissionError("User does not have permission to update some applications")
        
        try:
            updated_count = (
                db.query(Application)
                .filter(Application.id.in_(application_ids))
                .update({
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                }, synchronize_session=False)
            )
            db.commit()
            return updated_count
        except Exception as e:
            db.rollback()
            raise e
    
    def search_applications(self, db: Session, user_id: int, keywords: Optional[str] = None, 
                          status: Optional[ApplicationStatus] = None, is_shortlisted: Optional[bool] = None,
                          page: int = 1, limit: int = 20) -> Tuple[List[Application], int]:
        """Search applications with filters (for recruiters)"""
        # Get companies where user has permission
        from .company_service import company_service
        user_companies = company_service.get_companies_by_user(db, user_id)
        company_ids = [company.id for company in user_companies]
        
        if not company_ids:
            return [], 0
        
        query = (
            db.query(Application)
            .join(Job)
            .filter(Job.company_id.in_(company_ids))
            .join(User)
        )
        
        # Apply filters
        if keywords:
            keyword_filter = or_(
                User.first_name.ilike(f"%{keywords}%"),
                User.last_name.ilike(f"%{keywords}%"),
                User.email.ilike(f"%{keywords}%"),
                Application.cover_note.ilike(f"%{keywords}%"),
                Application.recruiter_notes.ilike(f"%{keywords}%")
            )
            query = query.filter(keyword_filter)
        
        if status:
            query = query.filter(Application.status == status)
        
        if is_shortlisted is not None:
            query = query.filter(Application.is_shortlisted == is_shortlisted)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        applications = (
            query
            .order_by(desc(Application.updated_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        
        return applications, total
    
    def _can_update_application(self, db: Session, application: Application, user_id: int) -> bool:
        """Check if user can update application"""
        # Check if user is the job poster or has company permission
        from .job_service import job_service
        job = job_service.get_job_by_id(db, application.job_id)
        if not job:
            return False
        
        # Job poster can update
        if job.posted_by == user_id:
            return True
        
        # Company admin/recruiter can update
        from .company_service import company_service
        return company_service._has_company_permission(db, job.company_id, user_id, ["admin", "recruiter"])


# Create singleton instance
application_service = ApplicationService()
