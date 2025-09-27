from flask import Blueprint, request, jsonify, current_app
import requests
import os
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json

from models import db, Task, User, Meeting

notify_bp = Blueprint('notify', __name__)

def send_email_notification(user_email, subject, message, task=None):
    """Send email notification using SendGrid"""
    try:
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        if not sendgrid_api_key:
            logging.warning("SendGrid API key not configured")
            return False
        
        headers = {
            'Authorization': f'Bearer {sendgrid_api_key}',
            'Content-Type': 'application/json'
        }
        
        # Prepare email data
        email_data = {
            'personalizations': [{
                'to': [{'email': user_email}],
                'subject': subject
            }],
            'from': {'email': os.getenv('FROM_EMAIL', 'noreply@meetingai.com')},
            'content': [{
                'type': 'text/html',
                'value': message
            }]
        }
        
        # Add task details if provided
        if task:
            email_data['personalizations'][0]['substitutions'] = {
                'task_name': task.name,
                'task_owner': task.owner or 'Unassigned',
                'task_deadline': task.deadline.strftime('%Y-%m-%d') if task.deadline else 'No deadline',
                'task_priority': task.priority.value.title() if task.priority else 'Medium',
                'task_status': task.status.value.title() if task.status else 'Pending'
            }
        
        response = requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            headers=headers,
            json=email_data,
            timeout=30
        )
        
        if response.status_code == 202:
            logging.info(f"Email sent successfully to {user_email}")
            return True
        else:
            logging.error(f"SendGrid error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logging.error(f"Email notification error: {str(e)}")
        return False

def create_calendar_event(task, user_email):
    """Create Google Calendar event for a task"""
    try:
        # This is a simplified implementation
        # In a real app, you'd need to handle OAuth2 flow for each user
        calendar_service = get_calendar_service(user_email)
        if not calendar_service:
            return False
        
        # Prepare event data
        event = {
            'summary': f"Task: {task.name}",
            'description': f"Priority: {task.priority.value.title()}\nCategory: {task.category.value.title()}\nMeeting: {task.meeting.title if task.meeting else 'N/A'}",
            'start': {
                'dateTime': task.deadline.isoformat() if task.deadline else (datetime.utcnow() + timedelta(days=1)).isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (task.deadline + timedelta(hours=1)).isoformat() if task.deadline else (datetime.utcnow() + timedelta(days=1, hours=1)).isoformat(),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 60},  # 1 hour before
                ],
            },
        }
        
        # Create event
        event = calendar_service.events().insert(
            calendarId='primary',
            body=event
        ).execute()
        
        logging.info(f"Calendar event created: {event.get('htmlLink')}")
        return True
        
    except Exception as e:
        logging.error(f"Calendar event creation error: {str(e)}")
        return False

def get_calendar_service(user_email):
    """Get Google Calendar service for user (simplified - in real app, store user tokens)"""
    try:
        # This is a placeholder - in a real app, you'd retrieve stored OAuth2 credentials
        # For now, we'll use a service account or return None
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
        if not credentials_file:
            logging.warning("Google credentials not configured")
            return None
        
        # Load service account credentials
        from google.oauth2 import service_account
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        return service
        
    except Exception as e:
        logging.error(f"Calendar service error: {str(e)}")
        return None

