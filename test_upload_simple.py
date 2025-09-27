#!/usr/bin/env python3
"""
Simple Upload Test - Without Supabase
This script tests the file upload functionality without requiring Supabase.
"""

import requests
import os
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_upload_simple():
    """Test file upload endpoint with simple file"""
    logger.info("🧪 Testing simple file upload...")
    
    # Create a test file
    test_content = b"test audio content for upload"
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
        temp_file.write(test_content)
        temp_file_path = temp_file.name
    
    try:
        # Test upload
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test.mp3', f, 'audio/mpeg')}
            data = {
                'title': 'Test Upload',
                'user_id': 'test-user-123',
                'user_name': 'Test User',
                'user_email': 'test@example.com'
            }
            
            response = requests.post('http://localhost:5000/api/upload', files=files, data=data)
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")
            
            if response.status_code == 201:
                result = response.json()
                logger.info("✅ Upload successful!")
                logger.info(f"   Meeting ID: {result.get('meeting_id')}")
                logger.info(f"   File URL: {result.get('file_url')}")
                logger.info(f"   Storage Type: {result.get('storage_type')}")
                return True
            else:
                logger.error(f"❌ Upload failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Upload test failed: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def main():
    logger.info("🎯 MeetingAI Simple Upload Test")
    logger.info("=" * 50)
    
    if test_upload_simple():
        logger.info("🎉 Upload test completed successfully!")
    else:
        logger.error("❌ Upload test failed!")
        return False
    
    return True

if __name__ == '__main__':
    main()
