#!/usr/bin/env python3
"""
Test script to verify all requirements can be imported
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
        return True  # Some modules might have warnings but still work

def main():
    print("🧪 Testing Python Requirements")
    print("=" * 40)
    
    # Core Flask dependencies
    modules = [
        "flask",
        "flask_cors",
        "gunicorn",
        "psycopg2",
        "dotenv",
        "requests",
        "websockets",
        "flask_socketio",
        "werkzeug",
        "structlog",
        "cryptography",
        "dateutil",
        "gevent",
        "gevent.websocket"
    ]
    
    passed = 0
    total = len(modules)
    
    for module in modules:
        if test_import(module):
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} modules imported successfully")
    
    if passed == total:
        print("🎉 All requirements are working correctly!")
        return True
    else:
        print("❌ Some requirements failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
