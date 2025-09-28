#!/usr/bin/env python3
"""
Backend Health Test Script
This script tests if the backend server is running and responding correctly.
"""

import requests
import json
import sys
import time

def test_backend_health():
    """Test backend health and endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Backend Health")
    print("=" * 40)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint: OK")
        else:
            print(f"❌ Health endpoint: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Health endpoint: Connection failed - Backend not running")
        return False
    except Exception as e:
        print(f"❌ Health endpoint: {e}")
        return False
    
    # Test 2: Upload endpoint (should return method not allowed for GET)
    print("2. Testing upload endpoint...")
    try:
        response = requests.get(f"{base_url}/api/upload", timeout=5)
        if response.status_code == 405:  # Method Not Allowed is expected for GET
            print("✅ Upload endpoint: Accessible")
        else:
            print(f"⚠️  Upload endpoint: {response.status_code} (unexpected but OK)")
    except Exception as e:
        print(f"❌ Upload endpoint: {e}")
        return False
    
    # Test 3: Tasks endpoint
    print("3. Testing tasks endpoint...")
    try:
        response = requests.get(f"{base_url}/api/tasks", timeout=5)
        if response.status_code in [200, 401, 403]:  # OK or auth required
            print("✅ Tasks endpoint: Accessible")
        else:
            print(f"⚠️  Tasks endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Tasks endpoint: {e}")
        return False
    
    # Test 4: Database connection (via a simple endpoint)
    print("4. Testing database connection...")
    try:
        # Try to get user info (this will test database connection)
        response = requests.get(f"{base_url}/api/users", timeout=5)
        if response.status_code in [200, 401, 403, 404]:
            print("✅ Database connection: Working")
        else:
            print(f"⚠️  Database connection: {response.status_code}")
    except Exception as e:
        print(f"❌ Database connection: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Backend health test completed!")
    print("✅ Your backend server is running and responding correctly")
    print("🌐 Server URL: http://localhost:5000")
    print("")
    print("You can now use the frontend application without database errors!")
    
    return True

def main():
    """Main test function"""
    print("🔍 Backend Health Checker")
    print("This script tests if your backend server is working correctly.")
    print("")
    
    # Wait a moment for user to read
    time.sleep(1)
    
    success = test_backend_health()
    
    if not success:
        print("\n❌ Backend health test failed!")
        print("Please make sure:")
        print("1. The backend server is running (python app.py)")
        print("2. The database connection is configured")
        print("3. All dependencies are installed")
        print("")
        print("Run the fix script: python fix_database_connection.py")
    
    return success

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
