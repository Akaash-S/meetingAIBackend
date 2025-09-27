#!/usr/bin/env python3
"""
Test the tasks endpoint
"""

import requests
import json

def test_tasks_endpoint():
    try:
        url = "http://localhost:5000/api/tasks/user/mJ5ODQaCxscD2EaFNOBWst9XJMg1"
        params = {"page": 1, "per_page": 20}
        
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_tasks_endpoint()
