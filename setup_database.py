#!/usr/bin/env python3
"""
Database Setup Script for MeetingAI Backend
This script initializes the database, creates tables, and sets up Supabase storage.
"""

import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL not found in environment variables")
        logger.info("Please set DATABASE_URL in your .env file")
        logger.info("Example: DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require")
        sys.exit(1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    return app

def setup_database():
    """Set up database tables and migrations"""
    logger.info("🚀 Setting up database...")
    
    # Create Flask app
    app = create_app()
    
    # Initialize database
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    
    # Import models after db initialization
    from models import User, Meeting, Task
    models.db = db
    
    with app.app_context():
        try:
            # Test database connection
            logger.info("🔗 Testing database connection...")
            db.engine.execute('SELECT 1')
            logger.info("✅ Database connection successful")
            
            # Create all tables
            logger.info("📋 Creating database tables...")
            db.create_all()
            logger.info("✅ Database tables created successfully")
            
            # Initialize migrations if not exists
            migrations_dir = 'migrations'
            if not os.path.exists(migrations_dir):
                logger.info("🔄 Initializing database migrations...")
                init()
                logger.info("✅ Migrations initialized")
            
            # Create initial migration
            logger.info("📝 Creating initial migration...")
            migrate(message='Initial migration')
            logger.info("✅ Initial migration created")
            
            # Apply migrations
            logger.info("⬆️ Applying migrations...")
            upgrade()
            logger.info("✅ Migrations applied successfully")
            
            # Verify tables exist
            logger.info("🔍 Verifying tables...")
            tables = db.engine.table_names()
            expected_tables = ['users', 'meetings', 'tasks']
            
            for table in expected_tables:
                if table in tables:
                    logger.info(f"✅ Table '{table}' exists")
                else:
                    logger.warning(f"⚠️ Table '{table}' not found")
            
            logger.info("🎉 Database setup completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            sys.exit(1)

def setup_supabase():
    """Set up Supabase storage bucket"""
    logger.info("🔧 Setting up Supabase storage...")
    
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
        
        # Check if bucket exists
        logger.info(f"🔍 Checking bucket '{supabase_bucket}'...")
        buckets = supabase.storage.list_buckets()
        
        bucket_exists = any(bucket.name == supabase_bucket for bucket in buckets)
        
        if not bucket_exists:
            logger.info(f"📦 Creating bucket '{supabase_bucket}'...")
            # Note: Bucket creation requires admin privileges
            # You may need to create the bucket manually in Supabase dashboard
            logger.warning("⚠️ Bucket creation requires admin privileges")
            logger.info(f"Please create bucket '{supabase_bucket}' manually in Supabase dashboard")
        else:
            logger.info(f"✅ Bucket '{supabase_bucket}' exists")
        
        # Test upload (small test file)
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
        logger.error(f"❌ Supabase setup failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🎯 MeetingAI Backend Database Setup")
    logger.info("=" * 50)
    
    # Check environment variables
    required_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please check your .env file")
        sys.exit(1)
    
    # Setup database
    setup_database()
    
    # Setup Supabase
    setup_supabase()
    
    logger.info("🎉 Setup completed successfully!")
    logger.info("You can now run: python app.py")

if __name__ == '__main__':
    main()
