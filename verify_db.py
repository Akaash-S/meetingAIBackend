#!/usr/bin/env python3
"""
Clean up test data and verify tables
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def cleanup_and_verify():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Clean up test data
        cursor.execute("DELETE FROM tasks WHERE id = 'test-task-123'")
        cursor.execute("DELETE FROM meetings WHERE id = 'test-meeting-123'")
        cursor.execute("DELETE FROM users WHERE id = 'test-user-123'")
        conn.commit()
        
        # Verify tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Tables found: {tables}")
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", ('mJ5ODQaCxscD2EaFNOBWst9XJMg1',))
        user = cursor.fetchone()
        print(f"User exists: {user is not None}")
        
        # Check tasks table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tasks'
        """)
        columns = cursor.fetchall()
        print(f"Tasks table columns: {columns}")
        
        cursor.close()
        conn.close()
        
        print("✅ Database verification completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    cleanup_and_verify()
