#!/usr/bin/env python3
"""
Start the Flask server with proper error handling
"""

import os
import sys
from app import app

if __name__ == "__main__":
    try:
        print("🚀 Starting Flask server...")
        print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
