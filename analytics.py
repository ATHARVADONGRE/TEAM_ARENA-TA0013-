from models import db, HR, Student, Job, Application, Resume, StudentSkill, JobSkill
from collections import Counter
from datetime import datetime, timedelta

def get_hr_analytics(hr_id):
    """
    Get analytics data for HR dashboard
    """
    # Total jobs posted by this HR
    total_jobs = Job.query.filter_by(hr_id=hr_id).count()
    
    # Active jobs
    active_jobs = Job.query.filter_by(hr_id=hr_id, is_active=True).count()
    
    # Total applicants across all jobs
    hr_jobs = Job.query.filter_by(hr_id=hr_id).all()
    job_ids = [job.id for job in hr_jobs]
    total_applicants = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    
    # Shortlisted candidates
    shortlisted = Application.query.filter(
        Application.job_id.in_(job_ids),
        Application.status == 'Shortlisted'
    ).count() if job_ids else 0
    
    # Rejected candidates
    rejected = Application.query.filter(
        Application.job_id.in_(job_ids),
        Application.status == 'Rejected'
    ).count() if job_ids else 0
    
    # Interview candidates
    interview = Application.query.filter(
        Application.job_id.in_(job_ids),
        Application.status == 'Interview'
    ).count() if job_ids else 0
    
    # Selected candidates
    selected = Application.query.filter(
        Application.job_id.in_(job_ids),
        Application.status == 'Selected'
    ).count() if job_ids else 0
    
    # Get top skills from applicants
    top_skills = get_top_applicant_skills(job_ids)
    
    # Applicants per job
    applicants_per_job = []
    for job in hr_jobs:
        app_count = Application.query.filter_by(job_id=job.id).count()
        applicants_per_job.append({
            'job_title': job.title,
            'applicants': app_count,
            'shortlisted': Application.query.filter_by(job_id=job.id, status='Shortlisted').count()
        })
    
    return {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applicants': total_applicants,
        'shortlisted': shortlisted,
        'rejected': rejected,
        'interview': interview,
        'selected': selected,
        'top_skills': top_skills,
        'applicants_per_job': applicants_per_job
    }

def get_top_applicant_skills(job_ids):
    """
    Get top skills demanded from applicants
    """
    if not job_ids:
        return []
    
    # Get all applications for these jobs
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all()
    student_ids = [app.student_id for app in applications]
    
    # Get skills of these students
    skills = StudentSkill.query.filter(StudentSkill.student_id.in_(student_ids)).all() if student_ids else []
    
    # Count skill occurrences
    skill_counts = Counter([s.skill_name.lower() for s in skills])
    
    # Return top 10
    return [{'skill': s[0].title(), 'count': s[1]} for s in skill_counts.most_common(10)]

def get_student_analytics(student_id):
    """
    Get analytics for student dashboard
    """
    # Get student
    student = Student.query.get(student_id)
    if not student:
        return None
    
    # Get student's resume
    resume = Resume.query.filter_by(student_id=student_id).first()
    
    # Get applications
    applications = Application.query.filter_by(student_id=student_id).all()
    
    # Count by status
    applied = len([a for a in applications if a.status == 'Applied'])
    shortlisted = len([a for a in applications if a.status == 'Shortlisted'])
    rejected = len([a for a in applications if a.status == 'Rejected'])
    interview = len([a for a in applications if a.status == 'Interview'])
    selected = len([a for a in applications if a.status == 'Selected'])
    
    # Get matched jobs
    from utils.ai_engine import get_recommended_jobs
    recommended = get_recommended_jobs(student_id, limit=5)
    
    return {
        'profile': student.to_dict(include_skills=True),
        'resume_score': resume.score if resume else 0,
        'total_applications': len(applications),
        'applied': applied,
        'shortlisted': shortlisted,
        'rejected': rejected,
        'interview': interview,
        'selected': selected,
        'recommended_jobs_count': len(recommended)
    }

def get_admin_analytics():
    """
    Get platform-wide analytics (for potential admin panel)
    """
    total_hr = HR.query.count()
    total_students = Student.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    
    # Active jobs
    active_jobs = Job.query.filter_by(is_active=True).count()
    
    # Jobs expiring soon (within 7 days)
    soon = datetime.utcnow() + timedelta(days=7)
    expiring_soon = Job.query.filter(
        Job.is_active == True,
        Job.expiry_date <= soon,
        Job.expiry_date >= datetime.utcnow()
    ).count()
    
    return {
        'total_hr': total_hr,
        'total_students': total_students,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'active_jobs': active_jobs,
        'expiring_soon': expiring_soon
    }

def export_applicants_csv(job_id):
    """
    Generate CSV data for applicants of a job
    Returns: list of dicts representing CSV rows
    """
    applications = Application.query.filter_by(job_id=job_id).all()
    job = Job.query.get(job_id)
    
    rows = []
    for app in applications:
        student = app.student
        resume = Resume.query.filter_by(student_id=student.id).first()
        
        rows.append({
            'Student Name': student.name,
            'Email': student.email,
            'Branch': student.branch,
            'Graduation Year': student.grad_year,
            'CGPA': student.cgpa,
            'Skills': ', '.join([s.skill_name for s in student.skills]),
            'Resume Score': resume.score if resume else 0,
            'Match Percentage': round(app.match_percentage, 2),
            'Status': app.status,
            'Applied Date': app.applied_at.strftime('%Y-%m-%d') if app.applied_at else ''
        })
    
    return rows, job.title if job else 'Unknown Job'

def update_job_expiry_status():
    """
    Update job expiry status - mark expired jobs as inactive
    Called periodically or on application load
    """
    now = datetime.utcnow()
    expired_jobs = Job.query.filter(
        Job.is_active == True,
        Job.expiry_date < now
    ).all()
    
    for job in expired_jobs:
        job.is_active = False
    
    if expired_jobs:
        db.session.commit()
    
    return len(expired_jobs)
