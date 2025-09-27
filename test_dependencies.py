#!/usr/bin/env python3
"""
Test script to verify all dependencies can be imported correctly.
This helps identify missing dependencies before deployment.
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            importlib.import_module(module_name, package_name)
        else:
            importlib.import_module(module_name)
        print(f"✅ {module_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {module_name} - FAILED: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name} - WARNING: {e}")
        return True

def main():
    """Test all critical dependencies"""
    print("🔍 Testing critical dependencies for Render deployment...")
    print("=" * 60)
    
    # Core Flask dependencies
    print("\n📦 Core Flask Dependencies:")
    test_import("flask")
    test_import("flask_cors")
    test_import("werkzeug")
    
    # Production server
    print("\n🚀 Production Server:")
    test_import("gunicorn")
    
    # Database
    print("\n🗄️  Database:")
    test_import("psycopg2")
    
    # Environment
    print("\n🔧 Environment:")
    test_import("dotenv")
    
    # HTTP requests
    print("\n🌐 HTTP Requests:")
    test_import("requests")
    test_import("urllib3")
    
    # WebSocket support
    print("\n🔌 WebSocket Support:")
    test_import("websockets")
    test_import("flask_socketio")
    test_import("socketio")
    test_import("engineio")
    
    # AWS SDK - This is the critical one
    print("\n☁️  AWS SDK (boto3):")
    test_import("boto3")
    test_import("botocore")
    test_import("s3transfer")
    test_import("jmespath")
    
    # Supabase
    print("\n🗃️  Supabase:")
    test_import("supabase")
    test_import("gotrue")
    test_import("httpx")
    test_import("postgrest")
    
    # Google AI
    print("\n🤖 Google AI:")
    test_import("google.generativeai")
    test_import("google.auth")
    test_import("google.auth.oauthlib")
    
    # Security
    print("\n🔒 Security:")
    test_import("cryptography")
    
    # Production dependencies
    print("\n⚙️  Production Dependencies:")
    test_import("gevent")
    test_import("gevent.websocket")
    
    # Utilities
    print("\n🛠️  Utilities:")
    test_import("structlog")
    test_import("dateutil")
    
    print("\n" + "=" * 60)
    print("✅ Dependency test completed!")
    print("\nIf any dependencies failed, they need to be added to requirements.txt")

if __name__ == "__main__":
    main()
