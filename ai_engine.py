# sklearn is optional - for text similarity
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from models import Student, StudentSkill, Resume, Job, JobSkill, Application
import json

# Learning path suggestions (static mapping)
LEARNING_PATHS = {
    'react': 'Learn React - 2 weeks roadmap: React docs → Components → State → Hooks → Projects',
    'python': 'Learn Python - 3 weeks roadmap: Syntax → Data Structures → OOP → Django/Flask → Projects',
    'java': 'Learn Java - 3 weeks roadmap: OOP → Collections → Spring Boot → REST APIs → Projects',
    'javascript': 'Learn JavaScript - 3 weeks roadmap: ES6 → DOM → Async → Node.js → Projects',
    'machine learning': 'Learn ML - 4 weeks roadmap: Python → NumPy/Pandas → Scikit-learn → Projects',
    'data science': 'Learn Data Science - 4 weeks roadmap: Statistics → Python → Pandas → Visualization → ML',
    'aws': 'Learn AWS - 2 weeks roadmap: EC2 → S3 → Lambda → DynamoDB → Solutions Architect',
    'docker': 'Learn Docker - 1 week roadmap: Images → Containers → Docker Compose → Kubernetes basics',
    'sql': 'Learn SQL - 2 weeks roadmap: Queries → Joins → Subqueries → Indexes → Database Design',
    'mongodb': 'Learn MongoDB - 1 week roadmap: CRUD → Aggregation → Indexing → Atlas → MERN Stack',
    'django': 'Learn Django - 2 weeks roadmap: Models → Views → Forms → REST → Deployment',
    'flask': 'Learn Flask - 1 week roadmap: Routes → Templates → SQLAlchemy → REST APIs → Deployment',
    'node.js': 'Learn Node.js - 2 weeks roadmap: Express → MongoDB → REST → Authentication → Projects',
    'angular': 'Learn Angular - 2 weeks roadmap: TypeScript → Components → Services → RxJS → Projects',
    'vue': 'Learn Vue.js - 2 weeks roadmap: Vue 3 → Composition API → Vuex → Router → Projects',
    'typescript': 'Learn TypeScript - 1 week roadmap: Types → Interfaces → Generics → OOP → React+TS',
    'kubernetes': 'Learn Kubernetes - 2 weeks roadmap: Pods → Services → Deployments → Helm → Cloud',
    'flutter': 'Learn Flutter - 3 weeks roadmap: Dart → Widgets → State → Firebase → App Store',
    'ios': 'Learn iOS - 3 weeks roadmap: Swift → UIKit → SwiftUI → Firebase → App Store',
    'android': 'Learn Android - 3 weeks roadmap: Kotlin → XML → Jetpack → Firebase → Play Store',
    'tensorflow': 'Learn TensorFlow - 3 weeks roadmap: Tensors → Models → CNN/RNN → Deployment → Projects',
    'pytorch': 'Learn PyTorch - 3 weeks roadmap: Tensors → Autograd → Networks → CNN/RNN → Projects',
    'nlp': 'Learn NLP - 3 weeks roadmap: Text Processing → NLTK → Transformers → BERT → Projects',
    'blockchain': 'Learn Blockchain - 3 weeks roadmap: Solidity → Smart Contracts → Web3 → DApps → Projects',
    'devops': 'Learn DevOps - 4 weeks roadmap: Git → Docker → CI/CD → Kubernetes → Cloud → Monitoring',
    'data analysis': 'Learn Data Analysis - 2 weeks roadmap: Excel → SQL → Python → Pandas → Tableau',
    'tableau': 'Learn Tableau - 1 week roadmap: Visualizations → Dashboards → Calculations → Stories',
    'power bi': 'Learn Power BI - 1 week roadmap: Power Query → DAX → Visualizations → Dashboards',
    'excel': 'Learn Excel - 1 week roadmap: Formulas → VLOOKUP → Pivot Tables → Macros → VBA',
    'git': 'Learn Git - 1 week roadmap: Init → Add → Commit → Branch → Merge → GitHub → CI/CD'
}

