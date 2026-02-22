from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, HR, Job, JobSkill, Application, Student, Resume, HRNote, InterviewEmail
from utils.auth import hr_required, validate_email, validate_password
from utils.ai_engine import get_recommended_students, calculate_ai_match_score, bulk_shortlist_top_students
from utils.analytics import get_hr_analytics
from datetime import datetime
import csv
import io

hr_bp = Blueprint('hr', __name__)

# ==================== HR AUTH ====================

@hr_bp.route('/register', methods=['POST'])
def register():
    """Register a new HR account"""
    data = request.get_json()
    
    # Validate required fields
    required = ['company_name', 'hr_name', 'email', 'password']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate email
    if not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate password
    if not validate_password(data['password']):
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if email already exists
    if HR.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new HR
    hr = HR(
        company_name=data['company_name'],
        hr_name=data['hr_name'],
        email=data['email']
    )
    hr.set_password(data['password'])
    
    db.session.add(hr)
    db.session.commit()
    
    # Generate token
    access_token = create_access_token(
        identity=data['email'],
        additional_claims={'role': 'hr', 'user_id': hr.id}
    )
    
    return jsonify({
        'message': 'HR registered successfully',
        'hr': hr.to_dict(),
        'access_token': access_token
    }), 201

@hr_bp.route('/login', methods=['POST'])
def login():
    """Login HR account"""
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    # Find HR
    hr = HR.query.filter_by(email=data['email']).first()
    
    if not hr or not hr.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Generate token
    access_token = create_access_token(
        identity=data['email'],
        additional_claims={'role': 'hr', 'user_id': hr.id}
    )
    
    return jsonify({
        'message': 'Login successful',
        'hr': hr.to_dict(),
        'access_token': access_token
    })

# ==================== HR JOB MANAGEMENT ====================

@hr_bp.route('/jobs', methods=['POST'])
@hr_required
def create_job():
    """Create a new job posting"""
    data = request.get_json()
    
    # Validate required fields
    required = ['title', 'description', 'branch', 'min_cgpa']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Get HR ID from JWT
    claims = get_jwt()
    hr_id = claims.get('user_id')
    
    # Parse expiry date
    expiry_date = None
    if data.get('expiry_date'):
        try:
            expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
        except:
            expiry_date = None
    
    # Create job
    job = Job(
        hr_id=hr_id,
        title=data['title'],
        description=data['description'],
        min_cgpa=data['min_cgpa'],
        branch=data['branch'],
        expiry_date=expiry_date
    )
    
    # Set active based on expiry
    if expiry_date and expiry_date < datetime.utcnow():
        job.is_active = False
    
    db.session.add(job)
    db.session.commit()
    
    # Add skills
    skills = data.get('skills', [])
    for skill in skills:
        job_skill = JobSkill(job_id=job.id, skill_name=skill)
        db.session.add(job_skill)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Job created successfully',
        'job': job.to_dict(include_skills=True)
    }), 201

@hr_bp.route('/jobs/<int:hr_id>', methods=['GET'])
@hr_required
def get_hr_jobs(hr_id):
    """Get all jobs posted by HR"""
    # Verify HR owns these jobs
    claims = get_jwt()
    if claims.get('user_id') != hr_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    jobs = Job.query.filter_by(hr_id=hr_id).order_by(Job.created_at.desc()).all()
    
    return jsonify({
        'jobs': [job.to_dict(include_skills=True) for job in jobs]
    })

@hr_bp.route('/jobs/<int:job_id>', methods=['GET'])
@hr_required
def get_job_details(job_id):
    """Get details of a specific job"""
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'job': job.to_dict(include_skills=True)
    })

@hr_bp.route('/jobs/<int:job_id>', methods=['PUT'])
@hr_required
def update_job(job_id):
    """Update a job posting"""
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Update fields
    if data.get('title'):
        job.title = data['title']
    if data.get('description'):
        job.description = data['description']
    if data.get('min_cgpa'):
        job.min_cgpa = data['min_cgpa']
    if data.get('branch'):
        job.branch = data['branch']
    if data.get('is_active') is not None:
        job.is_active = data['is_active']
    if data.get('expiry_date'):
        try:
            job.expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
        except:
            pass
    
    # Update skills
    if data.get('skills'):
        # Remove old skills
        JobSkill.query.filter_by(job_id=job.id).delete()
        # Add new skills
        for skill in data['skills']:
            job_skill = JobSkill(job_id=job.id, skill_name=skill)
            db.session.add(job_skill)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Job updated successfully',
        'job': job.to_dict(include_skills=True)
    })

@hr_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@hr_required
def delete_job(job_id):
    """Delete a job posting"""
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(job)
    db.session.commit()
    
    return jsonify({'message': 'Job deleted successfully'})

# ==================== APPLICANTS MANAGEMENT ====================

@hr_bp.route('/jobs/<int:job_id>/applicants', methods=['GET'])
@hr_required
def get_applicants(job_id):
    """Get all applicants for a job"""
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    applications = Application.query.filter_by(job_id=job_id).all()
    
    # Get HR notes for these students
    hr_id = claims.get('user_id')
    
    result = []
    for app in applications:
        student = app.student
        resume = Resume.query.filter_by(student_id=student.id).first()
        
        # Get HR note
        hr_note = HRNote.query.filter_by(hr_id=hr_id, student_id=student.id).first()
        
        result.append({
            'application': app.to_dict(include_student=True),
            'resume_score': resume.score if resume else 0,
            'hr_note': hr_note.note if hr_note else None
        })
    
    return jsonify({
        'job': job.to_dict(include_skills=True),
        'applicants': result
    })

