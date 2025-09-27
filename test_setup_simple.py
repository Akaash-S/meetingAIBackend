#!/usr/bin/env python3
"""
Simple Database Test Script
This script tests the basic database setup without complex dependencies.
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_environment():
    """Test environment variables"""
    logger.info("🔍 Testing environment variables...")
    
    required_vars = ['DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ Environment variables check passed")
    return True

def test_database_connection():
    """Test database connection"""
    logger.info("🔗 Testing database connection...")
    
    try:
        import psycopg2
        database_url = os.getenv('DATABASE_URL')
        
        # Parse connection string
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test connection
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        
        if result[0] == 1:
            logger.info("✅ Database connection successful")
            
            # Check if tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"📋 Found tables: {tables}")
            
            expected_tables = ['users', 'meetings', 'tasks']
            for table in expected_tables:
                if table in tables:
                    logger.info(f"✅ Table '{table}' exists")
                else:
                    logger.warning(f"⚠️ Table '{table}' not found")
            
            cursor.close()
            conn.close()
            return True
        else:
            logger.error("❌ Database connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_supabase_connection():
    """Test Supabase connection"""
    logger.info("🔧 Testing Supabase connection...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        logger.warning("⚠️ Supabase credentials not found")
        logger.info("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in your .env file")
        return False
    
    try:
        from supabase import create_client, Client
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test connection by listing buckets
        buckets = supabase.storage.list_buckets()
        logger.info(f"✅ Supabase connection successful")
        logger.info(f"📦 Found {len(buckets)} buckets")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🎯 MeetingAI Backend Simple Test")
    logger.info("=" * 50)
    
    # Test environment
    if not test_environment():
        logger.error("❌ Environment test failed")
        sys.exit(1)
    
    # Test database
    if not test_database_connection():
        logger.error("❌ Database test failed")
        logger.info("Please check your DATABASE_URL and ensure the database is accessible")
        sys.exit(1)
    
    # Test Supabase
    if not test_supabase_connection():
        logger.warning("⚠️ Supabase test failed")
        logger.info("Please check your Supabase credentials")
    
    logger.info("🎉 Basic tests completed!")
    logger.info("Your backend should be ready to use")

if __name__ == '__main__':
    main()
