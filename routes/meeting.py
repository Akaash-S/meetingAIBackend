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
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        # Get all tasks for this meeting
        tasks = Task.query.filter_by(meeting_id=meeting_id).all()
        
        # Categorize tasks
        decisions = [task.to_dict() for task in tasks if task.category == TaskCategory.DECISION]
        action_items = [task.to_dict() for task in tasks if task.category == TaskCategory.ACTION_ITEM]
        unresolved_questions = [task.to_dict() for task in tasks if task.category == TaskCategory.UNRESOLVED]
        
        # Calculate statistics
        stats = {
            'total_tasks': len(tasks),
            'decisions_count': len(decisions),
            'action_items_count': len(action_items),
            'unresolved_count': len(unresolved_questions),
            'completed_tasks': len([t for t in tasks if t.status.value == 'completed']),
            'pending_tasks': len([t for t in tasks if t.status.value == 'pending']),
            'in_progress_tasks': len([t for t in tasks if t.status.value == 'in-progress'])
        }
        
        # Get meeting duration in minutes
        duration_minutes = meeting.duration // 60 if meeting.duration else 0
        
        return jsonify({
            'meeting': meeting.to_dict(),
            'tasks': {
                'decisions': decisions,
                'action_items': action_items,
                'unresolved_questions': unresolved_questions
            },
            'statistics': stats,
            'duration_minutes': duration_minutes
        })
        
    except Exception as e:
        logging.error(f"Get meeting error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@meeting_bp.route('/meetings/user/<user_id>', methods=['GET'])
def get_user_meetings(user_id):
    """Get all meetings for a user"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if user exists
                cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                # Get query parameters
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                status_filter = request.args.get('status')
                
                # Build query
                query = "SELECT * FROM meetings WHERE user_id = %s"
                params = [user_id]
                
                if status_filter:
                    query += " AND status = %s"
                    params.append(status_filter)
                
                query += " ORDER BY created_at DESC"
                
                # Get total count
                count_query = "SELECT COUNT(*) FROM meetings WHERE user_id = %s"
                count_params = [user_id]
                if status_filter:
                    count_query += " AND status = %s"
                    count_params.append(status_filter)
                
                cursor.execute(count_query, count_params)
                total = cursor.fetchone()['count']
                
                # Add pagination
                offset = (page - 1) * per_page
                query += " LIMIT %s OFFSET %s"
                params.extend([per_page, offset])
                
                cursor.execute(query, params)
                meetings = cursor.fetchall()
                
                # Get task counts for each meeting
                meeting_data = []
                for meeting in meetings:
                    meeting_dict = dict(meeting)
                    
                    # Count tasks by category
                    cursor.execute("""
                        SELECT category, COUNT(*) as count 
                        FROM tasks 
                        WHERE meeting_id = %s 
                        GROUP BY category
                    """, (meeting['id'],))
                    task_counts = cursor.fetchall()
                    
                    counts = {'decisions': 0, 'action-items': 0, 'unresolved': 0}
                    for count in task_counts:
                        if count['category'] == 'decision':
                            counts['decisions'] = count['count']
                        elif count['category'] == 'action-item':
                            counts['action-items'] = count['count']
                        elif count['category'] == 'unresolved':
                            counts['unresolved'] = count['count']
                    
                    meeting_dict['task_counts'] = counts
                    meeting_data.append(meeting_dict)
                
                # Calculate pagination info
                pages = (total + per_page - 1) // per_page
                has_next = page < pages
                has_prev = page > 1
                
                return jsonify({
                    'meetings': meeting_data,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'pages': pages,
                        'has_next': has_next,
                        'has_prev': has_prev
                    }
                })
                
        except Exception as e:
            logging.error(f"Database error: {e}")
            return jsonify({'error': 'Database error'}), 500
        finally:
            conn.close()
        
    except Exception as e:
        logging.error(f"Get user meetings error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@meeting_bp.route('/meeting/<meeting_id>/timeline', methods=['GET'])
def get_meeting_timeline(meeting_id):
    """Get timeline data for a meeting (for timeline view)"""
    try:
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        if not meeting.transcript:
            return jsonify({'error': 'No transcript available for timeline'}), 400
        
        # Split transcript into timeline blocks (simplified approach)
        # In a real implementation, you'd use more sophisticated NLP to segment the transcript
        transcript_lines = meeting.transcript.split('. ')
        
        # Get tasks with timestamps (mock timestamps for now)
        tasks = Task.query.filter_by(meeting_id=meeting_id).all()
        
        # Create timeline blocks
        timeline_blocks = []
        block_duration = 3  # 3 minutes per block
        total_blocks = (meeting.duration // 60) // block_duration if meeting.duration else len(transcript_lines) // 5
        
        for i in range(min(total_blocks, len(transcript_lines) // 5)):
            start_time = i * block_duration
            end_time = min((i + 1) * block_duration, meeting.duration // 60 if meeting.duration else 60)
            
            # Get transcript segment
            start_line = i * 5
            end_line = min((i + 1) * 5, len(transcript_lines))
            transcript_segment = '. '.join(transcript_lines[start_line:end_line])
            
            # Determine block type based on content and tasks
            block_type = 'discussion'
            tags = []
            
            # Check if any tasks are associated with this time period
            for task in tasks:
                if task.category == TaskCategory.DECISION:
                    tags.append('decision')
                    block_type = 'decision'
                elif task.category == TaskCategory.ACTION_ITEM:
                    tags.append('action-item')
                    block_type = 'action'
                elif task.category == TaskCategory.UNRESOLVED:
                    tags.append('unresolved')
                    block_type = 'unresolved'
            
            timeline_blocks.append({
                'id': i + 1,
                'timeRange': f"{start_time:02d}:00 - {end_time:02d}:00",
                'type': block_type,
                'title': f"Meeting Segment {i + 1}",
                'summary': transcript_segment[:100] + "..." if len(transcript_segment) > 100 else transcript_segment,
                'tags': list(set(tags)),
                'transcript': transcript_segment
            })
        
        return jsonify({
            'meeting_id': meeting.id,
            'title': meeting.title,
            'duration': meeting.duration,
            'timeline_blocks': timeline_blocks,
            'total_blocks': len(timeline_blocks)
        })
        
    except Exception as e:
        logging.error(f"Get timeline error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@meeting_bp.route('/meeting/<meeting_id>', methods=['PUT'])
def update_meeting(meeting_id):
    """Update meeting details"""
    try:
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            meeting.title = data['title']
        
        if 'participants' in data:
            meeting.participants = data['participants']
        
        meeting.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Meeting updated successfully',
            'meeting': meeting.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Update meeting error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@meeting_bp.route('/meeting/<meeting_id>', methods=['DELETE'])
def delete_meeting(meeting_id):
    """Delete a meeting and all associated tasks"""
    try:
        meeting = Meeting.query.get(meeting_id)
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        # Delete associated tasks (cascade should handle this, but being explicit)
        Task.query.filter_by(meeting_id=meeting_id).delete()
        
        # Delete meeting
        db.session.delete(meeting)
        db.session.commit()
        
        return jsonify({'message': 'Meeting deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete meeting error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
