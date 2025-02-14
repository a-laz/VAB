# VocalAnalysisBuddy

An AI-powered public speaking coach that provides real-time feedback and analysis to help users improve their presentation skills.

## Project Description

VocalAnalysisBuddy leverages AI to analyze public speaking performances by:
- Providing real-time voice interaction and feedback
- Analyzing speech patterns, tone, and pacing
- Comparing against exemplary speeches
- Tracking progress over time
- Offering personalized improvement suggestions

### Key Features
- Real-time speech analysis
- Vector similarity search for speech comparison
- Performance metrics tracking (WPM, filler words, clarity)
- Database of exemplary speeches
- Personalized feedback system

## Backend Setup

### Prerequisites
- Python 3.x
- PostgreSQL

### Database Setup
1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Start PostgreSQL server:
   - Windows: PostgreSQL server runs as a service automatically
   - macOS/Linux: `sudo service postgresql start`
3. Create database:
```sql
CREATE DATABASE speech_coach_db;
```

### Django Backend Setup
1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install django djangorestframework psycopg2-binary
```

3. Configure database:
   - Update database credentials in `speech_coach/settings.py`

4. Run migrations:
```bash
python manage.py migrate
```

5. Start Django server:
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### API Endpoints
- `GET/POST /api/speeches/` - List/Create user speeches
- `GET/PUT/DELETE /api/speeches/<id>/` - Manage specific speeches
- `GET /api/exemplary-speeches/` - List exemplary speeches

### Admin Interface
1. Admin credentials:
   - Username: vab
   - Password: Vvaabb123

2. Access the admin interface:
   - Go to `http://localhost:8000/admin`
   - Log in with the credentials above
   - Navigate to "Exemplary speeches" to add/edit speeches
   - Required fields:
     - Speaker name
     - Title
     - Audio file (mp3/wav format)
   - Optional fields:
     - Transcript
     - Date delivered
     - Occasion
     - Category

Note: These credentials are for development purposes only. Change them in production.

## Frontend Setup

[Frontend setup instructions to be added by Vlad]

```

This README provides essential information about the project and clear setup instructions for the backend. I've left space for frontend setup instructions to be added later.
