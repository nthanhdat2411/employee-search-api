#!/usr/bin/env python3
"""
Database population script for Employee Search Directory API
Creates sample organizations and employees for testing
"""

import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, create_tables
from app.models import Organization, Employee, OrganizationColumnConfig
from app.schemas import EmployeeStatus

def create_sample_data():
    """Create sample organizations and employees"""
    db = SessionLocal()
    
    try:
        # Create organizations
        organizations = [
            Organization(name="TechCorp Inc."),
            Organization(name="Marketing Solutions Ltd."),
            Organization(name="Global Consulting Group")
        ]
        
        for org in organizations:
            db.add(org)
        db.commit()
        
        # Refresh to get IDs
        for org in organizations:
            db.refresh(org)
        
        # Sample employees data
        employees_data = [
            # TechCorp Inc. employees
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@techcorp.com",
                "phone": "+1-555-0101",
                "department": "Engineering",
                "position": "Senior Software Engineer",
                "location": "San Francisco",
                "company": "TechCorp Inc.",
                "status": "ACTIVE",
                "organization_id": organizations[0].id
            },
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@techcorp.com",
                "phone": "+1-555-0102",
                "department": "Engineering",
                "position": "Software Engineer",
                "location": "New York",
                "company": "TechCorp Inc.",
                "status": "ACTIVE",
                "organization_id": organizations[0].id
            },
            {
                "first_name": "Mike",
                "last_name": "Johnson",
                "email": "mike.johnson@techcorp.com",
                "phone": "+1-555-0103",
                "department": "Product",
                "position": "Product Manager",
                "location": "San Francisco",
                "company": "TechCorp Inc.",
                "status": "ACTIVE",
                "organization_id": organizations[0].id
            },
            {
                "first_name": "Sarah",
                "last_name": "Wilson",
                "email": "sarah.wilson@techcorp.com",
                "phone": "+1-555-0104",
                "department": "HR",
                "position": "HR Manager",
                "location": "New York",
                "company": "TechCorp Inc.",
                "status": "NOT_STARTED",
                "organization_id": organizations[0].id
            },
            
            # Marketing Solutions Ltd. employees
            {
                "first_name": "Alex",
                "last_name": "Brown",
                "email": "alex.brown@marketing.com",
                "phone": "+1-555-0201",
                "department": "Marketing",
                "position": "Marketing Director",
                "location": "Los Angeles",
                "company": "Marketing Solutions Ltd.",
                "status": "ACTIVE",
                "organization_id": organizations[1].id
            },
            {
                "first_name": "Emily",
                "last_name": "Davis",
                "email": "emily.davis@marketing.com",
                "phone": "+1-555-0202",
                "department": "Marketing",
                "position": "Content Strategist",
                "location": "Chicago",
                "company": "Marketing Solutions Ltd.",
                "status": "ACTIVE",
                "organization_id": organizations[1].id
            },
            {
                "first_name": "David",
                "last_name": "Miller",
                "email": "david.miller@marketing.com",
                "phone": "+1-555-0203",
                "department": "Sales",
                "position": "Sales Manager",
                "location": "Los Angeles",
                "company": "Marketing Solutions Ltd.",
                "status": "TERMINATED",
                "organization_id": organizations[1].id
            },
            
            # Global Consulting Group employees
            {
                "first_name": "Lisa",
                "last_name": "Garcia",
                "email": "lisa.garcia@consulting.com",
                "phone": "+1-555-0301",
                "department": "Consulting",
                "position": "Senior Consultant",
                "location": "Boston",
                "company": "Global Consulting Group",
                "status": "ACTIVE",
                "organization_id": organizations[2].id
            },
            {
                "first_name": "Robert",
                "last_name": "Taylor",
                "email": "robert.taylor@consulting.com",
                "phone": "+1-555-0302",
                "department": "Consulting",
                "position": "Consultant",
                "location": "Seattle",
                "company": "Global Consulting Group",
                "status": "ACTIVE",
                "organization_id": organizations[2].id
            },
            {
                "first_name": "Amanda",
                "last_name": "Anderson",
                "email": "amanda.anderson@consulting.com",
                "phone": "+1-555-0303",
                "department": "Finance",
                "position": "Financial Analyst",
                "location": "Boston",
                "company": "Global Consulting Group",
                "status": "NOT_STARTED",
                "organization_id": organizations[2].id
            }
        ]
        
        # Create employees
        for emp_data in employees_data:
            employee = Employee(**emp_data)
            db.add(employee)
        
        db.commit()
        
        print("✅ Sample data created successfully!")
        print(f"   Organizations: {len(organizations)}")
        print(f"   Employees: {len(employees_data)}")
        print()
        print("Organization IDs:")
        for org in organizations:
            print(f"   {org.id}: {org.name}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function"""
    print("🚀 Populating database with sample data...")
    
    try:
        # Create tables
        create_tables()
        print("✅ Database tables created")
        
        # Create sample data
        create_sample_data()
        
        print("\n🎉 Database population completed successfully!")
        print("\nYou can now test the API with:")
        print("  python cli.py health")
        print("  python cli.py search --org-id 1")
        print("  python cli.py filters --org-id 1")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 