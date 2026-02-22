"""
Skill-Link - AI-Driven Campus Placement Platform
================================================
Team Arena: Soumy Chavhan, Rudra Gupta, Atharva Dongre, Ishan Ukey, Avyesh Bhiwapurkar
"""

from flask import Flask, jsonify, request, render_template, session
from flask_cors import CORS
from flask_jwt_extended import JWTManager
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
from routes.ai_routes import ai_bp

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
    app.register_blueprint(ai_bp, url_prefix='/api/openai')
    
    # Create upload directories
    upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'resumes')
    os.makedirs(upload_folder, exist_ok=True)
    
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
    
    # NEW: AI Gap Analyzer
    @app.route('/dashboard/student/gap-analyzer')
    def student_gap_analyzer():
        return render_template('student_gap_analyzer.html')
    
    # NEW: AI Mock Test
    @app.route('/dashboard/student/mock-test')
    def student_mock_test():
        return render_template('student_mock_test.html')
    
    # HR Dashboard
    @app.route('/dashboard/hr')
    def hr_dashboard():
        return render_template('dashboard_hr.html')
    
    # NEW: Skill Demand Analytics
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