@notify_bp.route('/notify/task/<task_id>', methods=['POST'])
def notify_task(task_id):
    """Send notification for a specific task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        user = User.query.get(task.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get notification type from request
        notification_type = request.json.get('type', 'reminder') if request.is_json else 'reminder'
        
        # Prepare notification message
        if notification_type == 'reminder':
            subject = f"Task Reminder: {task.name}"
            message = f"""
            <h2>Task Reminder</h2>
            <p><strong>Task:</strong> {task.name}</p>
            <p><strong>Owner:</strong> {task.owner or 'Unassigned'}</p>
            <p><strong>Deadline:</strong> {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'No deadline'}</p>
            <p><strong>Priority:</strong> {task.priority.value.title() if task.priority else 'Medium'}</p>
            <p><strong>Status:</strong> {task.status.value.title() if task.status else 'Pending'}</p>
            """
        elif notification_type == 'overdue':
            subject = f"Overdue Task: {task.name}"
            message = f"""
            <h2>Overdue Task Alert</h2>
            <p><strong>Task:</strong> {task.name}</p>
            <p><strong>Was due:</strong> {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'No deadline'}</p>
            <p><strong>Priority:</strong> {task.priority.value.title() if task.priority else 'Medium'}</p>
            <p>Please update the status or deadline for this task.</p>
            """
        elif notification_type == 'completed':
            subject = f"Task Completed: {task.name}"
            message = f"""
            <h2>Task Completed</h2>
            <p><strong>Task:</strong> {task.name}</p>
            <p><strong>Completed by:</strong> {task.owner or 'Unassigned'}</p>
            <p><strong>Completed at:</strong> {task.completed_at.strftime('%Y-%m-%d %H:%M') if task.completed_at else 'Unknown'}</p>
            <p>Great job on completing this task!</p>
            """
        else:
            return jsonify({'error': 'Invalid notification type'}), 400
        
        # Send email notification
        email_sent = send_email_notification(user.email, subject, message, task)
        
        # Create calendar event if task has deadline
        calendar_created = False
        if task.deadline:
            calendar_created = create_calendar_event(task, user.email)
        
        return jsonify({
            'message': 'Notification sent successfully',
            'task_id': task_id,
            'notification_type': notification_type,
            'email_sent': email_sent,
            'calendar_created': calendar_created
        })
        
    except Exception as e:
        logging.error(f"Notify task error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@notify_bp.route('/notify/overdue/user/<user_id>', methods=['POST'])
def notify_overdue_tasks(user_id):
    """Send notifications for all overdue tasks for a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get overdue tasks
        overdue_tasks = Task.query.filter(
            Task.user_id == user_id,
            Task.deadline < datetime.utcnow(),
            Task.status != 'completed'
        ).all()
        
        if not overdue_tasks:
            return jsonify({'message': 'No overdue tasks found'})
        
        # Send notifications for each overdue task
        notifications_sent = 0
        for task in overdue_tasks:
            try:
                subject = f"Overdue Task: {task.name}"
                message = f"""
                <h2>Overdue Task Alert</h2>
                <p><strong>Task:</strong> {task.name}</p>
                <p><strong>Was due:</strong> {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'No deadline'}</p>
                <p><strong>Priority:</strong> {task.priority.value.title() if task.priority else 'Medium'}</p>
                <p>Please update the status or deadline for this task.</p>
                """
                
                if send_email_notification(user.email, subject, message, task):
                    notifications_sent += 1
                    
            except Exception as e:
                logging.error(f"Error sending notification for task {task.id}: {str(e)}")
        
        return jsonify({
            'message': f'Overdue task notifications sent',
            'overdue_tasks_count': len(overdue_tasks),
            'notifications_sent': notifications_sent
        })
        
    except Exception as e:
        logging.error(f"Notify overdue tasks error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@notify_bp.route('/notify/upcoming/user/<user_id>', methods=['POST'])
def notify_upcoming_tasks(user_id):
    """Send notifications for upcoming tasks (next 7 days) for a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get upcoming tasks (next 7 days)
        seven_days_from_now = datetime.utcnow() + timedelta(days=7)
        upcoming_tasks = Task.query.filter(
            Task.user_id == user_id,
            Task.deadline >= datetime.utcnow(),
            Task.deadline <= seven_days_from_now,
            Task.status != 'completed'
        ).all()
        
        if not upcoming_tasks:
            return jsonify({'message': 'No upcoming tasks found'})
        
        # Send notifications for upcoming tasks
        notifications_sent = 0
        for task in upcoming_tasks:
            try:
                days_until_deadline = (task.deadline - datetime.utcnow()).days
                subject = f"Upcoming Task: {task.name} (Due in {days_until_deadline} days)"
                message = f"""
                <h2>Upcoming Task Reminder</h2>
                <p><strong>Task:</strong> {task.name}</p>
                <p><strong>Due:</strong> {task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else 'No deadline'}</p>
                <p><strong>Days remaining:</strong> {days_until_deadline}</p>
                <p><strong>Priority:</strong> {task.priority.value.title() if task.priority else 'Medium'}</p>
                <p>Please make sure to complete this task on time.</p>
                """
                
                if send_email_notification(user.email, subject, message, task):
                    notifications_sent += 1
                    
            except Exception as e:
                logging.error(f"Error sending notification for task {task.id}: {str(e)}")
        
        return jsonify({
            'message': f'Upcoming task notifications sent',
            'upcoming_tasks_count': len(upcoming_tasks),
            'notifications_sent': notifications_sent
        })
        
    except Exception as e:
        logging.error(f"Notify upcoming tasks error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@notify_bp.route('/notify/settings/user/<user_id>', methods=['GET'])
def get_notification_settings(user_id):
    """Get notification settings for a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # In a real app, you'd have a separate settings table
        # For now, return default settings
        settings = {
            'email_notifications': True,
            'task_reminders': True,
            'overdue_alerts': True,
            'upcoming_reminders': True,
            'weekly_digest': True,
            'calendar_sync': True
        }
        
        return jsonify({'settings': settings})
        
    except Exception as e:
        logging.error(f"Get notification settings error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@notify_bp.route('/notify/settings/user/<user_id>', methods=['PUT'])
def update_notification_settings(user_id):
    """Update notification settings for a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # In a real app, you'd update a settings table
        # For now, just return success
        return jsonify({
            'message': 'Notification settings updated successfully',
            'settings': data
        })
        
    except Exception as e:
        logging.error(f"Update notification settings error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
