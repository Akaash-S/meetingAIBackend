from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import logging

from models import db, User, Meeting

upload_bp = Blueprint('upload', __name__)

# Configure file upload
ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'wav', 'm4a', 'avi', 'mov', 'wmv', 'flv', 'webm'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_s3(file, bucket_name, object_name):
    """Upload file to S3 bucket"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        
        s3_client.upload_fileobj(file, bucket_name, object_name)
        
        # Generate presigned URL for file access
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=3600  # 1 hour
        )
        
        return url
    except ClientError as e:
        logging.error(f"Error uploading to S3: {e}")
        return None

def upload_to_supabase(file, bucket_name, object_name):
    """Upload file to Supabase Storage"""
    try:
        from supabase import create_client, Client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        
        if not url or not key:
            logging.error("Supabase URL or key not configured")
            return None
        
        supabase: Client = create_client(url, key)
        
        # Reset file pointer to beginning
        file.seek(0)
        
        # Upload file to Supabase Storage
        result = supabase.storage.from_(bucket_name).upload(
            object_name, 
            file.read(),
            file_options={"content-type": file.content_type or "application/octet-stream"}
        )
        
        if hasattr(result, 'error') and result.error:
            logging.error(f"Supabase upload error: {result.error}")
            return None
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(object_name)
        return public_url
        
    except Exception as e:
        logging.error(f"Error uploading to Supabase: {e}")
        return None

@upload_bp.route('/upload', methods=['POST'])
def upload_meeting():
    """Upload meeting audio/video file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get user ID from request (in real app, this would come from JWT token)
        user_id = request.form.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Determine storage method based on environment
        is_production = os.getenv('FLASK_ENV') == 'production'
        use_s3 = os.getenv('USE_S3_STORAGE', 'false').lower() == 'true'
        
        if is_production and use_s3:
            # Upload to AWS S3 (production)
            bucket_name = os.getenv('AWS_S3_BUCKET')
            file_url = upload_to_s3(file, bucket_name, unique_filename)
            storage_type = 's3'
        else:
            # Upload to Supabase (development and default)
            bucket_name = os.getenv('SUPABASE_BUCKET', 'meeting-files')
            file_url = upload_to_supabase(file, bucket_name, unique_filename)
            storage_type = 'supabase'
        
        if not file_url:
            return jsonify({'error': 'Failed to upload file'}), 500
        
        # Get file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        # Create meeting record
        meeting = Meeting(
            title=request.form.get('title', filename),
            file_path=file_url,
            file_name=filename,
            file_size=file_size,
            user_id=user_id,
            status='uploaded'
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        return jsonify({
            'meeting_id': meeting.id,
            'title': meeting.title,
            'file_url': file_url,
            'file_size': file_size,
            'storage_type': storage_type,
            'status': 'uploaded',
            'message': 'File uploaded successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Upload error: {str(e)}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@upload_bp.route('/upload/status/<meeting_id>', methods=['GET'])
def get_upload_status(meeting_id):
    """Get upload status for a meeting"""
    try:
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        return jsonify({
            'meeting_id': meeting.id,
            'status': meeting.status,
            'file_name': meeting.file_name,
            'file_size': meeting.file_size,
            'created_at': meeting.created_at.isoformat() if meeting.created_at else None
        })
        
    except Exception as e:
        logging.error(f"Status check error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
