from flask import Blueprint, request, jsonify, current_app
import requests
import os
import logging
import json
from datetime import datetime, timedelta
import re

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

extract_bp = Blueprint('extract', __name__)

def extract_with_gemini(transcript, meeting_id):
    """Extract tasks, decisions, and unresolved questions using Gemini API ONLY"""
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Gemini API key not configured - extraction requires Gemini")
        
        # Prepare the prompt for Gemini
        prompt = f"""
        Analyze the following meeting transcript and extract structured information. 
        Return a JSON response with the following format:
        
        {{
            "decisions": [
                {{
                    "text": "Decision description",
                    "timestamp": "HH:MM",
                    "impact": "high|medium|low"
                }}
            ],
            "action_items": [
                {{
                    "text": "Action item description",
                    "owner": "Person responsible",
                    "deadline": "YYYY-MM-DD or relative date (e.g., 'next Friday')",
                    "priority": "high|medium|low"
                }}
            ],
            "unresolved_questions": [
                {{
                    "text": "Question or issue that needs resolution",
                    "context": "Brief context about when it was mentioned",
                    "urgency": "high|medium|low"
                }}
            ],
            "summary": "Brief meeting summary (2-3 sentences)"
        }}
        
        Meeting Transcript:
        {transcript}
        
        Please analyze this transcript carefully and extract all decisions made, action items assigned, and unresolved questions that need follow-up. 
        For action items, try to identify the person responsible and estimate reasonable deadlines.
        For decisions, note the approximate time they were made and their potential impact.
        For unresolved questions, provide context about when they were raised.
        """
        
        # Make request to Gemini API
        headers = {
            'Content-Type': 'application/json',
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "topK": 1,
                "topP": 0.8,
                "maxOutputTokens": 2048,
            }
        }
        
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}',
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                return {
                    'success': True,
                    'data': extracted_data
                }
            else:
                raise Exception("No valid JSON found in Gemini response")
        else:
            logging.error(f"Gemini API error: {response.status_code} - {response.text}")
            return {
                'success': False,
                'error': f"API error: {response.status_code}",
                'details': response.text
            }
            
    except Exception as e:
        logging.error(f"Gemini extraction error: {str(e)}")
        return {
            'success': False,
            'error': 'Extraction failed',
            'details': str(e)
        }

def parse_deadline(deadline_str):
    """Parse deadline string to datetime object"""
    try:
        # Handle relative dates
        if 'next' in deadline_str.lower():
            if 'friday' in deadline_str.lower():
                days_ahead = 4 - datetime.now().weekday()  # Friday is 4
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                return datetime.now() + timedelta(days=days_ahead)
            elif 'monday' in deadline_str.lower():
                days_ahead = 0 - datetime.now().weekday()  # Monday is 0
                if days_ahead <= 0:
                    days_ahead += 7
                return datetime.now() + timedelta(days=days_ahead)
            # Add more relative date parsing as needed
        
        # Handle absolute dates
        try:
            return datetime.strptime(deadline_str, '%Y-%m-%d')
        except ValueError:
            pass
        
        # Default to 1 week from now if parsing fails
        return datetime.now() + timedelta(days=7)
        
    except Exception:
        return datetime.now() + timedelta(days=7)

