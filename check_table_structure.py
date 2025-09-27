#!/usr/bin/env python3
"""
Check Table Structure Script
Checks the current database table structure.
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

def check_table_structure():
    """Check the current table structure"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            logger.error("❌ DATABASE_URL not set in .env file")
            return False
        
        conn = psycopg2.connect(DATABASE_URL)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Check users table structure
            logger.info("📋 Checking users table structure...")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                ORDER BY ordinal_position
            """)
            users_columns = cursor.fetchall()
            
            logger.info("Users table columns:")
            for col in users_columns:
                logger.info(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Check if photo_url column exists
            photo_url_exists = any(col['column_name'] == 'photo_url' for col in users_columns)
            if not photo_url_exists:
                logger.warning("⚠️ photo_url column does not exist in users table")
                logger.info("Adding photo_url column...")
                
                cursor.execute("""
                    ALTER TABLE users 
                    ADD COLUMN photo_url VARCHAR(500)
                """)
                conn.commit()
                logger.info("✅ Added photo_url column to users table")
            else:
                logger.info("✅ photo_url column exists in users table")
            
            # Check meetings table structure
            logger.info("\n📋 Checking meetings table structure...")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'meetings' 
                ORDER BY ordinal_position
            """)
            meetings_columns = cursor.fetchall()
            
            logger.info("Meetings table columns:")
            for col in meetings_columns:
                logger.info(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Check tasks table structure
            logger.info("\n📋 Checking tasks table structure...")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'tasks' 
                ORDER BY ordinal_position
            """)
            tasks_columns = cursor.fetchall()
            
            logger.info("Tasks table columns:")
            for col in tasks_columns:
                logger.info(f"   {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error checking table structure: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    logger.info("🎯 Checking Database Table Structure")
    logger.info("=" * 50)
    
    if check_table_structure():
        logger.info("🎉 Table structure check completed!")
    else:
        logger.error("❌ Table structure check failed!")

if __name__ == '__main__':
    main()
