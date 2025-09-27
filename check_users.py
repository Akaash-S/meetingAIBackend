#!/usr/bin/env python3
"""
Check Users Script
Lists all users in the database.
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

def check_users():
    """Check all users in the database"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            logger.error("❌ DATABASE_URL not set in .env file")
            return False
        
        conn = psycopg2.connect(DATABASE_URL)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get all users
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            logger.info(f"📋 Found {len(users)} users:")
            for user in users:
                logger.info(f"   ID: {user['id']}")
                logger.info(f"   Name: {user['name']}")
                logger.info(f"   Email: {user['email']}")
                logger.info(f"   Role: {user['role']}")
                logger.info(f"   Created: {user['created_at']}")
                logger.info("   ---")
            
            # Get all meetings
            cursor.execute("SELECT * FROM meetings")
            meetings = cursor.fetchall()
            
            logger.info(f"📋 Found {len(meetings)} meetings:")
            for meeting in meetings:
                logger.info(f"   ID: {meeting['id']}")
                logger.info(f"   Title: {meeting['title']}")
                logger.info(f"   User ID: {meeting['user_id']}")
                logger.info(f"   Status: {meeting['status']}")
                logger.info("   ---")
            
            # Get all tasks
            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()
            
            logger.info(f"📋 Found {len(tasks)} tasks:")
            for task in tasks:
                logger.info(f"   ID: {task['id']}")
                logger.info(f"   Name: {task['name']}")
                logger.info(f"   User ID: {task['user_id']}")
                logger.info(f"   Meeting ID: {task['meeting_id']}")
                logger.info(f"   Category: {task['category']}")
                logger.info("   ---")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error checking users: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    logger.info("🎯 Checking Database Users")
    logger.info("=" * 40)
    
    if check_users():
        logger.info("🎉 Database check completed!")
    else:
        logger.error("❌ Failed to check database")

if __name__ == '__main__':
    main()
