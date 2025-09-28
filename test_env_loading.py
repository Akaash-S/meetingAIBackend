#!/usr/bin/env python3
"""
Test Environment Variable Loading
This script tests if python-dotenv is working correctly.
"""

import os
from dotenv import load_dotenv

def test_env_loading():
    """Test environment variable loading"""
    print("Testing Environment Variable Loading")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("OK: .env file exists")
    else:
        print("ERROR: .env file not found")
        return False
    
    # Test key environment variables
    env_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'FLASK_ENV'
    ]
    
    print("\nEnvironment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == 'DATABASE_URL':
                print(f"OK: {var} = {value[:30]}...")
            else:
                print(f"OK: {var} = {value}")
        else:
            print(f"ERROR: {var} not found")
    
    # Test DATABASE_URL specifically
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgresql://'):
            print("\nOK: DATABASE_URL format is correct")
            return True
        else:
            print("\nERROR: DATABASE_URL format is incorrect")
            return False
    else:
        print("\nERROR: DATABASE_URL not found")
        return False

if __name__ == '__main__':
    success = test_env_loading()
    if success:
        print("\nSUCCESS: Environment variables are loaded correctly!")
    else:
        print("\nERROR: Environment variable loading failed!")
        print("Please run: python fix_database_connection_windows.py")
