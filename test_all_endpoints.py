#!/usr/bin/env python3
"""
Test all endpoints with populated data
"""

import requests
import json

def test_all_endpoints():
    base_url = "http://localhost:5000/api"
    user_id = "mJ5ODQaCxscD2EaFNOBWst9XJMg1"
    
    endpoints = [
        f"/tasks/user/{user_id}",
        f"/tasks/overdue/user/{user_id}",
        f"/tasks/upcoming/user/{user_id}",
        f"/user/{user_id}",
        f"/user/{user_id}/stats",
        "/meetings/user/mJ5ODQaCxscD2EaFNOBWst9XJMg1"
    ]
    
    print("🧪 Testing all endpoints with populated data...")
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url)
            
            print(f"\n📡 {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'tasks' in data:
                    print(f"   ✅ Tasks: {len(data['tasks'])}")
                if 'stats' in data:
                    print(f"   ✅ Stats: {data['stats']}")
                if 'name' in data:
                    print(f"   ✅ User: {data['name']}")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print("\n🎉 Endpoint testing completed!")

if __name__ == '__main__':
    test_all_endpoints()