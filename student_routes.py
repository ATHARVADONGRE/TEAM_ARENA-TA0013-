from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, Student, StudentSkill, Resume, Application, Job, JobSkill, SavedJob, Internship, BusinessJob, SkillTest, SKILL_DEMAND
from utils.auth import student_required, validate_email, validate_password
from utils.ai_engine import get_recommended_jobs, get_missing_skills, get_learning_paths_for_missing_skills
from utils.analytics import get_student_analytics
import os
import random

student_bp = Blueprint('student', __name__)

# ==================== STUDENT AUTH ====================

@student_bp.route('/register', methods=['POST'])
def register():
    """Register a new student"""
    data = request.get_json()
    
    # Validate required fields
    required = ['name', 'email', 'password', 'branch', 'grad_year']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate email
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password
    if not validate_password(data['password']):
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Validate grad year
    try:
        grad_year = int(data['grad_year'])
        if grad_year < 2020 or grad_year > 2030:
            return jsonify({'error': 'Invalid graduation year'}), 400
    except:
        return jsonify({'error': 'Invalid graduation year'}), 400
    
    # Check if email already exists
    if Student.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new student
    student = Student(
        name=data['name'],
        email=data['email'],
        branch=data['branch'],
        grad_year=grad_year,
        cgpa=data.get('cgpa', 0.0)
    )
    student.set_password(data['password'])
    
    db.session.add(student)
    db.session.commit()
    
    # Generate token
    access_token = create_access_token(
        identity=data['email'],
        additional_claims={'role': 'student', 'user_id': student.id}
    )
    
    return jsonify({
        'message': 'Student registered successfully',
        'student': student.to_dict(),
        'access_token': access_token
    }), 201

@student_bp.route('/login', methods=['POST'])
def login():
    """Login student"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    # Find student
    student = Student.query.filter_by(email=data['email']).first()
    
    if not student or not student.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate token
    access_token = create_access_token(
        identity=data['email'],
        additional_claims={'role': 'student', 'user_id': student.id}
    )
    
    return jsonify({
        'message': 'Login successful',
        'student': student.to_dict(include_skills=True),
        'access_token': access_token
    })

# ==================== STUDENT PROFILE ====================

@student_bp.route('/profile', methods=['GET'])
@student_required
def get_profile():
    """Get student profile"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({
        'student': student.to_dict(include_skills=True)
    })

@student_bp.route('/profile', methods=['PUT'])
@student_required
def update_profile():
    """Update student profile"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if data.get('name'):
        student.name = data['name']
    if data.get('cgpa'):
        student.cgpa = data['cgpa']
    if data.get('branch'):
        student.branch = data['branch']
    if data.get('grad_year'):
        student.grad_year = data['grad_year']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'student': student.to_dict(include_skills=True)
    })

# ==================== STUDENT SKILLS ====================

@student_bp.route('/skills', methods=['POST'])
@student_required
def add_skills():
    """Add skills for student"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    data = request.get_json()
    skills = data.get('skills', [])
    
    if not skills:
        return jsonify({'error': 'No skills provided'}), 400
    
    # Remove existing skills
    StudentSkill.query.filter_by(student_id=student_id).delete()
    
    # Add new skills
    added_skills = []
    for skill in skills:
        skill = skill.strip().title()
        if skill:
            # Check if already exists
            existing = StudentSkill.query.filter_by(
                student_id=student_id, 
                skill_name=skill
            ).first()
            
            if not existing:
                student_skill = StudentSkill(
                    student_id=student_id,
                    skill_name=skill
                )
                db.session.add(student_skill)
                added_skills.append(skill)
    
    db.session.commit()
    
    return jsonify({
        'message': f'{len(added_skills)} skills added',
        'skills': added_skills
    })

