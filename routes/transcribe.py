#!/usr/bin/env python3
"""
Perfect Transcription Service
Uses ONLY RapidAPI for high-quality speech-to-text transcription
Handles all edge cases and provides robust error handling
"""

from flask import Blueprint, request, jsonify
import os
import logging
import requests
import json
import threading
import asyncio
import base64
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

transcribe_bp = Blueprint('transcribe', __name__)

def get_db_connection():
    """Get database connection"""
    try:
        from app import get_db_connection as app_get_db_connection
        return app_get_db_connection()
    except ImportError:
        try:
            DATABASE_URL = os.getenv('DATABASE_URL')
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            logging.error(f"Database connection error: {e}")
            return None

def transcribe_with_rapidapi_perfect(audio_data: bytes, filename: str = 'audio.wav') -> Dict[str, Any]:
    """
    Perfect transcription using RapidAPI with comprehensive error handling
    """
    try:
        # Validate inputs
        if not audio_data:
            return {
                'success': False,
                'error': 'No audio data provided',
                'details': 'Audio data is empty or None'
            }
        
        if len(audio_data) < 1000:  # Less than 1KB is likely invalid
            return {
                'success': False,
                'error': 'Audio data too small',
                'details': f'Audio data is only {len(audio_data)} bytes, minimum 1000 bytes required'
            }
        
        # Get RapidAPI configuration
        rapidapi_key = os.getenv('RAPIDAPI_KEY')
        rapidapi_host = 'speech-to-text-ai.p.rapidapi.com'
        
        if not rapidapi_key:
            return {
                'success': False,
                'error': 'RapidAPI key not configured',
                'details': 'RAPIDAPI_KEY environment variable is not set'
            }
        
        # Prepare headers
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host
        }
        
        # Determine file type from filename
        file_extension = filename.lower().split('.')[-1] if '.' in filename else 'wav'
        content_type_map = {
            'wav': 'audio/wav',
            'mp3': 'audio/mpeg',
            'mp4': 'audio/mp4',
            'm4a': 'audio/mp4',
            'webm': 'audio/webm',
            'ogg': 'audio/ogg',
            'flac': 'audio/flac'
        }
        content_type = content_type_map.get(file_extension, 'audio/wav')
        
        # Prepare file upload
        files = {
            'file': (filename, audio_data, content_type)
        }
        
        # Make request to RapidAPI with retry logic
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Attempting RapidAPI transcription (attempt {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    f'https://{rapidapi_host}/transcribe',
                    headers=headers,
                    files=files,
                    timeout=300  # 5 minutes timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract transcript from various possible response formats
                    transcript = None
                    confidence = 0.0
                    duration = 0
                    language = 'en'
                    
                    # Try different possible keys for transcript
                    for key in ['transcript', 'text', 'transcription', 'result']:
                        if key in result and result[key]:
                            transcript = result[key].strip()
                            break
                    
                    if not transcript:
                        return {
                            'success': False,
                            'error': 'No transcript in response',
                            'details': f'RapidAPI response did not contain transcript: {result}'
                        }
                    
                    # Extract additional metadata
                    confidence = result.get('confidence', result.get('score', 0.0))
                    duration = result.get('duration', result.get('audio_duration', 0))
                    language = result.get('language', result.get('lang', 'en'))
                    
                    logging.info(f"RapidAPI transcription successful: {len(transcript)} characters, confidence: {confidence}")
                    
                    return {
                        'success': True,
                        'transcript': transcript,
                        'confidence': float(confidence),
                        'duration': float(duration),
                        'language': language,
                        'attempt': attempt + 1
                    }
                
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logging.warning(f"Rate limited, waiting {wait_time} seconds before retry")
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        return {
                            'success': False,
                            'error': 'Rate limit exceeded',
                            'details': 'Too many requests to RapidAPI, please try again later'
                        }
                
                elif response.status_code == 413:  # File too large
                    return {
                        'success': False,
                        'error': 'File too large',
                        'details': f'Audio file is too large for RapidAPI processing: {len(audio_data)} bytes'
                    }
                
                else:
                    last_error = f"HTTP {response.status_code}: {response.text}"
                    logging.error(f"RapidAPI error: {last_error}")
                    
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return {
                            'success': False,
                            'error': f'RapidAPI error: {response.status_code}',
                            'details': response.text
                        }
            
            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                logging.error(f"RapidAPI timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'Request timeout',
                        'details': 'Transcription took too long, please try with a shorter audio file'
                    }
            
            except requests.exceptions.ConnectionError:
                last_error = "Connection error"
                logging.error(f"RapidAPI connection error on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'Connection error',
                        'details': 'Failed to connect to RapidAPI service'
                    }
            
            except Exception as e:
                last_error = str(e)
                logging.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'Unexpected error',
                        'details': str(e)
                    }
        
        return {
            'success': False,
            'error': 'All retry attempts failed',
            'details': f'Last error: {last_error}'
        }
    
    except Exception as e:
        logging.error(f"Critical error in transcription: {e}")
        return {
            'success': False,
            'error': 'Critical transcription error',
            'details': str(e)
        }

def download_audio_file(file_url: str) -> Optional[bytes]:
    """Download audio file from URL with error handling"""
    try:
        if not file_url:
            logging.error("No file URL provided")
            return None
        
        # Handle different URL types
        if file_url.startswith('file://'):
            # Local file
            local_path = file_url[7:]  # Remove 'file://' prefix
            if os.path.exists(local_path):
                with open(local_path, 'rb') as f:
                    return f.read()
            else:
                logging.error(f"Local file not found: {local_path}")
                return None
        
        elif file_url.startswith(('http://', 'https://')):
            # Remote URL
            response = requests.get(file_url, timeout=60, stream=True)
            if response.status_code == 200:
                return response.content
            else:
                logging.error(f"Failed to download file: HTTP {response.status_code}")
                return None
        
        else:
            logging.error(f"Unsupported file URL format: {file_url}")
            return None
    
    except Exception as e:
        logging.error(f"Error downloading audio file: {e}")
        return None

@transcribe_bp.route('/transcribe/<meeting_id>', methods=['POST'])
def transcribe_meeting(meeting_id):
    """Perfect transcription endpoint with comprehensive error handling"""
    try:
        # Validate meeting ID
        if not meeting_id or len(meeting_id) < 10:
            return jsonify({
                'success': False,
                'error': 'Invalid meeting ID',
                'details': 'Meeting ID must be provided and valid'
            }), 400
        
        # Get database connection
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed',
                'details': 'Unable to connect to database'
            }), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get meeting details
                cursor.execute("SELECT * FROM meetings WHERE id = %s", (meeting_id,))
                meeting = cursor.fetchone()
                
                if not meeting:
                    return jsonify({
                        'success': False,
                        'error': 'Meeting not found',
                        'details': f'No meeting found with ID: {meeting_id}'
                    }), 404
                
                # Check meeting status
                current_status = meeting['status']
                if current_status not in ['uploaded', 'transcription_error', 'processing_error']:
                    return jsonify({
                        'success': False,
                        'error': f'Cannot transcribe meeting with status: {current_status}',
                        'details': f'Meeting status must be "uploaded", "transcription_error", or "processing_error" to transcribe'
                    }), 400
                
                # Check if file path exists
                file_path = meeting['file_path']
                if not file_path:
                    return jsonify({
                        'success': False,
                        'error': 'No file path found',
                        'details': 'Meeting has no associated audio file'
                    }), 400
                
                # Update status to transcribing
                cursor.execute("""
                    UPDATE meetings 
                    SET status = 'transcribing', updated_at = NOW()
                    WHERE id = %s
                """, (meeting_id,))
                conn.commit()
                
                logging.info(f"Starting perfect transcription for meeting {meeting_id}")
                
                # Start background transcription
                def transcribe_background():
                    try:
                        # Download audio file
                        audio_data = download_audio_file(file_path)
                        if not audio_data:
                            raise Exception("Failed to download audio file")
                        
                        # Get filename from meeting record or generate one
                        filename = meeting.get('file_name', f'meeting_{meeting_id}.wav')
                        
                        # Perform transcription
                        result = transcribe_with_rapidapi_perfect(audio_data, filename)
                        
                        if result['success']:
                            transcript = result['transcript']
                            confidence = result.get('confidence', 0.0)
                            duration = result.get('duration', 0)
                            language = result.get('language', 'en')
                            
                            # Update meeting with transcript
                            with conn.cursor() as update_cursor:
                                update_cursor.execute("""
                                    UPDATE meetings 
                                    SET transcript = %s, 
                                        status = 'transcribed',
                                        duration = %s,
                                        language = %s,
                                        confidence = %s,
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (transcript, duration, language, confidence, meeting_id))
                                conn.commit()
                            
                            logging.info(f"Perfect transcription completed for meeting {meeting_id}: {len(transcript)} characters")
                            
                        else:
                            # Handle transcription failure
                            error_msg = result.get('error', 'Unknown error')
                            error_details = result.get('details', 'No details available')
                            
                            with conn.cursor() as update_cursor:
                                update_cursor.execute("""
                                    UPDATE meetings 
                                    SET status = 'transcription_error',
                                        error_message = %s,
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (f"{error_msg}: {error_details}", meeting_id))
                                conn.commit()
                            
                            logging.error(f"Transcription failed for meeting {meeting_id}: {error_msg}")
                    
                    except Exception as e:
                        logging.error(f"Background transcription error for meeting {meeting_id}: {e}")
                        # Update status to error
                        try:
                            with conn.cursor() as update_cursor:
                                update_cursor.execute("""
                                    UPDATE meetings 
                                    SET status = 'transcription_error',
                                        error_message = %s,
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (str(e), meeting_id))
                                conn.commit()
                        except:
                            pass
                
                # Start background thread
                thread = threading.Thread(target=transcribe_background, daemon=True)
                thread.start()
                
                return jsonify({
                    'success': True,
                    'meeting_id': meeting_id,
                    'status': 'transcribing',
                    'message': 'Perfect transcription started successfully',
                    'file_path': file_path,
                    'file_size': len(download_audio_file(file_path)) if download_audio_file(file_path) else 0
                })
        
        except Exception as e:
            logging.error(f"Database error: {e}")
            return jsonify({
                'success': False,
                'error': 'Database error',
                'details': str(e)
            }), 500
        finally:
            conn.close()
    
    except Exception as e:
        logging.error(f"Transcription endpoint error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@transcribe_bp.route('/transcribe/<meeting_id>/status', methods=['GET'])
def get_transcription_status(meeting_id):
    """Get detailed transcription status"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, status, transcript, file_path, file_name, file_size,
                           duration, language, confidence, error_message,
                           created_at, updated_at
                    FROM meetings 
                    WHERE id = %s
                """, (meeting_id,))
                meeting = cursor.fetchone()
                
                if not meeting:
                    return jsonify({'error': 'Meeting not found'}), 404
                
                return jsonify({
                    'meeting_id': meeting['id'],
                    'status': meeting['status'],
                    'has_transcript': bool(meeting['transcript']),
                    'transcript_length': len(meeting['transcript']) if meeting['transcript'] else 0,
                    'file_path': meeting['file_path'],
                    'file_name': meeting['file_name'],
                    'file_size': meeting['file_size'],
                    'duration': meeting['duration'],
                    'language': meeting['language'],
                    'confidence': meeting['confidence'],
                    'error_message': meeting['error_message'],
                    'created_at': meeting['created_at'].isoformat() if meeting['created_at'] else None,
                    'updated_at': meeting['updated_at'].isoformat() if meeting['updated_at'] else None,
                    'can_retry': meeting['status'] in ['transcription_error', 'processing_error']
                })
        
        finally:
            conn.close()
    
    except Exception as e:
        logging.error(f"Status check error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@transcribe_bp.route('/transcribe/test', methods=['POST'])
def test_transcription():
    """Test transcription with sample audio data"""
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'details': 'Please provide an audio file for testing'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'details': 'Please select an audio file'
            }), 400
        
        # Read file data
        audio_data = file.read()
        filename = file.filename
        
        # Test transcription
        result = transcribe_with_rapidapi_perfect(audio_data, filename)
        
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"Test transcription error: {e}")
        return jsonify({
            'success': False,
            'error': 'Test failed',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    # Test the transcription function directly
    print("Transcription Service Ready!")
    print("Endpoints:")
    print("  POST /api/transcribe/<meeting_id> - Start transcription")
    print("  GET  /api/transcribe/<meeting_id>/status - Check status")
    print("  POST /api/transcribe/test - Test with file upload")
