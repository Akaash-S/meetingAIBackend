from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import logging
import base64
import json
import asyncio
import websockets
import threading
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import uuid

load_dotenv()

audio_bp = Blueprint('audio', __name__)

# WebSocket connections storage
websocket_connections = {}

def clean_base64_data(data):
    """Clean base64 data by removing BOM and invalid characters"""
    if not data:
        return data
    
    # Remove BOM (Byte Order Mark) if present
    if data.startswith('\ufeff'):
        data = data[1:]
    
    # Remove any non-base64 characters
    import re
    data = re.sub(r'[^A-Za-z0-9+/=]', '', data)
    
    # Ensure proper padding
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    
    return data

def get_db_connection():
    """Get database connection"""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

class AudioProcessor:
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.rapidapi_host = 'speech-to-text-ai.p.rapidapi.com'
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.current_transcript = ""
        self.meeting_tasks = []
        self.meeting_summary = ""
        
    async def process_audio_chunk(self, audio_data, user_id, meeting_id=None):
        """Process audio chunk for transcription"""
        try:
            # Validate and clean audio data
            if not audio_data or not isinstance(audio_data, str):
                logging.warning("Invalid audio data received")
                return None
            
            # Decode base64 audio data with proper error handling
            if audio_data.startswith('data:audio'):
                audio_data = audio_data.split(',')[1]
            
            # Clean the base64 data to remove BOM and invalid characters
            audio_data = clean_base64_data(audio_data.strip())
            
            # Validate base64 data
            if not audio_data or len(audio_data) < 4:
                logging.warning("Empty or too short audio data")
                return None
            
            try:
                audio_bytes = base64.b64decode(audio_data, validate=True)
            except Exception as decode_error:
                logging.error(f"Base64 decode error: {decode_error}")
                return None
            
            # Validate audio data size
            if len(audio_bytes) < 100:  # Minimum audio chunk size
                logging.warning("Audio chunk too small, skipping")
                return None
            
            # Send to RapidAPI for transcription
            transcript = await self.transcribe_audio(audio_bytes)
            
            if transcript:
                self.current_transcript += transcript + " "
                
                # Note: Task extraction moved to post-transcription phase using Gemini API
                # This ensures Gemini is only used for timeline generation and task extraction
                # not during the transcription process itself
                
                return transcript
                
        except Exception as e:
            logging.error(f"Error processing audio chunk: {e}")
            return None
    
    async def transcribe_audio(self, audio_bytes):
        """Transcribe audio using RapidAPI"""
        try:
            if not self.rapidapi_key:
                logging.warning("RapidAPI key not configured")
                return "Transcription not available - API key missing"
            
            # Prepare headers for RapidAPI
            headers = {
                'x-rapidapi-key': self.rapidapi_key,
                'x-rapidapi-host': self.rapidapi_host
            }
            
            # Prepare files for upload
            files = {
                'file': ('audio.webm', audio_bytes, 'audio/webm')
            }
            
            # Make request to RapidAPI
            response = requests.post(
                f'https://{self.rapidapi_host}/transcribe',
                headers=headers,
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    transcript = result.get('transcript', '')
                    if transcript and isinstance(transcript, str):
                        return transcript.strip()
                    else:
                        logging.warning("Empty or invalid transcript received")
                        return None
                except json.JSONDecodeError as json_error:
                    logging.error(f"JSON decode error in transcription response: {json_error}")
                    return None
            else:
                logging.error(f"Transcription API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error in transcription: {e}")
            return None
    
    async def extract_insights(self, user_id, meeting_id):
        """Extract tasks and insights using Gemini API - POST-TRANSCRIPTION ONLY"""
        try:
            if not self.gemini_api_key:
                logging.error("Gemini API key not configured - task extraction requires Gemini")
                return
            
            # Prepare prompt for Gemini
            prompt = f"""
            Analyze this meeting transcript and extract:
            1. Action items with owners and deadlines
            2. Decisions made
            3. Key discussion points
            4. Next steps
            
            Transcript: {self.current_transcript}
            
            Return as JSON with this structure:
            {{
                "action_items": [
                    {{"task": "string", "owner": "string", "deadline": "string", "priority": "high/medium/low"}}
                ],
                "decisions": ["string"],
                "key_points": ["string"],
                "next_steps": ["string"]
            }}
            """
            
            # Call Gemini API
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.gemini_api_key}'
            }
            
            data = {
                'contents': [{
                    'parts': [{'text': prompt}]
                }]
            }
            
            response = requests.post(
                'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                insights = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
                
                # Parse and store insights
                await self.store_insights(user_id, meeting_id, insights)
                
        except Exception as e:
            logging.error(f"Error extracting insights: {e}")
    
    async def store_insights(self, user_id, meeting_id, insights_json):
        """Store extracted insights in database"""
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            try:
                insights = json.loads(insights_json)
                
                with conn.cursor() as cursor:
                    # Store action items as tasks
                    for item in insights.get('action_items', []):
                        task_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO tasks (id, name, description, owner, category, priority, deadline, meeting_id, user_id, status, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            task_id,
                            item.get('task', ''),
                            f"Extracted from meeting: {item.get('task', '')}",
                            item.get('owner', ''),
                            'action-item',
                            item.get('priority', 'medium'),
                            item.get('deadline'),
                            meeting_id or str(uuid.uuid4()),
                            user_id,
                            'pending',
                            datetime.now(),
                            datetime.now()
                        ))
                    
                    conn.commit()
                    logging.info(f"Stored {len(insights.get('action_items', []))} tasks for user {user_id}")
                    
            except Exception as e:
                logging.error(f"Database error storing insights: {e}")
            finally:
                conn.close()
                
        except Exception as e:
            logging.error(f"Error storing insights: {e}")

