"""
Internship Routes - APIs for internship feature
Team Arena: Skill-Link Platform
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, HR, Student, Internship, InternshipSkill, InternshipApplication, StudentSkill, Resume
from utils.auth import hr_required, student_required
from datetime import datetime

internship_bp = Blueprint('internship', __name__)

# ==================== HR INTERNSHIP APIs ====================

@internship_bp.route('/create', methods=['POST'])
@hr_required
def create_internship():
    """Create a new internship posting"""
    data = request.get_json()
    
    # Validate required fields
    required = ['title', 'description', 'branch']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Get HR ID from JWT
    claims = get_jwt()
    hr_id = claims.get('user_id')
    
    # Get HR company name
    hr = HR.query.get(hr_id)
    company_name = data.get('company_name', hr.company_name if hr else '')
    
    # Parse expiry date
    expiry_date = None
    if data.get('expiry_date'):
        try:
            expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
        except:
            expiry_date = None
    
    # Create internship
    internship = Internship(
        hr_id=hr_id,
        title=data['title'],
        company=company_name,
        description=data['description'],
        internship_type=data.get('internship_type', 'Unpaid'),
        duration=data.get('duration', ''),
        stipend=data.get('stipend', ''),
        skills_required=data.get('skills_required', ''),
        branch=data['branch'],
        eligible_year=data.get('eligible_year'),
        expiry_date=expiry_date
    )
    
    # Set active based on expiry
    if expiry_date and expiry_date < datetime.utcnow():
        internship.is_active = False
    
    db.session.add(internship)
    db.session.commit()
    
    # Add skills
    skills = data.get('skills', [])
    for skill in skills:
        internship_skill = InternshipSkill(internship_id=internship.id, skill_name=skill)
        db.session.add(internship_skill)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Internship created successfully',
        'internship': internship.to_dict(include_skills=True)
    }), 201

@internship_bp.route('/hr/<int:hr_id>', methods=['GET'])
@hr_required
def get_hr_internships(hr_id):
    """Get all internships posted by HR"""
    # Verify HR owns these internships
    claims = get_jwt()
    if claims.get('user_id') != hr_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    internships = Internship.query.filter_by(hr_id=hr_id).order_by(Internship.created_at.desc()).all()
    
    return jsonify({
        'internships': [internship.to_dict(include_skills=True) for internship in internships]
    })

@internship_bp.route('/<int:internship_id>', methods=['GET'])
def get_internship(internship_id):
    """Get internship details"""
    internship = Internship.query.get(internship_id)
    
    if not internship:
        return jsonify({'error': 'Internship not found'}), 404
    
    return jsonify({
        'internship': internship.to_dict(include_skills=True)
    })

@internship_bp.route('/<int:internship_id>', methods=['PUT'])
@hr_required
def update_internship(internship_id):
    """Update internship posting"""
    internship = Internship.query.get(internship_id)
    
    if not internship:
        return jsonify({'error': 'Internship not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if internship.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if data.get('title'):
        internship.title = data['title']
    if data.get('description'):
        internship.description = data['description']
    if data.get('internship_type'):
        internship.internship_type = data['internship_type']
    if data.get('duration'):
        internship.duration = data['duration']
    if data.get('stipend'):
        internship.stipend = data['stipend']
    if data.get('branch'):
        internship.branch = data['branch']
    if data.get('eligible_year'):
        internship.eligible_year = data['eligible_year']
    if data.get('is_active') is not None:
        internship.is_active = data['is_active']
    if data.get('expiry_date'):
        try:
            internship.expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
        except:
            pass
    
    # Update skills
    if data.get('skills'):
        # Remove old skills
        InternshipSkill.query.filter_by(internship_id=internship.id).delete()
        # Add new skills
        for skill in data['skills']:
            internship_skill = InternshipSkill(internship_id=internship.id, skill_name=skill)
            db.session.add(internship_skill)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Internship updated successfully',
        'internship': internship.to_dict(include_skills=True)
    })

@internship_bp.route('/<int:internship_id>', methods=['DELETE'])
@hr_required
def delete_internship(internship_id):
    """Delete internship posting"""
    internship = Internship.query.get(internship_id)
    
    if not internship:
        return jsonify({'error': 'Internship not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if internship.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(internship)
    db.session.commit()
    
    return jsonify({'message': 'Internship deleted successfully'})

# ==================== HR APPLICANT MANAGEMENT ====================

@internship_bp.route('/<int:internship_id>/applicants', methods=['GET'])
@hr_required
def get_internship_applicants(internship_id):
    """Get all applicants for an internship"""
    internship = Internship.query.get(internship_id)
    
    if not internship:
        return jsonify({'error': 'Internship not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if internship.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    applications = InternshipApplication.query.filter_by(internship_id=internship_id).all()
    
    result = []
    for app in applications:
        student = app.student
        resume = Resume.query.filter_by(student_id=student.id).first()
        
        result.append({
            'application': app.to_dict(include_student=True),
            'resume_score': resume.score if resume else 0
        })
    
    return jsonify({
        'internship': internship.to_dict(include_skills=True),
        'applicants': result
    })

@internship_bp.route('/applications/<int:app_id>/shortlist', methods=['POST'])
@hr_required
def shortlist_internship_candidate(app_id):
    """Shortlist an internship candidate"""
    application = InternshipApplication.query.get(app_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Verify HR owns the internship
    internship = application.internship
    claims = get_jwt()
    if internship.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    application.status = 'Shortlisted'
    db.session.commit()
    
    return jsonify({
        'message': 'Candidate shortlisted',
        'application': application.to_dict()
    })

@internship_bp.route('/applications/<int:app_id>/reject', methods=['POST'])
@hr_required
def reject_internship_candidate(app_id):
    """Reject an internship candidate"""
    application = InternshipApplication.query.get(app_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Verify HR owns the internship
    internship = application.internship
    claims = get_jwt()
    if internship.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    application.status = 'Rejected'
    db.session.commit()
    
    return jsonify({
        'message': 'Candidate rejected',
        'application': application.to_dict()
    })

# ==================== STUDENT INTERNSHIP APIs ====================

@internship_bp.route('/list', methods=['GET'])
def get_all_internships():
    """Get all active internships"""
    internships = Internship.query.filter_by(is_active=True).order_by(Internship.created_at.desc()).all()
    
    return jsonify({
        'internships': [internship.to_dict(include_skills=True) for internship in internships]
    })

@internship_bp.route('/recommended', methods=['GET'])
@student_required
def get_recommended_internships():
    """Get recommended internships for student based on skills"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get student's skills
    student_skills = [skill.skill_name for skill in student.skills]
    
    # Get active internships
    internships = Internship.query.filter_by(is_active=True).all()
    
    recommendations = []
    for internship in internships:
        # Get internship skills
        internship_skills = [skill.skill_name for skill in internship.skills]
        
        # Calculate match percentage
        if internship_skills:
            skills_lower = [s.lower() for s in student_skills]
            matched = sum(1 for s in internship_skills if s.lower() in skills_lower)
            match_percentage = (matched / len(internship_skills)) * 100
        else:
            match_percentage = 0
        
        # Check if already applied
        existing_app = InternshipApplication.query.filter_by(
            student_id=student_id,
            internship_id=internship.id
        ).first()
        
        recommendations.append({
            'internship': internship.to_dict(include_skills=True),
            'match_percentage': round(match_percentage, 2),
            'has_applied': existing_app is not None,
            'application_status': existing_app.status if existing_app else None
        })
    
    # Sort by match percentage
    recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return jsonify({
        'internships': recommendations
    })