def calculate_skill_match(student_skills, job_skills):
    """
    Calculate skill match percentage between student and job
    Returns: match_percentage (0-100), matched_skills, missing_skills
    """
    if not student_skills or not job_skills:
        return 0, [], job_skills or []
    
    # Normalize skills to lowercase
    student_skills_lower = [s.lower() for s in student_skills]
    job_skills_lower = [s.lower() for s in job_skills]
    
    # Find matched skills
    matched_skills = []
    missing_skills = []
    
    for job_skill in job_skills_lower:
        if job_skill in student_skills_lower:
            matched_skills.append(job_skill.title())
        else:
            missing_skills.append(job_skill.title())
    
    # Calculate percentage
    match_percentage = (len(matched_skills) / len(job_skills_lower)) * 100 if job_skills_lower else 0
    
    return round(match_percentage, 2), matched_skills, missing_skills

def calculate_ai_match_score(student, job, resume=None):
    """
    Calculate comprehensive AI match score based on:
    - Skill match (60% weight)
    - CGPA match (20% weight)
    - Branch match (20% weight)
    """
    # Skill match (60%)
    student_skills = [skill.skill_name for skill in student.skills]
    job_skills = [skill.skill_name for skill in job.skills]
    skill_match, _, _ = calculate_skill_match(student_skills, job_skills)
    
    # CGPA match (20%)
    cgpa_score = 0
    if student.cgpa >= job.min_cgpa:
        cgpa_score = 100
    elif student.cgpa >= job.min_cgpa - 1:
        cgpa_score = 50
    else:
        cgpa_score = 0
    
    # Branch match (20%)
    branch_score = 100 if student.branch.lower() == job.branch.lower() or job.branch.lower() == 'all' else 0
    
    # Resume score bonus (if available)
    resume_bonus = 0
    if resume:
        resume_bonus = resume.score * 0.1  # Max 10 bonus points
    
    # Calculate weighted total
    total_score = (skill_match * 0.6) + (cgpa_score * 0.2) + (branch_score * 0.2) + resume_bonus
    
    return min(round(total_score, 2), 100)

def get_recommended_jobs(student_id, limit=10):
    """
    Get recommended jobs for a student based on skills and profile
    """
    student = Student.query.get(student_id)
    if not student:
        return []
    
    # Get student's skills
    student_skills = [skill.skill_name for skill in student.skills]
    
    # Get student's resume
    resume = Resume.query.filter_by(student_id=student_id).first()
    
    # Get active jobs
    active_jobs = Job.query.filter_by(is_active=True).all()
    
    recommendations = []
    for job in active_jobs:
        # Skip if already applied
        existing_app = Application.query.filter_by(
            student_id=student_id, 
            job_id=job.id
        ).first()
        
        if existing_app:
            continue
        
        # Calculate match score
        match_score = calculate_ai_match_score(student, job, resume)
        
        recommendations.append({
            'job': job.to_dict(include_skills=True),
            'match_score': match_score,
            'student_skills': student_skills
        })
    
    # Sort by match score (descending)
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    return recommendations[:limit]

def get_recommended_students(job_id, limit=10):
    """
    Get recommended students for a job (AI feature for HR)
    Even students who haven't applied
    """
    job = Job.query.get(job_id)
    if not job:
        return []
    
    # Get job required skills
    job_skills = [skill.skill_name for skill in job.skills]
    
    # Get all students
    students = Student.query.all()
    
    recommendations = []
    for student in students:
        # Get student skills
        student_skills = [skill.skill_name for skill in student.skills]
        
        # Get student resume
        resume = Resume.query.filter_by(student_id=student.id).first()
        
        # Calculate match score
        match_score = calculate_ai_match_score(student, job, resume)
        
        # Check if already applied
        application = Application.query.filter_by(
            student_id=student.id,
            job_id=job.id
        ).first()
        
        has_applied = application is not None
        
        recommendations.append({
            'student': student.to_dict(include_skills=True),
            'match_score': match_score,
            'has_applied': has_applied,
            'application_status': application.status if application else None,
            'resume_score': resume.score if resume else 0
        })
    
    # Sort by match score (descending)
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    return recommendations[:limit]

