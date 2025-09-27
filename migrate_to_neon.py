#!/usr/bin/env python3
"""
Database migration script for Neon PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app import app, db

def test_connection():
    """Test database connection"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
        
        print(f"🔗 Testing connection to: {database_url.split('@')[1] if '@' in database_url else 'database'}")
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully to PostgreSQL {version}")
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_tables():
    """Create database tables"""
    try:
        with app.app_context():
            print("📋 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

def verify_tables():
    """Verify tables were created"""
    try:
        with app.app_context():
            from models import User, Meeting, Task
            
            # Test if we can query the tables
            user_count = User.query.count()
            meeting_count = Meeting.query.count()
            task_count = Task.query.count()
            
            print(f"📊 Database verification:")
            print(f"   - Users: {user_count}")
            print(f"   - Meetings: {meeting_count}")
            print(f"   - Tasks: {task_count}")
            print("✅ All tables verified successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying tables: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Migrating to Neon PostgreSQL...")
    
    # Load environment variables
    load_dotenv()
    
    # Test connection
    if not test_connection():
        print("\n❌ Migration failed: Could not connect to database")
        print("Please check your DATABASE_URL in .env file")
        return False
    
    # Create tables
    if not create_tables():
        print("\n❌ Migration failed: Could not create tables")
        return False
    
    # Verify tables
    if not verify_tables():
        print("\n❌ Migration failed: Tables not created properly")
        return False
    
    print("\n🎉 Migration completed successfully!")
    print("\nYour backend is now ready to use with Neon PostgreSQL!")
    print("\nNext steps:")
    print("1. Configure Supabase for file storage")
    print("2. Set up your API keys in .env")
    print("3. Run: python run.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
