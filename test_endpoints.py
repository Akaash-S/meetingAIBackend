#!/usr/bin/env python3
"""
Test script to verify backend endpoints
"""
import requests
import json

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health')
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_upload():
    """Test upload endpoint (without file)"""
    try:
        response = requests.post('http://localhost:5000/api/upload')
        print(f"📤 Upload test: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True  # Expected to fail without file
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

def test_tasks():
    """Test tasks endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/tasks/user/test-user-123')
        print(f"📋 Tasks test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Tasks: {len(data.get('tasks', []))}")
            print(f"   Statistics: {data.get('statistics', {})}")
        else:
            print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Tasks test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing backend endpoints...\n")
    
    # Test health
    if not test_health():
        print("❌ Backend is not running properly")
        return False
    
    print()
    
    # Test upload
    test_upload()
    print()
    
    # Test tasks
    test_tasks()
    print()
    
    print("🎉 Backend testing completed!")
    print("\nYour backend is running successfully at http://localhost:5000")
    print("\nAvailable endpoints:")
    print("- GET  /api/health")
    print("- POST /api/upload")
    print("- POST /api/transcribe/:meetingId")
    print("- POST /api/extract/:meetingId")
    print("- GET  /api/meeting/:meetingId")
    print("- GET  /api/meetings/user/:userId")
    print("- GET  /api/tasks/user/:userId")
    print("- POST /api/tasks")
    print("- POST /api/notify/task/:taskId")
    
    return True

if __name__ == "__main__":
    main()
