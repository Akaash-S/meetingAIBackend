#!/usr/bin/env python3
"""
Server restart script with better configuration
"""

import subprocess
import sys
import os
import time
import signal
import psutil

def kill_existing_processes():
    """Kill any existing Flask processes"""
    print("🔄 Checking for existing Flask processes...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if 'python' in cmdline and ('app.py' in cmdline or 'flask' in cmdline):
                print(f"   Killing process {proc.info['pid']}: {cmdline}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def start_server():
    """Start the Flask server with proper configuration"""
    print("🚀 Starting Flask server with improved configuration...")
    
    # Set environment variables for better performance
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    env['PYTHONUNBUFFERED'] = '1'
    
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print(f"✅ Server started with PID: {process.pid}")
        print("📝 Server logs will appear below...")
        print("=" * 50)
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        process.terminate()
        process.wait()
        print("✅ Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Restarting AI Meeting Assistant Backend...")
    print("=" * 50)
    
    # Kill existing processes
    kill_existing_processes()
    
    # Wait a moment
    time.sleep(2)
    
    # Start server
    start_server()
