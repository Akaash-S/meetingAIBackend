#!/usr/bin/env python3
"""
Populate database with sample data for testing
"""

import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta
import uuid

load_dotenv()

def populate_database():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print("🚀 Populating database with sample data...")
        
        # Clear existing data
        cursor.execute("DELETE FROM tasks")
        cursor.execute("DELETE FROM meetings")
        cursor.execute("DELETE FROM users WHERE id != 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'")
        print("🧹 Cleared existing data")
        
        # Ensure the main user exists
        cursor.execute("""
            INSERT INTO users (id, name, email, role) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                email = EXCLUDED.email,
                role = EXCLUDED.role
        """, ('mJ5ODQaCxscD2EaFNOBWst9XJMg1', 'Sample User', 'sample@example.com', 'user'))
        print("✅ Main user created/updated")
        
        # Create sample meetings
        meetings_data = [
            {
                'id': str(uuid.uuid4()),
                'title': 'Weekly Team Standup',
                'transcript': 'Today we discussed the project progress. John mentioned that the frontend is 80% complete. Sarah reported that the backend API is ready for testing. Mike suggested we need to focus on the database optimization.',
                'file_path': '/uploads/meeting_1.wav',
                'file_name': 'weekly_standup_2024.wav',
                'file_size': 2048576,  # 2MB
                'duration': 1800,  # 30 minutes
                'participants': 5,
                'status': 'processed',
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Project Planning Meeting',
                'transcript': 'We planned the next sprint. Key deliverables include: 1) Complete user authentication, 2) Implement dashboard features, 3) Add file upload functionality. Timeline: 2 weeks.',
                'file_path': '/uploads/meeting_2.wav',
                'file_name': 'project_planning.wav',
                'file_size': 1536000,  # 1.5MB
                'duration': 2400,  # 40 minutes
                'participants': 8,
                'status': 'processed',
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'Client Review Session',
                'transcript': 'Client feedback session. They are happy with the progress but want to add more features. Priority items: mobile responsiveness, dark mode, and advanced analytics.',
                'file_path': '/uploads/meeting_3.wav',
                'file_name': 'client_review.wav',
                'file_size': 3072000,  # 3MB
                'duration': 3600,  # 60 minutes
                'participants': 6,
                'status': 'processed',
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            }
        ]
        
        for meeting in meetings_data:
            cursor.execute("""
                INSERT INTO meetings (id, title, transcript, file_path, file_name, file_size, duration, participants, status, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                meeting['id'], meeting['title'], meeting['transcript'], meeting['file_path'],
                meeting['file_name'], meeting['file_size'], meeting['duration'], 
                meeting['participants'], meeting['status'], meeting['user_id']
            ))
        
        print(f"✅ Created {len(meetings_data)} sample meetings")
        
        # Create sample tasks based on the meetings
        tasks_data = [
            # Tasks from Weekly Team Standup
            {
                'id': str(uuid.uuid4()),
                'name': 'Complete frontend development',
                'description': 'Finish the remaining 20% of frontend components and ensure all features are working properly',
                'owner': 'John Doe',
                'status': 'in_progress',
                'priority': 'high',
                'category': 'action-item',
                'deadline': datetime.now() + timedelta(days=3),
                'meeting_id': meetings_data[0]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Test backend API endpoints',
                'description': 'Run comprehensive tests on all backend API endpoints to ensure they work correctly',
                'owner': 'Sarah Wilson',
                'status': 'pending',
                'priority': 'high',
                'category': 'action-item',
                'deadline': datetime.now() + timedelta(days=2),
                'meeting_id': meetings_data[0]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Optimize database queries',
                'description': 'Review and optimize database queries for better performance',
                'owner': 'Mike Johnson',
                'status': 'pending',
                'priority': 'medium',
                'category': 'action-item',
                'deadline': datetime.now() + timedelta(days=5),
                'meeting_id': meetings_data[0]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            
            # Tasks from Project Planning Meeting
            {
                'id': str(uuid.uuid4()),
                'name': 'Implement user authentication',
                'description': 'Set up Firebase authentication and integrate with the application',
                'owner': 'Alex Chen',
                'status': 'completed',
                'priority': 'high',
                'category': 'action-item',
                'deadline': datetime.now() - timedelta(days=1),
                'completed_at': datetime.now() - timedelta(hours=2),
                'meeting_id': meetings_data[1]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Build dashboard features',
                'description': 'Create the main dashboard with task overview, statistics, and user interface',
                'owner': 'Emma Davis',
                'status': 'in_progress',
                'priority': 'high',
                'category': 'action-item',
                'deadline': datetime.now() + timedelta(days=7),
                'meeting_id': meetings_data[1]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Add file upload functionality',
                'description': 'Implement file upload feature for meeting recordings and documents',
                'owner': 'David Brown',
                'status': 'pending',
                'priority': 'medium',
                'category': 'action-item',
                'deadline': datetime.now() + timedelta(days=10),
                'meeting_id': meetings_data[1]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            
            # Tasks from Client Review Session
            {
                'id': str(uuid.uuid4()),
                'name': 'Implement mobile responsiveness',
                'description': 'Make the application fully responsive for mobile devices',
                'owner': 'Lisa Wang',
                'status': 'pending',
                'priority': 'high',
                'category': 'action-item',
                'deadline': datetime.now() + timedelta(days=14),
                'meeting_id': meetings_data[2]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Add dark mode feature',
                'description': 'Implement dark mode toggle and theme switching functionality',
                'owner': 'Tom Wilson',
                'status': 'pending',
                'priority': 'medium',
                'category': 'action-item',
                'deadline': datetime.now() + timedelta(days=21),
                'meeting_id': meetings_data[2]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Develop advanced analytics',
                'description': 'Create advanced analytics dashboard with charts and insights',
                'owner': 'Rachel Green',
                'status': 'pending',
                'priority': 'low',
                'category': 'action-item',
                'deadline': datetime.now() + timedelta(days=30),
                'meeting_id': meetings_data[2]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            
            # Some overdue tasks
            {
                'id': str(uuid.uuid4()),
                'name': 'Update project documentation',
                'description': 'Update all project documentation with latest changes',
                'owner': 'Mark Taylor',
                'status': 'pending',
                'priority': 'medium',
                'category': 'action-item',
                'deadline': datetime.now() - timedelta(days=2),
                'meeting_id': meetings_data[0]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Code review for authentication module',
                'description': 'Conduct thorough code review for the authentication module',
                'owner': 'Anna Smith',
                'status': 'pending',
                'priority': 'high',
                'category': 'action-item',
                'deadline': datetime.now() - timedelta(days=1),
                'meeting_id': meetings_data[1]['id'],
                'user_id': 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
            }
        ]
        
        for task in tasks_data:
            cursor.execute("""
                INSERT INTO tasks (id, name, description, owner, status, priority, category, deadline, completed_at, meeting_id, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task['id'], task['name'], task['description'], task['owner'], task['status'],
                task['priority'], task['category'], task['deadline'], task.get('completed_at'),
                task['meeting_id'], task['user_id']
            ))
        
        print(f"✅ Created {len(tasks_data)} sample tasks")
        
        # Commit all changes
        conn.commit()
        
        # Verify data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM meetings")
        meeting_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        
        print(f"📊 Database populated successfully:")
        print(f"   - Users: {user_count}")
        print(f"   - Meetings: {meeting_count}")
        print(f"   - Tasks: {task_count}")
        
        # Show task statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN deadline < NOW() AND status != 'completed' THEN 1 END) as overdue
            FROM tasks WHERE user_id = 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
        """)
        stats = cursor.fetchone()
        
        print(f"📈 Task Statistics:")
        print(f"   - Total: {stats[0]}")
        print(f"   - Pending: {stats[1]}")
        print(f"   - In Progress: {stats[2]}")
        print(f"   - Completed: {stats[3]}")
        print(f"   - Overdue: {stats[4]}")
        
        cursor.close()
        conn.close()
        
        print("🎉 Database population completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        return False

if __name__ == '__main__':
    populate_database()