def check_duplicate_resume(text, student_id):
    """
    Check if resume text is similar to other students' resumes
    Uses TF-IDF and cosine similarity
    """
    # Get all resumes except current student's
    resumes = Resume.query.filter(Resume.student_id != student_id).all()
    
    if not resumes:
        return [], []
    
    # Extract text from all resumes
    texts = [r.filename for r in resumes]  # Use filename as placeholder
    # In a real system, we'd store the extracted text
    
    # For now, we'll do a simple check
    # In production, you'd store extracted text in the database
    
    return [], []

def detect_duplicate_resume(new_text, exclude_student_id=None):
    """
    Detect potential duplicate resumes using text similarity
    Returns: list of potential duplicates with similarity scores
    """
    try:
        # Get all resumes with extracted text
        resumes = Resume.query.all()
        
        if not resumes:
            return []
        
        # For simplicity, compare by resume score and skills
        # In production, store extracted text in DB
        duplicates = []
        
        new_resume_skills = set(new_text.lower().split()) if new_text else set()
        
        for resume in resumes:
            if exclude_student_id and resume.student_id == exclude_student_id:
                continue
            
            # Compare skills if available
            if resume.skills:
                try:
                    resume_skills = set(json.loads(resume.skills.lower()))
                    # Calculate Jaccard similarity
                    if resume_skills and new_resume_skills:
                        intersection = len(new_resume_skills.intersection(resume_skills))
                        union = len(new_resume_skills.union(resume_skills))
                        similarity = intersection / union if union > 0 else 0
                        
                        if similarity > 0.7:  # 70% similarity threshold
                            duplicates.append({
                                'student_id': resume.student_id,
                                'similarity': round(similarity * 100, 2)
                            })
                except:
                    pass
        
        return duplicates
    except Exception as e:
        print(f"Duplicate detection error: {e}")
        return []

def get_missing_skills(student_skills, job_skills):
    """
    Get missing skills for a student to match a job
    """
    student_skills_lower = [s.lower() for s in student_skills]
    job_skills_lower = [s.lower() for s in job_skills]
    
    missing = []
    for skill in job_skills_lower:
        if skill not in student_skills_lower:
            missing.append(skill.title())
    
    return missing

def get_learning_path(skill):
    """
    Get learning path suggestion for a missing skill
    """
    skill_lower = skill.lower()
    return LEARNING_PATHS.get(skill_lower, f"Learn {skill.title()} - Check online courses and documentation")

def get_learning_paths_for_missing_skills(missing_skills):
    """
    Get learning paths for multiple missing skills
    """
    paths = {}
    for skill in missing_skills:
        paths[skill.title()] = get_learning_path(skill)
    return paths

def bulk_shortlist_top_students(job_id, count=10):
    """
    Automatically shortlist top matching students for a job
    """
    job = Job.query.get(job_id)
    if not job:
        return []
    
    # Get recommended students
    recommended = get_recommended_students(job_id, limit=count)
    
    shortlisted = []
    for rec in recommended[:count]:
        student_id = rec['student']['id']
        
        # Check if already applied
        application = Application.query.filter_by(
            student_id=student_id,
            job_id=job_id
        ).first()
        
        if application:
            # Update status to Shortlisted
            application.status = 'Shortlisted'
            shortlisted.append(application)
        else:
            # Create new application
            new_app = Application(
                student_id=student_id,
                job_id=job_id,
                status='Shortlisted',
                match_percentage=rec['match_score']
            )
            db.session.add(new_app)
            shortlisted.append(new_app)
    
    db.session.commit()
    return shortlisted

def get_skill_demand_analytics():
    """
    Get skill demand analytics across all HR job posts
    Returns: dict with top skills and their demand count
    """
    # Get all job skills
    job_skills = JobSkill.query.all()
    
    # Count skill occurrences
    skill_counts = {}
    for js in job_skills:
        skill = js.skill_name.lower()
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # Sort by count
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'top_skills': [{'skill': s[0].title(), 'count': s[1]} for s in sorted_skills[:20]],
        'total_jobs_with_skills': len(JobSkill.query.distinct(JobSkill.job_id).all())
    }

# Import db for bulk_shortlist
from models import db
