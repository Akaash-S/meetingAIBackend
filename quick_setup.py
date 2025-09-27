#!/usr/bin/env python3
"""
Quick Setup Script for MeetingAI Backend
This script automates the entire setup process.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors"""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        return False

def check_environment():
    """Check if environment variables are set"""
    logger.info("🔍 Checking environment variables...")
    
    required_vars = ['DATABASE_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set these variables in your .env file")
        return False
    
    logger.info("✅ Environment variables check passed")
    return True

def install_dependencies():
    """Install Python dependencies"""
    logger.info("📦 Installing dependencies...")
    
    # Try different requirement files
    requirements_files = [
        'requirements.txt',
        'requirements-windows.txt',
        'requirements-dev.txt'
    ]
    
    for req_file in requirements_files:
        if os.path.exists(req_file):
            logger.info(f"📋 Found {req_file}")
            if run_command(f"pip install -r {req_file}", f"Installing {req_file}"):
                return True
    
    logger.error("❌ No requirements file found")
    return False

def setup_database():
    """Set up database tables"""
    logger.info("🗄️ Setting up database...")
    
    if run_command("python setup_database.py", "Database setup"):
        return True
    else:
        logger.warning("⚠️ Database setup failed, trying manual setup...")
        return run_command("python check_database.py", "Database check")

def main():
    """Main setup function"""
    logger.info("🎯 MeetingAI Backend Quick Setup")
    logger.info("=" * 50)
    
    # Check environment
    if not check_environment():
        logger.error("❌ Environment check failed")
        logger.info("Please set up your .env file first")
        logger.info("Copy env.example to .env and update with your credentials")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        logger.error("❌ Dependency installation failed")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        logger.error("❌ Database setup failed")
        logger.info("Please check your DATABASE_URL and try again")
        sys.exit(1)
    
    logger.info("🎉 Setup completed successfully!")
    logger.info("You can now run: python app.py")
    logger.info("Or test with: python check_database.py")

if __name__ == '__main__':
    main()
