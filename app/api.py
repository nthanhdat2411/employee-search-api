from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from typing import List, Dict
import logging

from app.database import get_db
from app.schemas import (
    EmployeeSearchRequest, EmployeeSearchResponse, EmployeeResponse,
    OrganizationCreate, OrganizationResponse, ColumnConfigResponse
)
from app.services import EmployeeService, OrganizationService
from app.rate_limiter import rate_limiter
from app.models import Employee, Organization, OrganizationColumnConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Employee Search Directory API",
    description="A FastAPI microservice for employee search directory with dynamic columns and rate limiting",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_client_id(request: Request) -> str:
    """Extract client ID from request headers or IP"""
    # In production, you might want to use API keys or JWT tokens
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        client_id = request.client.host
    return client_id

def rate_limit_dependency(request: Request):
    """Dependency for rate limiting"""
    client_id = get_client_id(request)
    is_allowed, rate_limit_info = rate_limiter.is_allowed(client_id)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(rate_limit_info["limit"]),
                "X-RateLimit-Remaining": str(rate_limit_info["remaining"]),
                "X-RateLimit-Reset": str(rate_limit_info["reset_time"])
            }
        )
    
    # Add rate limit headers to response
    request.state.rate_limit_info = rate_limit_info

@app.middleware("http")
async def add_rate_limit_headers(request: Request, call_next):
    """Add rate limit headers to all responses"""
    response = await call_next(request)
    
    if hasattr(request.state, 'rate_limit_info'):
        rate_limit_info = request.state.rate_limit_info
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset_time"])
    
    return response

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Handle favicon requests"""
    return Response(status_code=204)  # No content response

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {"message": "Employee Search Directory API", "status": "healthy"}

@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Employee Search Directory API",
        "version": "1.0.0"
    }

@app.post("/api/v1/organizations", response_model=OrganizationResponse, tags=["Organizations"])
async def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
):
    """Create a new organization"""
    try:
        org = OrganizationService.create_organization(db, organization.name)
        # Setup default column configuration
        OrganizationService.setup_default_column_config(db, org.id)
        return org
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(status_code=500, detail="Failed to create organization")

@app.get("/api/v1/organizations/{organization_id}", response_model=OrganizationResponse, tags=["Organizations"])
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
):
    """Get organization by ID"""
    org = OrganizationService.get_organization(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@app.post("/api/v1/employees/search", response_model=EmployeeSearchResponse, tags=["Employees"])
async def search_employees(
    search_request: EmployeeSearchRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
):
    """
    Search employees with advanced filtering and pagination.
    Supports dynamic columns based on organization configuration.
    """
    try:
        # Verify organization exists
        org = OrganizationService.get_organization(db, search_request.organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Perform search
        result = EmployeeService.search_employees(db, search_request)
        
        return EmployeeSearchResponse(
            employees=result["employees"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching employees: {e}")
        raise HTTPException(status_code=500, detail="Failed to search employees")

@app.get("/api/v1/organizations/{organization_id}/columns", tags=["Columns"])
async def get_organization_columns(
    organization_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
):
    """Get column configuration for an organization"""
    try:
        # Verify organization exists
        org = OrganizationService.get_organization(db, organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        columns = EmployeeService.get_organization_column_config(db, organization_id)
        return {"organization_id": organization_id, "columns": columns}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting column config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get column configuration")

@app.get("/api/v1/organizations/{organization_id}/filters", tags=["Filters"])
async def get_available_filters(
    organization_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_dependency)
):
    """Get available filter options for an organization"""
    try:
        # Verify organization exists
        org = OrganizationService.get_organization(db, organization_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        filters = EmployeeService.get_available_filters(db, organization_id)
        return {"organization_id": organization_id, "filters": filters}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting filters: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available filters")

@app.get("/api/v1/rate-limit/info", tags=["Rate Limiting"])
async def get_rate_limit_info(request: Request):
    """Get current rate limit information for the client"""
    client_id = get_client_id(request)
    rate_limit_info = rate_limiter.get_rate_limit_info(client_id)
    return {
        "client_id": client_id,
        "rate_limit": rate_limit_info
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "status_code": 404}
    )

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded", "status_code": 429}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    ) 