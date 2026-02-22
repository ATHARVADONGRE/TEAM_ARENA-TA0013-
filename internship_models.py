"""
Internship Models - Additional tables for internship feature
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
        return data
