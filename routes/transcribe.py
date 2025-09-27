from flask import Blueprint, request, jsonify, current_app
import requests
import os
import logging
from datetime import datetime

from models import db, Meeting

transcribe_bp = Blueprint('transcribe', __name__)

def transcribe_with_rapidapi(file_url, language='en'):
    """Transcribe audio using RapidAPI"""
    try:
        # RapidAPI configuration
        rapidapi_key = os.getenv('RAPIDAPI_KEY')
        rapidapi_host = os.getenv('RAPIDAPI_HOST', 'speech-to-text-api1.p.rapidapi.com')
        
        if not rapidapi_key:
            raise ValueError("RapidAPI key not configured")
        
        # Prepare request headers
        headers = {
            'X-RapidAPI-Key': rapidapi_key,
            'X-RapidAPI-Host': rapidapi_host,
            'Content-Type': 'application/json'
        }
        
        # Prepare request payload
        payload = {
            'url': file_url,
            'language': language,
            'format': 'json'
        }
        
        # Make API request
        response = requests.post(
            f'https://{rapidapi_host}/transcribe',
            headers=headers,
            json=payload,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'transcript': result.get('transcript', ''),
                'confidence': result.get('confidence', 0.0),
                'duration': result.get('duration', 0),
                'language': result.get('language', language)
            }
        else:
            logging.error(f"RapidAPI error: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f"API error: {response.status_code}",
                'details': response.text
            }
            
    except requests.exceptions.Timeout:
        logging.error("RapidAPI request timeout")
        return {
            'success': False,
            'error': 'Request timeout',
            'details': 'Transcription took too long'
        }
    except Exception as e:
        logging.error(f"Transcription error: {str(e)}")
        return {
            'success': False,
            'error': 'Transcription failed',
            'details': str(e)
        }

def transcribe_with_assemblyai(file_url):
    """Alternative transcription using AssemblyAI"""
    try:
        api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not api_key:
            raise ValueError("AssemblyAI API key not configured")
        
        # Submit transcription job
        headers = {'authorization': api_key}
        submit_response = requests.post(
            'https://api.assemblyai.com/v2/transcript',
            headers=headers,
            json={'audio_url': file_url}
        )
        
        if submit_response.status_code != 200:
            raise Exception(f"AssemblyAI submit error: {submit_response.text}")
        
        transcript_id = submit_response.json()['id']
        
        # Poll for completion
        max_attempts = 60  # 5 minutes max
        for attempt in range(max_attempts):
            status_response = requests.get(
                f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
                headers=headers
            )
            
            if status_response.status_code != 200:
                raise Exception(f"AssemblyAI status error: {status_response.text}")
            
            status_data = status_response.json()
            status = status_data['status']
            
            if status == 'completed':
                return {
                    'success': True,
                    'transcript': status_data['text'],
                    'confidence': status_data.get('confidence', 0.0),
                    'duration': status_data.get('audio_duration', 0),
                    'language': status_data.get('language_code', 'en')
                }
            elif status == 'error':
                raise Exception(f"AssemblyAI processing error: {status_data.get('error', 'Unknown error')}")
            
            # Wait before next attempt
            import time
            time.sleep(5)
        
        raise Exception("Transcription timeout")
        
    except Exception as e:
        logging.error(f"AssemblyAI error: {str(e)}")
        return {
            'success': False,
            'error': 'AssemblyAI transcription failed',
            'details': str(e)
        }

@transcribe_bp.route('/transcribe/<meeting_id>', methods=['POST'])
def transcribe_meeting(meeting_id):
    """Transcribe meeting audio/video"""
    try:
        # Get meeting record
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        if meeting.status != 'uploaded':
            return jsonify({'error': f'Meeting status is {meeting.status}, expected uploaded'}), 400
        
        if not meeting.file_path:
            return jsonify({'error': 'No file path found for meeting'}), 400
        
        # Update status to processing
        meeting.status = 'processing'
        db.session.commit()
        
        # Choose transcription service
        transcription_service = os.getenv('TRANSCRIPTION_SERVICE', 'rapidapi')
        
        if transcription_service == 'assemblyai':
            result = transcribe_with_assemblyai(meeting.file_path)
        else:
            result = transcribe_with_rapidapi(meeting.file_path)
        
        if result['success']:
            # Update meeting with transcript
            meeting.transcript = result['transcript']
            meeting.duration = result.get('duration', 0)
            meeting.status = 'transcribed'
            meeting.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'meeting_id': meeting.id,
                'status': 'transcribed',
                'transcript': result['transcript'],
                'confidence': result.get('confidence', 0.0),
                'duration': result.get('duration', 0),
                'language': result.get('language', 'en'),
                'message': 'Transcription completed successfully'
            }), 200
        else:
            # Update status to error
            meeting.status = 'error'
            db.session.commit()
            
            return jsonify({
                'error': 'Transcription failed',
                'details': result.get('details', result.get('error', 'Unknown error')),
                'meeting_id': meeting.id
            }), 500
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"Transcription error: {str(e)}")
        
        # Update meeting status to error
        if 'meeting' in locals():
            meeting.status = 'error'
            db.session.commit()
        
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@transcribe_bp.route('/transcribe/<meeting_id>/status', methods=['GET'])
def get_transcription_status(meeting_id):
    """Get transcription status for a meeting"""
    try:
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        return jsonify({
            'meeting_id': meeting.id,
            'status': meeting.status,
            'has_transcript': bool(meeting.transcript),
            'transcript_length': len(meeting.transcript) if meeting.transcript else 0,
            'duration': meeting.duration,
            'updated_at': meeting.updated_at.isoformat() if meeting.updated_at else None
        })
        
    except Exception as e:
        logging.error(f"Status check error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
