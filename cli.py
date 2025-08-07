#!/usr/bin/env python3
"""
CLI tool for Employee Search Directory API
Provides easy command-line interface for interacting with the API
"""

import argparse
import requests
import json
import sys
from typing import Dict, Any, Optional
import os

class EmployeeSearchCLI:
    """CLI tool for Employee Search Directory API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            sys.exit(1)
    
    def health_check(self) -> None:
        """Check API health"""
        result = self._make_request("GET", "/health")
        print("✅ API Health Check:")
        print(f"   Status: {result.get('status')}")
        print(f"   Service: {result.get('service')}")
        print(f"   Version: {result.get('version')}")
    
    def search_employees(self, organization_id: int, **kwargs) -> None:
        """Search employees"""
        search_data = {
            "organization_id": organization_id,
            "page": kwargs.get("page", 1),
            "page_size": kwargs.get("page_size", 50)
        }
        
        # Add optional filters
        if kwargs.get("search"):
            search_data["search"] = kwargs["search"]
        if kwargs.get("status"):
            search_data["status"] = kwargs["status"]
        if kwargs.get("locations"):
            search_data["locations"] = kwargs["locations"]
        if kwargs.get("departments"):
            search_data["departments"] = kwargs["departments"]
        if kwargs.get("positions"):
            search_data["positions"] = kwargs["positions"]
        if kwargs.get("companies"):
            search_data["companies"] = kwargs["companies"]
        if kwargs.get("include_terminated"):
            search_data["include_terminated"] = kwargs["include_terminated"]
        
        result = self._make_request("POST", "/api/v1/employees/search", search_data)
        
        print(f"🔍 Employee Search Results:")
        print(f"   Total: {result.get('total')}")
        print(f"   Page: {result.get('page')}/{result.get('total_pages')}")
        print(f"   Page Size: {result.get('page_size')}")
        print()
        
        employees = result.get("employees", [])
        if not employees:
            print("   No employees found.")
            return
        
        for i, employee in enumerate(employees, 1):
            print(f"   {i}. {employee.get('first_name')} {employee.get('last_name')}")
            print(f"      Email: {employee.get('email')}")
            print(f"      Department: {employee.get('department') or 'N/A'}")
            print(f"      Position: {employee.get('position') or 'N/A'}")
            print(f"      Location: {employee.get('location') or 'N/A'}")
            print(f"      Status: {employee.get('status')}")
            print()
    
    def get_available_filters(self, organization_id: int) -> None:
        """Get available filter options"""
        result = self._make_request("GET", f"/api/v1/organizations/{organization_id}/filters")
        
        print(f"🔧 Available Filters for Organization {organization_id}:")
        filters = result.get("filters", {})
        
        for filter_type, values in filters.items():
            print(f"   {filter_type.title()}: {', '.join(values) if values else 'None'}")
    
    def get_rate_limit_info(self) -> None:
        """Get rate limit information"""
        result = self._make_request("GET", "/api/v1/rate-limit/info")
        
        print("⏱️  Rate Limit Information:")
        print(f"   Client ID: {result.get('client_id')}")
        rate_limit = result.get("rate_limit", {})
        print(f"   Remaining: {rate_limit.get('remaining')}")
        print(f"   Limit: {rate_limit.get('limit')}")
        print(f"   Reset Time: {rate_limit.get('reset_time')}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Employee Search Directory API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s health
  %(prog)s search --org-id 1 --search "john"
  %(prog)s search --org-id 1 --status ACTIVE --departments Engineering
  %(prog)s filters --org-id 1
  %(prog)s rate-limit
        """
    )
    
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check command
    subparsers.add_parser("health", help="Check API health")
    
    # Search employees command
    search_parser = subparsers.add_parser("search", help="Search employees")
    search_parser.add_argument("--org-id", type=int, required=True, help="Organization ID")
    search_parser.add_argument("--search", help="Search term")
    search_parser.add_argument("--status", nargs="+", help="Status filter(s)")
    search_parser.add_argument("--locations", nargs="+", help="Location filter(s)")
    search_parser.add_argument("--departments", nargs="+", help="Department filter(s)")
    search_parser.add_argument("--positions", nargs="+", help="Position filter(s)")
    search_parser.add_argument("--companies", nargs="+", help="Company filter(s)")
    search_parser.add_argument("--page", type=int, default=1, help="Page number")
    search_parser.add_argument("--page-size", type=int, default=50, help="Page size")
    search_parser.add_argument("--include-terminated", action="store_true", help="Include terminated employees")
    
    # Get filters command
    filters_parser = subparsers.add_parser("filters", help="Get available filter options")
    filters_parser.add_argument("--org-id", type=int, required=True, help="Organization ID")
    
    # Rate limit command
    subparsers.add_parser("rate-limit", help="Get rate limit information")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize CLI
    cli = EmployeeSearchCLI(args.base_url)
    
    try:
        if args.command == "health":
            cli.health_check()
        
        elif args.command == "search":
            cli.search_employees(
                organization_id=args.org_id,
                search=args.search,
                status=args.status,
                locations=args.locations,
                departments=args.departments,
                positions=args.positions,
                companies=args.companies,
                page=args.page,
                page_size=args.page_size,
                include_terminated=args.include_terminated
            )
        
        elif args.command == "filters":
            cli.get_available_filters(args.org_id)
        
        elif args.command == "rate-limit":
            cli.get_rate_limit_info()
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 