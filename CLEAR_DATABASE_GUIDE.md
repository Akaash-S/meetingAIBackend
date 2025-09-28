# 🗄️ Database Clearing Guide

This guide will help you clear all existing data from your Neon PostgreSQL database so you can start fresh with testing.

## ⚠️ Important Warning

**This action will permanently delete ALL data from your database tables. This cannot be undone!**

Make sure you have backups of any important data before proceeding.

## 📋 Prerequisites

1. **Neon PostgreSQL Database** - Your database must be set up and accessible
2. **Environment Configuration** - Your `.env` file must contain the correct `DATABASE_URL`
3. **Python Dependencies** - Make sure you have the required packages installed

## 🚀 Quick Start

### Step 1: Verify Your Setup

First, test that your database connection is working:

```bash
cd backend
python test_clear_script.py
```

This will:
- ✅ Check if your `.env` file exists
- ✅ Test database connection
- ✅ Show current table information and record counts

### Step 2: Clear the Database

If the test passes, run the clearing script:

```bash
python clear_database.py
```

The script will:
1. 📊 Show current database state (table names and record counts)
2. ⚠️ Ask for confirmation before proceeding
3. 🧹 Clear all data from all tables
4. 🔄 Reset any auto-increment sequences
5. ✅ Verify that all tables are empty

## 📊 What Gets Cleared

The script will clear data from these tables (if they exist):

- **`tasks`** - All task records
- **`meetings`** - All meeting records  
- **`users`** - All user records
- **Any other tables** in the public schema

## 🔧 Manual Database Clearing (Alternative)

If you prefer to clear the database manually, you can use these SQL commands:

```sql
-- Connect to your Neon database and run:

-- Clear all data (in dependency order)
DELETE FROM tasks;
DELETE FROM meetings;
DELETE FROM users;

-- Reset sequences (if any)
ALTER SEQUENCE IF EXISTS tasks_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS meetings_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS users_id_seq RESTART WITH 1;
```

## 🛠️ Troubleshooting

### Error: "DATABASE_URL not found"

**Solution:** Make sure your `.env` file contains the correct database URL:

```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### Error: "Failed to connect to database"

**Solutions:**
1. Check your internet connection
2. Verify your Neon database is active
3. Ensure your connection string is correct
4. Check if your Neon database has been paused (Neon pauses inactive databases)

### Error: "Permission denied"

**Solution:** Make sure your database user has DELETE permissions on all tables.

## 🔄 After Clearing

Once the database is cleared, you can:

1. **Start Fresh Testing:**
   ```bash
   python app.py
   ```

2. **Recreate Test Data:**
   ```bash
   python create_test_user.py
   ```

3. **Verify Empty State:**
   ```bash
   python check_database.py
   ```

## 📝 Example Output

```
🗄️  Neon PostgreSQL Database Data Clearing Tool
============================================================
⏰ Started at: 2024-01-15 14:30:25

🚀 Starting database data clearing process...
============================================================
📊 Getting current database state...
📋 Current database state:
   • meetings: 5 records
   • tasks: 12 records
   • users: 3 records
📊 Total records to clear: 20
============================================================
⚠️  Are you sure you want to clear ALL data? This action cannot be undone! (yes/no): yes
🧹 Clearing database data...
✅ Cleared 12 records from 'tasks' table
✅ Cleared 5 records from 'meetings' table
✅ Cleared 3 records from 'users' table
🔍 Verifying data clearing...
============================================================
📊 Final database state:
   • meetings: 0 records
   • tasks: 0 records
   • users: 0 records
✅ Database successfully cleared - all tables are now empty
============================================================
🎉 Database clearing completed successfully!
💡 You can now start fresh with your testing
```

## 🆘 Need Help?

If you encounter any issues:

1. **Check the logs** - The script provides detailed logging
2. **Verify your setup** - Run `python test_clear_script.py` first
3. **Check Neon dashboard** - Ensure your database is active
4. **Review environment variables** - Make sure `DATABASE_URL` is correct

## 🔒 Security Note

- The script only clears data, it doesn't drop tables
- Your database structure remains intact
- Only the `public` schema is affected
- The script requires explicit confirmation before proceeding
