# AI-Powered Dynamic Meeting Assistant - Backend

A comprehensive Flask backend for an AI-powered meeting assistant that processes audio/video files, extracts insights, and manages tasks.

## Features

- **File Upload & Storage**: Support for audio/video files with Supabase (dev) and AWS S3 (prod)
- **Speech-to-Text**: Integration with RapidAPI and AssemblyAI for transcription
- **AI Analysis**: Gemini API integration for extracting decisions, action items, and unresolved questions
- **Task Management**: Complete CRUD operations for tasks with filtering and pagination
- **Notifications**: SendGrid email integration and Google Calendar sync
- **Database**: PostgreSQL with SQLAlchemy ORM

## Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL (Neon for dev, AWS RDS for prod)
- **Storage**: Supabase (dev) / AWS S3 (prod)
- **AI/NLP**: RapidAPI, Gemini API, AssemblyAI
- **Notifications**: SendGrid, Google Calendar API

## Quick Start

### 1. Install Dependencies

**Option A: Automatic Setup (Recommended)**
```bash
python setup.py
```

**Option B: Manual Installation**

For Windows:
```bash
pip install -r requirements-windows.txt
```

For Linux/Mac:
```bash
pip install -r requirements.txt
```

For Development (SQLite - no PostgreSQL required):
```bash
pip install -r requirements-dev.txt
```

### 2. Environment Setup

Copy the example environment file and configure your settings:

```bash
cp env.example .env
```

Edit `.env` with your API keys and configuration.

### 3. Database Setup

```bash
# Create database tables
python run.py
```

### 4. Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### File Upload
- `POST /api/upload` - Upload meeting audio/video
- `GET /api/upload/status/<meeting_id>` - Get upload status

### Transcription
- `POST /api/transcribe/<meeting_id>` - Transcribe meeting audio
- `GET /api/transcribe/<meeting_id>/status` - Get transcription status

### AI Analysis
- `POST /api/extract/<meeting_id>` - Extract insights from transcript
- `GET /api/extract/<meeting_id>/status` - Get extraction status

### Meetings
- `GET /api/meeting/<meeting_id>` - Get meeting details
- `GET /api/meetings/user/<user_id>` - Get user meetings
- `GET /api/meeting/<meeting_id>/timeline` - Get timeline data
- `PUT /api/meeting/<meeting_id>` - Update meeting
- `DELETE /api/meeting/<meeting_id>` - Delete meeting

### Tasks
- `GET /api/tasks/user/<user_id>` - Get user tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks/<task_id>` - Get specific task
- `PUT /api/tasks/<task_id>` - Update task
- `DELETE /api/tasks/<task_id>` - Delete task
- `POST /api/tasks/<task_id>/complete` - Complete task
- `GET /api/tasks/overdue/user/<user_id>` - Get overdue tasks
- `GET /api/tasks/upcoming/user/<user_id>` - Get upcoming tasks

### Notifications
- `POST /api/notify/task/<task_id>` - Send task notification
- `POST /api/notify/overdue/user/<user_id>` - Notify overdue tasks
- `POST /api/notify/upcoming/user/<user_id>` - Notify upcoming tasks
- `GET /api/notify/settings/user/<user_id>` - Get notification settings
- `PUT /api/notify/settings/user/<user_id>` - Update notification settings

## Database Schema

### Users Table
- `id` (String, Primary Key)
- `name` (String)
- `email` (String, Unique)
- `role` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Meetings Table
- `id` (String, Primary Key)
- `title` (String)
- `transcript` (Text)
- `file_path` (String)
- `file_name` (String)
- `file_size` (BigInteger)
- `duration` (Integer)
- `participants` (Integer)
- `status` (String)
- `user_id` (String, Foreign Key)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### Tasks Table
- `id` (String, Primary Key)
- `name` (String)
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

## Environment Variables

### Required
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini API key

### File Storage (Choose one)
**Development:**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_BUCKET` - Supabase storage bucket name

**Production:**
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_REGION` - AWS region
- `AWS_S3_BUCKET` - S3 bucket name

### AI/NLP Services
- `RAPIDAPI_KEY` - RapidAPI key for speech-to-text
- `RAPIDAPI_HOST` - RapidAPI host (default: speech-to-text-api1.p.rapidapi.com)
- `ASSEMBLYAI_API_KEY` - AssemblyAI API key (alternative to RapidAPI)
- `TRANSCRIPTION_SERVICE` - Service to use (rapidapi or assemblyai)

### Notifications
- `SENDGRID_API_KEY` - SendGrid API key for email
- `FROM_EMAIL` - Sender email address
- `GOOGLE_CREDENTIALS_FILE` - Path to Google service account key

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
```

### Database Migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Variables
Set all required environment variables in your production environment.

### Database
Use a managed PostgreSQL service like AWS RDS or Neon.

## API Usage Examples

### Upload a Meeting
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@meeting.mp3" \
  -F "title=Weekly Team Sync" \
  -F "user_id=user123"
```

### Transcribe Meeting
```bash
curl -X POST http://localhost:5000/api/transcribe/meeting123 \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

### Extract Insights
```bash
curl -X POST http://localhost:5000/api/extract/meeting123 \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

### Get Meeting Details
```bash
curl http://localhost:5000/api/meeting/meeting123
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a JSON object with error details:
```json
{
  "error": "Error message",
  "details": "Additional error details"
}
```

## License

This project is part of the AI Hackathon submission.
