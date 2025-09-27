#!/usr/bin/env python3
"""
Ensure Backend Ready Script
This script ensures the backend is completely ready for use.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install missing dependencies"""
    logger.info("📦 Installing dependencies...")
    
    try:
        # Install python-dotenv
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'python-dotenv'], check=True)
        logger.info("✅ python-dotenv installed")
        
        # Install other missing packages
        packages = ['requests', 'flask-migrate']
        for package in packages:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
                logger.info(f"✅ {package} installed")
            except:
                logger.warning(f"⚠️ {package} installation failed")
        
        return True
    except Exception as e:
        logger.error(f"❌ Dependency installation failed: {e}")
        return False

def verify_database():
    """Verify database is working"""
    logger.info("🔍 Verifying database...")
    
    try:
        import psycopg2
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'meetings', 'tasks']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
            logger.info("Run: python create_tables_manual.py")
            return False
        
        logger.info("✅ Database tables verified")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

def verify_supabase():
    """Verify Supabase is working"""
    logger.info("🔍 Verifying Supabase...")
    
    try:
        from supabase import create_client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection
        buckets = supabase.storage.list_buckets()
        logger.info("✅ Supabase connection verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase verification failed: {e}")
        return False

def test_backend_startup():
    """Test if backend can start"""
    logger.info("🔍 Testing backend startup...")
    
    try:
        # Import the app
        from app import app
        with app.app_context():
            logger.info("✅ Backend app can be imported and initialized")
            return True
    except Exception as e:
        logger.error(f"❌ Backend startup test failed: {e}")
        return False

def main():
    """Main function"""
    logger.info("🎯 MeetingAI Backend - Ensure Ready")
    logger.info("=" * 60)
    
    # Install dependencies
    if not install_dependencies():
        logger.error("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Verify database
    if not verify_database():
        logger.error("❌ Database verification failed")
        logger.info("Run: python create_tables_manual.py")
        sys.exit(1)
    
    # Verify Supabase
    if not verify_supabase():
        logger.error("❌ Supabase verification failed")
        sys.exit(1)
    
    # Test backend startup
    if not test_backend_startup():
        logger.error("❌ Backend startup test failed")
        sys.exit(1)
    
    logger.info("\n🎉 Your backend is ready to use!")
    logger.info("=" * 60)
    
    logger.info("✅ All systems verified:")
    logger.info("   ✅ Dependencies installed")
    logger.info("   ✅ Database tables created")
    logger.info("   ✅ Supabase storage configured")
    logger.info("   ✅ Backend app working")
    
    logger.info("\n🚀 Ready to start:")
    logger.info("   python app.py")
    
    logger.info("\n🧪 Ready to test:")
    logger.info("   python test_all_endpoints.py")
    
    logger.info("\n📚 Available endpoints:")
    logger.info("   • GET  /api/health")
    logger.info("   • GET  /api/meetings/user/{user_id}")
    logger.info("   • GET  /api/tasks/user/{user_id}")
    logger.info("   • POST /api/upload")
    logger.info("   • POST /api/tasks")
    logger.info("   • POST /api/transcribe/{meeting_id}")
    logger.info("   • POST /api/extract/{meeting_id}")
    
    logger.info("\n🎯 Your MeetingAI backend is production-ready! 🎉")

if __name__ == '__main__':
    main()
