#!/usr/bin/env python3
"""
Test the tasks API endpoint
"""

import requests
import json

def test_tasks_api():
    """Test the tasks API endpoint"""
    try:
        url = "http://localhost:5000/api/tasks/user/mJ5ODQaCxscD2EaFNOBWst9XJMg1"
        params = {"page": 1, "per_page": 20}
        
        print(f"Testing API: {url}")
        print(f"Parameters: {params}")
        
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2))
        else:
            print("❌ API Error:")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_tasks_api()
