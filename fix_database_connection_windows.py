#!/usr/bin/env python3
"""
Database Connection Fix Script (Windows Compatible)
This script diagnoses and fixes database connection issues for the MeetingAI backend.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_dependencies():
    """Check if required Python packages are installed"""
    print("Checking Python dependencies...")
    
    required_packages = [
        'psycopg2',
        'flask',
        'flask_cors',
        'python-dotenv',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"OK: {package}")
        except ImportError:
            print(f"Missing: {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("Missing packages installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install packages: {e}")
            return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\nSetting up environment file...")
    
    if os.path.exists('.env'):
        print("OK: .env file already exists")
        return True
    
    if os.path.exists('env.example'):
        try:
            shutil.copy('env.example', '.env')
            print("OK: Created .env file from env.example")
            return True
        except Exception as e:
            print(f"Failed to create .env file: {e}")
            return False
    else:
        print("ERROR: env.example file not found")
        return False

def get_database_url_from_user():
    """Get database URL from user input"""
    print("\nDatabase Configuration Required")
    print("=" * 50)
    print("Your Neon PostgreSQL database URL is required.")
    print("Get it from: https://console.neon.tech")
    print("")
    print("Example format:")
    print("postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require")
    print("")
    
    while True:
        database_url = input("Enter your DATABASE_URL: ").strip()
        
        if not database_url:
            print("ERROR: Database URL cannot be empty")
            continue
            
        if not database_url.startswith('postgresql://'):
            print("ERROR: Database URL must start with 'postgresql://'")
            continue
            
        return database_url

def update_env_file(database_url):
    """Update .env file with database URL"""
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace DATABASE_URL
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('DATABASE_URL='):
                lines[i] = f'DATABASE_URL={database_url}'
                updated = True
                break
        
        if not updated:
            # Add DATABASE_URL if not found
            lines.append(f'DATABASE_URL={database_url}')
        
        # Write back to file
        with open('.env', 'w') as f:
            f.write('\n'.join(lines))
        
        print("OK: Updated .env file with database URL")
        return True
        
    except Exception as e:
        print(f"ERROR updating .env file: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("ERROR: DATABASE_URL not found in .env file")
            return False
        
        print(f"DATABASE_URL: {database_url[:30]}...")
        
        # Test connection
        import psycopg2
        conn = psycopg2.connect(database_url)
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        print("OK: Database connection successful!")
        print(f"Found tables: {tables}")
        
        return True
        
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

def setup_database_tables():
    """Set up database tables if they don't exist"""
    print("\nSetting up database tables...")
    
    try:
        # Import and run the database setup
        from setup_database import setup_database
        success = setup_database()
        
        if success:
            print("OK: Database tables set up successfully")
        else:
            print("ERROR: Failed to set up database tables")
        
        return success
        
    except Exception as e:
        print(f"ERROR setting up database tables: {e}")
        return False

def test_backend_startup():
    """Test if the backend can start properly"""
    print("\nTesting backend startup...")
    
    try:
        # Test importing the app
        from app import app, get_db_connection
        
        # Test database connection function
        conn = get_db_connection()
        if conn:
            conn.close()
            print("OK: Backend app imports and database connection work")
            return True
        else:
            print("ERROR: Database connection failed in app")
            return False
            
    except Exception as e:
        print(f"ERROR: Backend startup test failed: {e}")
        return False

def create_startup_script():
    """Create a simple startup script"""
    print("\nCreating startup script...")
    
    startup_script = """#!/usr/bin/env python3
# Quick startup script for MeetingAI backend

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if DATABASE_URL is set
if not os.getenv('DATABASE_URL'):
    print("ERROR: DATABASE_URL not found in .env file")
    print("Please run: python fix_database_connection_windows.py")
    sys.exit(1)

# Start the app
try:
    from app import app
    print("Starting MeetingAI Backend...")
    print("Database URL configured")
    print("Server will be available at: http://localhost:5000")
    print("")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
except Exception as e:
    print(f"Failed to start server: {e}")
    sys.exit(1)
"""
    
    try:
        with open('start_backend.py', 'w') as f:
            f.write(startup_script)
        print("OK: Created start_backend.py")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create startup script: {e}")
        return False

def main():
    """Main fix function"""
    print("MeetingAI Database Connection Fix")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("ERROR: Please run this script from the backend directory")
        return False
    
    # Step 1: Check dependencies
    if not check_python_dependencies():
        print("ERROR: Dependency check failed")
        return False
    
    # Step 2: Create .env file
    if not create_env_file():
        print("ERROR: Failed to create .env file")
        return False
    
    # Step 3: Get database URL
    database_url = get_database_url_from_user()
    if not database_url:
        print("ERROR: Database URL is required")
        return False
    
    # Step 4: Update .env file
    if not update_env_file(database_url):
        print("ERROR: Failed to update .env file")
        return False
    
    # Step 5: Test database connection
    if not test_database_connection():
        print("ERROR: Database connection test failed")
        return False
    
    # Step 6: Set up database tables
    if not setup_database_tables():
        print("ERROR: Database table setup failed")
        return False
    
    # Step 7: Test backend startup
    if not test_backend_startup():
        print("ERROR: Backend startup test failed")
        return False
    
    # Step 8: Create startup script
    create_startup_script()
    
    print("\n" + "=" * 50)
    print("SUCCESS: Database connection fix completed!")
    print("")
    print("Your backend is now ready to run!")
    print("")
    print("To start the backend server:")
    print("  python start_backend.py")
    print("  or")
    print("  python app.py")
    print("")
    print("The server will be available at: http://localhost:5000")
    print("")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nFix cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
