# Skill-Link - AI-Driven Campus Placement Platform

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Skill--Link-blue" alt="Skill-Link">
  <img src="https://img.shields.io/badge/AI-CareerBot-green" alt="CareerBot">
  <img src="https://img.shields.io/badge/Team-Arena-orange" alt="Team Arena">
</p>

## 🔗 About Skill-Link

**Skill-Link** is an AI-driven campus placement platform that connects talented students with top companies through intelligent matching. The platform features **CareerBot**, an AI-powered career assistant that helps students with job recommendations, resume analysis, and learning paths.

### Team Arena

- **Soumy Chavhan** - Team Lead
- **Rudra Gupta** - Backend Lead
- **Atharva Dongre** - AI Engineer
- **Ishan Ukey** - Frontend Lead
- **Avyesh Bhiwapurkar** - Database Engineer

---

## 🚀 Features

### For Students
- ✨ **AI Resume Parser** - Automatic extraction of skills, education, experience
- 📊 **Resume Scoring** - Get score out of 100 with improvement suggestions
- 🎯 **Job Recommendations** - AI-powered job matching based on skills
- 💡 **CareerBot** - AI assistant for career guidance
- 📚 **Learning Paths** - Personalized roadmaps for missing skills
- 📈 **Application Tracking** - Track application status (Applied → Shortlisted → Interview → Selected)

### For HR/Recruiters
- 📋 **Job Posting** - Create and manage job listings
- 👥 **Applicant Management** - View and manage all applicants
- 🤖 **AI Match Engine** - Automatically find best matching students
- 📊 **Analytics Dashboard** - Track hiring metrics and skill demands
- 📥 **Export CSV** - Download applicant data
- ✉️ **Interview Scheduling** - Send interview invitations

### AI Features
- 🧠 **Skill Matching Algorithm** - Calculates match percentage based on skills
- 🔍 **Duplicate Resume Detection** - Flags potential copy resumes
- 📈 **Skill Demand Analytics** - Shows trending skills in job market
- 👨‍🎓 **Auto-Recommend Students** - Suggests top candidates even if they haven't applied

---

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (development) / MySQL (production)
- **Frontend**: HTML, CSS, Bootstrap 5, Vanilla JavaScript
- **Authentication**: JWT (JSON Web Tokens)
- **AI/NLP**: Python (rule-based + regex parsing)
- **Deployment**: Render / Railway
- also used Openai's API key

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Local Setup

1. **Clone the repository**
```
bash
git clone <repository-url>
cd skill-link
```

2. **Create virtual environment**
```
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```
bash
pip install -r requirements.txt
```

4. **Run the application**
```
bash
python app.py
```

5. **Access the application**
- Open browser: http://localhost:5000

---

## 🚀 Deployment

### Option 1: Render.com (Recommended)

1. **Push code to GitHub**
```
bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo>
git push -u origin main
```

2. **Deploy on Render**
- Go to [Render Dashboard](https://dashboard.render.com)
- Create new **Web Service**
- Connect your GitHub repository
- Configure:
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `python app.py`
  - Environment: Python 3

3. **Set Environment Variables**
```
FLASK_CONFIG=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=your-database-url
```

### Option 2: Railway

1. **Install Railway CLI**
```
bash
npm install -g @railway/cli
```

2. **Login and create project**
```
bash
railway login
railway init
```

3. **Deploy**
```
bash
railway up
```

---

## 📁 Project Structure

```
skill-link/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── models.py                # Database models
├── README.md                # This file
│
├── routes/
│   ├── hr_routes.py         # HR APIs
│   ├── student_routes.py     # Student APIs
│   └── resume_routes.py     # Resume APIs
│
├── utils/
│   ├── auth.py              # JWT authentication
│   ├── resume_parser.py     # NLP resume parsing
│   ├── ai_engine.py         # AI matching logic
│   └── analytics.py         # Analytics functions
│
├── templates/
│   ├── index.html           # Landing page
│   ├── student_login.html   # Student login
│   ├── student_signup.html  # Student signup
│   ├── hr_login.html        # HR login
│   ├── hr_signup.html       # HR signup
│   ├── dashboard_student.html
│   └── dashboard_hr.html
│
└── static/
    └── uploads/
        └── resumes/          # Resume uploads
```

---

## 🔐 API Endpoints

### Student APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/students/register` | POST | Register new student |
| `/api/students/login` | POST | Student login |
| `/api/students/profile` | GET | Get student profile |
| `/api/students/skills` | POST | Add skills |
| `/api/students/dashboard` | GET | Get dashboard data |
| `/api/students/jobs/recommended` | GET | Get recommended jobs |
| `/api/students/jobs/apply/<id>` | POST | Apply for job |
| `/api/students/applications` | GET | Get applications |

### HR APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/hr/register` | POST | Register new HR |
| `/api/hr/login` | POST | HR login |
| `/api/hr/jobs` | POST | Create job |
| `/api/hr/jobs/<id>` | GET | Get HR jobs |
| `/api/hr/jobs/<id>/applicants` | GET | Get applicants |
| `/api/hr/applications/<id>/shortlist` | POST | Shortlist candidate |
| `/api/hr/applications/<id>/reject` | POST | Reject candidate |
| `/api/hr/analytics` | GET | Get analytics |

### Resume APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/resume/upload` | POST | Upload resume |
| `/api/resume/score` | GET | Get resume score |
| `/api/resume/download/<id>` | GET | Download resume |

---

## 🎨 UI Features

- **Dark Mode** - Professional dark theme toggle
- **Responsive Design** - Works on all devices
- **Drag & Drop** - Resume upload with drag & drop
- **Skill Tags** - Dynamic skill input with tags
- **Real-time Updates** - Instant application status

---

## 📝 License

This project is built by **Team Arena** for educational purposes.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<p align="center">Made with ❤️ by Team Arena</p>
<p align="center">Skill-Link - Connecting Talent with Opportunity</p>

