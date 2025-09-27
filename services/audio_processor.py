"""
Audio Processing Service
Handles complete workflow: upload -> transcription -> timeline -> tasks -> calendar
"""

import os
import logging
import asyncio
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

load_dotenv()

class AudioProcessorService:
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.rapidapi_host = os.getenv('RAPIDAPI_HOST', 'speech-to-text-api1.p.rapidapi.com')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        
        # Initialize Gemini AI
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize Supabase
        if self.supabase_url and self.supabase_key:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        else:
            self.supabase = None
    
    def get_db_connection(self):
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
    
    def return_db_connection(self, conn):
        """Return database connection to pool"""
        try:
            from app import return_db_connection as app_return_db_connection
            app_return_db_connection(conn)
        except ImportError:
            if conn:
                conn.close()
    
    async def upload_audio_to_supabase(self, audio_data: bytes, meeting_id: str, user_id: str) -> Optional[str]:
        """Upload audio data to Supabase Storage"""
        try:
            if not self.supabase:
                logging.error("Supabase not configured")
                return None
            
            # Generate filename
            filename = f"meetings/{user_id}/{meeting_id}.webm"
            
            # Upload to Supabase Storage
            result = self.supabase.storage.from_('meeting-recordings').upload(
                filename,
                audio_data,
                file_options={"content-type": "audio/webm"}
            )
            
            if hasattr(result, 'error') and result.error:
                logging.error(f"Supabase upload error: {result.error}")
                return None
            
            # Get public URL
            public_url = self.supabase.storage.from_('meeting-recordings').get_public_url(filename)
            return public_url
            
        except Exception as e:
            logging.error(f"Error uploading to Supabase: {e}")
            return None
    
    async def transcribe_audio(self, audio_url: str) -> Optional[str]:
        """Transcribe audio using Gemini API"""
        try:
            if not self.gemini_api_key or not self.gemini_model:
                logging.warning("Gemini API not configured")
                return None
            
            # Download audio file
            response = requests.get(audio_url, timeout=30)
            if response.status_code != 200:
                logging.error(f"Failed to download audio: {response.status_code}")
                return None
            
            audio_data = response.content
            
            # Convert audio to base64 for Gemini
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Create prompt for Gemini
            prompt = f"""
            Please transcribe this audio file accurately. The audio is from a meeting recording.
            
            Audio data (base64): {audio_base64}
            
            Please provide a clean, accurate transcript of the meeting content. Include:
            - All spoken words
            - Speaker changes (if detectable)
            - Important pauses or emphasis
            - Any background context that might be relevant
            
            Return only the transcript text, no additional formatting or commentary.
            """
            
            # Use Gemini to transcribe
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                transcript = response.text.strip()
                logging.info(f"Transcription completed: {len(transcript)} characters")
                return transcript
            else:
                logging.warning("Empty transcript received from Gemini")
                return None
                
        except Exception as e:
            logging.error(f"Error in Gemini transcription: {e}")
            return None
    
    async def generate_timeline(self, transcript: str, meeting_duration: int) -> Optional[Dict]:
        """Generate minute-to-minute timeline using Gemini AI"""
        try:
            if not self.gemini_api_key or not self.gemini_model:
                logging.warning("Gemini API not configured")
                return None
            
            # Calculate approximate minutes
            minutes = max(1, meeting_duration // 60)
            
            prompt = f"""
            Analyze this meeting transcript and create a comprehensive minute-to-minute timeline with key discussion points, decisions, and action items.
            
            Meeting Duration: {minutes} minutes
            Transcript: {transcript}
            
            Please provide a JSON response with the following structure:
            {{
                "timeline": [
                    {{
                        "minute": 1,
                        "summary": "Key discussion points in minute 1",
                        "key_points": ["Point 1", "Point 2"],
                        "decisions": ["Decision made"],
                        "action_items": ["Action item 1", "Action item 2"],
                        "speakers": ["Speaker 1", "Speaker 2"],
                        "topics": ["Topic 1", "Topic 2"]
                    }},
                    ...
                ],
                "overall_summary": "Brief overall meeting summary",
                "key_decisions": ["Major decision 1", "Major decision 2"],
                "action_items": ["Action item 1", "Action item 2", "Action item 3"],
                "participants": ["Participant 1", "Participant 2"],
                "meeting_type": "Type of meeting (standup, planning, review, etc.)",
                "next_steps": ["Next step 1", "Next step 2"],
                "blockers": ["Blocker 1", "Blocker 2"],
                "success_metrics": ["Metric 1", "Metric 2"]
            }}
            
            Make sure the timeline covers the entire meeting duration and includes specific, actionable items.
            Focus on:
            - Clear, actionable next steps
            - Important decisions made
            - Key discussion points
            - Any blockers or concerns raised
            - Success metrics or KPIs mentioned
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            # Parse JSON response
            try:
                timeline_data = json.loads(response.text)
                logging.info(f"Timeline generated with {len(timeline_data.get('timeline', []))} minute segments")
                return timeline_data
            except json.JSONDecodeError:
                logging.error("Failed to parse Gemini response as JSON")
                # Try to extract JSON from response
                try:
                    import re
                    json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                    if json_match:
                        timeline_data = json.loads(json_match.group())
                        return timeline_data
                except:
                    pass
                return None
                
        except Exception as e:
            logging.error(f"Error generating timeline: {e}")
            return None
    
    async def extract_tasks(self, transcript: str, timeline: Dict) -> List[Dict]:
        """Extract tasks from transcript and timeline"""
        try:
            if not self.gemini_api_key or not self.gemini_model:
                logging.warning("Gemini API not configured")
                return []
            
            prompt = f"""
            Extract specific, actionable tasks from this meeting transcript and timeline.
            
            Transcript: {transcript}
            Timeline: {json.dumps(timeline, indent=2)}
            
            For each task, provide:
            - Clear, actionable description
            - Priority level (high, medium, low)
            - Assigned person (if mentioned)
            - Due date (if mentioned)
            - Category (work, personal, follow-up, etc.)
            - Estimated effort (1-5 scale)
            - Dependencies (if any)
            
            Return as JSON array:
            [
                {{
                    "name": "Task description",
                    "description": "Detailed task description",
                    "priority": "high|medium|low",
                    "assignee": "Person name or 'Unassigned'",
                    "due_date": "YYYY-MM-DD or null",
                    "category": "work|personal|follow-up|other",
                    "status": "pending",
                    "effort": 1-5,
                    "dependencies": ["Task 1", "Task 2"],
                    "tags": ["tag1", "tag2"],
                    "context": "Additional context from meeting"
                }}
            ]
            
            Focus on concrete, actionable items that can be tracked and completed.
            Include:
            - All explicit action items mentioned
            - Follow-up tasks
            - Research tasks
            - Communication tasks
            - Review tasks
            - Any commitments made during the meeting
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            try:
                tasks = json.loads(response.text)
                if isinstance(tasks, list):
                    logging.info(f"Extracted {len(tasks)} tasks from meeting")
                    return tasks
                else:
                    logging.warning("Tasks response is not a list")
                    return []
            except json.JSONDecodeError:
                logging.error("Failed to parse tasks as JSON")
                # Try to extract JSON from response
                try:
                    import re
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    if json_match:
                        tasks = json.loads(json_match.group())
                        return tasks if isinstance(tasks, list) else []
                except:
                    pass
                return []
                
        except Exception as e:
            logging.error(f"Error extracting tasks: {e}")
            return []
    
    async def save_tasks_to_database(self, tasks: List[Dict], meeting_id: str, user_id: str) -> bool:
        """Save extracted tasks to database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                logging.error("Database connection failed")
                return False
            
            try:
                with conn.cursor() as cursor:
                    for task in tasks:
                        # Insert task with enhanced fields
                        cursor.execute("""
                            INSERT INTO tasks (
                                name, description, priority, status, category, 
                                owner, user_id, meeting_id, deadline, created_at, updated_at,
                                effort, dependencies, tags, context
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            task.get('name', ''),
                            task.get('description', ''),
                            task.get('priority', 'medium'),
                            task.get('status', 'pending'),
                            task.get('category', 'general'),
                            task.get('assignee', 'Unassigned'),
                            user_id,
                            meeting_id,
                            task.get('due_date'),
                            datetime.now(),
                            datetime.now(),
                            task.get('effort', 1),
                            json.dumps(task.get('dependencies', [])),
                            json.dumps(task.get('tags', [])),
                            task.get('context', '')
                        ))
                
                conn.commit()
                logging.info(f"Saved {len(tasks)} tasks to database with enhanced fields")
                return True
                
            except Exception as e:
                logging.error(f"Database error saving tasks: {e}")
                conn.rollback()
                return False
            finally:
                self.return_db_connection(conn)
                
        except Exception as e:
            logging.error(f"Error saving tasks: {e}")
            return False
    
    async def update_meeting_with_results(self, meeting_id: str, transcript: str, timeline: Dict, file_url: str) -> bool:
        """Update meeting record with processing results"""
        try:
            conn = self.get_db_connection()
            if not conn:
                logging.error("Database connection failed")
                return False
            
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE meetings 
                        SET 
                            transcript = %s,
                            timeline = %s,
                            file_path = %s,
                            status = 'processed',
                            updated_at = %s
                        WHERE id = %s
                    """, (
                        transcript,
                        json.dumps(timeline),
                        file_url,
                        datetime.now(),
                        meeting_id
                    ))
                
                conn.commit()
                logging.info(f"Updated meeting {meeting_id} with processing results")
                return True
                
            except Exception as e:
                logging.error(f"Database error updating meeting: {e}")
                conn.rollback()
                return False
            finally:
                self.return_db_connection(conn)
                
        except Exception as e:
            logging.error(f"Error updating meeting: {e}")
            return False
    
    async def schedule_tasks_in_calendar(self, tasks: List[Dict], user_id: str) -> Dict:
        """Schedule extracted tasks in Google Calendar"""
        try:
            from services.calendar_service import CalendarService
            
            calendar_service = CalendarService()
            
            # Check if user has calendar authorization
            # For now, we'll skip calendar integration if not configured
            if not calendar_service.client_secret_file:
                logging.info("Calendar integration not configured, skipping calendar scheduling")
                return {"skipped": True, "reason": "Calendar not configured"}
            
            # Schedule tasks
            results = calendar_service.schedule_tasks(tasks, user_id)
            return results
            
        except Exception as e:
            logging.error(f"Error scheduling tasks in calendar: {e}")
            return {"error": str(e)}

    async def process_complete_workflow(self, audio_data: bytes, meeting_id: str, user_id: str, meeting_title: str = "Meeting Recording") -> Dict:
        """Process complete audio workflow: upload -> transcribe -> timeline -> tasks"""
        try:
            logging.info(f"Starting complete workflow for meeting {meeting_id}")
            
            # Step 1: Upload audio to Supabase
            logging.info("Step 1: Uploading audio to Supabase...")
            file_url = await self.upload_audio_to_supabase(audio_data, meeting_id, user_id)
            if not file_url:
                return {"error": "Failed to upload audio to Supabase"}
            
            # Step 2: Transcribe audio
            logging.info("Step 2: Transcribing audio...")
            transcript = await self.transcribe_audio(file_url)
            if not transcript:
                return {"error": "Failed to transcribe audio"}
            
            # Step 3: Generate timeline
            logging.info("Step 3: Generating timeline...")
            timeline = await self.generate_timeline(transcript, len(audio_data) // 1000)  # Rough duration estimate
            if not timeline:
                return {"error": "Failed to generate timeline"}
            
            # Step 4: Extract tasks
            logging.info("Step 4: Extracting tasks...")
            tasks = await self.extract_tasks(transcript, timeline)
            
            # Step 5: Save tasks to database
            logging.info("Step 5: Saving tasks to database...")
            tasks_saved = await self.save_tasks_to_database(tasks, meeting_id, user_id)
            
            # Step 6: Schedule tasks in calendar
            logging.info("Step 6: Scheduling tasks in calendar...")
            calendar_results = await self.schedule_tasks_in_calendar(tasks, user_id)
            
            # Step 7: Update meeting record
            logging.info("Step 7: Updating meeting record...")
            meeting_updated = await self.update_meeting_with_results(meeting_id, transcript, timeline, file_url)
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "file_url": file_url,
                "transcript": transcript,
                "timeline": timeline,
                "tasks_count": len(tasks),
                "tasks_saved": tasks_saved,
                "calendar_scheduled": calendar_results,
                "meeting_updated": meeting_updated
            }
            
        except Exception as e:
            logging.error(f"Error in complete workflow: {e}")
            return {"error": f"Workflow failed: {str(e)}"}
