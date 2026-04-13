"""
Job Management Service
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime

from ..models import Job, Company, Application, User, JobType
from ..schemas import JobCreate, JobUpdate, JobSearchRequest


class JobService:
    """Service for managing job postings"""

    def _normalize_job_payload(self, payload: dict) -> dict:
        """Normalize schema enum values to model enum values."""
        job_type = payload.get("job_type")
        if job_type is None:
            return payload

        # Handle pydantic enum from schemas, plain string, or model enum.
        if hasattr(job_type, "value"):
            job_type_value = job_type.value
        else:
            job_type_value = str(job_type)

        payload["job_type"] = JobType(job_type_value)
        return payload
    
    def create_job(self, db: Session, job_data: JobCreate, poster_id: int) -> Optional[Job]:
        """Create a new job posting"""
        # Check if user has permission to post for this company
        from .company_service import company_service
        if not company_service._has_company_permission(db, job_data.company_id, poster_id, ["admin", "recruiter"]):
            raise PermissionError("User does not have permission to post jobs for this company")
        
        try:
            payload = self._normalize_job_payload(job_data.dict(exclude={'company_id'}))
            job = Job(
                **payload,
                company_id=job_data.company_id,
                posted_by=poster_id
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            return job
        except Exception as e:
            db.rollback()
            raise e
    
    def get_job_by_id(self, db: Session, job_id: int) -> Optional[Job]:
        """Get job by ID"""
        return (
            db.query(Job)
            .filter(Job.id == job_id)
            .filter(Job.is_active == True)
            .first()
        )
    
    def update_job(self, db: Session, job_id: int, update_data: JobUpdate, user_id: int) -> Optional[Job]:
        """Update job posting"""
        job = self.get_job_by_id(db, job_id)
        if not job:
            return None
        
        # Check if user has permission to update this job
        from .company_service import company_service
        if not company_service._has_company_permission(db, job.company_id, user_id, ["admin", "recruiter"]):
            raise PermissionError("User does not have permission to update this job")
        
        try:
            update_dict = update_data.dict(exclude_unset=True)
            update_dict = self._normalize_job_payload(update_dict)
            for field, value in update_dict.items():
                setattr(job, field, value)
            
            db.commit()
            db.refresh(job)
            return job
        except Exception as e:
            db.rollback()
            raise e
    
    def delete_job(self, db: Session, job_id: int, user_id: int) -> bool:
        """Delete job posting (soft delete)"""
        job = self.get_job_by_id(db, job_id)
        if not job:
            return False
        
        # Check if user has permission to delete this job
        from .company_service import company_service
        if not company_service._has_company_permission(db, job.company_id, user_id, ["admin", "recruiter"]):
            raise PermissionError("User does not have permission to delete this job")
        
        try:
            job.is_active = False
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def search_jobs(self, db: Session, search_request: JobSearchRequest) -> Tuple[List[Job], int]:
        """Search jobs with filters"""
        query = (
            db.query(Job)
            .join(Company)
            .filter(Job.is_active == True)
            .filter(Company.is_active == True)
        )
        
        # Apply filters
        if search_request.keywords:
            keyword_filter = or_(
                Job.title.ilike(f"%{search_request.keywords}%"),
                Job.description.ilike(f"%{search_request.keywords}%"),
                Job.required_skills.ilike(f"%{search_request.keywords}%")
            )
            query = query.filter(keyword_filter)
        
        if search_request.company:
            query = query.filter(Company.name.ilike(f"%{search_request.company}%"))
        
        if search_request.location:
            query = query.filter(
                or_(
                    Job.location.ilike(f"%{search_request.location}%"),
                    Company.location.ilike(f"%{search_request.location}%")
                )
            )
        
        if search_request.job_type:
            query = query.filter(Job.job_type == search_request.job_type)
        
        if search_request.salary_min:
            query = query.filter(Job.salary_min >= search_request.salary_min)
        
        if search_request.salary_max:
            query = query.filter(Job.salary_max <= search_request.salary_max)
        
        if search_request.is_featured is not None:
            query = query.filter(Job.is_featured == search_request.is_featured)
        
        # Filter out expired jobs
        query = query.filter(
            or_(
                Job.application_deadline.is_(None),
                Job.application_deadline > datetime.utcnow()
            )
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        jobs = (
            query
            .order_by(desc(Job.is_featured), desc(Job.created_at))
            .offset((search_request.page - 1) * search_request.limit)
            .limit(search_request.limit)
            .all()
        )
        
        return jobs, total
    
    def get_jobs_by_company(self, db: Session, company_id: int, active_only: bool = True) -> List[Job]:
        """Get jobs for a specific company"""
        query = db.query(Job).filter(Job.company_id == company_id)
        
        if active_only:
            query = query.filter(Job.is_active == True)
        
        return query.order_by(desc(Job.created_at)).all()
    
    def get_jobs_by_poster(self, db: Session, poster_id: int, active_only: bool = True) -> List[Job]:
        """Get jobs posted by a specific user"""
        query = db.query(Job).filter(Job.posted_by == poster_id)
        
        if active_only:
            query = query.filter(Job.is_active == True)
        
        return query.order_by(desc(Job.created_at)).all()
    
    def get_featured_jobs(self, db: Session, limit: int = 10) -> List[Job]:
        """Get featured jobs"""
        return (
            db.query(Job)
            .join(Company)
            .filter(Job.is_active == True)
            .filter(Job.is_featured == True)
            .filter(Company.is_active == True)
            .filter(
                or_(
                    Job.application_deadline.is_(None),
                    Job.application_deadline > datetime.utcnow()
                )
            )
            .order_by(desc(Job.created_at))
            .limit(limit)
            .all()
        )
    
    def get_recent_jobs(self, db: Session, limit: int = 10) -> List[Job]:
        """Get recent job postings"""
        return (
            db.query(Job)
            .join(Company)
            .filter(Job.is_active == True)
            .filter(Company.is_active == True)
            .filter(
                or_(
                    Job.application_deadline.is_(None),
                    Job.application_deadline > datetime.utcnow()
                )
            )
            .order_by(desc(Job.created_at))
            .limit(limit)
            .all()
        )
    
    def get_job_statistics(self, db: Session, company_id: Optional[int] = None) -> dict:
        """Get job statistics"""
        query = db.query(Job).join(Company)
        
        if company_id:
            query = query.filter(Job.company_id == company_id)
        
        total_jobs = query.filter(Job.is_active == True).count()
        featured_jobs = query.filter(Job.is_featured == True).filter(Job.is_active == True).count()
        
        # Get job type distribution
        job_types = (
            query
            .filter(Job.is_active == True)
            .with_entities(Job.job_type, func.count(Job.id))
            .group_by(Job.job_type)
            .all()
        )
        
        return {
            "total_jobs": total_jobs,
            "featured_jobs": featured_jobs,
            "job_type_distribution": dict(job_types)
        }
    
    def can_user_apply(self, db: Session, job_id: int, user_id: int) -> bool:
        """Check if user can apply to a job"""
        # Check if job exists and is active
        job = self.get_job_by_id(db, job_id)
        if not job:
            return False
        
        # Check if application deadline has passed
        if job.application_deadline and job.application_deadline < datetime.utcnow():
            return False
        
        # Check if user has already applied
        existing_application = (
            db.query(Application)
            .filter(
                and_(
                    Application.job_id == job_id,
                    Application.applicant_id == user_id
                )
            )
            .first()
        )
        
        return existing_application is None


# Create singleton instance
job_service = JobService()