@internship_bp.route('/apply/<int:internship_id>', methods=['POST'])
@student_required
def apply_internship(internship_id):
    """Apply for an internship"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    # Check if internship exists
    internship = Internship.query.get(internship_id)
    if not internship:
        return jsonify({'error': 'Internship not found'}), 404
    
    # Check if internship is active
    if not internship.is_active:
        return jsonify({'error': 'Internship is no longer accepting applications'}), 400
    
    # Check if already applied
    existing = InternshipApplication.query.filter_by(
        student_id=student_id,
        internship_id=internship_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Already applied for this internship'}), 400
    
    # Get student
    student = Student.query.get(student_id)
    
    # Get internship skills
    internship_skills = [skill.skill_name for skill in internship.skills]
    student_skills = [skill.skill_name for skill in student.skills]
    
    # Calculate match percentage
    if internship_skills:
        skills_lower = [s.lower() for s in student_skills]
        matched = sum(1 for s in internship_skills if s.lower() in skills_lower)
        match_percentage = (matched / len(internship_skills)) * 100
    else:
        match_percentage = 0
    
    # Create application
    application = InternshipApplication(
        student_id=student_id,
        internship_id=internship_id,
        status='Applied',
        match_percentage=match_percentage
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({
        'message': 'Applied for internship successfully',
        'application': application.to_dict()
    }), 201

@internship_bp.route('/my-applications', methods=['GET'])
@student_required
def get_my_applications():
    """Get student's internship applications"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    applications = InternshipApplication.query.filter_by(student_id=student_id).all()
    
    result = []
    for app in applications:
        internship = app.internship
        result.append({
            'application': app.to_dict(),
            'internship': internship.to_dict(include_skills=True)
        })
    
    return jsonify({
        'applications': result
    })

@internship_bp.route('/<int:internship_id>/status', methods=['GET'])
@student_required
def check_application_status(internship_id):
    """Check if student has applied for an internship"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    application = InternshipApplication.query.filter_by(
        student_id=student_id,
        internship_id=internship_id
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

@internship_bp.route('/skill-gap/<int:internship_id>', methods=['GET'])
@student_required
def get_skill_gap(internship_id):
    """Get missing skills for an internship"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    internship = Internship.query.get(internship_id)
    if not internship:
        return jsonify({'error': 'Internship not found'}), 404
    
    student = Student.query.get(student_id)
    student_skills = [skill.skill_name for skill in student.skills]
    internship_skills = [skill.skill_name for skill in internship.skills]
    
    # Find missing skills
    student_skills_lower = [s.lower() for s in student_skills]
    missing_skills = []
    
    for skill in internship_skills:
        if skill.lower() not in student_skills_lower:
            missing_skills.append(skill)
    
    # Get learning paths for missing skills
    from utils.ai_engine import get_learning_paths_for_missing_skills
    learning_paths = get_learning_paths_for_missing_skills(missing_skills)
    
    return jsonify({
        'internship': internship.to_dict(include_skills=True),
        'student_skills': student_skills,
        'required_skills': internship_skills,
        'missing_skills': missing_skills,
        'learning_paths': learning_paths
    })
