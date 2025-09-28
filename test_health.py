#!/usr/bin/env python3
"""
Test the health endpoint
"""

import requests
import time

def test_health():
    """Test the health endpoint"""
    try:
        # Wait a bit for server to start
        time.sleep(2)
        
        url = "http://localhost:5000/api/health"
        print(f"Testing health endpoint: {url}")
        
        response = requests.get(url, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed:")
            print(f"Response: {data}")
        else:
            print("❌ Health check failed:")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server not running")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_health()
