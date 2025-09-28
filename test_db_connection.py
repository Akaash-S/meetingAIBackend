#!/usr/bin/env python3
"""
Test database connection
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_db_connection():
    """Test database connection"""
    try:
        # Check environment variables
        print("Environment variables:")
        print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
        print(f"DB_HOST: {os.getenv('DB_HOST', 'Not set')}")
        print(f"DB_NAME: {os.getenv('DB_NAME', 'Not set')}")
        print(f"DB_USER: {os.getenv('DB_USER', 'Not set')}")
        print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'Not set')}")
        
        # Try to connect using DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            print(f"\nTrying to connect using DATABASE_URL...")
            conn = psycopg2.connect(database_url)
            print("✅ Connected successfully using DATABASE_URL")
            
            # Test a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"PostgreSQL version: {version[0]}")
            
            # Check if tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")
            
            cursor.close()
            conn.close()
            
        else:
            print("❌ DATABASE_URL not set")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_db_connection()
