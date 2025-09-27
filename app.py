from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys
import os
import uuid
from datetime import datetime, timedelta
import requests
import json
from dotenv import load_dotenv
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Database connection pool
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require')

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes
from routes import upload_bp, transcribe_bp, extract_bp, meeting_bp, notify_bp
from routes.task_simple import task_bp

# Register blueprints
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(transcribe_bp, url_prefix='/api')
app.register_blueprint(extract_bp, url_prefix='/api')
app.register_blueprint(meeting_bp, url_prefix='/api')
app.register_blueprint(task_bp, url_prefix='/api')
app.register_blueprint(notify_bp, url_prefix='/api')

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    try:
        # Test database connection
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT 1')
            conn.close()
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            print("Please check your DATABASE_URL in .env file")
            sys.exit(1)
        
        print("🚀 Starting Flask development server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)
