from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import sys
import os
import uuid
from datetime import datetime, timedelta
import requests
import json
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Set db instance in models
import models
models.db = db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models and routes after db initialization
from models import User, Meeting, Task
from routes import upload_bp, transcribe_bp, extract_bp, meeting_bp, task_bp, notify_bp

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
    db.session.rollback()
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            # Test database connection
            with db.engine.connect() as connection:
                connection.execute(db.text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Check if tables exist
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                tables = [row[0] for row in result]
            
            expected_tables = ['users', 'meetings', 'tasks']
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                print(f"⚠️ Missing tables: {missing_tables}")
                print("📋 Creating missing tables...")
                db.create_all()
                print("✅ Database tables created successfully")
                
                # Verify tables were created
                with db.engine.connect() as connection:
                    result = connection.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
                    tables = [row[0] for row in result]
                
                print(f"📋 Found tables: {tables}")
                for table in expected_tables:
                    if table in tables:
                        print(f"✅ Table '{table}' exists")
                    else:
                        print(f"❌ Table '{table}' still missing")
            else:
                print("✅ All required tables exist")
                print(f"📋 Found tables: {tables}")
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            print("Please check your DATABASE_URL in .env file")
            print("Run 'python init_database.py' to initialize the database")
            sys.exit(1)
    
    print("🚀 Starting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
