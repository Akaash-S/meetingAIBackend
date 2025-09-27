# Backend Prompt – AI-Powered Dynamic Meeting Assistant

**Objective:**  
Create a complete backend for an AI-powered Dynamic Meeting Assistant. The backend should be built with **Python Flask**, handle all AI/NLP integrations securely, manage database operations, and provide APIs for the frontend. All API keys (RapidAPI, Gemini API, Google Calendar, SendGrid) are handled by the backend; users do not input any keys.

---

## **Requirements**

### 1️⃣ API Endpoints
- **Upload Meeting Audio / Video**
  - Endpoint: `POST /upload`
  - Accepts audio/video file
  - Stores file in **Supabase (dev)** or **AWS S3 (prod)**
  - Returns a unique meeting ID
- **Transcription**
  - Endpoint: `POST /transcribe/:meetingId`
  - Uses **RapidAPI** for speech-to-text
  - Saves transcript in **PostgreSQL** (Neon for dev, AWS RDS for prod)
- **Task Extraction & Summarization**
  - Endpoint: `POST /extract/:meetingId`
  - Uses **Gemini API** to extract:
    - Decisions
    - Action Items (with owner & deadline)
    - Unresolved Questions
  - Stores structured tasks in DB
- **Dashboard / Timeline Data**
  - Endpoint: `GET /meeting/:meetingId`
  - Returns transcript, action items, decisions, unresolved questions
- **Task Management**
  - CRUD endpoints for tasks:
    - `GET /tasks/:userId`
    - `POST /tasks`
    - `PUT /tasks/:taskId`
    - `DELETE /tasks/:taskId`
- **Calendar & Notifications**
  - Endpoint: `POST /notify/:taskId`
  - Sends notifications via **SendGrid**
  - Syncs tasks with **Google Calendar** via API

---

### 2️⃣ Database Structure
- **Tables:**
  - `users` → id, name, email, role
  - `meetings` → id, title, transcript, created_at
  - `tasks` → id, meeting_id, name, owner, status, deadline, category
- Use **SQLAlchemy ORM** for database operations
- Ensure **relations**: meetings ↔ tasks, users ↔ tasks

---

### 3️⃣ Security & Environment
- Use **environment variables** for all API keys
- Secure file storage and access
- Proper error handling for external API calls
- Input validation for all endpoints

---

### 4️⃣ Orchestrator Logic
- Process flow:
  1. Upload meeting → store file
  2. Transcription → save transcript
  3. Task extraction → save structured tasks
  4. Serve data to frontend dashboard/timeline/tasks
  5. Trigger notifications and calendar sync

---

### 5️⃣ Tech Stack
- **Backend:** Python Flask
- **Database:** Neon PostgreSQL (dev) / AWS RDS (prod)
- **Storage:** Supabase (dev) / AWS S3 (prod)
- **AI/NLP:** RapidAPI (Speech-to-Text), Gemini API (Task Extraction)
- **Notifications & Calendar:** SendGrid, Google Calendar API

---

### 6️⃣ Output
- Fully functional Flask backend code with:
  - API routes
  - Database models
  - Integration with AI/NLP APIs
  - Task orchestration logic
  - Notification and calendar integration
- Ready to connect with React.js frontend
- Configured for dev and production environments