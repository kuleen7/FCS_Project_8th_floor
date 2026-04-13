"""
Application Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil

from app.database import get_db
from app.schemas import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse, SuccessResponse
)
from ..services.application_service import application_service
from ..services.company_service import company_service
from ..models import Application, Job
from .auth import get_current_user
from app.schemas import UserResponse

router = APIRouter()


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_to_job(
    application_data: ApplicationCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply to a job
    
    - Users can apply to active jobs
    - Cannot apply to the same job multiple times
    """
    try:
        application = application_service.create_application(db, application_data, current_user.id)
        return ApplicationResponse.from_orm(application)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit application"
        )


@router.get("/my-applications", response_model=List[ApplicationResponse])
async def get_my_applications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get applications submitted by current user
    """
    try:
        applications, total = application_service.get_applications_by_applicant(
            db, current_user.id, page, limit
        )
        return [ApplicationResponse.from_orm(app) for app in applications]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve applications"
        )


@router.get("/recruiter/my-applicants", response_model=List[ApplicationResponse])
async def get_my_recruiter_applicants(
    job_id: Optional[int] = Query(None, description="Optional job filter"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get applicants visible to the current recruiter/admin.

    Includes:
    - applications for jobs posted by the current user
    - applications for jobs in companies where user is admin/recruiter
    """
    try:
        if current_user.role not in ["recruiter", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only recruiters/admins can view recruiter applicants"
            )

        user_companies = company_service.get_companies_by_user(db, current_user.id)
        company_ids = [company.id for company in user_companies]

        query = db.query(Application).join(Job)
        query = query.filter(
            (Job.posted_by == current_user.id) |
            (Job.company_id.in_(company_ids) if company_ids else False)
        )

        if job_id:
            query = query.filter(Application.job_id == job_id)

        applications = (
            query
            .order_by(Application.applied_at.desc())
            .limit(500)
            .all()
        )
        return [ApplicationResponse.from_orm(app) for app in applications]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recruiter applicants"
        )


@router.get("/job/{job_id}", response_model=List[ApplicationResponse])
async def get_job_applications(
    job_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get applications for a specific job
    
    - Only company admins and recruiters can view job applications
    """
    try:
        applications, total = application_service.get_applications_by_job(
            db, job_id, current_user.id, page, limit
        )
        return [ApplicationResponse.from_orm(app) for app in applications]
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job applications"
        )


@router.get("/shortlisted", response_model=List[ApplicationResponse])
async def get_shortlisted_applications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get shortlisted applications
    
    - Only company admins and recruiters can view shortlisted applications
    """
    try:
        applications, total = application_service.get_shortlisted_applications(
            db, current_user.id, page, limit
        )
        return [ApplicationResponse.from_orm(app) for app in applications]
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve shortlisted applications"
        )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get application details by ID
    
    - Applicants can view their own applications
    - Company admins/recruiters can view applications for their jobs
    """
    try:
        application = application_service.get_application_by_id(db, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Check permissions
        if application.applicant_id != current_user.id:
            # Check if user has permission to view this application
            if not application_service._can_update_application(db, application, current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission to view this application"
                )
        
        return ApplicationResponse.from_orm(application)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve application"
        )


@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: int,
    update_data: ApplicationUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update application status and notes
    
    - Only company admins and recruiters can update applications
    """
    try:
        application = application_service.update_application(
            db, application_id, update_data, current_user.id
        )
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        return ApplicationResponse.from_orm(application)
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
            detail="Failed to update application"
        )


@router.delete("/{application_id}/withdraw", response_model=SuccessResponse)
async def withdraw_application(
    application_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Withdraw an application
    
    - Only the applicant can withdraw their application
    - Cannot withdraw if already rejected or offered
    """
    try:
        success = application_service.withdraw_application(db, application_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        return SuccessResponse(message="Application withdrawn successfully")
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
            detail="Failed to withdraw application"
        )


@router.post("/bulk-update", response_model=SuccessResponse)
async def bulk_update_applications(
    application_ids: List[int],
    new_status: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk update application status
    
    - Only company admins and recruiters can bulk update
    """
    try:
        from app.schemas import ApplicationStatus
        status_enum = ApplicationStatus(new_status)
        
        updated_count = application_service.bulk_update_status(
            db, application_ids, status_enum, current_user.id
        )
        return SuccessResponse(
            message=f"Updated {updated_count} applications successfully",
            data={"updated_count": updated_count}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {str(e)}"
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to bulk update applications"
        )


@router.get("/search/advanced", response_model=List[ApplicationResponse])
async def search_applications(
    keywords: Optional[str] = Query(None, description="Search keywords"),
    status: Optional[str] = Query(None, description="Application status"),
    is_shortlisted: Optional[bool] = Query(None, description="Shortlisted applications only"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Advanced search for applications
    
    - Only company admins and recruiters can search applications
    """
    try:
        from app.schemas import ApplicationStatus
        
        status_enum = None
        if status:
            status_enum = ApplicationStatus(status)
        
        applications, total = application_service.search_applications(
            db, current_user.id, keywords, status_enum, is_shortlisted, page, limit
        )
        return [ApplicationResponse.from_orm(app) for app in applications]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {str(e)}"
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search applications"
        )


@router.get("/statistics/overview", response_model=dict)
async def get_application_statistics(
    job_id: Optional[int] = Query(None, description="Job ID for job-specific stats"),
    company_id: Optional[int] = Query(None, description="Company ID for company-specific stats"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get application statistics
    
    - Admins can view global statistics
    - Company members can view their company statistics
    - Job posters can view their job statistics
    """
    try:
        # Check permissions based on parameters
        if job_id:
            # Check if user can view this job's applications
            from ..services.job_service import job_service
            job = job_service.get_job_by_id(db, job_id)
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found"
                )
            
            if not application_service._can_update_application(db, type('obj', (object,), {'job_id': job_id, 'applicant_id': None})(), current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission to view these statistics"
                )
        
        elif company_id:
            # Check if user is company member
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
        
        stats = application_service.get_application_statistics(db, job_id, company_id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve application statistics"
        )
