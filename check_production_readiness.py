#!/usr/bin/env python3
"""
Production Readiness Check
This script checks if the backend is ready for production use.
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

def check_environment():
    """Check environment variables"""
    logger.info("🔍 Checking environment variables...")
    
    required_vars = [
        'DATABASE_URL',
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True

def check_dependencies():
    """Check if all dependencies are installed"""
    logger.info("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'flask-sqlalchemy',
        'flask-cors',
        'psycopg2',
        'supabase',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"❌ Missing packages: {', '.join(missing_packages)}")
        logger.info("Run: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All dependencies are installed")
    return True

def check_database():
    """Check database connection"""
    logger.info("🔍 Checking database connection...")
    
    try:
        import psycopg2
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def check_supabase():
    """Check Supabase connection"""
    logger.info("🔍 Checking Supabase connection...")
    
    try:
        from supabase import create_client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        supabase = create_client(supabase_url, supabase_key)
        buckets = supabase.storage.list_buckets()
        logger.info("✅ Supabase connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False

def check_files():
    """Check if all required files exist"""
    logger.info("🔍 Checking required files...")
    
    required_files = [
        'app.py',
        'models.py',
        'config.py',
        'requirements.txt',
        '.env'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    logger.info("✅ All required files exist")
    return True

def check_security():
    """Check security configurations"""
    logger.info("🔍 Checking security configurations...")
    
    # Check if secret key is set
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or secret_key == 'dev-secret-key':
        logger.warning("⚠️ SECRET_KEY is not set or using default value")
        logger.info("Please set a strong SECRET_KEY in production")
    
    # Check if database URL is secure
    database_url = os.getenv('DATABASE_URL')
    if 'localhost' in database_url or '127.0.0.1' in database_url:
        logger.warning("⚠️ Database URL contains localhost")
        logger.info("Use production database URL in production")
    
    logger.info("✅ Security check completed")
    return True

def main():
    """Main check function"""
    logger.info("🎯 MeetingAI Backend Production Readiness Check")
    logger.info("=" * 70)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Dependencies", check_dependencies),
        ("Database Connection", check_database),
        ("Supabase Connection", check_supabase),
        ("Required Files", check_files),
        ("Security Configuration", check_security),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        logger.info(f"\n🧪 Running {check_name}...")
        if check_func():
            passed += 1
        else:
            logger.error(f"❌ {check_name} failed")
    
    logger.info("\n" + "=" * 70)
    logger.info(f"📊 Readiness Check: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 Your backend is production-ready!")
        logger.info("\n✅ Production Checklist:")
        logger.info("   ✅ Environment variables configured")
        logger.info("   ✅ All dependencies installed")
        logger.info("   ✅ Database connection working")
        logger.info("   ✅ Supabase storage configured")
        logger.info("   ✅ All required files present")
        logger.info("   ✅ Security configurations checked")
        
        logger.info("\n🚀 Ready for deployment!")
        logger.info("   • Development: python app.py")
        logger.info("   • Production: gunicorn app:app")
        logger.info("   • Docker: docker build -t meeting-ai-backend .")
        
    else:
        logger.error(f"❌ {total - passed} checks failed")
        logger.error("Please fix the issues above before deploying")
        return False
    
    return True

if __name__ == '__main__':
    main()
