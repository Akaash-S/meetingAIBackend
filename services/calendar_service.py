"""
Calendar Integration Service
Handles Google Calendar integration for task scheduling
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class CalendarService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self.client_secret_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/callback')
    
    def get_authorization_url(self) -> str:
        """Get Google Calendar authorization URL"""
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secret_file,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            return auth_url
            
        except Exception as e:
            logging.error(f"Error generating authorization URL: {e}")
            return None
    
    def handle_callback(self, authorization_code: str) -> bool:
        """Handle OAuth callback and store credentials"""
        try:
            flow = Flow.from_client_secrets_file(
                self.client_secret_file,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            flow.fetch_token(code=authorization_code)
            self.credentials = flow.credentials
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            
            return True
            
        except Exception as e:
            logging.error(f"Error handling OAuth callback: {e}")
            return False
    
    def create_event(self, task: Dict, user_id: str) -> Optional[str]:
        """Create a calendar event for a task"""
        try:
            if not self.service:
                logging.error("Calendar service not initialized")
                return None
            
            # Extract task details
            task_name = task.get('name', 'Untitled Task')
            task_description = task.get('description', '')
            due_date = task.get('due_date')
            priority = task.get('priority', 'medium')
            
            # Set event time
            if due_date:
                start_time = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            else:
                # Default to tomorrow if no due date
                start_time = datetime.now() + timedelta(days=1)
            
            end_time = start_time + timedelta(hours=1)  # 1-hour event
            
            # Create event
            event = {
                'summary': f"📋 {task_name}",
                'description': f"{task_description}\n\nPriority: {priority.title()}\nTask ID: {task.get('id', 'N/A')}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},       # 1 hour before
                    ],
                },
                'colorId': self._get_color_id(priority),
            }
            
            # Add attendees if assignee is specified
            assignee = task.get('assignee')
            if assignee and assignee != 'Unassigned':
                event['attendees'] = [{'email': f"{assignee.lower().replace(' ', '.')}@company.com"}]
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            logging.info(f"Created calendar event: {event_id}")
            
            return event_id
            
        except HttpError as e:
            logging.error(f"Calendar API error: {e}")
            return None
        except Exception as e:
            logging.error(f"Error creating calendar event: {e}")
            return None
    
    def create_recurring_event(self, task: Dict, user_id: str, recurrence: str = 'weekly') -> Optional[str]:
        """Create a recurring calendar event for a task"""
        try:
            if not self.service:
                logging.error("Calendar service not initialized")
                return None
            
            task_name = task.get('name', 'Untitled Task')
            task_description = task.get('description', '')
            due_date = task.get('due_date')
            priority = task.get('priority', 'medium')
            
            # Set event time
            if due_date:
                start_time = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            else:
                start_time = datetime.now() + timedelta(days=1)
            
            end_time = start_time + timedelta(hours=1)
            
            # Create recurring event
            event = {
                'summary': f"🔄 {task_name}",
                'description': f"{task_description}\n\nPriority: {priority.title()}\nTask ID: {task.get('id', 'N/A')}\nRecurring: {recurrence}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'recurrence': [f'RRULE:FREQ={recurrence.upper()};COUNT=10'],  # 10 occurrences
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 60},
                    ],
                },
                'colorId': self._get_color_id(priority),
            }
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            logging.info(f"Created recurring calendar event: {event_id}")
            
            return event_id
            
        except Exception as e:
            logging.error(f"Error creating recurring calendar event: {e}")
            return None
    
    def update_event(self, event_id: str, task: Dict) -> bool:
        """Update an existing calendar event"""
        try:
            if not self.service:
                logging.error("Calendar service not initialized")
                return False
            
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update event details
            event['summary'] = f"📋 {task.get('name', 'Untitled Task')}"
            event['description'] = f"{task.get('description', '')}\n\nPriority: {task.get('priority', 'medium').title()}\nTask ID: {task.get('id', 'N/A')}"
            event['colorId'] = self._get_color_id(task.get('priority', 'medium'))
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logging.info(f"Updated calendar event: {event_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error updating calendar event: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            if not self.service:
                logging.error("Calendar service not initialized")
                return False
            
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logging.info(f"Deleted calendar event: {event_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting calendar event: {e}")
            return False
    
    def _get_color_id(self, priority: str) -> str:
        """Get Google Calendar color ID based on priority"""
        color_map = {
            'high': '11',    # Red
            'medium': '5',   # Yellow
            'low': '10',     # Green
        }
        return color_map.get(priority.lower(), '5')  # Default to yellow
    
    def schedule_tasks(self, tasks: List[Dict], user_id: str) -> Dict:
        """Schedule multiple tasks in calendar with enhanced scheduling logic"""
        try:
            results = {
                'successful': [],
                'failed': [],
                'total': len(tasks),
                'scheduled_count': 0,
                'skipped_count': 0
            }
            
            for task in tasks:
                try:
                    task_name = task.get('name', 'Untitled Task')
                    priority = task.get('priority', 'medium')
                    category = task.get('category', 'general')
                    effort = task.get('effort', 1)
                    dependencies = task.get('dependencies', [])
                    tags = task.get('tags', [])
                    
                    # Enhanced scheduling logic
                    due_date = task.get('due_date')
                    if not due_date:
                        # Auto-schedule based on priority and effort
                        if priority == 'high':
                            due_date = (datetime.now() + timedelta(days=1)).isoformat()
                        elif priority == 'medium':
                            due_date = (datetime.now() + timedelta(days=3)).isoformat()
                        else:
                            due_date = (datetime.now() + timedelta(days=7)).isoformat()
                    
                    # Create enhanced calendar event
                    event_id = self._create_enhanced_event(task, user_id, due_date)
                    
                    if event_id:
                        results['successful'].append({
                            'task_id': task.get('id'),
                            'task_name': task_name,
                            'event_id': event_id,
                            'scheduled_date': due_date,
                            'priority': priority,
                            'category': category
                        })
                        
                        # Update task with calendar event ID
                        self._update_task_calendar_id(task.get('id'), event_id)
                        results['scheduled_count'] += 1
                    else:
                        results['failed'].append({
                            'task_id': task.get('id'),
                            'task_name': task_name,
                            'reason': 'Failed to create calendar event'
                        })
                        
                except Exception as e:
                    logging.error(f"Error scheduling task {task.get('id')}: {e}")
                    results['failed'].append({
                        'task_id': task.get('id'),
                        'task_name': task.get('name'),
                        'reason': str(e)
                    })
            
            logging.info(f"Calendar scheduling completed: {results['scheduled_count']} successful, {len(results['failed'])} failed")
            return results
            
        except Exception as e:
            logging.error(f"Error scheduling tasks: {e}")
            return {'error': str(e)}
    
    def _create_enhanced_event(self, task: Dict, user_id: str, due_date: str) -> Optional[str]:
        """Create an enhanced calendar event with better details"""
        try:
            if not self.service:
                logging.error("Calendar service not initialized")
                return None
            
            task_name = task.get('name', 'Untitled Task')
            task_description = task.get('description', '')
            priority = task.get('priority', 'medium')
            category = task.get('category', 'general')
            effort = task.get('effort', 1)
            dependencies = task.get('dependencies', [])
            tags = task.get('tags', [])
            context = task.get('context', '')
            
            # Calculate event duration based on effort
            duration_hours = max(1, min(8, effort * 2))  # 1-8 hours based on effort
            
            # Set event time
            start_time = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            end_time = start_time + timedelta(hours=duration_hours)
            
            # Create enhanced event description
            description_parts = [
                task_description,
                f"\n📊 Priority: {priority.title()}",
                f"🏷️ Category: {category.title()}",
                f"⏱️ Effort: {effort}/5",
                f"⏰ Duration: {duration_hours} hours"
            ]
            
            if tags:
                description_parts.append(f"🏷️ Tags: {', '.join(tags)}")
            
            if dependencies:
                description_parts.append(f"🔗 Dependencies: {', '.join(dependencies)}")
            
            if context:
                description_parts.append(f"\n📝 Context: {context}")
            
            description_parts.append(f"\n🆔 Task ID: {task.get('id', 'N/A')}")
            description_parts.append(f"👤 User ID: {user_id}")
            
            # Create enhanced event
            event = {
                'summary': f"📋 {task_name}",
                'description': '\n'.join(description_parts),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60},       # 1 hour before
                    ],
                },
                'colorId': self._get_color_id(priority),
                'visibility': 'private',
                'transparency': 'opaque',
            }
            
            # Add attendees if assignee is specified
            assignee = task.get('assignee')
            if assignee and assignee != 'Unassigned':
                event['attendees'] = [{'email': f"{assignee.lower().replace(' ', '.')}@company.com"}]
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            logging.info(f"Created enhanced calendar event: {event_id}")
            
            return event_id
            
        except Exception as e:
            logging.error(f"Error creating enhanced calendar event: {e}")
            return None
    
    def _update_task_calendar_id(self, task_id: str, event_id: str) -> bool:
        """Update task with calendar event ID"""
        try:
            from app import get_db_connection, return_db_connection
            
            conn = get_db_connection()
            if not conn:
                return False
            
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE tasks 
                        SET calendar_event_id = %s, updated_at = %s
                        WHERE id = %s
                    """, (event_id, datetime.now(), task_id))
                
                conn.commit()
                return True
                
            except Exception as e:
                logging.error(f"Error updating task calendar ID: {e}")
                conn.rollback()
                return False
            finally:
                return_db_connection(conn)
                
        except Exception as e:
            logging.error(f"Error updating task calendar ID: {e}")
            return False