@student_bp.route('/skills', methods=['GET'])
@student_required
def get_skills():
    """Get student skills"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    skills = StudentSkill.query.filter_by(student_id=student_id).all()
    
    return jsonify({
        'skills': [s.skill_name for s in skills]
    })

# ==================== PROFILE STRENGTH ====================

@student_bp.route('/profile-strength', methods=['GET'])
@student_required
def get_profile_strength():
    """Calculate profile strength percentage"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    student = Student.query.get(student_id)
    resume = Resume.query.filter_by(student_id=student_id).first()
    skills = StudentSkill.query.filter_by(student_id=student_id).all()
    
    # Calculate strength components
    score = 0
    max_score = 100
    
    # Basic info (20%)
    if student.name: score += 5
    if student.email: score += 5
    if student.branch: score += 5
    if student.grad_year: score += 5
    
    # Skills (25%)
    skill_count = len(skills)
    if skill_count >= 10: score += 25
    elif skill_count >= 5: score += 15
    elif skill_count >= 1: score += 5
    
    # Resume (30%)
    if resume:
        score += 15  # Has resume
        if resume.score >= 80: score += 15
        elif resume.score >= 50: score += 10
        else: score += 5
        
        # Resume completeness
        if resume.education and resume.education != 'Not found': score += 5
        if resume.experience and resume.experience != 'Fresher': score += 5
    
    # Applications (25%)
    apps = Application.query.filter_by(student_id=student_id).count()
    if apps >= 5: score += 25
    elif apps >= 3: score += 15
    elif apps >= 1: score += 5
    
    # CGPA bonus
    if student.cgpa >= 8: score += 5
    elif student.cgpa >= 6: score += 3
    
    strength = min(score, 100)
    
    return jsonify({
        'profile_strength': strength,
        'components': {
            'basic_info': min(20, 5 if student.name else 0 + 5 if student.email else 0 + 5 if student.branch else 0 + 5 if student.grad_year else 0),
            'skills': min(25, skill_count * 3),
            'resume': 30 if resume else 0,
            'applications': min(25, apps * 5),
            'cgpa': 5 if student.cgpa >= 8 else 3 if student.cgpa >= 6 else 0
        }
    })

# ==================== SKILL GAP ANALYZER ====================

@student_bp.route('/skill-gap/<int:job_id>', methods=['GET'])
@student_required
def analyze_skill_gap(job_id):
    """Compare student skills vs job required skills"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Get student skills
    student_skills = [s.skill_name for s in StudentSkill.query.filter_by(student_id=student_id).all()]
    
    # Get job skills
    job_skills = [s.skill_name for s in JobSkill.query.filter_by(job_id=job_id).all()]
    
    # Find missing skills
    missing_skills = []
    matched_skills = []
    
    for skill in job_skills:
        if skill in student_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)
    
    # Get learning paths for missing skills
    learning_paths = get_learning_paths_for_missing_skills(missing_skills[:5])
    
    # Calculate match percentage
    match_pct = (len(matched_skills) / len(job_skills) * 100) if job_skills else 0
    
    return jsonify({
        'job_title': job.title,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'match_percentage': round(match_pct, 2),
        'learning_paths': learning_paths
    })

# ==================== DEMAND SKILLS ====================

@student_bp.route('/skill-demand', methods=['GET'])
@student_required
def get_skill_demand():
    """Get high and low demand skills"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    # Get student's skills
    student_skills = [s.skill_name for s in StudentSkill.query.filter_by(student_id=student_id).all()]
    
    high_demand = []
    low_demand = []
    neutral = []
    
    for skill in student_skills:
        if skill in SKILL_DEMAND['high_demand']:
            high_demand.append(skill)
        elif skill in SKILL_DEMAND['low_demand']:
            low_demand.append(skill)
        else:
            neutral.append(skill)
    
    return jsonify({
        'high_demand_skills': high_demand,
        'low_demand_skills': low_demand,
        'neutral_skills': neutral,
        'all_high_demand': SKILL_DEMAND['high_demand'][:10],
        'all_low_demand': SKILL_DEMAND['low_demand'][:5]
    })

# ==================== ROLE SUGGESTIONS ====================

@student_bp.route('/role-suggestions', methods=['GET'])
@student_required
def get_role_suggestions():
    """Suggest roles based on student skills"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    # Get student skills
    student_skills = [s.skill_name.lower() for s in StudentSkill.query.filter_by(student_id=student_id).all()]
    
    # Role definitions
    roles = {
        'Frontend Developer': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'bootstrap'],
        'Backend Developer': ['python', 'java', 'node.js', 'django', 'flask', 'express', 'sql'],
        'Full Stack Developer': ['javascript', 'react', 'node.js', 'python', 'sql', 'mongodb'],
        'Data Analyst': ['python', 'sql', 'excel', 'tableau', 'data analysis'],
        'Machine Learning Engineer': ['python', 'machine learning', 'tensorflow', 'deep learning', 'data science'],
        'DevOps Engineer': ['aws', 'docker', 'kubernetes', 'jenkins', 'git', 'linux'],
        'Mobile Developer': ['flutter', 'kotlin', 'swift', 'react native'],
        'Cloud Engineer': ['aws', 'azure', 'gcp', 'docker', 'kubernetes']
    }
    
    suggestions = []
    for role, required_skills in roles.items():
        matched = sum(1 for s in required_skills if s in student_skills)
        match_pct = (matched / len(required_skills)) * 100
        if match_pct >= 20:  # At least 20% match
            suggestions.append({
                'role': role,
                'match_percentage': round(match_pct, 2),
                'skills_gap': [s for s in required_skills if s not in student_skills]
            })
    
    # Sort by match percentage
    suggestions.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return jsonify({
        'role_suggestions': suggestions[:5]
    })

# ==================== SAVED JOBS ====================

@student_bp.route('/saved-jobs', methods=['GET'])
@student_required
def get_saved_jobs():
    """Get student's saved/bookmarked jobs"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    saved = SavedJob.query.filter_by(student_id=student_id).all()
    
    jobs = []
    for s in saved:
        job = Job.query.get(s.job_id)
        if job:
            jobs.append(job.to_dict(include_skills=True))
    
    return jsonify({'saved_jobs': jobs})

