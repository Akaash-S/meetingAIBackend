#!/usr/bin/env python3
"""
Test Database Connection (Windows Compatible)
"""

import os
import psycopg2
from dotenv import load_dotenv

def test_db_connection():
    """Test database connection"""
    print("Testing Database Connection")
    print("=" * 30)
    
    # Load environment variables
    load_dotenv()
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in .env file")
        return False
    
    print(f"DATABASE_URL: {database_url[:50]}...")
    
    try:
        # Test connection
        conn = psycopg2.connect(database_url)
        print("OK: Database connection successful!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        print("OK: Basic query test passed")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Found tables: {tables}")
        
        cursor.close()
        conn.close()
        
        print("SUCCESS: Database connection test completed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

if __name__ == '__main__':
    success = test_db_connection()
    if not success:
        print("Please check your DATABASE_URL configuration")
