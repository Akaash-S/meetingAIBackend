#!/usr/bin/env python3
"""
Test the Flask app directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import json

def test_flask_endpoint():
    with app.test_client() as client:
        response = client.get('/api/tasks/user/mJ5ODQaCxscD2EaFNOBWst9XJMg1?page=1&per_page=20')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error Response: {response.get_data(as_text=True)}")

if __name__ == '__main__':
    test_flask_endpoint()
