#!/usr/bin/env python3
"""
Setup script for the Meeting Assistant Backend
"""
import os
import sys
import subprocess
import platform

def install_requirements():
    """Install requirements based on the operating system"""
    system = platform.system().lower()
    
    print(f"Detected operating system: {system}")
    
    if system == "windows":
        print("Installing Windows-compatible requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-windows.txt"])
    else:
        print("Installing standard requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_environment():
    """Setup environment file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("Creating .env file from template...")
        with open('env.example', 'r') as f:
            content = f.read()
        with open('.env', 'w') as f:
            f.write(content)
        print("✅ Created .env file. Please edit it with your API keys.")
    else:
        print("✅ .env file already exists.")

def create_database():
    """Create database tables"""
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully.")
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        print("Make sure to set up your database connection in .env file.")

def main():
    """Main setup function"""
    print("🚀 Setting up Meeting Assistant Backend...")
    
    try:
        # Install requirements
        install_requirements()
        print("✅ Requirements installed successfully.")
        
        # Setup environment
        setup_environment()
        
        # Create database
        create_database()
        
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your API keys")
        print("2. Run: python run.py")
        print("3. API will be available at http://localhost:5000")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
