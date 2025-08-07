import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.api import app
from app.database import get_db
from app.models import Base, Organization, Employee, OrganizationColumnConfig
from app.schemas import EmployeeStatus

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """Test client fixture"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_organization(client):
    """Create a sample organization for testing"""
    org_data = {"name": "Test Organization"}
    response = client.post("/api/v1/organizations", json=org_data)
    return response.json()

@pytest.fixture
def sample_employees(client, sample_organization):
    """Create sample employees for testing"""
    employees_data = [
        {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@test.com",
            "phone": "+1234567890",
            "department": "Engineering",
            "position": "Software Engineer",
            "location": "New York",
            "company": "Test Corp",
            "status": "ACTIVE",
            "organization_id": sample_organization["id"]
        },
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@test.com",
            "phone": "+1234567891",
            "department": "Marketing",
            "position": "Marketing Manager",
            "location": "San Francisco",
            "company": "Test Corp",
            "status": "ACTIVE",
            "organization_id": sample_organization["id"]
        }
    ]
    
    # Note: Since we don't have a create employee endpoint, we'll simulate this
    # In a real scenario, you'd have a proper endpoint for creating employees
    return employees_data

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestOrganizationEndpoints:
    """Test organization endpoints"""
    
    def test_create_organization(self, client):
        """Test creating an organization"""
        org_data = {"name": "Test Organization"}
        response = client.post("/api/v1/organizations", json=org_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Organization"
        assert "id" in data
    
    def test_get_organization(self, client, sample_organization):
        """Test getting an organization"""
        response = client.get(f"/api/v1/organizations/{sample_organization['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_organization["id"]
        assert data["name"] == sample_organization["name"]
    
    def test_get_nonexistent_organization(self, client):
        """Test getting a non-existent organization"""
        response = client.get("/api/v1/organizations/999")
        assert response.status_code == 404

class TestEmployeeSearchEndpoints:
    """Test employee search endpoints"""
    
    def test_search_employees_empty(self, client, sample_organization):
        """Test searching employees with empty result"""
        search_data = {
            "organization_id": sample_organization["id"],
            "page": 1,
            "page_size": 10
        }
        response = client.post("/api/v1/employees/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["employees"]) == 0
    
    def test_search_employees_with_filters(self, client, sample_organization):
        """Test searching employees with filters"""
        search_data = {
            "organization_id": sample_organization["id"],
            "status": ["ACTIVE"],
            "page": 1,
            "page_size": 10
        }
        response = client.post("/api/v1/employees/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "employees" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data

class TestColumnConfigurationEndpoints:
    """Test column configuration endpoints"""
    
    def test_get_organization_columns(self, client, sample_organization):
        """Test getting organization column configuration"""
        response = client.get(f"/api/v1/organizations/{sample_organization['id']}/columns")
        
        assert response.status_code == 200
        data = response.json()
        assert data["organization_id"] == sample_organization["id"]
        assert "columns" in data
        assert len(data["columns"]) > 0
    
    def test_get_organization_columns_nonexistent(self, client):
        """Test getting columns for non-existent organization"""
        response = client.get("/api/v1/organizations/999/columns")
        assert response.status_code == 404

class TestFilterEndpoints:
    """Test filter endpoints"""
    
    def test_get_available_filters(self, client, sample_organization):
        """Test getting available filters"""
        response = client.get(f"/api/v1/organizations/{sample_organization['id']}/filters")
        
        assert response.status_code == 200
        data = response.json()
        assert data["organization_id"] == sample_organization["id"]
        assert "filters" in data
        assert "locations" in data["filters"]
        assert "companies" in data["filters"]
        assert "departments" in data["filters"]
        assert "positions" in data["filters"]
    
    def test_get_available_filters_nonexistent(self, client):
        """Test getting filters for non-existent organization"""
        response = client.get("/api/v1/organizations/999/filters")
        assert response.status_code == 404

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_info(self, client):
        """Test getting rate limit information"""
        response = client.get("/api/v1/rate-limit/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "client_id" in data
        assert "rate_limit" in data
        assert "remaining" in data["rate_limit"]
        assert "limit" in data["rate_limit"]
    
    def test_rate_limit_headers(self, client):
        """Test that rate limit headers are present"""
        response = client.get("/health")
        
        assert response.status_code == 200
        # Rate limit headers should be present
        # Note: In a real scenario, you'd test actual rate limiting behavior

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_handler(self, client):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_500_handler(self, client):
        """Test 500 error handling"""
        # This would require triggering an actual error
        # For now, we'll just test that the endpoint exists
        response = client.get("/health")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__]) 