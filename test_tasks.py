#!/usr/bin/env python3
"""
Test the tasks endpoint directly
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_tasks_endpoint():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        user_id = 'mJ5ODQaCxscD2EaFNOBWst9XJMg1'
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        print(f"User exists: {user is not None}")
        
        if not user:
            print("User not found!")
            return
        
        # Check tasks table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f"Tasks table columns: {columns}")
        
        # Try to query tasks
        try:
            cursor.execute("SELECT * FROM tasks WHERE user_id = %s LIMIT 5", (user_id,))
            tasks = cursor.fetchall()
            print(f"Found {len(tasks)} tasks")
        except Exception as e:
            print(f"Error querying tasks: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == '__main__':
    test_tasks_endpoint()
