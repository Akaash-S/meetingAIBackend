#!/usr/bin/env python3
"""
Migrate tasks table to include enhanced fields for Gemini API integration
"""

import os
import psycopg2
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_tasks_table():
    """Add enhanced fields to tasks table"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        logger.info("🔧 Migrating tasks table to include enhanced fields...")
        
        # Check if enhanced columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tasks' AND column_name IN ('effort', 'dependencies', 'tags', 'context')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add missing columns
        if 'effort' not in existing_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN effort INTEGER DEFAULT 1")
            logger.info("✅ Added 'effort' column")
        
        if 'dependencies' not in existing_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN dependencies TEXT")
            logger.info("✅ Added 'dependencies' column")
        
        if 'tags' not in existing_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN tags TEXT")
            logger.info("✅ Added 'tags' column")
        
        if 'context' not in existing_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN context TEXT")
            logger.info("✅ Added 'context' column")
        
        # Add timeline column to meetings table if it doesn't exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'meetings' AND column_name = 'timeline'
        """)
        timeline_exists = cursor.fetchone()
        
        if not timeline_exists:
            cursor.execute("ALTER TABLE meetings ADD COLUMN timeline TEXT")
            logger.info("✅ Added 'timeline' column to meetings table")
        
        # Commit changes
        conn.commit()
        logger.info("✅ Migration completed successfully")
        
        # Verify the changes
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tasks' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        logger.info("📋 Current tasks table structure:")
        for col_name, data_type in columns:
            logger.info(f"  - {col_name}: {data_type}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

if __name__ == "__main__":
    migrate_tasks_table()
