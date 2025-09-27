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
        self.rapidapi_host = os.getenv('RAPIDAPI_HOST', 'speech-to-text-api1.p.rapidapi.com')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.current_transcript = ""
        self.meeting_tasks = []
        self.meeting_summary = ""
        
    async def process_audio_chunk(self, audio_data, user_id, meeting_id=None):
        """Process audio chunk for transcription"""
        try:
            # Decode base64 audio data
            if audio_data.startswith('data:audio'):
                audio_data = audio_data.split(',')[1]
            
            audio_bytes = base64.b64decode(audio_data)
            
            # Send to RapidAPI for transcription
            transcript = await self.transcribe_audio(audio_bytes)
            
            if transcript:
                self.current_transcript += transcript + " "
                
                # Extract tasks and insights every 60 seconds
                if len(self.current_transcript.split()) > 100:  # Roughly 60 seconds
                    await self.extract_insights(user_id, meeting_id)
                    self.current_transcript = ""  # Reset for next chunk
                
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
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': self.rapidapi_host
            }
            
            # Prepare files for upload
            files = {
                'audio': ('audio.webm', audio_bytes, 'audio/webm')
            }
            
            # Make request to RapidAPI
            response = requests.post(
                'https://speech-to-text-api1.p.rapidapi.com/transcribe',
                headers=headers,
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('transcript', '')
            else:
                logging.error(f"Transcription API error: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Error in transcription: {e}")
            return None
    
    async def extract_insights(self, user_id, meeting_id):
        """Extract tasks and insights using Gemini API"""
        try:
            if not self.gemini_api_key:
                logging.warning("Gemini API key not configured")
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
                data = json.loads(message)
                
                if data.get('type') == 'audio_chunk':
                    user_id = data.get('userId', 'anonymous')
                    meeting_id = data.get('meetingId')
                    
                    # Process audio chunk
                    transcript = await audio_processor.process_audio_chunk(
                        data.get('data', ''),
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
            async with websockets.serve(handle_websocket_connection, "localhost", 5000):
                logging.info("WebSocket server started on ws://localhost:5000/audio")
                await asyncio.Future()  # Run forever
        
        # Run WebSocket server in a separate thread
        def run_server():
            asyncio.run(server())
        
        websocket_thread = threading.Thread(target=run_server, daemon=True)
        websocket_thread.start()
        logging.info("WebSocket server thread started")
        
    except Exception as e:
        logging.error(f"Error starting WebSocket server: {e}")

# Start WebSocket server when module is imported
start_websocket_server()
