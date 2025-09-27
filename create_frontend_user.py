#!/usr/bin/env python3
"""
Create Frontend User Script
Creates the user ID that the frontend is expecting.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def create_frontend_user():
    """Create the user ID that the frontend is expecting"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            logger.error("❌ DATABASE_URL not set in .env file")
            return False
        
        conn = psycopg2.connect(DATABASE_URL)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Frontend user ID (from Firebase auth)
            user_id = "mJ5ODQaCxscD2EaFNOBWst9XJMg1"
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                logger.info(f"✅ User {user_id} already exists")
                return True
            
            # Create frontend user
            cursor.execute("""
                INSERT INTO users (id, name, email, role, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                "Frontend User",
                "frontend@example.com",
                "user",
                datetime.now(),
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"✅ Created frontend user: {user_id}")
            
            # Create a test meeting for this user
            meeting_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO meetings (id, title, file_path, file_name, file_size, user_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                meeting_id,
                "Frontend Test Meeting",
                "file://frontend-test-path.mp3",
                "frontend-test.mp3",
                2048,
                user_id,
                "uploaded",
                datetime.now(),
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"✅ Created test meeting: {meeting_id}")
            
            # Create a test task for this user
            task_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO tasks (id, name, description, category, meeting_id, user_id, status, priority, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task_id,
                "Frontend Test Task",
                "This is a test task for the frontend user",
                "action-item",
                meeting_id,
                user_id,
                "pending",
                "medium",
                datetime.now(),
                datetime.now()
            ))
            
            conn.commit()
            logger.info(f"✅ Created test task: {task_id}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creating frontend user: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    logger.info("🎯 Creating Frontend User")
    logger.info("=" * 40)
    
    if create_frontend_user():
        logger.info("🎉 Frontend user created successfully!")
        logger.info("User ID: mJ5ODQaCxscD2EaFNOBWst9XJMg1")
        logger.info("The frontend should now work without 404 errors!")
    else:
        logger.error("❌ Failed to create frontend user")

if __name__ == '__main__':
    main()
