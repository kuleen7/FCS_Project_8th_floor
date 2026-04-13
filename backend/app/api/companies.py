"""
Company Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import (
    CompanyCreate, CompanyUpdate, CompanyResponse, CompanyMemberCreate,
    CompanyMemberResponse, SuccessResponse
)
from ..services.company_service import company_service
from .auth import get_current_user
from app.schemas import UserResponse

router = APIRouter()


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new company
    
    - Users can create companies
    - Creator automatically becomes admin member
    """
    try:
        company = company_service.create_company(db, company_data, current_user.id)
        return CompanyResponse.from_orm(company)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create company"
        )


@router.get("/", response_model=List[CompanyResponse])
async def get_user_companies(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get companies where current user is a member
    """
    try:
        companies = company_service.get_companies_by_user(db, current_user.id)
        return [CompanyResponse.from_orm(company) for company in companies]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve companies"
        )


@router.get("/search", response_model=List[CompanyResponse])
async def search_companies(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Search companies by name or description
    """
    try:
        companies = company_service.search_companies(db, q, limit, offset)
        return [CompanyResponse.from_orm(company) for company in companies]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search companies"
        )


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Get company details by ID
    """
    try:
        company = company_service.get_company_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return CompanyResponse.from_orm(company)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company"
        )


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    update_data: CompanyUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update company details
    
    - Only company admins can update
    """
    try:
        company = company_service.update_company(db, company_id, update_data, current_user.id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return CompanyResponse.from_orm(company)
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
            detail="Failed to update company"
        )


@router.delete("/{company_id}", response_model=SuccessResponse)
async def delete_company(
    company_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a company (soft delete)
    
    - Only company creator can delete
    """
    try:
        success = company_service.delete_company(db, company_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        return SuccessResponse(message="Company deleted successfully")
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
            detail="Failed to delete company"
        )


@router.post("/{company_id}/members", response_model=CompanyMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_company_member(
    company_id: int,
    member_data: CompanyMemberCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a member to a company
    
    - Only company admins can add members
    """
    try:
        # Override company_id from URL
        member_data.company_id = company_id
        member = company_service.add_company_member(
            db, company_id, member_data.user_id, member_data.role
        )
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return CompanyMemberResponse.from_orm(member)
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
            detail="Failed to add company member"
        )


@router.get("/{company_id}/members", response_model=List[CompanyMemberResponse])
async def get_company_members(
    company_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all members of a company
    
    - Only company members can view
    """
    try:
        # Check if user is a member
        companies = company_service.get_companies_by_user(db, current_user.id)
        company_ids = [company.id for company in companies]
        
        if company_id not in company_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of this company"
            )
        
        members = company_service.get_company_members(db, company_id)
        return [CompanyMemberResponse.from_orm(member) for member in members]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company members"
        )


@router.delete("/{company_id}/members/{user_id}", response_model=SuccessResponse)
async def remove_company_member(
    company_id: int,
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a member from a company
    
    - Only company admins can remove members
    - Users can remove themselves
    """
    try:
        success = company_service.remove_company_member(db, company_id, user_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
        return SuccessResponse(message="Member removed successfully")
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
            detail="Failed to remove company member"
        )


@router.put("/{company_id}/members/{user_id}/role", response_model=SuccessResponse)
async def update_member_role(
    company_id: int,
    user_id: int,
    new_role: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update member role
    
    - Only company admins can update roles
    """
    try:
        success = company_service.update_member_role(db, company_id, user_id, new_role, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
        return SuccessResponse(message="Member role updated successfully")
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
            detail="Failed to update member role"
        )
