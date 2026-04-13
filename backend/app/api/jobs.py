"""
Job Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil

from app.database import get_db
from app.schemas import (
    JobCreate, JobUpdate, JobResponse, JobSearchRequest, JobSearchResponse,
    SuccessResponse
)
from ..services.job_service import job_service
from ..services.april_security_service import april_security_service
from ..config import settings
from .auth import get_current_user
from app.schemas import UserResponse

router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new job posting
    
    - Only company admins and recruiters can post jobs
    """
    try:
        payload_json = request.headers.get("X-Security-Payload")
        signature_b64 = request.headers.get("X-Security-Signature")
        challenge_id = request.headers.get("X-OTP-Challenge-ID")
        positions_header = request.headers.get("X-OTP-Positions", "")
        positions = [int(p.strip()) for p in positions_header.split(",") if p.strip() != ""]
        if not (payload_json and signature_b64 and challenge_id and positions):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="High-risk verification headers required for job creation",
            )

        ok, msg = april_security_service.verify_high_risk_action(
            db,
            current_user.id,
            "job.create",
            payload_json,
            signature_b64,
            challenge_id,
            positions,
        )
        if not ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

        job = job_service.create_job(db, job_data, current_user.id)
        return JobResponse.from_orm(job)
    except HTTPException:
        raise
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create job posting: {str(e)}" if settings.DEBUG else "Failed to create job posting"
        )


@router.get("/search", response_model=JobSearchResponse)
async def search_jobs(
    keywords: Optional[str] = Query(None, description="Search keywords"),
    company: Optional[str] = Query(None, description="Company name"),
    location: Optional[str] = Query(None, description="Job location"),
    job_type: Optional[str] = Query(None, description="Job type"),
    salary_min: Optional[int] = Query(None, ge=0, description="Minimum salary"),
    salary_max: Optional[int] = Query(None, ge=0, description="Maximum salary"),
    is_featured: Optional[bool] = Query(None, description="Featured jobs only"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Search jobs with various filters
    """
    try:
        search_request = JobSearchRequest(
            keywords=keywords,
            company=company,
            location=location,
            job_type=job_type,
            salary_min=salary_min,
            salary_max=salary_max,
            is_featured=is_featured,
            page=page,
            limit=limit
        )
        
        jobs, total = job_service.search_jobs(db, search_request)
        total_pages = ceil(total / limit)
        
        return JobSearchResponse(
            jobs=[JobResponse.from_orm(job) for job in jobs],
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search jobs"
        )


@router.get("/featured", response_model=List[JobResponse])
async def get_featured_jobs(
    limit: int = Query(10, ge=1, le=50, description="Number of jobs to return"),
    db: Session = Depends(get_db)
):
    """
    Get featured job postings
    """
    try:
        jobs = job_service.get_featured_jobs(db, limit)
        return [JobResponse.from_orm(job) for job in jobs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve featured jobs"
        )


@router.get("/recent", response_model=List[JobResponse])
async def get_recent_jobs(
    limit: int = Query(10, ge=1, le=50, description="Number of jobs to return"),
    db: Session = Depends(get_db)
):
    """
    Get recent job postings
    """
    try:
        jobs = job_service.get_recent_jobs(db, limit)
        return [JobResponse.from_orm(job) for job in jobs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent jobs"
        )


@router.get("/my-postings", response_model=List[JobResponse])
async def get_my_postings(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get jobs posted by current user
    """
    try:
        jobs = job_service.get_jobs_by_poster(db, current_user.id)
        return [JobResponse.from_orm(job) for job in jobs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user's job postings"
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get job details by ID
    """
    try:
        job = job_service.get_job_by_id(db, job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        return JobResponse.from_orm(job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job"
        )


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    update_data: JobUpdate,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update job posting
    
    - Only job poster or company admin/recruiter can update
    """
    try:
        payload_json = request.headers.get("X-Security-Payload")
        signature_b64 = request.headers.get("X-Security-Signature")
        challenge_id = request.headers.get("X-OTP-Challenge-ID")
        positions_header = request.headers.get("X-OTP-Positions", "")
        positions = [int(p.strip()) for p in positions_header.split(",") if p.strip() != ""]
        if not (payload_json and signature_b64 and challenge_id and positions):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="High-risk verification headers required for job update",
            )

        ok, msg = april_security_service.verify_high_risk_action(
            db,
            current_user.id,
            "job.update",
            payload_json,
            signature_b64,
            challenge_id,
            positions,
        )
        if not ok:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

        job = job_service.update_job(db, job_id, update_data, current_user.id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        return JobResponse.from_orm(job)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update job posting"
        )


@router.delete("/{job_id}", response_model=SuccessResponse)
async def delete_job(
    job_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete job posting (soft delete)
    
    - Only job poster or company admin/recruiter can delete
    """
    try:
        success = job_service.delete_job(db, job_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        return SuccessResponse(message="Job posting deleted successfully")
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete job posting"
        )


@router.get("/company/{company_id}", response_model=List[JobResponse])
async def get_company_jobs(
    company_id: int,
    active_only: bool = Query(True, description="Show only active jobs"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get jobs for a specific company
    
    - Only company members can view all jobs (including inactive)
    - Public users can only view active jobs
    """
    try:
        # Check if user is company member
        from ..services.company_service import company_service
        user_companies = company_service.get_companies_by_user(db, current_user.id)
        company_ids = [company.id for company in user_companies]
        
        if company_id not in company_ids:
            # User is not a member, only show active jobs
            active_only = True
        
        jobs = job_service.get_jobs_by_company(db, company_id, active_only)
        return [JobResponse.from_orm(job) for job in jobs]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company jobs"
        )


@router.get("/statistics/overview", response_model=dict)
async def get_job_statistics(
    company_id: Optional[int] = Query(None, description="Company ID for company-specific stats"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get job statistics
    
    - Admins can view global statistics
    - Company members can view their company statistics
    """
    try:
        # Check permissions
        if company_id:
            from ..services.company_service import company_service
            user_companies = company_service.get_companies_by_user(db, current_user.id)
            company_ids = [company.id for company in user_companies]
            
            if company_id not in company_ids and current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission to view these statistics"
                )
        elif current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can view global statistics"
            )
        
        stats = job_service.get_job_statistics(db, company_id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job statistics"
        )
