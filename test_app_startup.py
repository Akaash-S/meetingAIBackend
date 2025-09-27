#!/usr/bin/env python3
"""
Test script to verify the Flask app can start properly.
This helps identify any remaining startup issues.
"""

import sys
import os
import traceback

def test_app_startup():
    """Test if the Flask app can start properly"""
    try:
        print("🔍 Testing Flask app startup...")
        
        # Import the app
        import app
        print("✅ App imported successfully")
        
        # Test if app object exists
        if hasattr(app, 'app'):
            flask_app = app.app
            print("✅ Flask app object found")
        else:
            print("❌ Flask app object not found")
            return False
        
        # Test app configuration
        print(f"✅ App name: {flask_app.name}")
        print(f"✅ Debug mode: {flask_app.debug}")
        
        # Test if we can create app context
        with flask_app.app_context():
            print("✅ App context created successfully")
        
        # Test if we can get the app config
        config = flask_app.config
        print(f"✅ Config loaded: {len(config)} settings")
        
        # Test if blueprints are registered
        blueprints = list(flask_app.blueprints.keys())
        print(f"✅ Blueprints registered: {blueprints}")
        
        print("\n🎉 App startup test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ App startup test FAILED!")
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔧 Testing environment...")
    
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    optional_vars = ['RAPIDAPI_KEY', 'GEMINI_API_KEY', 'SUPABASE_URL']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"⚠️  {var}: Not set (will use default)")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"ℹ️  {var}: Not set (optional)")

def main():
    """Run all tests"""
    print("🚀 Flask App Startup Test")
    print("=" * 50)
    
    # Test environment
    test_environment()
    
    # Test app startup
    success = test_app_startup()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests PASSED! App should work on Render.")
    else:
        print("❌ Tests FAILED! Check the errors above.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
