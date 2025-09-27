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
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
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
            
            # Build base query
            base_query = "SELECT id, name, description, status, priority, category, deadline, created_at FROM tasks WHERE user_id = %s"
            params = [user_id]
            
            # Apply filters
            if status_filter:
                base_query += " AND status = %s"
                params.append(status_filter)
            
            if priority_filter:
                base_query += " AND priority = %s"
                params.append(priority_filter)
            
            if category_filter:
                base_query += " AND category = %s"
                params.append(category_filter)
            
            if meeting_id:
                base_query += " AND meeting_id = %s"
                params.append(meeting_id)
            
            if search_term:
                base_query += " AND (name ILIKE %s OR description ILIKE %s)"
                search_param = f'%{search_term}%'
                params.extend([search_param, search_param])
            
            # Count total tasks
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as filtered_tasks"
            cur.execute(count_query, params)
            total_tasks = cur.fetchone()[0]
            
            # Add ordering and pagination
            base_query += " ORDER BY created_at DESC"
            base_query += " LIMIT %s OFFSET %s"
            params.extend([per_page, (page - 1) * per_page])
            
            # Execute query
            cur.execute(base_query, params)
            tasks = cur.fetchall()
            
            # Calculate statistics
            stats_query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed
                FROM tasks WHERE user_id = %s
            """
            cur.execute(stats_query, (user_id,))
            stats = cur.fetchone()
            
            # Convert tasks to dict format
            tasks_list = []
            column_names = ['id', 'name', 'description', 'status', 'priority', 'category', 'deadline', 'created_at']
            for task in tasks:
                task_dict = {}
                for i, value in enumerate(task):
                    key = column_names[i]
                    if isinstance(value, datetime):
                        task_dict[key] = value.isoformat()
                    else:
                        task_dict[key] = value
                tasks_list.append(task_dict)
        
        return jsonify({
            'tasks': tasks_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_tasks,
                'pages': (total_tasks + per_page - 1) // per_page
            },
            'stats': {
                'total': stats[0],
                'pending': stats[1],
                'completed': stats[2]
            }
        })
        
    except Exception as e:
        logging.error(f"Error fetching tasks: {e}")
        return jsonify({'error': 'Failed to fetch tasks'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@task_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
            
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            
            # Convert to dict and handle datetime objects
            task_dict = dict(task)
            for key, value in task_dict.items():
                if isinstance(value, datetime):
                    task_dict[key] = value.isoformat()
            
            return jsonify(task_dict)
            
    except Exception as e:
        logging.error(f"Error fetching task: {e}")
        return jsonify({'error': 'Failed to fetch task'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'user_id']
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
            
            # Insert new task
            insert_query = """
                INSERT INTO tasks (name, description, user_id, meeting_id, priority, status, category, owner, deadline, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING *
            """
            
            cur.execute(insert_query, (
                data['name'],
                data.get('description', ''),
                data['user_id'],
                data.get('meeting_id'),
                data.get('priority', 'medium'),
                data.get('status', 'pending'),
                data.get('category', 'general'),
                data.get('owner', ''),
                data.get('deadline')
            ))
            
            task = cur.fetchone()
            conn.commit()
            
            # Convert to dict and handle datetime objects
            task_dict = dict(task)
            for key, value in task_dict.items():
                if isinstance(value, datetime):
                    task_dict[key] = value.isoformat()
            
            return jsonify(task_dict), 201
            
    except Exception as e:
        logging.error(f"Error creating task: {e}")
        return jsonify({'error': 'Failed to create task'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@task_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if task exists
            cur.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            allowed_fields = ['name', 'description', 'priority', 'status', 'category', 'owner', 'deadline']
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])
            
            if not update_fields:
                return jsonify({'error': 'No valid fields to update'}), 400
            
            # Add updated_at
            update_fields.append("updated_at = NOW()")
            params.append(task_id)
            
            update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s RETURNING *"
            cur.execute(update_query, params)
            
            updated_task = cur.fetchone()
            conn.commit()
            
            # Convert to dict and handle datetime objects
            task_dict = dict(updated_task)
            for key, value in task_dict.items():
                if isinstance(value, datetime):
                    task_dict[key] = value.isoformat()
            
            return jsonify(task_dict)
            
    except Exception as e:
        logging.error(f"Error updating task: {e}")
        return jsonify({'error': 'Failed to update task'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@task_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
            
        with conn.cursor() as cur:
            # Check if task exists
            cur.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
            task = cur.fetchone()
            if not task:
                return jsonify({'error': 'Task not found'}), 404
            
            # Delete task
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            conn.commit()
            
            return jsonify({'message': 'Task deleted successfully'})
            
    except Exception as e:
        logging.error(f"Error deleting task: {e}")
        return jsonify({'error': 'Failed to delete task'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@task_bp.route('/tasks/user/<user_id>/stats', methods=['GET'])
def get_task_stats(user_id):
    """Get task statistics for a user"""
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
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tasks,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_tasks,
                    COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority_tasks,
                    COUNT(CASE WHEN priority = 'medium' THEN 1 END) as medium_priority_tasks,
                    COUNT(CASE WHEN priority = 'low' THEN 1 END) as low_priority_tasks,
                    COUNT(CASE WHEN deadline < NOW() AND status != 'completed' THEN 1 END) as overdue_tasks,
                    COUNT(CASE WHEN deadline BETWEEN NOW() AND NOW() + INTERVAL '7 days' AND status != 'completed' THEN 1 END) as due_this_week,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as created_last_30_days,
                    COUNT(CASE WHEN updated_at >= NOW() - INTERVAL '7 days' AND status = 'completed' THEN 1 END) as completed_last_7_days
                FROM tasks WHERE user_id = %s
            """
            cur.execute(stats_query, (user_id,))
            stats = cur.fetchone()
            
            return jsonify(dict(stats))
            
    except Exception as e:
        logging.error(f"Error fetching task stats: {e}")
        return jsonify({'error': 'Failed to fetch task statistics'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@task_bp.route('/tasks/overdue/user/<user_id>', methods=['GET'])
def get_overdue_tasks(user_id):
    """Get overdue tasks for a user"""
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
            
            # Get overdue tasks
            cur.execute("""
                SELECT * FROM tasks 
                WHERE user_id = %s 
                AND deadline < NOW() 
                AND status != 'completed'
                ORDER BY deadline ASC
            """, (user_id,))
            
            tasks = cur.fetchall()
            
            return jsonify({
                'tasks': [dict(task) for task in tasks],
                'count': len(tasks)
            })
            
    except Exception as e:
        logging.error(f"Error fetching overdue tasks: {e}")
        return jsonify({'error': 'Failed to fetch overdue tasks'}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@task_bp.route('/tasks/upcoming/user/<user_id>', methods=['GET'])
def get_upcoming_tasks(user_id):
    """Get upcoming tasks for a user"""
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
            
            # Get upcoming tasks (due within next 7 days)
            cur.execute("""
                SELECT * FROM tasks 
                WHERE user_id = %s 
                AND deadline BETWEEN NOW() AND NOW() + INTERVAL '7 days'
                AND status != 'completed'
                ORDER BY deadline ASC
            """, (user_id,))
            
            tasks = cur.fetchall()
            
            return jsonify({
                'tasks': [dict(task) for task in tasks],
                'count': len(tasks)
            })
            
    except Exception as e:
        logging.error(f"Error fetching upcoming tasks: {e}")
        return jsonify({'error': 'Failed to fetch upcoming tasks'}), 500
    finally:
        if 'conn' in locals():
            conn.close()