@student_bp.route('/saved-jobs/<int:job_id>', methods=['POST'])
@student_required
def save_job(job_id):
    """Save a job for later"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Check if already saved
    existing = SavedJob.query.filter_by(student_id=student_id, job_id=job_id).first()
    if existing:
        return jsonify({'error': 'Job already saved'}), 400
    
    saved = SavedJob(student_id=student_id, job_id=job_id)
    db.session.add(saved)
    db.session.commit()
    
    return jsonify({'message': 'Job saved successfully'})

@student_bp.route('/saved-jobs/<int:job_id>', methods=['DELETE'])
@student_required
def unsave_job(job_id):
    """Remove saved job"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    saved = SavedJob.query.filter_by(student_id=student_id, job_id=job_id).first()
    if not saved:
        return jsonify({'error': 'Job not saved'}), 404
    
    db.session.delete(saved)
    db.session.commit()
    
    return jsonify({'message': 'Job removed from saved'})

# ==================== INTERNSHIPS ====================

@student_bp.route('/internships', methods=['GET'])
@student_required
def get_internships():
    """Get all available internships"""
    internships = Internship.query.filter_by(is_active=True).all()
    
    return jsonify({
        'internships': [i.to_dict() for i in internships]
    })

@student_bp.route('/internships/<int:internship_id>', methods=['GET'])
@student_required
def get_internship_details(internship_id):
    """Get internship details"""
    internship = Internship.query.get(internship_id)
    if not internship:
        return jsonify({'error': 'Internship not found'}), 404
    
    return jsonify({'internship': internship.to_dict()})

# ==================== BUSINESS JOBS ====================

@student_bp.route('/business-jobs', methods=['GET'])
@student_required
def get_business_jobs():
    """Get all business/non-tech jobs"""
    jobs = BusinessJob.query.filter_by(is_active=True).all()
    
    return jsonify({
        'business_jobs': [j.to_dict() for j in jobs]
    })

@student_bp.route('/business-jobs/<int:job_id>', methods=['GET'])
@student_required
def get_business_job_details(job_id):
    """Get business job details"""
    job = BusinessJob.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({'job': job.to_dict()})

# ==================== SKILL TESTS ====================

@student_bp.route('/skill-tests', methods=['GET'])
@student_required
def get_available_tests():
    """Get available skill tests"""
    skills = db.session.query(SkillTest.skill_name).distinct().all()
    
    return jsonify({
        'available_skills': [s[0] for s in skills]
    })

@student_bp.route('/skill-tests/<skill_name>', methods=['GET'])
@student_required
def get_skill_test(skill_name):
    """Get MCQ test for a specific skill"""
    questions = SkillTest.query.filter_by(skill_name=skill_name).limit(5).all()
    
    if not questions:
        return jsonify({'error': 'No questions available for this skill'}), 404
    
    # Return questions without correct answers (for test)
    return jsonify({
        'skill': skill_name,
        'questions': [{
            'id': q.id,
            'question': q.question,
            'option_a': q.option_a,
            'option_b': q.option_b,
            'option_c': q.option_c,
            'option_d': q.option_d,
            'difficulty': q.difficulty
        } for q in questions]
    })

@student_bp.route('/skill-tests/submit', methods=['POST'])
@student_required
def submit_skill_test():
    """Submit skill test answers"""
    data = request.get_json()
    answers = data.get('answers', [])  # List of {question_id, answer}
    
    correct = 0
    total = len(answers)
    
    for ans in answers:
        question = SkillTest.query.get(ans.get('question_id'))
        if question and question.correct_answer.upper() == ans.get('answer', '').upper():
            correct += 1
    
    score = (correct / total * 100) if total > 0 else 0
    
    return jsonify({
        'score': round(score, 2),
        'correct': correct,
        'total': total,
        'message': f'You scored {correct} out of {total}'
    })

