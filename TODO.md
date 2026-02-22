# Skill-Link - AI-Driven Campus Placement Platform

## Project Overview
- **Platform Name**: Skill-Link
- **AI Chatbot Name**: CareerBot
- **Team Name**: Team Arena
- **Team Members**: Soumy Chavhan, Rudra Gupta, Atharva Dongre, Ishan Ukey, Avyesh Bhiwapurkar

## Implementation Status - COMPLETED ✅

### Phase 1: Project Setup & Backend Foundation
- [x] Create project directory structure
- [x] Create Flask app with app.py
- [x] Set up SQLite database with all tables
- [x] Configure JWT authentication
- [x] Set up CORS and environment variables

### Phase 2: HR Module - Authentication & UI
- [x] HR Signup API (/api/hr/register)
- [x] HR Login API (/api/hr/login)
- [x] HR Signup UI (hr_signup.html)
- [x] HR Login UI (hr_login.html)
- [x] HR Dashboard (dashboard_hr.html)

### Phase 3: HR Module - Job Management
- [x] Create Job API (/api/jobs/create)
- [x] Get HR Jobs API (/api/hr/jobs/<hr_id>)
- [x] Post Job UI
- [x] Active Jobs UI with cards

### Phase 4: HR Module - Applicant Management
- [x] Get Applicants API (/api/jobs/applicants/<job_id>)
- [x] Shortlist Candidate API
- [x] Reject Candidate API
- [x] Applicants List UI
- [x] Shortlisted Candidates UI
- [x] Download Resume feature

### Phase 5: Student Module - Authentication & UI
- [x] Student Signup API (/api/students/register)
- [x] Student Login API (/api/students/login)
- [x] Student Signup UI (student_signup.html)
- [x] Student Login UI (student_login.html)
- [x] Student Dashboard (dashboard_student.html)

### Phase 6: Student Module - Resume System
- [x] Resume Upload API (/api/resume/upload)
- [x] Resume Upload UI with drag-drop
- [x] NLP Resume Parser (spaCy/regex)
- [x] Resume Score API & Algorithm
- [x] Skills Tag Input UI
- [x] Save Skills API

### Phase 7: Student Module - Job Features
- [x] Job Recommendation Engine
- [x] Recommended Jobs API (/api/jobs/recommended/<student_id>)
- [x] Recommended Jobs UI with cards
- [x] Apply Job API
- [x] Applied Jobs Status UI
- [x] Learning Path Suggestions

### Phase 8: AI & Analytics
- [x] AI Match Score Calculation
- [x] Duplicate Resume Detection
- [x] HR Analytics API
- [x] HR Analytics Dashboard
- [x] Skills Demand Analytics
- [x] Missing Skills Analyzer

### Phase 9: Advanced HR Features
- [x] Bulk Shortlist Top 10
- [x] AI Recommended Students (/api/hr/recommended/<job_id>)
- [x] Interview Round Status Tracker
- [x] Send Interview Email (Mock)
- [x] Job Expiry System
- [x] HR Notes on Candidates
- [x] Export Applicants CSV
- [x] Dark Mode Toggle

### Phase 10: Internship Module (NEW)
- [x] Internship Model with skills
- [x] Student Internships UI (student_internships.html)
- [x] Student Internship Applications UI (student_internship_applications.html)
- [x] HR Post Internship UI (hr_post_internship.html)
- [x] HR Internships List UI (hr_internships.html)
- [x] HR Internship Applicants UI (hr_internship_applicants.html)
- [x] Internship Application APIs

### Phase 11: Security & Deployment
- [x] Role-based JWT validation
- [x] CORS configuration
- [x] Environment variables setup
- [x] README.md with deployment steps
- [x] Demo data seeding

## Quick Start

### Run the Application
```
bash
cd c:/Users/soumy/Desktop/techalfaday2
pip install -r requirements.txt
python app.py
```

### Access the Platform
- URL: http://localhost:5000
- HR Login: hr@techcorp.com / password123
- Student Login: aryan.sharma@student.edu / password123

### Seed Demo Data
```
bash
flask seed-demo
```

## Key Features Implemented

### HR Features
- ✅ HR Authentication (Signup/Login)
- ✅ Job Posting with Skills
- ✅ Applicant Management
- ✅ AI Match Score
- ✅ Bulk Shortlist
- ✅ Interview Status Tracking
- ✅ Export to CSV
- ✅ Analytics Dashboard
- ✅ Skill Demand Analytics
- ✅ Dark Mode

### Student Features
- ✅ Student Authentication
- ✅ Profile Management
- ✅ Resume Upload & Parsing
- ✅ AI Resume Scoring
- ✅ Skills Management
- ✅ Job Recommendations
- ✅ Internship Listings
- ✅ Application Tracking
- ✅ Gap Analyzer
- ✅ Mock Tests

### AI Features
- ✅ CareerBot Chatbot
- ✅ Profile Summary Generation
- ✅ Eligibility Checker
- ✅ Progress Analyzer
- ✅ Skill Matching
- ✅ Learning Path Suggestions

## File Structure
```
skill-link/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── models.py                # SQLAlchemy models
├── demo_data.py            # Demo data seeder
├── test_api.py             # API test script
├── README.md               # Deployment guide
├── utils/
│   ├── auth.py             # JWT utilities
│   ├── resume_parser.py    # NLP resume parsing
│   ├── ai_engine.py        # AI matching logic
│   └── analytics.py        # Analytics functions
├── routes/
│   ├── hr_routes.py       # HR APIs
│   ├── student_routes.py   # Student APIs
│   ├── resume_routes.py    # Resume APIs
│   ├── feature_routes.py   # AI features
│   └── internship_routes.py # Internship APIs
├── static/
│   ├── css/
│   └── js/
└── templates/
    ├── index.html
    ├── student_login.html
    ├── student_signup.html
    ├── hr_login.html
    ├── hr_signup.html
    ├── dashboard_student.html
    ├── dashboard_hr.html
    ├── student_jobs.html
    ├── student_applications.html
    ├── student_resume.html
    ├── student_skills.html
    ├── student_internships.html
    ├── student_internship_applications.html
    ├── hr_post_internship.html
    ├── hr_internships.html
    ├── hr_internship_applicants.html
    └── ... (more templates)
