from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EmployeeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    NOT_STARTED = "NOT_STARTED"
    TERMINATED = "TERMINATED"

class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    status: EmployeeStatus = EmployeeStatus.ACTIVE

class EmployeeCreate(EmployeeBase):
    organization_id: int

class EmployeeResponse(EmployeeBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EmployeeSearchRequest(BaseModel):
    search: Optional[str] = Field(None, description="Search term for first name, last name, email")
    status: Optional[List[EmployeeStatus]] = Field(None, description="Filter by employee status")
    locations: Optional[List[str]] = Field(None, description="Filter by locations")
    companies: Optional[List[str]] = Field(None, description="Filter by companies")
    departments: Optional[List[str]] = Field(None, description="Filter by departments")
    positions: Optional[List[str]] = Field(None, description="Filter by positions")
    organization_id: int = Field(..., description="Organization ID for data isolation")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")
    include_terminated: bool = Field(False, description="Include terminated employees")

class EmployeeSearchResponse(BaseModel):
    employees: List[EmployeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ColumnConfigBase(BaseModel):
    column_name: str = Field(..., description="Column name (e.g., 'first_name', 'department')")
    display_order: int = Field(..., ge=0, description="Display order (0-based)")
    is_visible: bool = Field(True, description="Whether column is visible")

class ColumnConfigCreate(ColumnConfigBase):
    organization_id: int

class ColumnConfigResponse(ColumnConfigBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 