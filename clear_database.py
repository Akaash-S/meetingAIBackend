#!/usr/bin/env python3
"""
Clear Database Script for Neon PostgreSQL
This script clears all existing data from the database tables while preserving the table structure.
Use this when you want to start fresh with testing.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_database_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL not found in environment variables")
        logger.error("Please make sure your .env file contains the DATABASE_URL")
        return None
    
    try:
        conn = psycopg2.connect(database_url)
        logger.info("✅ Database connection established")
        return conn
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        return None

def get_table_info(conn):
    """Get information about existing tables and their record counts"""
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all tables in the public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row['table_name'] for row in cursor.fetchall()]
        
        table_info = {}
        for table in tables:
            # Get record count for each table
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            table_info[table] = count
        
        cursor.close()
        return table_info
    except Exception as e:
        logger.error(f"❌ Error getting table info: {e}")
        return {}

def clear_table_data(conn, table_name):
    """Clear all data from a specific table"""
    try:
        cursor = conn.cursor()
        
        # Get count before deletion
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count_before = cursor.fetchone()[0]
        
        if count_before == 0:
            logger.info(f"📋 Table '{table_name}' is already empty")
            cursor.close()
            return True
        
        # Clear the table
        cursor.execute(f"DELETE FROM {table_name}")
        deleted_rows = cursor.rowcount
        
        # Reset auto-increment sequences if they exist
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND column_default LIKE 'nextval%'
        """)
        sequences = cursor.fetchall()
        
        for seq_col, seq_type in sequences:
            try:
                cursor.execute(f"ALTER SEQUENCE {table_name}_{seq_col}_seq RESTART WITH 1")
                logger.info(f"🔄 Reset sequence for {table_name}.{seq_col}")
            except Exception as seq_e:
                logger.warning(f"⚠️ Could not reset sequence for {table_name}.{seq_col}: {seq_e}")
        
        conn.commit()
        cursor.close()
        
        logger.info(f"✅ Cleared {deleted_rows} records from '{table_name}' table")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error clearing table '{table_name}': {e}")
        conn.rollback()
        return False

def clear_all_data():
    """Clear all data from all tables"""
    logger.info("🚀 Starting database data clearing process...")
    logger.info("=" * 60)
    
    # Get database connection
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        # Get current table information
        logger.info("📊 Getting current database state...")
        table_info = get_table_info(conn)
        
        if not table_info:
            logger.warning("⚠️ No tables found in the database")
            return True
        
        # Display current state
        logger.info("📋 Current database state:")
        total_records = 0
        for table, count in table_info.items():
            logger.info(f"   • {table}: {count} records")
            total_records += count
        
        if total_records == 0:
            logger.info("✅ Database is already empty - no data to clear")
            return True
        
        logger.info(f"📊 Total records to clear: {total_records}")
        logger.info("=" * 60)
        
        # Confirm before clearing
        response = input("⚠️  Are you sure you want to clear ALL data? This action cannot be undone! (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            logger.info("❌ Operation cancelled by user")
            return False
        
        # Clear data from each table
        logger.info("🧹 Clearing database data...")
        success_count = 0
        failed_tables = []
        
        # Clear tables in reverse dependency order to avoid foreign key issues
        # Clear tasks first (has foreign keys to meetings and users)
        # Then meetings (has foreign key to users)
        # Finally users
        table_order = ['tasks', 'meetings', 'users']
        
        for table in table_order:
            if table in table_info:
                if clear_table_data(conn, table):
                    success_count += 1
                else:
                    failed_tables.append(table)
        
        # Clear any remaining tables not in the ordered list
        for table in table_info:
            if table not in table_order:
                if clear_table_data(conn, table):
                    success_count += 1
                else:
                    failed_tables.append(table)
        
        # Final verification
        logger.info("🔍 Verifying data clearing...")
        final_table_info = get_table_info(conn)
        
        logger.info("=" * 60)
        logger.info("📊 Final database state:")
        all_empty = True
        for table, count in final_table_info.items():
            logger.info(f"   • {table}: {count} records")
            if count > 0:
                all_empty = False
        
        if all_empty:
            logger.info("✅ Database successfully cleared - all tables are now empty")
        else:
            logger.warning("⚠️ Some tables still contain data")
        
        if failed_tables:
            logger.error(f"❌ Failed to clear tables: {', '.join(failed_tables)}")
            return False
        
        logger.info("=" * 60)
        logger.info("🎉 Database clearing completed successfully!")
        logger.info("💡 You can now start fresh with your testing")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Unexpected error during database clearing: {e}")
        return False
    finally:
        if conn:
            conn.close()
            logger.info("🔌 Database connection closed")

def main():
    """Main function"""
    logger.info("🗄️  Neon PostgreSQL Database Data Clearing Tool")
    logger.info("=" * 60)
    logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        logger.error("❌ DATABASE_URL environment variable is not set")
        logger.error("Please make sure your .env file contains the DATABASE_URL")
        logger.error("Example: DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require")
        return False
    
    # Run the clearing process
    success = clear_all_data()
    
    logger.info("")
    logger.info("=" * 60)
    if success:
        logger.info("✅ Database clearing completed successfully!")
        logger.info("🚀 You can now start fresh with your testing")
    else:
        logger.error("❌ Database clearing failed!")
        logger.error("Please check the error messages above and try again")
    
    return success

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)