def create_tasks_from_extraction(meeting_id, user_id, extracted_data):
    """Create task records from extracted data"""
    tasks_created = []
    
    try:
        # Create decision tasks
        for decision in extracted_data.get('decisions', []):
            task = Task(
                name=decision['text'],
                description=f"Decision made at {decision.get('timestamp', 'unknown time')}",
                category=TaskCategory.DECISION,
                priority=TaskPriority.HIGH if decision.get('impact') == 'high' else 
                        TaskPriority.MEDIUM if decision.get('impact') == 'medium' else TaskPriority.LOW,
                status=TaskStatus.COMPLETED,  # Decisions are considered completed when made
                meeting_id=meeting_id,
                user_id=user_id,
                completed_at=datetime.utcnow()
            )
            db.session.add(task)
            tasks_created.append(task)
        
        # Create action item tasks
        for action in extracted_data.get('action_items', []):
            deadline = parse_deadline(action.get('deadline', 'next week'))
            
            task = Task(
                name=action['text'],
                description=f"Action item assigned to {action.get('owner', 'TBD')}",
                owner=action.get('owner', 'TBD'),
                category=TaskCategory.ACTION_ITEM,
                priority=TaskPriority.HIGH if action.get('priority') == 'high' else 
                        TaskPriority.MEDIUM if action.get('priority') == 'medium' else TaskPriority.LOW,
                status=TaskStatus.PENDING,
                deadline=deadline,
                meeting_id=meeting_id,
                user_id=user_id
            )
            db.session.add(task)
            tasks_created.append(task)
        
        # Create unresolved question tasks
        for question in extracted_data.get('unresolved_questions', []):
            task = Task(
                name=question['text'],
                description=question.get('context', 'Unresolved question from meeting'),
                category=TaskCategory.UNRESOLVED,
                priority=TaskPriority.HIGH if question.get('urgency') == 'high' else 
                        TaskPriority.MEDIUM if question.get('urgency') == 'medium' else TaskPriority.LOW,
                status=TaskStatus.PENDING,
                meeting_id=meeting_id,
                user_id=user_id
            )
            db.session.add(task)
            tasks_created.append(task)
        
        db.session.commit()
        return tasks_created
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating tasks: {str(e)}")
        raise e

@extract_bp.route('/extract/<meeting_id>', methods=['POST'])
def extract_meeting_insights(meeting_id):
    """Extract tasks, decisions, and unresolved questions from meeting transcript"""
    try:
        # Get meeting record
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        if meeting.status != 'transcribed':
            return jsonify({'error': f'Meeting status is {meeting.status}, expected transcribed'}), 400
        
        if not meeting.transcript:
            return jsonify({'error': 'No transcript found for meeting'}), 400
        
        # Get user ID from request
        user_id = request.json.get('user_id') if request.is_json else request.form.get('user_id')
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Update status to processing
        meeting.status = 'processing'
        db.session.commit()
        
        # Extract insights using Gemini
        extraction_result = extract_with_gemini(meeting.transcript, meeting_id)
        
        if extraction_result['success']:
            # Create tasks from extracted data
            tasks_created = create_tasks_from_extraction(
                meeting_id, 
                user_id, 
                extraction_result['data']
            )
            
            # Update meeting status
            meeting.status = 'processed'
            meeting.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'meeting_id': meeting.id,
                'status': 'processed',
                'summary': extraction_result['data'].get('summary', ''),
                'decisions_count': len(extraction_result['data'].get('decisions', [])),
                'action_items_count': len(extraction_result['data'].get('action_items', [])),
                'unresolved_questions_count': len(extraction_result['data'].get('unresolved_questions', [])),
                'tasks_created': len(tasks_created),
                'message': 'Meeting insights extracted successfully'
            }), 200
        else:
            # Update status to error
            meeting.status = 'error'
            db.session.commit()
            
            return jsonify({
                'error': 'Extraction failed',
                'details': extraction_result.get('details', extraction_result.get('error', 'Unknown error')),
                'meeting_id': meeting.id
            }), 500
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"Extraction error: {str(e)}")
        
        # Update meeting status to error
        if 'meeting' in locals():
            meeting.status = 'error'
            db.session.commit()
        
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@extract_bp.route('/extract/<meeting_id>/status', methods=['GET'])
def get_extraction_status(meeting_id):
    """Get extraction status for a meeting"""
    try:
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        # Count tasks by category
        tasks = Task.query.filter_by(meeting_id=meeting_id).all()
        task_counts = {
            'decisions': len([t for t in tasks if t.category == TaskCategory.DECISION]),
            'action_items': len([t for t in tasks if t.category == TaskCategory.ACTION_ITEM]),
            'unresolved': len([t for t in tasks if t.category == TaskCategory.UNRESOLVED])
        }
        
        return jsonify({
            'meeting_id': meeting.id,
            'status': meeting.status,
            'task_counts': task_counts,
            'total_tasks': len(tasks),
            'updated_at': meeting.updated_at.isoformat() if meeting.updated_at else None
        })
        
    except Exception as e:
        logging.error(f"Status check error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
