#!/usr/bin/env python3
"""
Test script to verify backend setup
"""
import sys
import os

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test Flask app
        from app import app, db
        print("✅ Flask app imported successfully")
        
        # Test models
        from models import User, Meeting, Task
        print("✅ Models imported successfully")
        
        # Test routes
        from routes import upload_bp, transcribe_bp, extract_bp, meeting_bp, task_bp, notify_bp
        print("✅ Routes imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database():
    """Test database connection"""
    try:
        from app import app, db
        
        with app.app_context():
            # Try to create tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test a simple query
            from models import User
            user_count = User.query.count()
            print(f"✅ Database query successful (users: {user_count})")
            
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing backend setup...\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed!")
        return False
    
    print()
    
    # Test database
    if not test_database():
        print("\n❌ Database test failed!")
        return False
    
    print("\n🎉 All tests passed! Backend is ready to run.")
    print("\nTo start the server, run:")
    print("python run.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
