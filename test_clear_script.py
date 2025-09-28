#!/usr/bin/env python3
"""
Test script to verify the clear_database.py script works correctly
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test if we can connect to the database"""
    print("🧪 Testing database connection...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        print("Please make sure your .env file contains the DATABASE_URL")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        # Get table information
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"✅ Database connection successful")
        print(f"📋 Found tables: {tables}")
        
        # Get record counts
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count} records")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Testing clear_database.py prerequisites...")
    print("=" * 50)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("Please copy env.example to .env and configure your DATABASE_URL")
        sys.exit(1)
    
    # Test database connection
    if test_database_connection():
        print("\n✅ All tests passed!")
        print("🚀 You can now run: python clear_database.py")
    else:
        print("\n❌ Tests failed!")
        print("Please check your DATABASE_URL configuration")
        sys.exit(1)
