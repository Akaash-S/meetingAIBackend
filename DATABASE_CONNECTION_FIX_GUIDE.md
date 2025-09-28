# 🔧 Database Connection Fix Guide

This guide will help you resolve the "Database connection failed" error in your MeetingAI application.

## 🚨 Problem Identified

Based on the error analysis, the main issues are:

1. **Missing `.env` file** - The backend can't find the database configuration
2. **Database connection not configured** - No DATABASE_URL is set
3. **Backend server not running** - The API endpoints are returning connection errors

## 🎯 Quick Fix Solution

### Step 1: Run the Automatic Fix Script

```bash
cd backend
python fix_database_connection.py
```

This script will:
- ✅ Check and install missing Python dependencies
- ✅ Create the `.env` file from `env.example`
- ✅ Prompt you for your Neon PostgreSQL database URL
- ✅ Test the database connection
- ✅ Set up database tables
- ✅ Create a startup script

### Step 2: Start the Backend Server

After the fix script completes successfully:

```bash
python start_backend.py
```

Or alternatively:

```bash
python app.py
```

## 🔍 Manual Fix (If Automatic Fix Fails)

### Step 1: Create .env File

```bash
cd backend
cp env.example .env
```

### Step 2: Configure Database URL

Edit the `.env` file and replace the DATABASE_URL with your actual Neon PostgreSQL connection string:

```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Test Database Connection

```bash
python test_db_connection.py
```

### Step 5: Set Up Database Tables

```bash
python setup_database.py
```

### Step 6: Start the Server

```bash
python app.py
```

## 🗄️ Getting Your Neon Database URL

1. Go to [Neon Console](https://console.neon.tech)
2. Select your project
3. Go to "Connection Details"
4. Copy the connection string
5. It should look like: `postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require`

## 🧪 Testing the Fix

### Test 1: Database Connection
```bash
python test_db_connection.py
```

### Test 2: Backend Health Check
```bash
curl http://localhost:5000/health
```

### Test 3: Upload Endpoint
```bash
curl -X POST http://localhost:5000/api/upload
```

## 🚀 Expected Results

After the fix:

1. **Backend server starts successfully** on `http://localhost:5000`
2. **Database connection works** - no more "Database connection failed" errors
3. **Upload functionality works** - you can upload meeting recordings
4. **API endpoints respond** - no more `net::ERR_CONNECTION_RESET` errors

## 🔧 Troubleshooting

### Error: "DATABASE_URL not found"
**Solution:** Make sure your `.env` file exists and contains the DATABASE_URL

### Error: "Failed to connect to database"
**Solutions:**
1. Check your internet connection
2. Verify your Neon database is active (not paused)
3. Ensure your connection string is correct
4. Check if your database credentials are valid

### Error: "Module not found"
**Solution:** Install missing dependencies:
```bash
pip install psycopg2 flask flask-cors python-dotenv werkzeug
```

### Error: "Port 5000 already in use"
**Solution:** Kill the process using port 5000:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Or use a different port
python app.py --port 5001
```

## 📊 Verification Checklist

- [ ] `.env` file exists in backend directory
- [ ] DATABASE_URL is set in `.env` file
- [ ] Database connection test passes
- [ ] Backend server starts without errors
- [ ] Health check endpoint responds
- [ ] Upload endpoint is accessible
- [ ] Frontend can connect to backend API

## 🆘 Still Having Issues?

If you're still experiencing problems:

1. **Check the logs** - Look at the console output for specific error messages
2. **Verify Neon database** - Make sure your database is active and accessible
3. **Test network connectivity** - Ensure you can reach the Neon database from your machine
4. **Check firewall settings** - Make sure port 5000 is not blocked

## 🎉 Success!

Once the fix is complete, you should be able to:

- ✅ Upload meeting recordings without errors
- ✅ See "Connected" status in the frontend
- ✅ Access all API endpoints
- ✅ Use the full MeetingAI functionality

The "Database connection failed" error should be completely resolved!