# Global audio processor instance
audio_processor = AudioProcessor()

@audio_bp.route('/audio/websocket', methods=['GET'])
def websocket_endpoint():
    """WebSocket endpoint for audio streaming"""
    return jsonify({
        'message': 'WebSocket endpoint available at ws://localhost:5000/audio',
        'status': 'ready'
    })

async def handle_websocket_connection(websocket, path):
    """Handle WebSocket connections for audio streaming"""
    client_id = None
    user_id = None
    meeting_id = None
    
    try:
        logging.info(f"New WebSocket connection: {websocket.remote_address}")
        
        async for message in websocket:
            try:
                # Validate message format
                if not message or not isinstance(message, str):
                    logging.warning("Invalid message format received")
                    continue
                
                # Parse JSON with error handling
                try:
                    data = json.loads(message)
                except json.JSONDecodeError as json_error:
                    logging.error(f"JSON decode error: {json_error}")
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }))
                    continue
                
                if data.get('type') == 'audio_chunk':
                    user_id = data.get('userId', 'anonymous')
                    meeting_id = data.get('meetingId')
                    
                    # Validate audio data before processing
                    audio_data = data.get('data', '')
                    if not audio_data:
                        logging.warning("Empty audio data received")
                        continue
                    
                    # Process audio chunk
                    transcript = await audio_processor.process_audio_chunk(
                        audio_data,
                        user_id,
                        meeting_id
                    )
                    
                    if transcript:
                        # Send transcript back to client
                        await websocket.send(json.dumps({
                            'type': 'transcript',
                            'text': transcript,
                            'timestamp': datetime.now().isoformat()
                        }))
                
                elif data.get('type') == 'recording_started':
                    user_id = data.get('userId', 'anonymous')
                    meeting_id = str(uuid.uuid4())
                    
                    # Create meeting record
                    conn = get_db_connection()
                    if conn:
                        try:
                            with conn.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO meetings (id, title, user_id, status, created_at, updated_at)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                """, (
                                    meeting_id,
                                    f"Live Meeting - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                    user_id,
                                    'recording',
                                    datetime.now(),
                                    datetime.now()
                                ))
                                conn.commit()
                        except Exception as e:
                            logging.error(f"Error creating meeting record: {e}")
                        finally:
                            conn.close()
                    
                    await websocket.send(json.dumps({
                        'type': 'meeting_created',
                        'meetingId': meeting_id,
                        'message': 'Meeting recording started'
                    }))
                
                elif data.get('type') == 'recording_stopped':
                    if meeting_id:
                        # Update meeting status
                        conn = get_db_connection()
                        if conn:
                            try:
                                with conn.cursor() as cursor:
                                    cursor.execute("""
                                        UPDATE meetings 
                                        SET status = 'completed', updated_at = %s
                                        WHERE id = %s
                                    """, (datetime.now(), meeting_id))
                                    conn.commit()
                            except Exception as e:
                                logging.error(f"Error updating meeting status: {e}")
                            finally:
                                conn.close()
                    
                    await websocket.send(json.dumps({
                        'type': 'recording_stopped',
                        'message': 'Meeting recording completed'
                    }))
                
                elif data.get('type') == 'process_audio':
                    # Process complete audio workflow
                    meeting_id = data.get('meetingId')
                    user_id = data.get('userId')
                    audio_data = data.get('audioData')
                    meeting_title = data.get('meetingTitle', 'Meeting Recording')
                    
                    if not all([meeting_id, user_id, audio_data]):
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': 'Missing required data for audio processing'
                        }))
                        continue
                    
                    try:
                        # Decode base64 audio data
                        if audio_data.startswith('data:audio'):
                            audio_data = audio_data.split(',')[1]
                        
                        audio_bytes = base64.b64decode(audio_data)
                        
                        # Import and use the audio processor service
                        from services.audio_processor import AudioProcessorService
                        processor = AudioProcessorService()
                        
                        # Send processing started message
                        await websocket.send(json.dumps({
                            'type': 'processing_started',
                            'message': 'Starting audio processing...'
                        }))
                        
                        # Process complete workflow
                        result = await processor.process_complete_workflow(
                            audio_bytes, meeting_id, user_id, meeting_title
                        )
                        
                        if result.get('success'):
                            await websocket.send(json.dumps({
                                'type': 'processing_completed',
                                'message': 'Audio processing completed successfully',
                                'data': {
                                    'meeting_id': result['meeting_id'],
                                    'tasks_count': result['tasks_count'],
                                    'file_url': result['file_url']
                                }
                            }))
                        else:
                            await websocket.send(json.dumps({
                                'type': 'processing_error',
                                'message': result.get('error', 'Unknown processing error')
                            }))
                            
                    except Exception as e:
                        logging.error(f"Error processing audio: {e}")
                        await websocket.send(json.dumps({
                            'type': 'processing_error',
                            'message': f'Processing failed: {str(e)}'
                        }))
                
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': 'Invalid JSON format'
                }))
            except Exception as e:
                logging.error(f"Error processing WebSocket message: {e}")
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': str(e)
                }))
                
    except websockets.exceptions.ConnectionClosed:
        logging.info(f"WebSocket connection closed: {websocket.remote_address}")
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        if client_id in websocket_connections:
            del websocket_connections[client_id]

def start_websocket_server():
    """Start WebSocket server for audio streaming"""
    try:
        import asyncio
        import websockets
        
        async def server():
            # Try different ports if 5001 is busy
            ports_to_try = [5001, 5002, 5003, 5004, 5005]
            
            for port in ports_to_try:
                try:
                    async with websockets.serve(handle_websocket_connection, "localhost", port):
                        logging.info(f"WebSocket server started on ws://localhost:{port}/audio")
                        await asyncio.Future()  # Run forever
                        break
                except OSError as e:
                    if "Address already in use" in str(e) or "only one usage of each socket address" in str(e):
                        logging.warning(f"Port {port} is busy, trying next port...")
                        continue
                    else:
                        raise e
            else:
                logging.error("Could not find an available port for WebSocket server")
        
        # Run WebSocket server in a separate thread
        def run_server():
            try:
                asyncio.run(server())
            except Exception as e:
                logging.error(f"WebSocket server error: {e}")
        
        websocket_thread = threading.Thread(target=run_server, daemon=True)
        websocket_thread.start()
        logging.info("WebSocket server thread started")
        
    except Exception as e:
        logging.error(f"Error starting WebSocket server: {e}")

# Only start WebSocket server if not in test mode
if not os.getenv('TESTING', '').lower() in ['true', '1', 'yes']:
    start_websocket_server()
