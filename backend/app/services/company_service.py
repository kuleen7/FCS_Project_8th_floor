"""
Company Management Service
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models import Company, CompanyMember, User, UserRole
from ..schemas import CompanyCreate, CompanyUpdate, CompanyMemberCreate


class CompanyService:
    """Service for managing companies and their members"""
    
    def create_company(self, db: Session, company_data: CompanyCreate, creator_id: int) -> Optional[Company]:
        """Create a new company"""
        try:
            company = Company(
                **company_data.dict(),
                created_by=creator_id
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            
            # Add creator as admin member
            self.add_company_member(
                db, company.id, creator_id, "admin"
            )
            
            return company
        except Exception as e:
            db.rollback()
            raise e
    
    def get_company_by_id(self, db: Session, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        return db.query(Company).filter(Company.id == company_id).first()
    
    def get_companies_by_user(self, db: Session, user_id: int) -> List[Company]:
        """Get companies where user is a member"""
        return (
            db.query(Company)
            .join(CompanyMember)
            .filter(CompanyMember.user_id == user_id)
            .filter(CompanyMember.is_active == True)
            .filter(Company.is_active == True)
            .all()
        )
    
    def update_company(self, db: Session, company_id: int, update_data: CompanyUpdate, user_id: int) -> Optional[Company]:
        """Update company details"""
        company = self.get_company_by_id(db, company_id)
        if not company:
            return None
        
        # Check if user has permission (admin or creator)
        if not self._has_company_permission(db, company_id, user_id, ["admin"]):
            raise PermissionError("User does not have permission to update this company")
        
        try:
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(company, field, value)
            
            db.commit()
            db.refresh(company)
            return company
        except Exception as e:
            db.rollback()
            raise e
    
    def delete_company(self, db: Session, company_id: int, user_id: int) -> bool:
        """Delete company (soft delete)"""
        company = self.get_company_by_id(db, company_id)
        if not company:
            return False
        
        # Only creator can delete company
        if company.created_by != user_id:
            raise PermissionError("Only company creator can delete the company")
        
        try:
            company.is_active = False
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def add_company_member(self, db: Session, company_id: int, user_id: int, role: str = "member") -> Optional[CompanyMember]:
        """Add a member to a company"""
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Check if already a member
        existing_member = (
            db.query(CompanyMember)
            .filter(
                and_(
                    CompanyMember.company_id == company_id,
                    CompanyMember.user_id == user_id
                )
            )
            .first()
        )
        
        if existing_member:
            # Reactivate if inactive
            if not existing_member.is_active:
                existing_member.is_active = True
                existing_member.role = role
                db.commit()
                db.refresh(existing_member)
            return existing_member
        
        try:
            member = CompanyMember(
                company_id=company_id,
                user_id=user_id,
                role=role
            )
            db.add(member)
            db.commit()
            db.refresh(member)
            return member
        except Exception as e:
            db.rollback()
            raise e
    
    def remove_company_member(self, db: Session, company_id: int, user_id: int, remover_id: int) -> bool:
        """Remove a member from a company"""
        # Check permissions
        if not self._has_company_permission(db, company_id, remover_id, ["admin"]):
            raise PermissionError("User does not have permission to remove members")
        
        member = (
            db.query(CompanyMember)
            .filter(
                and_(
                    CompanyMember.company_id == company_id,
                    CompanyMember.user_id == user_id
                )
            )
            .first()
        )
        
        if not member:
            return False
        
        try:
            member.is_active = False
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def get_company_members(self, db: Session, company_id: int) -> List[CompanyMember]:
        """Get all active members of a company"""
        return (
            db.query(CompanyMember)
            .filter(CompanyMember.company_id == company_id)
            .filter(CompanyMember.is_active == True)
            .all()
        )
    
    def update_member_role(self, db: Session, company_id: int, user_id: int, new_role: str, updater_id: int) -> bool:
        """Update member role"""
        # Check permissions
        if not self._has_company_permission(db, company_id, updater_id, ["admin"]):
            raise PermissionError("User does not have permission to update member roles")
        
        member = (
            db.query(CompanyMember)
            .filter(
                and_(
                    CompanyMember.company_id == company_id,
                    CompanyMember.user_id == user_id
                )
            )
            .first()
        )
        
        if not member:
            return False
        
        try:
            member.role = new_role
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
    
    def search_companies(self, db: Session, query: str, limit: int = 20, offset: int = 0) -> List[Company]:
        """Search companies by name or description"""
        return (
            db.query(Company)
            .filter(
                and_(
                    Company.is_active == True,
                    or_(
                        Company.name.ilike(f"%{query}%"),
                        Company.description.ilike(f"%{query}%")
                    )
                )
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    def _has_company_permission(self, db: Session, company_id: int, user_id: int, required_roles: List[str]) -> bool:
        """Check if user has required role in company"""
        # Check if user is company creator
        company = self.get_company_by_id(db, company_id)
        if company and company.created_by == user_id:
            return True
        
        # Check user role in company
        member = (
            db.query(CompanyMember)
            .filter(
                and_(
                    CompanyMember.company_id == company_id,
                    CompanyMember.user_id == user_id,
                    CompanyMember.is_active == True,
                    CompanyMember.role.in_(required_roles)
                )
            )
            .first()
        )
        
        return member is not None


# Create singleton instance
company_service = CompanyService()
