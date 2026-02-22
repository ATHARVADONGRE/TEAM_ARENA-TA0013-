from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Resume, Student
from utils.auth import student_required, hr_required
from utils.resume_parser import parse_resume, calculate_resume_score, extract_text_from_file
from utils.ai_engine import detect_duplicate_resume
from werkzeug.utils import secure_filename
import os
import uuid
import json

resume_bp = Blueprint('resume', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== RESUME UPLOAD ====================

@resume_bp.route('/upload', methods=['POST'])
@student_required
def upload_resume():
    """Upload and parse student resume"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: PDF, DOCX, DOC'}), 400
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{student_id}_{uuid.uuid4().hex}.{ext}"
    
    # Create upload folder if not exists
    upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads', 'resumes')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # Extract text from file
    extracted_text = extract_text_from_file(file_path)
    
    # Parse resume
    parsed_data = parse_resume(extracted_text)
    
    # Check for duplicates
    duplicates = detect_duplicate_resume(extracted_text, student_id)
    
    # Calculate resume score
    # Get job requirements if provided
    job_requirements = request.form.get('job_requirements')
    job_req_list = []
    if job_requirements:
        try:
            job_req_list = json.loads(job_requirements)
        except:
            pass
    
    score, suggestions = calculate_resume_score(parsed_data, job_req_list if job_req_list else None)
    
    # Check if resume already exists for this student
    existing_resume = Resume.query.filter_by(student_id=student_id).first()
    
    if existing_resume:
        # Update existing resume
        existing_resume.filename = unique_filename
        existing_resume.file_path = file_path
        existing_resume.score = score
        existing_resume.skills = json.dumps(parsed_data['skills'])
        existing_resume.education = parsed_data['education']
        existing_resume.experience = parsed_data['experience']
        existing_resume.is_duplicate = len(duplicates) > 0
        
        if duplicates:
            existing_resume.duplicate_of = duplicates[0].get('student_id')
        
        db.session.commit()
        resume = existing_resume
    else:
        # Create new resume
        resume = Resume(
            student_id=student_id,
            filename=unique_filename,
            file_path=file_path,
            score=score,
            skills=json.dumps(parsed_data['skills']),
            education=parsed_data['education'],
            experience=parsed_data['experience'],
            is_duplicate=len(duplicates) > 0
        )
        
        if duplicates:
            resume.duplicate_of = duplicates[0].get('student_id')
        
        db.session.add(resume)
        db.session.commit()
    
    return jsonify({
        'message': 'Resume uploaded successfully',
        'resume': resume.to_dict(),
        'parsed_data': parsed_data,
        'score': score,
        'suggestions': suggestions,
        'duplicates': duplicates
    }), 201

# ==================== RESUME SCORE ====================

@resume_bp.route('/score', methods=['GET'])
@student_required
def get_resume_score():
    """Get resume score for current student"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    resume = Resume.query.filter_by(student_id=student_id).first()
    
    if not resume:
        return jsonify({'error': 'No resume uploaded'}), 404
    
    # Get resume data
    parsed_data = {
        'skills': json.loads(resume.skills) if resume.skills else [],
        'education': resume.education,
        'experience': resume.experience
    }
    
    # Calculate score with suggestions
    score, suggestions = calculate_resume_score(parsed_data)
    
    return jsonify({
        'resume': resume.to_dict(),
        'score': score,
        'suggestions': suggestions
    })

@resume_bp.route('/score/<int:job_id>', methods=['GET'])
@student_required
def get_resume_score_for_job(job_id):
    """Get resume score for a specific job"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    resume = Resume.query.filter_by(student_id=student_id).first()
    
    if not resume:
        return jsonify({'error': 'No resume uploaded'}), 404
    
    # Get job requirements
    from models import Job, JobSkill
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    job_skills = [skill.skill_name for skill in job.skills]
    
    # Get resume data
    parsed_data = {
        'skills': json.loads(resume.skills) if resume.skills else [],
        'education': resume.education,
        'experience': resume.experience
    }
    
    # Calculate score with job-specific suggestions
    score, suggestions = calculate_resume_score(parsed_data, job_skills)
    
    return jsonify({
        'resume': resume.to_dict(),
        'score': score,
        'suggestions': suggestions,
        'job_title': job.title
    })

# ==================== RESUME DOWNLOAD ====================

@resume_bp.route('/download/<int:student_id>', methods=['GET'])
@hr_required
def download_resume(student_id):
    """Download student resume (HR only)"""
    resume = Resume.query.filter_by(student_id=student_id).first()
    
    if not resume:
        return jsonify({'error': 'Resume not found'}), 404
    
    if not os.path.exists(resume.file_path):
        return jsonify({'error': 'Resume file not found on server'}), 404
    
    return send_file(
        resume.file_path,
        as_attachment=True,
        download_name=resume.filename
    )

# ==================== RESUME DATA ====================

@resume_bp.route('/data', methods=['GET'])
@student_required
def get_resume_data():
    """Get parsed resume data"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    resume = Resume.query.filter_by(student_id=student_id).first()
    
    if not resume:
        return jsonify({'error': 'No resume uploaded'}), 404
    
    return jsonify({
        'resume': resume.to_dict()
    })

# ==================== RESUME DELETE ====================

@resume_bp.route('/delete', methods=['DELETE'])
@student_required
def delete_resume():
    """Delete student resume"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    resume = Resume.query.filter_by(student_id=student_id).first()
    
    if not resume:
        return jsonify({'error': 'No resume uploaded'}), 404
    
    # Delete file from server
    if os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except:
            pass
    
    # Delete from database
    db.session.delete(resume)
    db.session.commit()
    
    return jsonify({'message': 'Resume deleted successfully'})
