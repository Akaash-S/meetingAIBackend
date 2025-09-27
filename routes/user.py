from flask import Blueprint, request, jsonify
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

load_dotenv()

user_bp = Blueprint('user', __name__)

def get_db_connection():
    """Get database connection"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None

@user_bp.route('/user/register', methods=['POST'])
def register_user():
    """Register a new user from Firebase authentication"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('user_id'):
            return jsonify({'error': 'User ID is required'}), 400
        
        user_id = data['user_id']
        name = data.get('name', 'Unknown User')
        email = data.get('email', f'{user_id}@example.com')
        photo_url = data.get('photo_url')
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Check if user already exists
                cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    # Update existing user info
                    cursor.execute("""
                        UPDATE users 
                        SET name = %s, email = %s, photo_url = %s, updated_at = %s
                        WHERE id = %s
                    """, (name, email, photo_url, datetime.now(), user_id))
                    conn.commit()
                    logging.info(f"Updated existing user: {user_id}")
                    
                    return jsonify({
                        'message': 'User updated successfully',
                        'user_id': user_id,
                        'name': name,
                        'email': email
                    }), 200
                
                # Create new user
                cursor.execute("""
                    INSERT INTO users (id, name, email, photo_url, role, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    name,
                    email,
                    photo_url,
                    'user',
                    datetime.now(),
                    datetime.now()
                ))
                
                conn.commit()
                logging.info(f"Created new user: {user_id}")
                
                return jsonify({
                    'message': 'User registered successfully',
                    'user_id': user_id,
                    'name': name,
                    'email': email
                }), 201
                
        except Exception as e:
            logging.error(f"Database error: {e}")
            return jsonify({'error': 'Database error'}), 500
        finally:
            conn.close()
        
    except Exception as e:
        logging.error(f"Register user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user information"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                
                if not user:
                    return jsonify({'error': 'User not found'}), 404
                
                return jsonify(dict(user))
                
        except Exception as e:
            logging.error(f"Database error: {e}")
            return jsonify({'error': 'Database error'}), 500
        finally:
            conn.close()
        
    except Exception as e:
        logging.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
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
                
                # Update user fields
                update_fields = []
                params = []
                
                if 'name' in data:
                    update_fields.append("name = %s")
                    params.append(data['name'])
                
                if 'email' in data:
                    update_fields.append("email = %s")
                    params.append(data['email'])
                
                if 'photo_url' in data:
                    update_fields.append("photo_url = %s")
                    params.append(data['photo_url'])
                
                if update_fields:
                    update_fields.append("updated_at = %s")
                    params.append(datetime.now())
                    params.append(user_id)
                    
                    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
                    cursor.execute(query, params)
                    conn.commit()
                    
                    logging.info(f"Updated user: {user_id}")
                
                return jsonify({'message': 'User updated successfully'})
                
        except Exception as e:
            logging.error(f"Database error: {e}")
            return jsonify({'error': 'Database error'}), 500
        finally:
            conn.close()
        
    except Exception as e:
        logging.error(f"Update user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/user/<user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user statistics"""
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
                
                # Get meeting count
                cursor.execute("SELECT COUNT(*) as meeting_count FROM meetings WHERE user_id = %s", (user_id,))
                meeting_count = cursor.fetchone()['meeting_count']
                
                # Get task count
                cursor.execute("SELECT COUNT(*) as task_count FROM tasks WHERE user_id = %s", (user_id,))
                task_count = cursor.fetchone()['task_count']
                
                # Get completed task count
                cursor.execute("SELECT COUNT(*) as completed_tasks FROM tasks WHERE user_id = %s AND status = 'completed'", (user_id,))
                completed_tasks = cursor.fetchone()['completed_tasks']
                
                # Get pending task count
                cursor.execute("SELECT COUNT(*) as pending_tasks FROM tasks WHERE user_id = %s AND status = 'pending'", (user_id,))
                pending_tasks = cursor.fetchone()['pending_tasks']
                
                return jsonify({
                    'user_id': user_id,
                    'meeting_count': meeting_count,
                    'task_count': task_count,
                    'completed_tasks': completed_tasks,
                    'pending_tasks': pending_tasks,
                    'completion_rate': (completed_tasks / task_count * 100) if task_count > 0 else 0
                })
                
        except Exception as e:
            logging.error(f"Database error: {e}")
            return jsonify({'error': 'Database error'}), 500
        finally:
            conn.close()
        
    except Exception as e:
        logging.error(f"Get user stats error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
