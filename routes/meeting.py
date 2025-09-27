from flask import Blueprint, request, jsonify, current_app
import logging
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import os
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

meeting_bp = Blueprint('meeting', __name__)

@meeting_bp.route('/meeting/<meeting_id>', methods=['GET'])
def get_meeting(meeting_id):
    """Get meeting details with transcript, tasks, and insights"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get meeting details
            cur.execute("SELECT * FROM meetings WHERE id = %s", (meeting_id,))
            meeting = cur.fetchone()
            
            if not meeting:
                return jsonify({'error': 'Meeting not found'}), 404
            
            # Get tasks for this meeting
            cur.execute("SELECT * FROM tasks WHERE meeting_id = %s ORDER BY created_at DESC", (meeting_id,))
            tasks = cur.fetchall()
            
            # Convert to dict and handle datetime objects
            meeting_dict = dict(meeting)
            for key, value in meeting_dict.items():
                if isinstance(value, datetime):
                    meeting_dict[key] = value.isoformat()
            
            tasks_list = []
            for task in tasks:
                task_dict = dict(task)
                for key, value in task_dict.items():
                    if isinstance(value, datetime):
                        task_dict[key] = value.isoformat()
                tasks_list.append(task_dict)
            
            meeting_dict['tasks'] = tasks_list
            
            return jsonify(meeting_dict)
            
    except Exception as e:
        logging.error(f"Error fetching meeting: {e}")
        return jsonify({'error': 'Failed to fetch meeting'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@meeting_bp.route('/meetings/user/<user_id>', methods=['GET'])
def get_user_meetings(user_id):
    """Get all meetings for a user with pagination"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if user exists
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Count total meetings
            cur.execute("SELECT COUNT(*) as total FROM meetings WHERE user_id = %s", (user_id,))
            total_meetings = cur.fetchone()['total']
            
            # Get meetings with pagination
            cur.execute("""
                SELECT * FROM meetings 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """, (user_id, per_page, (page - 1) * per_page))
            meetings = cur.fetchall()
            
            # Convert to dict and handle datetime objects
            meetings_list = []
            for meeting in meetings:
                meeting_dict = dict(meeting)
                for key, value in meeting_dict.items():
                    if isinstance(value, datetime):
                        meeting_dict[key] = value.isoformat()
                meetings_list.append(meeting_dict)
            
            return jsonify({
                'meetings': meetings_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_meetings,
                    'pages': (total_meetings + per_page - 1) // per_page
                }
            })
            
    except Exception as e:
        logging.error(f"Error fetching meetings: {e}")
        return jsonify({'error': 'Failed to fetch meetings'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@meeting_bp.route('/meetings', methods=['POST'])
def create_meeting():
    """Create a new meeting"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if user exists
            cur.execute("SELECT id FROM users WHERE id = %s", (data['user_id'],))
            user = cur.fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Insert new meeting
            insert_query = """
                INSERT INTO meetings (title, description, user_id, duration, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING *
            """
            
            cur.execute(insert_query, (
                data['title'],
                data.get('description', ''),
                data['user_id'],
                data.get('duration', 0),
                data.get('status', 'scheduled')
            ))
            
            meeting = cur.fetchone()
            conn.commit()
            
            # Convert to dict and handle datetime objects
            meeting_dict = dict(meeting)
            for key, value in meeting_dict.items():
                if isinstance(value, datetime):
                    meeting_dict[key] = value.isoformat()
            
            return jsonify(meeting_dict), 201
            
    except Exception as e:
        logging.error(f"Error creating meeting: {e}")
        return jsonify({'error': 'Failed to create meeting'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@meeting_bp.route('/meetings/<meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    """Update an existing meeting"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if meeting exists
            cur.execute("SELECT id FROM meetings WHERE id = %s", (meeting_id,))
            meeting = cur.fetchone()
            if not meeting:
                return jsonify({'error': 'Meeting not found'}), 404
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            allowed_fields = ['title', 'description', 'duration', 'status', 'transcript', 'summary']
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])
            
            if not update_fields:
                return jsonify({'error': 'No valid fields to update'}), 400
            
            # Add updated_at
            update_fields.append("updated_at = NOW()")
            params.append(meeting_id)
            
            update_query = f"UPDATE meetings SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
            cur.execute(update_query, params)
            
            updated_meeting = cur.fetchone()
            conn.commit()
            
            # Convert to dict and handle datetime objects
            meeting_dict = dict(updated_meeting)
            for key, value in meeting_dict.items():
                if isinstance(value, datetime):
                    meeting_dict[key] = value.isoformat()
            
            return jsonify(meeting_dict)
            
    except Exception as e:
        logging.error(f"Error updating meeting: {e}")
        return jsonify({'error': 'Failed to update meeting'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@meeting_bp.route('/meetings/<meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    """Delete a meeting and its associated tasks"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor() as cur:
            # Check if meeting exists
            cur.execute("SELECT id FROM meetings WHERE id = %s", (meeting_id,))
            meeting = cur.fetchone()
            if not meeting:
                return jsonify({'error': 'Meeting not found'}), 404
            
            # Delete associated tasks first
            cur.execute("DELETE FROM tasks WHERE meeting_id = %s", (meeting_id,))
            
            # Delete meeting
            cur.execute("DELETE FROM meetings WHERE id = %s", (meeting_id,))
            conn.commit()
            
            return jsonify({'message': 'Meeting and associated tasks deleted successfully'})
            
    except Exception as e:
        logging.error(f"Error deleting meeting: {e}")
        return jsonify({'error': 'Failed to delete meeting'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@meeting_bp.route('/meetings/user/<user_id>/stats', methods=['GET'])
def get_meeting_stats(user_id):
    """Get meeting statistics for a user"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if user exists
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Get comprehensive statistics
            stats_query = """
                SELECT 
                    COUNT(*) as total_meetings,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_meetings,
                    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_meetings,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_meetings,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_meetings,
                    AVG(duration) as avg_duration,
                    SUM(duration) as total_duration,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as meetings_last_30_days,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as meetings_last_7_days
                FROM meetings WHERE user_id = %s
            """
            cur.execute(stats_query, (user_id,))
            stats = cur.fetchone()
            
            return jsonify(dict(stats))
            
    except Exception as e:
        logging.error(f"Error fetching meeting stats: {e}")
        return jsonify({'error': 'Failed to fetch meeting statistics'}), 500
    finally:
        if 'conn' in locals():
            conn.close()