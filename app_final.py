"""
Skill-Link - AI-Driven Campus Placement Platform
================================================
Team Arena: Soumy Chavhan, Rudra Gupta, Atharva Dongre, Ishan Ukey, Avyesh Bhiwapurkar
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from config import config
from models import db, HR, Student, Job, JobSkill, Application, StudentSkill, Resume, SavedJob, Internship, BusinessJob, SkillTest, HRNote, InterviewEmail
from datetime import timedelta

# Import blueprints
from routes.hr_routes import hr_bp
from routes.student_routes import student_bp
from routes.resume_routes import resume_bp
from routes.feature_routes import feature_bp

# Get OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
try:
    from openai import OpenAI
    if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here":
        client = OpenAI(api_key=OPENAI_API_KEY)
        OPENAI_AVAILABLE = True
    else:
        client = None
        OPENAI_AVAILABLE = False
except ImportError:
    client = None
    OPENAI_AVAILABLE = False

def create_app(config_name=None):
    """Application Factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['development']))
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    jwt = JWTManager(app)
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = app.config.get('JWT_SECRET_KEY', 'skill-link-jwt-secret-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
    
    # Register blueprints
    app.register_blueprint(hr_bp, url_prefix='/api/hr')
    app.register_blueprint(student_bp, url_prefix='/api/students')
    app.register_blueprint(resume_bp, url_prefix='/api/resume')
    app.register_blueprint(feature_bp, url_prefix='/api/ai')
    
    # Create upload directories
    upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'resumes')
    os.makedirs(upload_folder, exist_ok=True)
    
    # ==================== OPENAI ROUTES ====================
    
    @app.route('/api/openai/status', methods=['GET'], endpoint='openai_status')
    def openai_status():
        """Check AI service status"""
        return jsonify({
            'openai_available': OPENAI_AVAILABLE,
            'api_key_configured': bool(OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here"),
            'platform': 'Skill-Link',
            'team': 'Team Arena'
        }), 200
    
    @app.route('/api/openai/test-ai', methods=['GET'], endpoint='test_ai')
    def test_ai():
        """Test if AI is working"""
        if not OPENAI_AVAILABLE or not client:
            return jsonify({
                'status': 'AI not configured',
                'message': 'Please set OPENAI_API_KEY in .env file',
                'ai_working': False
            }), 200
        
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'AI working' if you can understand this."}
                ],
                max_tokens=50
            )
            
            ai_response = response.choices[0].message.content
            
            return jsonify({
                'status': 'success',
                'message': ai_response,
                'ai_working': True
            }), 200
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e),
                'ai_working': False
            }), 500
    
    @app.route('/api/openai/profile', methods=['POST'], endpoint='generate_profile')
    @jwt_required()
    def generate_profile():
        """Generate professional profile summary from student data"""
        if not OPENAI_AVAILABLE or not client:
            return jsonify({
                'error': 'AI not configured',
                'message': 'Please set OPENAI_API_KEY in .env file'
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '')
        branch = data.get('branch', '')
        skills = data.get('skills', [])
        projects = data.get('projects', [])
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        try:
            skills_str = ', '.join(skills) if skills else 'Not specified'
            projects_str = ', '.join(projects) if projects else 'Not specified'
            
            prompt = f"""Generate a professional profile summary for a campus placement candidate.

Student Details:
- Name: {name}
- Branch: {branch}
- Skills: {skills_str}
- Projects: {projects_str}

Generate a compelling 2-3 sentence professional summary."""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a career counselor AI."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            
            profile_summary = response.choices[0].message.content
            
            return jsonify({
                'name': name,
                'branch': branch,
                'skills': skills,
                'projects': projects,
                'profile_summary': profile_summary
            }), 200
            
        except Exception as e:
            return jsonify({
                'error': 'Failed to generate profile',
                'message': str(e)
            }), 500
    
    @app.route('/api/openai/eligibility', methods=['POST'], endpoint='check_eligibility')
    @jwt_required()
    def check_eligibility():
        """Check if student is eligible for a job"""
        if not OPENAI_AVAILABLE or not client:
            return jsonify({
                'error': 'AI not configured',
                'message': 'Please set OPENAI_API_KEY in .env file'
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        student_skills = data.get('student_skills', [])
        cgpa = data.get('cgpa', 0.0)
        job_skills = data.get('job_skills', [])
        min_cgpa = data.get('min_cgpa', 0.0)
        
        if job_skills:
            skills_lower = [s.lower() for s in student_skills]
            matched = sum(1 for s in job_skills if s.lower() in skills_lower)
            match_percentage = (matched / len(job_skills)) * 100
        else:
            match_percentage = 0
        
        cgpa_eligible = cgpa >= min_cgpa
        skills_eligible = match_percentage >= 50
        
        if not cgpa_eligible:
            eligible = False
            reason = f"CGPA {cgpa} is below minimum requirement of {min_cgpa}"
        elif not skills_eligible:
            eligible = False
            reason = f"Skill match ({match_percentage:.1f}%) is below 50% threshold"
        else:
            eligible = True
            reason = f"CGPA meets requirement and skill match is {match_percentage:.1f}%"
        
        return jsonify({
            'eligible': eligible,
            'reason': reason,
            'match_percentage': round(match_percentage, 2),
            'cgpa_eligible': cgpa_eligible,
            'skills_eligible': skills_eligible
        }), 200
    
    @app.route('/api/openai/progress', methods=['POST'], endpoint='analyze_progress')
    @jwt_required()
    def analyze_progress():
        """Analyze student progress and provide improvement plan"""
        if not OPENAI_AVAILABLE or not client:
            return jsonify({
                'error': 'AI not configured',
                'message': 'Please set OPENAI_API_KEY in .env file'
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        skills = data.get('skills', [])
        resume_score = data.get('resume_score', 0)
        applied_jobs = data.get('applied_jobs', 0)
        shortlisted = data.get('shortlisted', 0)
        
        if resume_score >= 80 and shortlisted >= 3:
            readiness_level = "High"
        elif resume_score >= 60 and shortlisted >= 1:
            readiness_level = "Intermediate"
        elif resume_score >= 40:
            readiness_level = "Beginner"
        else:
            readiness_level = "Needs Improvement"
        
        important_skills = [
            "Python", "JavaScript", "React", "SQL", "Git",
            "Machine Learning", "Data Structures", "Problem Solving"
        ]
        
        skills_lower = [s.lower() for s in skills]
        missing_skills = [s for s in important_skills if s.lower() not in skills_lower]
        
        try:
            prompt = f"""Create a 2-week improvement plan for a campus placement candidate.

Current Status:
- Skills: {', '.join(skills) if skills else 'None'}
- Resume Score: {resume_score}/100
- Jobs Applied: {applied_jobs}
- Shortlisted: {shortlisted}
- Missing Skills: {', '.join(missing_skills[:5]) if missing_skills else 'None'}

Provide readiness level and a detailed improvement plan."""

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a career progress analyzer AI."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            
            improvement_plan = response.choices[0].message.content
            
        except Exception as e:
            improvement_plan = f"Focus on improving your resume score and learning {', '.join(missing_skills[:3]) if missing_skills else 'key skills'}."
        
        return jsonify({
            'readiness_level': readiness_level,
            'missing_skills': missing_skills[:5],
            'improvement_plan': improvement_plan,
            'current_stats': {
                'resume_score': resume_score,
                'applied_jobs': applied_jobs,
                'shortlisted': shortlisted
            }
        }), 200
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'platform': 'Skill-Link',
            'chatbot': 'CareerBot',
            'version': '1.0.0',
            'team': 'Team Arena'
        })
    
    # Platform info endpoint
    @app.route('/api/info', methods=['GET'])
    def platform_info():
        return jsonify({
            'name': 'Skill-Link',
            'chatbot': 'CareerBot',
            'team': 'Team Arena',
            'members': ['Soumy Chavhan', 'Rudra Gupta', 'Atharva Dongre', 'Ishan Ukey', 'Avyesh Bhiwapurkar']
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'code': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'code': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization required',
            'code': 'authorization_required'
        }), 401
    
    # ==================== HTML Routes ====================
    
    # Landing Pages
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Student Auth
    @app.route('/student/login')
    def student_login():
        return render_template('student_login.html')
    
    @app.route('/student/signup')
    def student_signup():
        return render_template('student_signup.html')
    
    # HR Auth
    @app.route('/hr/login')
    def hr_login():
        return render_template('hr_login.html')
    
    @app.route('/hr/signup')
    def hr_signup():
        return render_template('hr_signup.html')
    
    # Student Dashboard & Tabs
    @app.route('/dashboard/student')
    def student_dashboard():
        return render_template('dashboard_student.html')
    
    @app.route('/dashboard/student/jobs')
    def student_jobs():
        return render_template('student_jobs.html')
    
    @app.route('/dashboard/student/applications')
    def student_applications():
        return render_template('student_applications.html')
    
    @app.route('/dashboard/student/resume')
    def student_resume():
        return render_template('student_resume.html')
    
    @app.route('/dashboard/student/skills')
    def student_skills():
        return render_template('student_skills.html')
    
    # AI Gap Analyzer
    @app.route('/dashboard/student/gap-analyzer')
    def student_gap_analyzer():
        return render_template('student_gap_analyzer.html')
    
    # AI Mock Test
    @app.route('/dashboard/student/mock-test')
    def student_mock_test():
        return render_template('student_mock_test.html')
    
    # HR Dashboard
    @app.route('/dashboard/hr')
    def hr_dashboard():
        return render_template('dashboard_hr.html')
    
    # Skill Demand Analytics
    @app.route('/dashboard/hr/skill-demand')
    def hr_skill_demand():
        return render_template('hr_skill_demand.html')
    
    return app

# Create the application
app = create_app()

# Database initialization command
@app.cli.command('init-db')
def init_db_command():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully!")

# Seed demo data command
@app.cli.command('seed-demo')
def seed_demo_command():
    """Seed demo data"""
    from demo_data import seed_demo_data
    seed_demo_data()

# Run the application
if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        db.create_all()
        print("Database tables created!")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
