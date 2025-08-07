from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Dict, Optional
from app.models import Employee, Organization, OrganizationColumnConfig
from app.schemas import EmployeeSearchRequest, EmployeeStatus
import logging

logger = logging.getLogger(__name__)

class EmployeeService:
    """Service class for employee-related operations"""
    
    @staticmethod
    def get_organization_column_config(db: Session, organization_id: int) -> List[Dict]:
        """Get column configuration for an organization"""
        configs = db.query(OrganizationColumnConfig).filter(
            OrganizationColumnConfig.organization_id == organization_id,
            OrganizationColumnConfig.is_visible == True
        ).order_by(OrganizationColumnConfig.display_order).all()
        
        return [
            {
                "column_name": config.column_name,
                "display_order": config.display_order,
                "is_visible": config.is_visible
            }
            for config in configs
        ]
    
    @staticmethod
    def search_employees(db: Session, search_request: EmployeeSearchRequest) -> Dict:
        """
        Search employees with advanced filtering and pagination.
        Optimized for millions of records with proper indexing.
        """
        query = db.query(Employee).filter(Employee.organization_id == search_request.organization_id)
        
        # Apply search filter
        if search_request.search:
            search_term = f"%{search_request.search}%"
            query = query.filter(
                or_(
                    Employee.first_name.ilike(search_term),
                    Employee.last_name.ilike(search_term),
                    Employee.email.ilike(search_term)
                )
            )
        
        # Apply status filter
        if search_request.status:
            status_values = [status.value for status in search_request.status]
            query = query.filter(Employee.status.in_(status_values))
        elif not search_request.include_terminated:
            # Exclude terminated by default unless explicitly included
            query = query.filter(Employee.status != EmployeeStatus.TERMINATED.value)
        
        # Apply location filter
        if search_request.locations:
            query = query.filter(Employee.location.in_(search_request.locations))
        
        # Apply company filter
        if search_request.companies:
            query = query.filter(Employee.company.in_(search_request.companies))
        
        # Apply department filter
        if search_request.departments:
            query = query.filter(Employee.department.in_(search_request.departments))
        
        # Apply position filter
        if search_request.positions:
            query = query.filter(Employee.position.in_(search_request.positions))
        
        # Get total count for pagination
        total_count = query.count()
        
        # Order by most recent first (BEFORE pagination)
        query = query.order_by(desc(Employee.updated_at))
        
        # Apply pagination (AFTER ordering)
        offset = (search_request.page - 1) * search_request.page_size
        query = query.offset(offset).limit(search_request.page_size)
        
        # Execute query
        employees = query.all()
        
        # Calculate pagination info
        total_pages = (total_count + search_request.page_size - 1) // search_request.page_size
        
        return {
            "employees": employees,
            "total": total_count,
            "page": search_request.page,
            "page_size": search_request.page_size,
            "total_pages": total_pages
        }
    
    @staticmethod
    def get_available_filters(db: Session, organization_id: int) -> Dict:
        """Get available filter options for the organization"""
        # Get distinct values for each filter type
        locations = db.query(Employee.location).filter(
            Employee.organization_id == organization_id,
            Employee.location.isnot(None)
        ).distinct().all()
        
        companies = db.query(Employee.company).filter(
            Employee.organization_id == organization_id,
            Employee.company.isnot(None)
        ).distinct().all()
        
        departments = db.query(Employee.department).filter(
            Employee.organization_id == organization_id,
            Employee.department.isnot(None)
        ).distinct().all()
        
        positions = db.query(Employee.position).filter(
            Employee.organization_id == organization_id,
            Employee.position.isnot(None)
        ).distinct().all()
        
        return {
            "locations": [loc[0] for loc in locations if loc[0]],
            "companies": [comp[0] for comp in companies if comp[0]],
            "departments": [dept[0] for dept in departments if dept[0]],
            "positions": [pos[0] for pos in positions if pos[0]]
        }

class OrganizationService:
    """Service class for organization-related operations"""
    
    @staticmethod
    def create_organization(db: Session, name: str) -> Organization:
        """Create a new organization"""
        organization = Organization(name=name)
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization
    
    @staticmethod
    def get_organization(db: Session, organization_id: int) -> Optional[Organization]:
        """Get organization by ID"""
        return db.query(Organization).filter(Organization.id == organization_id).first()
    
    @staticmethod
    def setup_default_column_config(db: Session, organization_id: int):
        """Setup default column configuration for an organization"""
        default_configs = [
            {"column_name": "first_name", "display_order": 0, "is_visible": True},
            {"column_name": "last_name", "display_order": 1, "is_visible": True},
            {"column_name": "email", "display_order": 2, "is_visible": True},
            {"column_name": "phone", "display_order": 3, "is_visible": True},
            {"column_name": "department", "display_order": 4, "is_visible": True},
            {"column_name": "position", "display_order": 5, "is_visible": True},
            {"column_name": "location", "display_order": 6, "is_visible": True},
            {"column_name": "company", "display_order": 7, "is_visible": True},
            {"column_name": "status", "display_order": 8, "is_visible": True},
        ]
        
        for config in default_configs:
            column_config = OrganizationColumnConfig(
                organization_id=organization_id,
                **config
            )
            db.add(column_config)
        
        db.commit() 