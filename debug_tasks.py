#!/usr/bin/env python3
"""
Detailed test of the tasks endpoint with error logging
"""

import os
import psycopg2
from dotenv import load_dotenv
import logging

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_database_directly():
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
        
        # Try the exact query from the endpoint
        try:
            base_query = "SELECT id, name, description, status, priority, category, deadline, created_at FROM tasks WHERE user_id = %s"
            cursor.execute(base_query, (user_id,))
            tasks = cursor.fetchall()
            print(f"Found {len(tasks)} tasks")
            
            for task in tasks:
                print(f"Task: {task}")
                
        except Exception as e:
            print(f"Error querying tasks: {e}")
            logger.exception("Full error details:")
        
        # Try the count query
        try:
            count_query = f"SELECT COUNT(*) as total FROM ({base_query}) as filtered_tasks"
            cursor.execute(count_query, (user_id,))
            count = cursor.fetchone()
            print(f"Count query result: {count}")
        except Exception as e:
            print(f"Error with count query: {e}")
            logger.exception("Count query error details:")
        
        # Try the stats query
        try:
            stats_query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed
                FROM tasks WHERE user_id = %s
            """
            cursor.execute(stats_query, (user_id,))
            stats = cursor.fetchone()
            print(f"Stats query result: {stats}")
        except Exception as e:
            print(f"Error with stats query: {e}")
            logger.exception("Stats query error details:")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")
        logger.exception("Full database error details:")

if __name__ == '__main__':
    test_database_directly()
