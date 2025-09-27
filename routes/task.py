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

task_bp = Blueprint('task', __name__)

@task_bp.route('/tasks/user/<user_id>', methods=['GET'])
def get_user_tasks(user_id):
    """Get all tasks for a user with filtering and pagination"""
    try:
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        category_filter = request.args.get('category')
        search_term = request.args.get('search')
        meeting_id = request.args.get('meeting_id')
        
        # Build query
        query = Task.query.filter_by(user_id=user_id)
        
        # Apply filters
        if status_filter:
            query = query.filter_by(status=TaskStatus(status_filter))
        
        if priority_filter:
            query = query.filter_by(priority=TaskPriority(priority_filter))
        
        if category_filter:
            query = query.filter_by(category=TaskCategory(category_filter))
        
        if meeting_id:
            query = query.filter_by(meeting_id=meeting_id)
        
        if search_term:
            query = query.filter(
                or_(
                    Task.name.ilike(f'%{search_term}%'),
                    Task.description.ilike(f'%{search_term}%'),
                    Task.owner.ilike(f'%{search_term}%')
                )
            )
        
        # Order by priority and deadline
        query = query.order_by(
            Task.priority.desc(),
            Task.deadline.asc(),
            Task.created_at.desc()
        )
        
        # Paginate
        tasks = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Calculate statistics
        all_tasks = Task.query.filter_by(user_id=user_id).all()
        stats = {
            'total': len(all_tasks),
            'completed': len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]),
            'pending': len([t for t in all_tasks if t.status == TaskStatus.PENDING]),
            'in_progress': len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]),
            'overdue': len([t for t in all_tasks if t.deadline and t.deadline < datetime.utcnow() and t.status != TaskStatus.COMPLETED]),
            'decisions': len([t for t in all_tasks if t.category == TaskCategory.DECISION]),
            'action_items': len([t for t in all_tasks if t.category == TaskCategory.ACTION_ITEM]),
            'unresolved': len([t for t in all_tasks if t.category == TaskCategory.UNRESOLVED])
        }
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks.items],
            'statistics': stats,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': tasks.total,
                'pages': tasks.pages,
                'has_next': tasks.has_next,
                'has_prev': tasks.has_prev
            }
        })
        
    except Exception as e:
        logging.error(f"Get user tasks error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'meeting_id', 'user_id', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate meeting exists
        meeting = Meeting.query.get(data['meeting_id'])
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        # Validate user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create task
        task = Task(
            name=data['name'],
            description=data.get('description', ''),
            owner=data.get('owner', ''),
            status=TaskStatus(data.get('status', 'pending')),
            priority=TaskPriority(data.get('priority', 'medium')),
            category=TaskCategory(data['category']),
            meeting_id=data['meeting_id'],
            user_id=data['user_id']
        )
        
        # Parse deadline if provided
        if 'deadline' in data and data['deadline']:
            try:
                task.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid deadline format. Use ISO 8601 format.'}), 400
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid enum value: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Create task error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@task_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'task': task.to_dict()})
        
    except Exception as e:
        logging.error(f"Get task error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@task_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            task.name = data['name']
        
        if 'description' in data:
            task.description = data['description']
        
        if 'owner' in data:
            task.owner = data['owner']
        
        if 'status' in data:
            task.status = TaskStatus(data['status'])
            
            # Set completed_at if status is completed
            if task.status == TaskStatus.COMPLETED and not task.completed_at:
                task.completed_at = datetime.utcnow()
            elif task.status != TaskStatus.COMPLETED:
                task.completed_at = None
        
        if 'priority' in data:
            task.priority = TaskPriority(data['priority'])
        
        if 'category' in data:
            task.category = TaskCategory(data['category'])
        
        if 'deadline' in data:
            if data['deadline']:
                try:
                    task.deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Invalid deadline format. Use ISO 8601 format.'}), 400
            else:
                task.deadline = None
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid enum value: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Update task error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@task_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Delete task error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@task_bp.route('/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark a task as completed"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task completed successfully',
            'task': task.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Complete task error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@task_bp.route('/tasks/overdue/user/<user_id>', methods=['GET'])
def get_overdue_tasks(user_id):
    """Get overdue tasks for a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        overdue_tasks = Task.query.filter(
            and_(
                Task.user_id == user_id,
                Task.deadline < datetime.utcnow(),
                Task.status != TaskStatus.COMPLETED
            )
        ).order_by(Task.deadline.asc()).all()
        
        return jsonify({
            'overdue_tasks': [task.to_dict() for task in overdue_tasks],
            'count': len(overdue_tasks)
        })
        
    except Exception as e:
        logging.error(f"Get overdue tasks error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@task_bp.route('/tasks/upcoming/user/<user_id>', methods=['GET'])
def get_upcoming_tasks(user_id):
    """Get upcoming tasks for a user (next 7 days)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get tasks due in the next 7 days
        seven_days_from_now = datetime.utcnow() + timedelta(days=7)
        
        upcoming_tasks = Task.query.filter(
            and_(
                Task.user_id == user_id,
                Task.deadline >= datetime.utcnow(),
                Task.deadline <= seven_days_from_now,
                Task.status != TaskStatus.COMPLETED
            )
        ).order_by(Task.deadline.asc()).all()
        
        return jsonify({
            'upcoming_tasks': [task.to_dict() for task in upcoming_tasks],
            'count': len(upcoming_tasks)
        })
        
    except Exception as e:
        logging.error(f"Get upcoming tasks error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
