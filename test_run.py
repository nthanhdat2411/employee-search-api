#!/usr/bin/env python3
"""
Quick test script to verify the Employee Search Directory API
"""

import requests
import time
import json

def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Employee Search Directory API...")
    print(f"Base URL: {base_url}")
    print()
    
    try:
        # Test 1: Health check
        print("1. Testing health check...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json().get('status')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Search employees (using existing organization ID 1)
        print("\n2. Testing employee search...")
        search_data = {
            "organization_id": 1,
            "page": 1,
            "page_size": 10
        }
        response = requests.post(f"{base_url}/api/v1/employees/search", json=search_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Employee search successful")
            print(f"   Total employees: {result.get('total')}")
            print(f"   Page: {result.get('page')}/{result.get('total_pages')}")
        else:
            print(f"❌ Employee search failed: {response.status_code}")
            return False
        
        # Test 3: Get available filters
        print("\n3. Testing available filters...")
        response = requests.get(f"{base_url}/api/v1/organizations/1/filters")
        if response.status_code == 200:
            result = response.json()
            filters = result.get('filters', {})
            print(f"✅ Available filters retrieved")
            for filter_type, values in filters.items():
                print(f"   {filter_type}: {len(values)} values")
        else:
            print(f"❌ Available filters failed: {response.status_code}")
            return False
        
        # Test 4: Rate limiting info
        print("\n4. Testing rate limiting...")
        response = requests.get(f"{base_url}/api/v1/rate-limit/info")
        if response.status_code == 200:
            result = response.json()
            rate_limit = result.get('rate_limit', {})
            print(f"✅ Rate limit info retrieved")
            print(f"   Remaining: {rate_limit.get('remaining')}")
            print(f"   Limit: {rate_limit.get('limit')}")
        else:
            print(f"❌ Rate limit info failed: {response.status_code}")
            return False
        
        print("\n🎉 All tests passed! The API is working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("Employee Search Directory API - Quick Test")
    print("=" * 50)
    print()
    
    success = test_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python scripts/populate_db.py' to add sample data")
        print("2. Use 'python cli.py' to interact with the API")
        print("3. Visit http://localhost:8000/docs for API documentation")
    else:
        print("❌ Tests failed. Please check the API is running.")
    print("=" * 50)

if __name__ == "__main__":
    main() 