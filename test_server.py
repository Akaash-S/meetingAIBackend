#!/usr/bin/env python3
"""
Simple server test script to check if the Flask app is running properly
"""

import requests
import time
import sys

def test_server():
    """Test if the server is responding to requests"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Flask server...")
    
    # Test health endpoint
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test a simple API endpoint
    try:
        print("2. Testing user tasks endpoint...")
        test_user_id = "test-user-123"
        response = requests.get(f"{base_url}/api/tasks/user/{test_user_id}", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 404, 500]:
            print("✅ Tasks endpoint responding")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection reset on tasks endpoint")
        return False
    except Exception as e:
        print(f"❌ Tasks endpoint error: {e}")
        return False
    
    # Test meetings endpoint
    try:
        print("3. Testing meetings endpoint...")
        test_user_id = "test-user-123"
        response = requests.get(f"{base_url}/api/meetings/user/{test_user_id}", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 404, 500]:
            print("✅ Meetings endpoint responding")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection reset on meetings endpoint")
        return False
    except Exception as e:
        print(f"❌ Meetings endpoint error: {e}")
        return False
    
    print("🎉 All tests completed!")
    return True

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
