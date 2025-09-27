#!/usr/bin/env python3
"""
Manual Table Creation Script
This script creates tables directly using SQL DDL statements.
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def create_tables_manually():
    """Create tables using direct SQL DDL"""
    logger.info("🚀 Creating tables manually...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL not found in environment variables")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        logger.info("🔗 Database connection successful")
        
        # Create users table
        logger.info("📋 Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ Users table created")
        
        # Create meetings table
        logger.info("📋 Creating meetings table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                transcript TEXT,
                file_path VARCHAR(500),
                file_name VARCHAR(200),
                file_size BIGINT,
                duration INTEGER,
                participants INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'uploaded',
                user_id VARCHAR(36) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        logger.info("✅ Meetings table created")
        
        # Create tasks table
        logger.info("📋 Creating tasks table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(500) NOT NULL,
                description TEXT,
                owner VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                priority VARCHAR(10) DEFAULT 'medium',
                category VARCHAR(20) NOT NULL,
                deadline TIMESTAMP,
                completed_at TIMESTAMP,
                meeting_id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meeting_id) REFERENCES meetings(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        logger.info("✅ Tasks table created")
        
        # Commit changes
        conn.commit()
        logger.info("✅ All tables created successfully")
        
        # Verify tables exist
        logger.info("🔍 Verifying tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'meetings', 'tasks']
        logger.info(f"📋 Found tables: {tables}")
        
        for table in expected_tables:
            if table in tables:
                logger.info(f"✅ Table '{table}' exists")
            else:
                logger.error(f"❌ Table '{table}' not found")
        
        # Test inserting data
        logger.info("🧪 Testing data insertion...")
        
        # Insert test user
        cursor.execute("""
            INSERT INTO users (id, name, email, role) 
            VALUES (%s, %s, %s, %s)
        """, ('test-user-123', 'Test User', 'test@example.com', 'user'))
        logger.info("✅ User insertion test successful")
        
        # Insert test meeting
        cursor.execute("""
            INSERT INTO meetings (id, title, user_id, status) 
            VALUES (%s, %s, %s, %s)
        """, ('test-meeting-123', 'Test Meeting', 'test-user-123', 'uploaded'))
        logger.info("✅ Meeting insertion test successful")
        
        # Insert test task
        cursor.execute("""
            INSERT INTO tasks (id, name, category, meeting_id, user_id) 
            VALUES (%s, %s, %s, %s, %s)
        """, ('test-task-123', 'Test Task', 'action-item', 'test-meeting-123', 'test-user-123'))
        logger.info("✅ Task insertion test successful")
        
        # Clean up test data
        cursor.execute("DELETE FROM tasks WHERE id = 'test-task-123'")
        cursor.execute("DELETE FROM meetings WHERE id = 'test-meeting-123'")
        cursor.execute("DELETE FROM users WHERE id = 'test-user-123'")
        logger.info("🧹 Test data cleaned up")
        
        # Commit cleanup
        conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 Manual table creation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Manual table creation failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("🎯 MeetingAI Backend Manual Table Creation")
    logger.info("=" * 60)
    
    if create_tables_manually():
        logger.info("🎉 All tables created successfully!")
        logger.info("You can now run: python app.py")
    else:
        logger.error("❌ Table creation failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