@hr_bp.route('/applications/<int:app_id>/shortlist', methods=['POST'])
@hr_required
def shortlist_candidate(app_id):
    """Shortlist a candidate"""
    application = Application.query.get(app_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Verify HR owns the job
    job = application.job
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    application.status = 'Shortlisted'
    db.session.commit()
    
    return jsonify({
        'message': 'Candidate shortlisted',
        'application': application.to_dict()
    })

@hr_bp.route('/applications/<int:app_id>/reject', methods=['POST'])
@hr_required
def reject_candidate(app_id):
    """Reject a candidate"""
    application = Application.query.get(app_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Verify HR owns the job
    job = application.job
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    application.status = 'Rejected'
    db.session.commit()
    
    return jsonify({
        'message': 'Candidate rejected',
        'application': application.to_dict()
    })

@hr_bp.route('/applications/<int:app_id>/interview', methods=['POST'])
@hr_required
def update_interview_status(app_id):
    """Update interview status"""
    application = Application.query.get(app_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Verify HR owns the job
    job = application.job
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_status = data.get('status', 'Interview')
    round_num = data.get('round', application.interview_round + 1)
    
    application.status = new_status
    application.interview_round = round_num
    db.session.commit()
    
    return jsonify({
        'message': 'Interview status updated',
        'application': application.to_dict()
    })

@hr_bp.route('/applications/<int:app_id>/note', methods=['POST'])
@hr_required
def add_hr_note(app_id):
    """Add HR note for a candidate"""
    application = Application.query.get(app_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Verify HR owns the job
    job = application.job
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    note_text = data.get('note', '')
    
    if not note_text:
        return jsonify({'error': 'Note text required'}), 400
    
    # Check if note exists
    hr_id = claims.get('user_id')
    hr_note = HRNote.query.filter_by(hr_id=hr_id, student_id=application.student_id).first()
    
    if hr_note:
        hr_note.note = note_text
    else:
        hr_note = HRNote(
            hr_id=hr_id,
            student_id=application.student_id,
            note=note_text
        )
        db.session.add(hr_note)
    
    db.session.commit()
    
    return jsonify({'message': 'Note added successfully'})

@hr_bp.route('/jobs/<int:job_id>/shortlist-bulk', methods=['POST'])
@hr_required
def bulk_shortlist(job_id):
    """Shortlist top N candidates"""
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    count = data.get('count', 10)
    
    shortlisted = bulk_shortlist_top_students(job_id, count)
    
    return jsonify({
        'message': f'{len(shortlisted)} candidates shortlisted',
        'shortlisted_count': len(shortlisted)
    })

@hr_bp.route('/jobs/<int:job_id>/recommended', methods=['GET'])
@hr_required
def get_ai_recommendations(job_id):
    """Get AI recommended students for a job"""
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    recommendations = get_recommended_students(job_id)
    
    return jsonify({
        'recommendations': recommendations
    })

@hr_bp.route('/send-interview', methods=['POST'])
@hr_required
def send_interview_email():
    """Simulate sending interview email"""
    data = request.get_json()
    
    app_id = data.get('application_id')
    message = data.get('message')
    
    if not app_id or not message:
        return jsonify({'error': 'application_id and message required'}), 400
    
    application = Application.query.get(app_id)
    
    if not application:
        return jsonify({'error': 'Application not found'}), 404
    
    # Verify HR owns the job
    job = application.job
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Create interview email record
    email = InterviewEmail(
        hr_id=claims.get('user_id'),
        application_id=app_id,
        message=message
    )
    
    # Update status
    application.status = 'Interview'
    application.interview_round = 1
    
    db.session.add(email)
    db.session.commit()
    
    return jsonify({
        'message': 'Interview email sent successfully',
        'email': email.to_dict()
    })

# ==================== ANALYTICS ====================

@hr_bp.route('/analytics', methods=['GET'])
@hr_required
def get_analytics():
    """Get HR analytics"""
    claims = get_jwt()
    hr_id = claims.get('user_id')
    
    analytics = get_hr_analytics(hr_id)
    
    return jsonify(analytics)

# ==================== EXPORT ====================

@hr_bp.route('/jobs/<int:job_id>/export', methods=['GET'])
@hr_required
def export_applicants(job_id):
    """Export applicants as CSV"""
    from utils.analytics import export_applicants_csv
    
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Verify ownership
    claims = get_jwt()
    if job.hr_id != claims.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    rows, job_title = export_applicants_csv(job_id)
    
    # Create CSV
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    csv_content = output.getvalue()
    
    return jsonify({
        'csv': csv_content,
        'filename': f'{job_title}_applicants.csv'
    })

@hr_bp.route('/profile', methods=['GET'])
@hr_required
def get_profile():
    """Get HR profile"""
    claims = get_jwt()
    hr_id = claims.get('user_id')
    
    hr = HR.query.get(hr_id)
    
    if not hr:
        return jsonify({'error': 'HR not found'}), 404
    
    return jsonify({'hr': hr.to_dict()})