# ==================== STUDENT DASHBOARD ====================

@student_bp.route('/dashboard', methods=['GET'])
@student_required
def get_dashboard():
    """Get student dashboard data"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    analytics = get_student_analytics(student_id)
    
    if not analytics:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get recommended jobs
    recommended = get_recommended_jobs(student_id, limit=5)
    
    # Get saved jobs count
    saved_count = SavedJob.query.filter_by(student_id=student_id).count()
    
    # Get applied jobs
    applications = Application.query.filter_by(student_id=student_id).all()
    
    applied_jobs = []
    for app in applications:
        job = app.job
        applied_jobs.append({
            'application': app.to_dict(),
            'job': job.to_dict()
        })
    
    # Get internships
    internships = Internship.query.filter_by(is_active=True).limit(3).all()
    
    # Get business jobs
    business_jobs = BusinessJob.query.filter_by(is_active=True).limit(3).all()
    
    return jsonify({
        'profile': analytics['profile'],
        'resume_score': analytics['resume_score'],
        'total_applications': analytics['total_applications'],
        'applied': analytics['applied'],
        'shortlisted': analytics['shortlisted'],
        'rejected': analytics['rejected'],
        'interview': analytics['interview'],
        'selected': analytics['selected'],
        'saved_jobs_count': saved_count,
        'recommended_jobs': recommended,
        'applied_jobs': applied_jobs,
        'internships': [i.to_dict() for i in internships],
        'business_jobs': [b.to_dict() for b in business_jobs]
    })

# ==================== JOB APPLICATIONS ====================

@student_bp.route('/jobs/recommended', methods=['GET'])
@student_required
def get_recommended():
    """Get recommended jobs for student"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    recommended = get_recommended_jobs(student_id)
    
    return jsonify({
        'jobs': recommended
    })

@student_bp.route('/jobs/apply/<int:job_id>', methods=['POST'])
@student_required
def apply_job(job_id):
    """Apply for a job"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    # Check if job exists
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Check if job is active
    if not job.is_active:
        return jsonify({'error': 'Job is no longer accepting applications'}), 400
    
    # Check if already applied
    existing = Application.query.filter_by(
        student_id=student_id,
        job_id=job_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Already applied for this job'}), 400
    
    # Get student
    student = Student.query.get(student_id)
    
    # Get job skills
    job_skills = [skill.skill_name for skill in job.skills]
    student_skills = [skill.skill_name for skill in student.skills]
    
    # Calculate match percentage
    from utils.ai_engine import calculate_skill_match
    match_percentage, _, _ = calculate_skill_match(student_skills, job_skills)
    
    # Create application
    application = Application(
        student_id=student_id,
        job_id=job_id,
        status='Applied',
        match_percentage=match_percentage
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({
        'message': 'Job applied successfully',
        'application': application.to_dict()
    }), 201

@student_bp.route('/applications', methods=['GET'])
@student_required
def get_applications():
    """Get student's job applications"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    applications = Application.query.filter_by(student_id=student_id).all()
    
    result = []
    for app in applications:
        job = app.job
        result.append({
            'application': app.to_dict(),
            'job': job.to_dict(include_skills=True)
        })
    
    return jsonify({
        'applications': result
    })

@student_bp.route('/applications/<int:app_id>', methods=['GET'])
@student_required
def get_application_details(app_id):
    """Get details of a specific application"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    application = Application.query.get(app_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    if application.student_id != student_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    job = application.job
    
    # Get missing skills for this job
    student = Student.query.get(student_id)
    student_skills = [s.skill_name for s in student.skills]
    job_skills = [s.skill_name for s in job.skills]
    missing_skills = get_missing_skills(student_skills, job_skills)
    
    # Get learning paths
    learning_paths = get_learning_paths_for_missing_skills(missing_skills[:3])
    
    return jsonify({
        'application': application.to_dict(),
        'job': job.to_dict(include_skills=True),
        'missing_skills': missing_skills,
        'learning_paths': learning_paths
    })

# ==================== CHECK APPLICATION STATUS ====================

@student_bp.route('/jobs/<int:job_id>/status', methods=['GET'])
@student_required
def check_application_status(job_id):
    """Check if student has applied for a job"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    application = Application.query.filter_by(
        student_id=student_id,
        job_id=job_id
    ).first()
    
    if application:
        return jsonify({
            'has_applied': True,
            'status': application.status,
            'application': application.to_dict()
        })
    
    return jsonify({
        'has_applied': False
    })
