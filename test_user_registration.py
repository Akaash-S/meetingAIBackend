#!/usr/bin/env python3
"""
Test User Registration Script
Tests the user registration and management endpoints.
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_user_registration():
    """Test user registration endpoint"""
    logger.info("🧪 Testing user registration...")
    
    # Test user data
    user_data = {
        "user_id": "test-firebase-user-123",
        "name": "Test Firebase User",
        "email": "testfirebase@example.com",
        "photo_url": "https://example.com/photo.jpg"
    }
    
    try:
        response = requests.post('http://localhost:5000/api/user/register', json=user_data)
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            logger.info("✅ User registration successful!")
            logger.info(f"   User ID: {result.get('user_id')}")
            logger.info(f"   Name: {result.get('name')}")
            logger.info(f"   Email: {result.get('email')}")
            return True
        else:
            logger.error(f"❌ User registration failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ User registration test failed: {e}")
        return False

def test_user_info():
    """Test getting user information"""
    logger.info("🧪 Testing user info retrieval...")
    
    user_id = "test-firebase-user-123"
    
    try:
        response = requests.get(f'http://localhost:5000/api/user/{user_id}')
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ User info retrieval successful!")
            logger.info(f"   User ID: {result.get('id')}")
            logger.info(f"   Name: {result.get('name')}")
            logger.info(f"   Email: {result.get('email')}")
            return True
        else:
            logger.error(f"❌ User info retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ User info test failed: {e}")
        return False

def test_user_stats():
    """Test getting user statistics"""
    logger.info("🧪 Testing user statistics...")
    
    user_id = "test-firebase-user-123"
    
    try:
        response = requests.get(f'http://localhost:5000/api/user/{user_id}/stats')
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ User stats retrieval successful!")
            logger.info(f"   Meeting Count: {result.get('meeting_count')}")
            logger.info(f"   Task Count: {result.get('task_count')}")
            logger.info(f"   Completed Tasks: {result.get('completed_tasks')}")
            return True
        else:
            logger.error(f"❌ User stats retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ User stats test failed: {e}")
        return False

def test_upload_with_user():
    """Test file upload with user creation"""
    logger.info("🧪 Testing file upload with user creation...")
    
    # Create a test file
    import tempfile
    import os
    
    test_content = b"test audio content for user creation"
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test-user-creation.mp3', f, 'audio/mpeg')}
            data = {
                'title': 'Test User Creation Upload',
                'user_id': 'new-firebase-user-456',
                'user_name': 'New Firebase User',
                'user_email': 'newfirebase@example.com',
                'user_photo_url': 'https://example.com/new-photo.jpg'
            }
            
            response = requests.post('http://localhost:5000/api/upload', files=files, data=data)
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")
            
            if response.status_code == 201:
                result = response.json()
                logger.info("✅ File upload with user creation successful!")
                logger.info(f"   Meeting ID: {result.get('meeting_id')}")
                logger.info(f"   User ID: {data['user_id']}")
                return True
            else:
                logger.error(f"❌ File upload with user creation failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ File upload test failed: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def main():
    logger.info("🎯 MeetingAI User Registration Test")
    logger.info("=" * 50)
    
    tests = [
        ("User Registration", test_user_registration),
        ("User Info Retrieval", test_user_info),
        ("User Statistics", test_user_stats),
        ("File Upload with User Creation", test_upload_with_user)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} passed!")
        else:
            logger.error(f"❌ {test_name} failed!")
    
    logger.info(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All user registration tests passed!")
        logger.info("Users will now be automatically created in Neon PostgreSQL when they log in through Firebase!")
    else:
        logger.error("❌ Some tests failed. Please check the logs above.")

if __name__ == '__main__':
    main()
