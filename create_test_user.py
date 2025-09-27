#!/usr/bin/env python3
"""
Create Test User Script
Creates a test user in the database for frontend testing.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def create_test_user():
    """Create a test user in the database"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            logger.error("❌ DATABASE_URL not set in .env file")
            return False
        
        conn = psycopg2.connect(DATABASE_URL)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Test user ID (from Firebase auth)
            user_id = "mJ5ODQaCxscD2EaFNOBWst9XJMg1"
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                logger.info(f"✅ User {user_id} already exists")
                return True
            
            # Create test user
            cursor.execute("""
                INSERT INTO users (id, name, email, role, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                "Test User",
                "test@example.com",
                "user",
                "2025-09-27 13:30:00",
                "2025-09-27 13:30:00"
            ))
            
            conn.commit()
            logger.info(f"✅ Created test user: {user_id}")
            
            # Create a test meeting
            meeting_id = "test-meeting-123"
            cursor.execute("""
                INSERT INTO meetings (id, title, file_path, file_name, file_size, user_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                meeting_id,
                "Test Meeting",
                "file://test-path.mp3",
                "test.mp3",
                1024,
                user_id,
                "uploaded",
                "2025-09-27 13:30:00",
                "2025-09-27 13:30:00"
            ))
            
            conn.commit()
            logger.info(f"✅ Created test meeting: {meeting_id}")
            
            # Create a test task
            task_id = "test-task-456"
            cursor.execute("""
                INSERT INTO tasks (id, name, description, category, meeting_id, user_id, status, priority, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task_id,
                "Test Task",
                "This is a test task",
                "action-item",
                meeting_id,
                user_id,
                "pending",
                "medium",
                "2025-09-27 13:30:00",
                "2025-09-27 13:30:00"
            ))
            
            conn.commit()
            logger.info(f"✅ Created test task: {task_id}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creating test user: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    logger.info("🎯 Creating Test User")
    logger.info("=" * 30)
    
    if create_test_user():
        logger.info("🎉 Test user created successfully!")
        logger.info("You can now test the frontend with this user ID: mJ5ODQaCxscD2EaFNOBWst9XJMg1")
    else:
        logger.error("❌ Failed to create test user")

if __name__ == '__main__':
    main()
