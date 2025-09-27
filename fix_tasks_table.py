#!/usr/bin/env python3
"""
Fix tasks table structure and add missing columns
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def fix_tasks_table():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print("🔧 Fixing tasks table structure...")
        
        # Drop and recreate tasks table with correct structure
        cursor.execute("DROP TABLE IF EXISTS tasks CASCADE")
        print("✅ Dropped existing tasks table")
        
        # Create tasks table with all required columns
        cursor.execute("""
            CREATE TABLE tasks (
                id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                name VARCHAR(500) NOT NULL,
                description TEXT,
                owner VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                priority VARCHAR(10) DEFAULT 'medium',
                category VARCHAR(20) NOT NULL,
                deadline TIMESTAMP,
                completed_at TIMESTAMP,
                meeting_id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meeting_id) REFERENCES meetings(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("✅ Created tasks table with correct structure")
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX idx_tasks_user_id ON tasks(user_id)")
        cursor.execute("CREATE INDEX idx_tasks_meeting_id ON tasks(meeting_id)")
        cursor.execute("CREATE INDEX idx_tasks_status ON tasks(status)")
        cursor.execute("CREATE INDEX idx_tasks_deadline ON tasks(deadline)")
        print("✅ Created indexes")
        
        # Insert some sample data for testing
        cursor.execute("""
            INSERT INTO tasks (id, name, description, owner, status, priority, category, deadline, meeting_id, user_id)
            VALUES 
            ('task-1', 'Review project proposal', 'Review the new project proposal and provide feedback', 'John Doe', 'pending', 'high', 'action-item', NOW() + INTERVAL '3 days', (SELECT id FROM meetings LIMIT 1), 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'),
            ('task-2', 'Schedule team meeting', 'Schedule the weekly team meeting for next week', 'Jane Smith', 'completed', 'medium', 'action-item', NOW() - INTERVAL '1 day', (SELECT id FROM meetings LIMIT 1), 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'),
            ('task-3', 'Update documentation', 'Update the API documentation with new endpoints', 'Mike Johnson', 'in_progress', 'low', 'action-item', NOW() + INTERVAL '7 days', (SELECT id FROM meetings LIMIT 1), 'mJ5ODQaCxscD2EaFNOBWst9XJMg1')
        """)
        print("✅ Inserted sample data")
        
        conn.commit()
        
        # Verify the table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("📋 Tasks table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # Test query
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s", ('mJ5ODQaCxscD2EaFNOBWst9XJMg1',))
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} tasks for user")
        
        cursor.close()
        conn.close()
        
        print("🎉 Tasks table fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing tasks table: {e}")
        return False

if __name__ == '__main__':
    fix_tasks_table()
