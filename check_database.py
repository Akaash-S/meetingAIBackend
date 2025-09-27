#!/usr/bin/env python3
"""
Database Check Script for MeetingAI Backend
This script checks database connection and table status.
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database():
    """Check database connection and tables"""
    logger.info("🔍 Checking database status...")
    
    # Create Flask app
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL not found in environment variables")
        return False
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize database
    db = SQLAlchemy(app)
    
    # Import models after db initialization
    import models
    from models import User, Meeting, Task
    models.db = db
    
    with app.app_context():
        try:
            # Test database connection
            logger.info("🔗 Testing database connection...")
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            logger.info("✅ Database connection successful")
            
            # Check tables
            logger.info("📋 Checking database tables...")
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                tables = [row[0] for row in result]
            expected_tables = ['users', 'meetings', 'tasks']
            
            logger.info(f"Found tables: {tables}")
            
            for table in expected_tables:
                if table in tables:
                    logger.info(f"✅ Table '{table}' exists")
                    
                    # Check table structure
                    try:
                        with db.engine.connect() as connection:
                            result = connection.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
                            count = result.fetchone()[0]
                        logger.info(f"   📊 Records in '{table}': {count}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Could not count records in '{table}': {e}")
                else:
                    logger.error(f"❌ Table '{table}' not found")
            
            # Test model creation
            logger.info("🧪 Testing model creation...")
            try:
                # Test User model
                test_user = User(
                    name="Test User",
                    email="test@example.com",
                    role="user"
                )
                db.session.add(test_user)
                db.session.commit()
                logger.info("✅ User model test successful")
                
                # Test Meeting model
                test_meeting = Meeting(
                    title="Test Meeting",
                    user_id=test_user.id,
                    status="uploaded"
                )
                db.session.add(test_meeting)
                db.session.commit()
                logger.info("✅ Meeting model test successful")
                
                # Test Task model
                test_task = Task(
                    name="Test Task",
                    description="Test task description",
                    category="action-item",
                    meeting_id=test_meeting.id,
                    user_id=test_user.id
                )
                db.session.add(test_task)
                db.session.commit()
                logger.info("✅ Task model test successful")
                
                # Clean up test data
                db.session.delete(test_task)
                db.session.delete(test_meeting)
                db.session.delete(test_user)
                db.session.commit()
                logger.info("🧹 Test data cleaned up")
                
            except Exception as e:
                logger.error(f"❌ Model test failed: {e}")
                return False
            
            logger.info("🎉 Database check completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database check failed: {e}")
            return False

def check_supabase():
    """Check Supabase storage connection"""
    logger.info("🔧 Checking Supabase storage...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    supabase_bucket = os.getenv('SUPABASE_BUCKET', 'meeting-files')
    
    if not supabase_url or not supabase_key:
        logger.warning("⚠️ Supabase credentials not found")
        logger.info("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in your .env file")
        return False
    
    try:
        from supabase import create_client, Client
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Check bucket
        logger.info(f"🔍 Checking bucket '{supabase_bucket}'...")
        buckets = supabase.storage.list_buckets()
        
        bucket_exists = any(bucket.name == supabase_bucket for bucket in buckets)
        
        if bucket_exists:
            logger.info(f"✅ Bucket '{supabase_bucket}' exists")
        else:
            logger.warning(f"⚠️ Bucket '{supabase_bucket}' not found")
            logger.info("Please create the bucket in Supabase dashboard")
            return False
        
        # Test upload
        logger.info("🧪 Testing Supabase upload...")
        test_content = b"test file content"
        test_path = "test/connection-test.txt"
        
        result = supabase.storage.from_(supabase_bucket).upload(
            test_path,
            test_content,
            file_options={"content-type": "text/plain"}
        )
        
        if hasattr(result, 'error') and result.error:
            logger.error(f"❌ Supabase upload test failed: {result.error}")
            return False
        
        # Clean up test file
        supabase.storage.from_(supabase_bucket).remove([test_path])
        logger.info("✅ Supabase storage test successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase check failed: {e}")
        return False

def main():
    """Main check function"""
    logger.info("🎯 MeetingAI Backend Database Check")
    logger.info("=" * 50)
    
    # Check database
    db_ok = check_database()
    
    # Check Supabase
    supabase_ok = check_supabase()
    
    if db_ok and supabase_ok:
        logger.info("🎉 All checks passed! Your backend is ready to use.")
    else:
        logger.error("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
