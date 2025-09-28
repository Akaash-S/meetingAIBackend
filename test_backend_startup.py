#!/usr/bin/env python3
"""
Test Backend Startup
"""

import os
import sys
from dotenv import load_dotenv

def test_backend_startup():
    """Test if backend can start properly"""
    print("Testing Backend Startup")
    print("=" * 25)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Test importing the app
        print("1. Testing app import...")
        from app import app, get_db_connection
        print("OK: App imported successfully")
        
        # Test database connection function
        print("2. Testing database connection...")
        conn = get_db_connection()
        if conn:
            conn.close()
            print("OK: Database connection works")
        else:
            print("ERROR: Database connection failed")
            return False
        
        # Test Flask app configuration
        print("3. Testing Flask app configuration...")
        if app.config.get('SECRET_KEY'):
            print("OK: Flask app configured")
        else:
            print("ERROR: Flask app not configured properly")
            return False
        
        print("\nSUCCESS: Backend startup test completed!")
        print("Your backend is ready to run!")
        print("\nTo start the server, run:")
        print("  python app.py")
        print("\nThe server will be available at: http://localhost:5000")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Backend startup test failed: {e}")
        return False

if __name__ == '__main__':
    success = test_backend_startup()
    if not success:
        print("Please check your configuration and try again")
