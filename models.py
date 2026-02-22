from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class HR(db.Model):
    """HR Model - Represents HR/Recruiter accounts"""
    __tablename__ = 'hr'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    hr_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='hr', lazy=True, cascade='all, delete-orphan')
    internships = db.relationship('Internship', backref='hr', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'hr_name': self.hr_name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Student(db.Model):
    """Student Model - Represents student accounts"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    grad_year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    skills = db.relationship('StudentSkill', backref='student', lazy=True, cascade='all, delete-orphan')
    resumes = db.relationship('Resume', backref='student', lazy=True, cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')
    internship_applications = db.relationship('InternshipApplication', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def to_dict(self, include_skills=False):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'branch': self.branch,
            'grad_year': self.grad_year,
            'cgpa': self.cgpa,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_skills:
            data['skills'] = [skill.skill_name for skill in self.skills]
        return data

class Job(db.Model):
    """Job Model - Represents job postings"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('hr.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    min_cgpa = db.Column(db.Float, default=0.0)
    branch = db.Column(db.String(100), nullable=False)
    required_skills = db.Column(db.Text, nullable=True)
    expiry_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    skills = db.relationship('JobSkill', backref='job', lazy=True, cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_skills=False):
        data = {
            'id': self.id,
            'hr_id': self.hr_id,
            'title': self.title,
            'description': self.description,
            'min_cgpa': self.min_cgpa,
            'branch': self.branch,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'applicant_count': len(self.applications)
        }
        if include_skills:
            data['required_skills_list'] = [skill.skill_name for skill in self.skills]
        return data

class StudentSkill(db.Model):
    """Student Skills Model"""
    __tablename__ = 'student_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'skill_name', name='unique_student_skill'),)

class JobSkill(db.Model):
    """Job Skills Model"""
    __tablename__ = 'job_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('job_id', 'skill_name', name='unique_job_skill'),)

class Resume(db.Model):
    """Resume Model - Stores resume information"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    score = db.Column(db.Integer, default=0)
    skills = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_duplicate = db.Column(db.Boolean, default=False)
    duplicate_of = db.Column(db.Integer, nullable=True)
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'student_id': self.student_id,
            'filename': self.filename,
            'score': self.score,
            'skills': json.loads(self.skills) if self.skills else [],
            'education': self.education,
            'experience': self.experience,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'is_duplicate': self.is_duplicate
        }

class Application(db.Model):
    """Application Model - Tracks job applications"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(50), default='Applied')
    interview_round = db.Column(db.Integer, default=0)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    match_percentage = db.Column(db.Float, default=0.0)
    hr_notes = db.Column(db.Text, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'job_id', name='unique_application'),)
    
    def to_dict(self, include_student=False, include_job=False):
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'job_id': self.job_id,
            'status': self.status,
            'interview_round': self.interview_round,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'match_percentage': self.match_percentage,
            'hr_notes': self.hr_notes
        }
        if include_student and self.student:
            data['student'] = self.student.to_dict(include_skills=True)
            resume = Resume.query.filter_by(student_id=self.student_id).first()
            if resume:
                data['resume_score'] = resume.score
        if include_job and self.job:
            data['job'] = self.job.to_dict(include_skills=True)
        return data

class HRNote(db.Model):
    """HR Notes on Candidates"""
    __tablename__ = 'hr_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('hr.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('hr_id', 'student_id', name='unique_hr_note'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hr_id': self.hr_id,
            'student_id': self.student_id,
            'note': self.note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class InterviewEmail(db.Model):
    """Interview Email Mock Model"""
    __tablename__ = 'interview_emails'
    
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('hr.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hr_id': self.hr_id,
            'application_id': self.application_id,
            'message': self.message,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }

class SavedJob(db.Model):
    """Saved/Bookmarked Jobs"""
    __tablename__ = 'saved_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'job_id', name='unique_saved_job'),)

class Internship(db.Model):
    """Internship Opportunities"""
    __tablename__ = 'internships'
    
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('hr.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    internship_type = db.Column(db.String(50), nullable=True)  # Paid/Unpaid
    duration = db.Column(db.String(100), nullable=True)  # in months
    stipend = db.Column(db.String(100), nullable=True)
    skills_required = db.Column(db.Text, nullable=True)
    branch = db.Column(db.String(100), nullable=False)
    eligible_year = db.Column(db.Integer, nullable=True)  # Year of study
    expiry_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    skills = db.relationship('InternshipSkill', backref='internship', lazy=True, cascade='all, delete-orphan')
    applications = db.relationship('InternshipApplication', backref='internship', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_skills=False):
        data = {
            'id': self.id,
            'hr_id': self.hr_id,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'internship_type': self.internship_type,
            'duration': self.duration,
            'stipend': self.stipend,
            'skills_required': self.skills_required,
            'branch': self.branch,
            'eligible_year': self.eligible_year,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'applicant_count': len(self.applications) if hasattr(self, 'applications') else 0
        }
        if include_skills:
            data['skills_list'] = [skill.skill_name for skill in self.skills]
        return data

class InternshipSkill(db.Model):
    """Internship Skills Model"""
    __tablename__ = 'internship_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('internship_id', 'skill_name', name='unique_internship_skill'),)

class InternshipApplication(db.Model):
    """Internship Application Model"""
    __tablename__ = 'internship_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    internship_id = db.Column(db.Integer, db.ForeignKey('internships.id'), nullable=False)
    status = db.Column(db.String(50), default='Applied')
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    match_percentage = db.Column(db.Float, default=0.0)
    hr_notes = db.Column(db.Text, nullable=True)
    
    __table_args__ = (db.UniqueConstraint('student_id', 'internship_id', name='unique_internship_application'),)
    
    def to_dict(self, include_student=False, include_internship=False):
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'internship_id': self.internship_id,
            'status': self.status,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'match_percentage': self.match_percentage,
            'hr_notes': self.hr_notes
        }
        if include_student and self.student:
            data['student'] = self.student.to_dict(include_skills=True)
        if include_internship and self.internship:
            data['internship'] = self.internship.to_dict(include_skills=True)
        return data

class BusinessJob(db.Model):
    """Business/Non-Tech Job Roles"""
    __tablename__ = 'business_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('hr.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    salary = db.Column(db.String(100), nullable=True)
    skills_required = db.Column(db.Text, nullable=True)
    branch = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hr_id': self.hr_id,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'job_type': self.job_type,
            'salary': self.salary,
            'skills_required': self.skills_required,
            'branch': self.branch,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }

class SkillTest(db.Model):
    """Skill Test / MCQ Generator"""
    __tablename__ = 'skill_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)
    difficulty = db.Column(db.String(20), default='Easy')
    
    def to_dict(self):
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'question': self.question,
            'option_a': self.option_a,
            'option_b': self.option_b,
            'option_c': self.option_c,
            'option_d': self.option_d,
            'correct_answer': self.correct_answer,
            'difficulty': self.difficulty
        }

# Skill demand data
SKILL_DEMAND = {
    'high_demand': ['Python', 'Java', 'JavaScript', 'React', 'SQL', 'AWS', 'Machine Learning', 'Data Analysis', 'Node.js', 'Docker', 'Git', 'C++', 'Angular', 'MongoDB', 'TypeScript', 'Kubernetes', 'Flutter', 'Go', 'Rust', 'TensorFlow'],
    'low_demand': ['Perl', 'Ruby', 'Scala', 'Haskell', 'Erlang', 'COBOL', 'Fortran', 'Pascal', 'Assembly', 'VB.NET', 'Objective-C', 'Shell Scripting', 'Lua', 'MATLAB', 'R Programming', 'SPSS', 'SAS']
}
