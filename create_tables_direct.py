#!/usr/bin/env python3
"""
Direct Table Creation Script
This script directly creates the database tables using SQLAlchemy.
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

def create_tables():
    """Create database tables directly"""
    logger.info("🚀 Creating database tables...")
    
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
                    logger.warning(f"⚠️ Table '{table}' not found")
            
            # Test inserting data
            logger.info("🧪 Testing data insertion...")
            try:
                # Create a test user
                test_user = User(
                    name="Test User",
                    email="test@example.com",
                    role="user"
                )
                db.session.add(test_user)
                db.session.commit()
                logger.info("✅ User creation test successful")
                
                # Create a test meeting
                test_meeting = Meeting(
                    title="Test Meeting",
                    user_id=test_user.id,
                    status="uploaded"
                )
                db.session.add(test_meeting)
                db.session.commit()
                logger.info("✅ Meeting creation test successful")
                
                # Create a test task
                test_task = Task(
                    name="Test Task",
                    description="Test task description",
                    category="action-item",
                    meeting_id=test_meeting.id,
                    user_id=test_user.id
                )
                db.session.add(test_task)
                db.session.commit()
                logger.info("✅ Task creation test successful")
                
                # Clean up test data
                db.session.delete(test_task)
                db.session.delete(test_meeting)
                db.session.delete(test_user)
                db.session.commit()
                logger.info("🧹 Test data cleaned up")
                
            except Exception as e:
                logger.error(f"❌ Data insertion test failed: {e}")
                return False
            
            logger.info("🎉 Database setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False

def main():
    """Main function"""
    logger.info("🎯 MeetingAI Backend Direct Table Creation")
    logger.info("=" * 50)
    
    if create_tables():
        logger.info("🎉 All tables created successfully!")
        logger.info("You can now run: python app.py")
    else:
        logger.error("❌ Table creation failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
