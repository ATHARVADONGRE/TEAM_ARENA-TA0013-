"""
OpenAI Routes for Skill-Link Platform
=====================================
OpenAI-powered features for campus placement

Team Arena: Soumy Chavhan, Rudra Gupta, Atharva Dongre, Ishan Ukey, Avyesh Bhiwapurkar
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Get OpenAI API key from environment
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

openai_bp = Blueprint('openai_features', __name__)

# ==================== AI Test Route ====================

@openai_bp.route('/test-ai', methods=['GET'])
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

# ==================== AI Student Profile Generator ====================

@openai_bp.route('/profile', methods=['POST'])
@jwt_required
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

# ==================== AI Eligibility Checker ====================

@openai_bp.route('/eligibility', methods=['POST'])
@jwt_required
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

# ==================== AI Progress Analyzer ====================

@openai_bp.route('/progress', methods=['POST'])
@jwt_required
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

# ==================== Health Check for AI ====================

@openai_bp.route('/status', methods=['GET'])
def ai_status():
    """Check AI service status"""
    return jsonify({
        'openai_available': OPENAI_AVAILABLE,
        'api_key_configured': bool(OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here"),
        'platform': 'Skill-Link',
        'team': 'Team Arena'
    }), 200

# Export the blueprint
ai_bp = openai_bp
