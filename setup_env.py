#!/usr/bin/env python3
"""
Environment Setup Script
This script helps you create the .env file and configure your database connection.
"""

import os
import sys
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from env.example"""
    print("🔧 Setting up environment configuration...")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Do you want to overwrite it? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Setup cancelled")
            return False
    
    # Copy from env.example
    if os.path.exists('env.example'):
        shutil.copy('env.example', '.env')
        print("✅ Created .env file from env.example")
    else:
        print("❌ env.example file not found")
        return False
    
    return True

def get_database_url():
    """Get database URL from user"""
    print("\n🗄️  Database Configuration")
    print("=" * 50)
    print("You need to provide your Neon PostgreSQL connection string.")
    print("Get it from: https://console.neon.tech")
    print("")
    print("Example format:")
    print("postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require")
    print("")
    
    while True:
        database_url = input("Enter your DATABASE_URL: ").strip()
        
        if not database_url:
            print("❌ Database URL cannot be empty")
            continue
            
        if not database_url.startswith('postgresql://'):
            print("❌ Database URL must start with 'postgresql://'")
            continue
            
        # Test the connection
        print("🔍 Testing database connection...")
        try:
            import psycopg2
            conn = psycopg2.connect(database_url)
            conn.close()
            print("✅ Database connection successful!")
            return database_url
        except ImportError:
            print("⚠️  psycopg2 not installed, skipping connection test")
            return database_url
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            retry = input("Do you want to try again? (yes/no): ")
            if retry.lower() not in ['yes', 'y']:
                return database_url

def update_env_file(database_url):
    """Update .env file with database URL"""
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace DATABASE_URL
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('DATABASE_URL='):
                lines[i] = f'DATABASE_URL={database_url}'
                break
        
        # Write back to file
        with open('.env', 'w') as f:
            f.write('\n'.join(lines))
        
        print("✅ Updated .env file with your database URL")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_setup():
    """Test the setup"""
    print("\n🧪 Testing setup...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in .env file")
            return False
        
        print(f"✅ DATABASE_URL loaded: {database_url[:30]}...")
        
        # Test database connection
        try:
            import psycopg2
            conn = psycopg2.connect(database_url)
            conn.close()
            print("✅ Database connection test successful!")
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 MeetingAI Backend Environment Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the backend directory")
        return False
    
    # Step 1: Create .env file
    if not create_env_file():
        return False
    
    # Step 2: Get database URL
    database_url = get_database_url()
    if not database_url:
        print("❌ Database URL is required")
        return False
    
    # Step 3: Update .env file
    if not update_env_file(database_url):
        return False
    
    # Step 4: Test setup
    if not test_setup():
        print("❌ Setup test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Environment setup completed successfully!")
    print("")
    print("Next steps:")
    print("1. Start the backend server: python app.py")
    print("2. Or run database setup: python setup_database.py")
    print("3. Test the connection: python test_db_connection.py")
    print("")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
