#!/usr/bin/env python3
"""
Fix ORM Models Script
This script ensures the SQLAlchemy models work with the manually created tables.
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

def fix_orm_models():
    """Fix ORM models to work with existing tables"""
    logger.info("🔧 Fixing ORM models...")
    
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
            
            # Check if tables exist
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                tables = [row[0] for row in result]
            
            logger.info(f"📋 Found tables: {tables}")
            
            # Test model queries
            logger.info("🧪 Testing model queries...")
            
            # Test User model
            try:
                users = User.query.all()
                logger.info(f"✅ User query successful: {len(users)} users found")
            except Exception as e:
                logger.error(f"❌ User query failed: {e}")
                return False
            
            # Test Meeting model
            try:
                meetings = Meeting.query.all()
                logger.info(f"✅ Meeting query successful: {len(meetings)} meetings found")
            except Exception as e:
                logger.error(f"❌ Meeting query failed: {e}")
                return False
            
            # Test Task model
            try:
                tasks = Task.query.all()
                logger.info(f"✅ Task query successful: {len(tasks)} tasks found")
            except Exception as e:
                logger.error(f"❌ Task query failed: {e}")
                return False
            
            # Test creating a new record
            logger.info("🧪 Testing record creation...")
            try:
                # Create a test user
                test_user = User(
                    name="ORM Test User",
                    email="orm-test@example.com",
                    role="user"
                )
                db.session.add(test_user)
                db.session.commit()
                logger.info("✅ User creation via ORM successful")
                
                # Create a test meeting
                test_meeting = Meeting(
                    title="ORM Test Meeting",
                    user_id=test_user.id,
                    status="uploaded"
                )
                db.session.add(test_meeting)
                db.session.commit()
                logger.info("✅ Meeting creation via ORM successful")
                
                # Create a test task
                test_task = Task(
                    name="ORM Test Task",
                    description="Test task created via ORM",
                    category=TaskCategory.ACTION_ITEM,
                    meeting_id=test_meeting.id,
                    user_id=test_user.id
                )
                db.session.add(test_task)
                db.session.commit()
                logger.info("✅ Task creation via ORM successful")
                
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
                logger.error(f"❌ ORM test failed: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            logger.info("🎉 ORM models are working correctly!")
            return True
            
        except Exception as e:
            logger.error(f"❌ ORM fix failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main function"""
    logger.info("🎯 MeetingAI Backend ORM Fix")
    logger.info("=" * 50)
    
    if fix_orm_models():
        logger.info("🎉 ORM models are working correctly!")
        logger.info("Your backend should now work properly with the database")
    else:
        logger.error("❌ ORM fix failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
