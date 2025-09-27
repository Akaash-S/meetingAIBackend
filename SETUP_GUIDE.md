# 🚀 Backend Setup Guide - Neon PostgreSQL + Supabase

This guide will help you set up the backend with Neon PostgreSQL for the database and Supabase for file storage.

## 📋 Prerequisites

1. **Neon PostgreSQL Account** - Sign up at [neon.tech](https://neon.tech)
2. **Supabase Account** - Sign up at [supabase.com](https://supabase.com)
3. **Python 3.8+** installed on your system

## 🔧 Step 1: Install Dependencies

```bash
# Install requirements
pip install -r requirements.txt

# If you encounter PostgreSQL issues on Windows, use:
pip install -r requirements-windows.txt
```

## 🗄️ Step 2: Set Up Neon PostgreSQL

### 2.1 Create Neon Database
1. Go to [Neon Console](https://console.neon.tech)
2. Create a new project
3. Copy the connection string (it looks like: `postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require`)

### 2.2 Configure Environment
1. Copy `env.example` to `.env`:
```bash
cp env.example .env
```

2. Update your `.env` file with your Neon connection string:
```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### 2.3 Run Database Migration
```bash
python migrate_to_neon.py
```

## 📁 Step 3: Set Up Supabase Storage

### 3.1 Create Supabase Project
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Create a new project
3. Go to Settings > API
4. Copy your:
   - Project URL (e.g., `https://your-project.supabase.co`)
   - Service Role Key (for server-side operations)

### 3.2 Configure Supabase in .env
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_BUCKET=meeting-files
```

### 3.3 Set Up Storage Bucket
```bash
python setup_supabase.py
```

## 🔑 Step 4: Configure API Keys

Add these to your `.env` file:

```env
# AI/NLP Services
RAPIDAPI_KEY=your-rapidapi-key
GEMINI_API_KEY=your-gemini-api-key

# Email (Optional)
SENDGRID_API_KEY=your-sendgrid-key
FROM_EMAIL=noreply@yourdomain.com

# Google Calendar (Optional)
GOOGLE_CREDENTIALS_FILE=path/to/service-account.json
```

## 🚀 Step 5: Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## 🧪 Step 6: Test the Setup

### Test Database Connection
```bash
curl http://localhost:5000/api/health
```

### Test File Upload
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@test-audio.mp3" \
  -F "title=Test Meeting" \
  -F "user_id=test-user-123"
```

## 📊 Database Schema

The following tables will be created:

- **users** - User accounts
- **meetings** - Meeting records with file paths
- **tasks** - Extracted tasks, decisions, and action items

## 🔧 Troubleshooting

### PostgreSQL Connection Issues
- Ensure your Neon connection string includes `?sslmode=require`
- Check that your IP is whitelisted in Neon (if required)

### Supabase Upload Issues
- Verify your Service Role Key has storage permissions
- Check that the bucket exists and is public
- Ensure file size is under 50MB (Supabase limit)

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

## 🌐 Production Deployment

For production, consider:

1. **Database**: Use Neon's production tier
2. **Storage**: Switch to AWS S3 by setting `USE_S3_STORAGE=true`
3. **Environment**: Set `FLASK_ENV=production`
4. **Security**: Use strong SECRET_KEY and secure API keys

## 📚 API Documentation

Once running, the API provides these endpoints:

- `POST /api/upload` - Upload meeting files
- `POST /api/transcribe/:meetingId` - Transcribe audio
- `POST /api/extract/:meetingId` - Extract insights
- `GET /api/meeting/:meetingId` - Get meeting details
- `GET /api/tasks/user/:userId` - Get user tasks
- `POST /api/notify/task/:taskId` - Send notifications

## 🆘 Need Help?

1. Check the logs: `python run.py` will show detailed error messages
2. Verify your `.env` file has all required variables
3. Test individual components: `python migrate_to_neon.py` and `python setup_supabase.py`
4. Check the main README.md for additional documentation
