# 🚀 MeetingAI Backend Setup Guide

Complete setup guide for MeetingAI backend with Neon PostgreSQL and Supabase storage.

## 🎯 Quick Start

### **Option 1: Automated Setup (Recommended)**
```bash
# Run the automated setup script
python quick_setup.py
```

### **Option 2: Manual Setup**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up database
python setup_database.py

# 3. Verify setup
python check_database.py

# 4. Start server
python app.py
```

## 📋 Prerequisites

### **1. Neon PostgreSQL Database**
- Sign up at [neon.tech](https://neon.tech)
- Create a new project
- Get your connection string

### **2. Supabase Storage**
- Sign up at [supabase.com](https://supabase.com)
- Create a new project
- Create a storage bucket named `meeting-files`

### **3. Environment Variables**
Copy `env.example` to `.env` and update:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
SUPABASE_BUCKET=meeting-files

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

## 🛠️ Setup Steps

### **Step 1: Environment Setup**
```bash
# Copy environment template
cp env.example .env

# Edit .env with your credentials
# Add your Neon PostgreSQL connection string
# Add your Supabase credentials
```

### **Step 2: Install Dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Or for Windows (if psycopg2 issues)
pip install -r requirements-windows.txt

# Or for development (SQLite)
pip install -r requirements-dev.txt
```

### **Step 3: Database Setup**
```bash
# Set up database tables
python setup_database.py

# Verify database setup
python check_database.py
```

### **Step 4: Start Backend**
```bash
# Start Flask development server
python app.py
```

## 🧪 Testing

### **Test Database Connection**
```bash
# Check database status
python check_database.py
```

### **Test API Endpoints**
```bash
# Health check
curl http://localhost:5000/api/health

# Test database connection
curl http://localhost:5000/api/meetings/user/test-user-123
```

### **Test File Upload**
```bash
# Test file upload to Supabase
curl -X POST http://localhost:5000/api/upload \
  -F "file=@test-audio.mp3" \
  -F "title=Test Meeting" \
  -F "user_id=test-user-123"
```

## 📊 Database Schema

### **Users Table**
- `id` (String, Primary Key)
- `name` (String, Required)
- `email` (String, Unique, Required)
- `role` (String, Default: 'user')
- `created_at` (DateTime)
- `updated_at` (DateTime)

### **Meetings Table**
- `id` (String, Primary Key)
- `title` (String, Required)
- `transcript` (Text)
- `file_path` (String)
- `file_name` (String)
- `file_size` (BigInteger)
- `duration` (Integer)
- `participants` (Integer)
- `status` (String, Default: 'uploaded')
- `user_id` (String, Foreign Key)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### **Tasks Table**
- `id` (String, Primary Key)
- `name` (String, Required)
- `description` (Text)
- `owner` (String)
- `status` (Enum: pending, in-progress, completed)
- `priority` (Enum: low, medium, high)
- `category` (Enum: decision, action-item, unresolved)
- `deadline` (DateTime)
- `completed_at` (DateTime)
- `meeting_id` (String, Foreign Key)
- `user_id` (String, Foreign Key)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## 🔧 API Endpoints

### **Health Check**
```
GET /api/health
```

### **File Upload**
```
POST /api/upload
- file: Audio/Video file
- title: Meeting title
- user_id: User ID
```

### **Meetings**
```
GET /api/meetings/user/{user_id}
GET /api/meeting/{meeting_id}
POST /api/meeting
PUT /api/meeting/{meeting_id}
DELETE /api/meeting/{meeting_id}
```

### **Tasks**
```
GET /api/tasks/user/{user_id}
GET /api/tasks/overdue/user/{user_id}
GET /api/tasks/upcoming/user/{user_id}
POST /api/tasks
PUT /api/tasks/{task_id}
DELETE /api/tasks/{task_id}
POST /api/tasks/{task_id}/complete
```

### **Transcription**
```
POST /api/transcribe/{meeting_id}
```

### **Insights**
```
POST /api/extract/{meeting_id}
```

### **Notifications**
```
POST /api/notify/task/{task_id}
```

## 🐛 Troubleshooting

### **Common Issues**

#### **1. Database Connection Failed**
```bash
# Check your DATABASE_URL
echo $DATABASE_URL

# Test connection
python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

#### **2. Tables Not Created**
```bash
# Run database setup
python setup_database.py

# Check tables
python check_database.py
```

#### **3. Supabase Upload Failed**
```bash
# Check Supabase credentials
python -c "from supabase import create_client; print('Supabase OK')"

# Test upload
python check_database.py
```

#### **4. psycopg2 Installation Failed**
```bash
# Use Windows-specific requirements
pip install -r requirements-windows.txt

# Or use development requirements
pip install -r requirements-dev.txt
```

### **Debug Commands**

#### **Check Environment**
```bash
# Check if .env is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('DATABASE_URL:', os.getenv('DATABASE_URL'))"
```

#### **Test Database**
```bash
# Test PostgreSQL connection
python -c "import psycopg2; conn = psycopg2.connect(os.getenv('DATABASE_URL')); print('DB OK')"
```

#### **Test Supabase**
```bash
# Test Supabase connection
python -c "from supabase import create_client; client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY')); print('Supabase OK')"
```

## ✅ Success Criteria

Your backend is working when:

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

Your backend should now be fully configured and ready to use! 🎉
