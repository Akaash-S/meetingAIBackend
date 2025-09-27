#!/usr/bin/env python3
"""
Database Initialization Script
This script properly initializes the database with all tables using SQLAlchemy ORM.
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
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL not found in environment variables")
        logger.info("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    return app

def init_database():
    """Initialize database with all tables"""
    logger.info("🚀 Initializing database...")
    
    # Create Flask app
    app = create_app()
    
    # Initialize database
    db = SQLAlchemy(app)
    
    # Import and configure models
    import models
    from models import User, Meeting, Task, TaskStatus, TaskPriority, TaskCategory
    models.db = db
    
    with app.app_context():
        try:
            # Test database connection
            logger.info("🔗 Testing database connection...")
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            logger.info("✅ Database connection successful")
            
            # Drop existing tables (for clean setup)
            logger.info("🧹 Dropping existing tables...")
            db.drop_all()
            logger.info("✅ Existing tables dropped")
            
            # Create all tables
            logger.info("📋 Creating database tables...")
            db.create_all()
            logger.info("✅ Database tables created successfully")
            
            # Verify tables exist
            logger.info("🔍 Verifying tables...")
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                tables = [row[0] for row in result]
            
            expected_tables = ['users', 'meetings', 'tasks']
            logger.info(f"📋 Found tables: {tables}")
            
            for table in expected_tables:
                if table in tables:
                    logger.info(f"✅ Table '{table}' exists")
                else:
                    logger.error(f"❌ Table '{table}' not found")
            
            # Test model creation
            logger.info("🧪 Testing model creation...")
            try:
                # Create a test user
                test_user = User(
                    name="Test User",
                    email="test@example.com",
                    role="user"
                )
                db.session.add(test_user)
                db.session.commit()
                logger.info("✅ User model test successful")
                
                # Create a test meeting
                test_meeting = Meeting(
                    title="Test Meeting",
                    user_id=test_user.id,
                    status="uploaded"
                )
                db.session.add(test_meeting)
                db.session.commit()
                logger.info("✅ Meeting model test successful")
                
                # Create a test task
                test_task = Task(
                    name="Test Task",
                    description="Test task description",
                    category=TaskCategory.ACTION_ITEM,
                    meeting_id=test_meeting.id,
                    user_id=test_user.id
                )
                db.session.add(test_task)
                db.session.commit()
                logger.info("✅ Task model test successful")
                
                # Test relationships
                logger.info("🔗 Testing relationships...")
                user_meetings = test_user.meetings
                user_tasks = test_user.tasks
                meeting_tasks = test_meeting.tasks
                
                logger.info(f"   User has {len(user_meetings)} meetings")
                logger.info(f"   User has {len(user_tasks)} tasks")
                logger.info(f"   Meeting has {len(meeting_tasks)} tasks")
                
                # Clean up test data
                db.session.delete(test_task)
                db.session.delete(test_meeting)
                db.session.delete(test_user)
                db.session.commit()
                logger.info("🧹 Test data cleaned up")
                
            except Exception as e:
                logger.error(f"❌ Model test failed: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            logger.info("🎉 Database initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function"""
    logger.info("🎯 MeetingAI Backend Database Initialization")
    logger.info("=" * 60)
    
    if init_database():
        logger.info("🎉 Database initialization successful!")
        logger.info("You can now run: python app.py")
    else:
        logger.error("❌ Database initialization failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
