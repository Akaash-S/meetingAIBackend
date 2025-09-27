# 🗄️ Database Setup Guide for MeetingAI Backend

This guide will help you set up Neon PostgreSQL database and Supabase storage for your MeetingAI backend.

## 📋 Prerequisites

1. **Neon PostgreSQL Account** - Sign up at [neon.tech](https://neon.tech)
2. **Supabase Account** - Sign up at [supabase.com](https://supabase.com)
3. **Python Environment** - Python 3.8+ with pip

## 🚀 Step 1: Set Up Neon PostgreSQL

### 1.1 Create Neon Database
1. Go to [Neon Console](https://console.neon.tech)
2. Click "Create Project"
3. Enter project name: `meeting-ai-db`
4. Choose region closest to you
5. Click "Create Project"

### 1.2 Get Connection String
1. In your Neon project dashboard
2. Go to "Connection Details"
3. Copy the connection string
4. It should look like: `postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require`

### 1.3 Update Environment Variables
1. Copy `env.example` to `.env`:
```bash
cp env.example .env
```

2. Update `.env` with your Neon connection string:
```env
# Database Configuration - Neon PostgreSQL
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

## 🔧 Step 2: Set Up Supabase Storage

### 2.1 Create Supabase Project
1. Go to [Supabase Console](https://supabase.com/dashboard)
2. Click "New Project"
3. Enter project name: `meeting-ai-storage`
4. Choose organization
5. Set database password
6. Choose region
7. Click "Create new project"

### 2.2 Get Supabase Credentials
1. In your Supabase project dashboard
2. Go to "Settings" > "API"
3. Copy the following:
   - **Project URL** (e.g., `https://your-project.supabase.co`)
   - **Anon Key** (public key)
   - **Service Role Key** (secret key)

### 2.3 Create Storage Bucket
1. In Supabase dashboard, go to "Storage"
2. Click "Create a new bucket"
3. Enter bucket name: `meeting-files`
4. Make it **Public** (for file access)
5. Click "Create bucket"

### 2.4 Update Environment Variables
Add to your `.env` file:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
SUPABASE_BUCKET=meeting-files
```

## 🛠️ Step 3: Install Dependencies

### 3.1 Install Python Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Or for Windows (if psycopg2 issues)
pip install -r requirements-windows.txt

# Or for development (SQLite)
pip install -r requirements-dev.txt
```

### 3.2 Install Supabase Python Client
```bash
pip install supabase
```

## 🗄️ Step 4: Initialize Database

### 4.1 Run Database Setup
```bash
# Set up database tables
python setup_database.py
```

This script will:
- ✅ Test database connection
- ✅ Create all tables (users, meetings, tasks)
- ✅ Initialize Flask-Migrate
- ✅ Set up Supabase storage

### 4.2 Verify Database Setup
```bash
# Check database status
python check_database.py
```

This script will:
- ✅ Test database connection
- ✅ Verify all tables exist
- ✅ Test model creation
- ✅ Test Supabase storage

## 🧪 Step 5: Test the Setup

### 5.1 Start the Backend
```bash
# Start Flask development server
python app.py
```

### 5.2 Test API Endpoints
```bash
# Test health check
curl http://localhost:5000/api/health

# Test database connection
curl http://localhost:5000/api/meetings/user/test-user-123
```

### 5.3 Test File Upload
```bash
# Test file upload to Supabase
curl -X POST http://localhost:5000/api/upload \
  -F "file=@test-audio.mp3" \
  -F "title=Test Meeting" \
  -F "user_id=test-user-123"
```

## 🔍 Step 6: Verify Everything Works

### 6.1 Check Database Tables
1. Go to your Neon dashboard
2. Navigate to "SQL Editor"
3. Run this query:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

You should see:
- ✅ `users`
- ✅ `meetings`
- ✅ `tasks`

### 6.2 Check Supabase Storage
1. Go to your Supabase dashboard
2. Navigate to "Storage"
3. Check that `meeting-files` bucket exists
4. Verify you can upload files

### 6.3 Test Backend Endpoints
```bash
# Health check
curl http://localhost:5000/api/health

# Get user meetings
curl http://localhost:5000/api/meetings/user/test-user-123

# Get user tasks
curl http://localhost:5000/api/tasks/user/test-user-123
```

## 🐛 Troubleshooting

### Common Issues

#### **Issue 1: "psycopg2" installation fails**
**Solution**: Use Windows-specific requirements
```bash
pip install -r requirements-windows.txt
```

#### **Issue 2: "Database connection failed"**
**Solution**: Check your DATABASE_URL
```bash
# Test connection string
python -c "import psycopg2; psycopg2.connect('your-connection-string')"
```

#### **Issue 3: "Supabase upload failed"**
**Solution**: Check Supabase credentials
```bash
# Test Supabase connection
python -c "from supabase import create_client; print('Supabase OK')"
```

#### **Issue 4: "Tables not created"**
**Solution**: Run database setup
```bash
python setup_database.py
```

#### **Issue 5: "Permission denied" on Supabase**
**Solution**: Check bucket permissions
1. Go to Supabase dashboard > Storage
2. Check bucket is public
3. Verify service key has correct permissions

### Debug Commands

#### **Check Environment Variables**
```bash
# Check if .env is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('DATABASE_URL:', os.getenv('DATABASE_URL'))"
```

#### **Test Database Connection**
```bash
# Test PostgreSQL connection
python -c "import psycopg2; conn = psycopg2.connect(os.getenv('DATABASE_URL')); print('DB OK')"
```

#### **Test Supabase Connection**
```bash
# Test Supabase connection
python -c "from supabase import create_client; client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY')); print('Supabase OK')"
```

## ✅ Success Criteria

Your setup is working when:

- ✅ **Database connection** successful
- ✅ **All tables created** (users, meetings, tasks)
- ✅ **Supabase storage** accessible
- ✅ **Backend API** responding
- ✅ **File uploads** working
- ✅ **No console errors**

## 🚀 Next Steps

After successful setup:

1. **Test Frontend Integration** - Connect frontend to backend
2. **Test File Uploads** - Upload meeting recordings
3. **Test AI Processing** - Transcribe and extract insights
4. **Deploy to Production** - Use production database and storage

## 📞 Support

If you encounter issues:

1. Check the logs for specific error messages
2. Verify all environment variables are set
3. Test database and Supabase connections separately
4. Check the troubleshooting section above

Your database and storage should now be fully configured! 🎉
