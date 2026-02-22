"""
Demo Data Seeder for Skill-Link
This script populates the database with realistic demo data for judges
"""

from app import create_app
from models import db, HR, Student, Job, JobSkill, Resume, Application, StudentSkill, SavedJob, Internship, InternshipSkill, InternshipApplication, BusinessJob, SkillTest, SKILL_DEMAND
from datetime import datetime, timedelta
import random

def seed_demo_data():
    """Seed the database with demo data"""
    
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("Creating HR accounts...")
        
        # Create HR accounts
        hr1 = HR(company_name="Tech Corp India", hr_name="Rahul Sharma", email="hr@techcorp.com")
        hr1.set_password("password123")
        
        hr2 = HR(company_name="Digital Solutions", hr_name="Priya Patel", email="hr@digitalsol.com")
        hr2.set_password("password123")
        
        hr3 = HR(company_name="StartupHub", hr_name="Amit Kumar", email="hr@startuphub.com")
        hr3.set_password("password123")
        
        hr4 = HR(company_name="MNC Technologies", hr_name="Sneha Reddy", email="hr@mnctech.com")
        hr4.set_password("password123")
        
        hr5 = HR(company_name="Cloud Systems Inc", hr_name="Vikram Singh", email="hr@cloudsys.com")
        hr5.set_password("password123")
        
        db.session.add_all([hr1, hr2, hr3, hr4, hr5])
        db.session.commit()
        
        print("Creating Students...")
        
        # Create Students
        students_data = [
            {"name": "Aryan Sharma", "email": "aryan.sharma@student.edu", "branch": "Computer Science", "grad_year": 2025, "cgpa": 8.5},
            {"name": "Priya Singh", "email": "priya.singh@student.edu", "branch": "Information Technology", "grad_year": 2025, "cgpa": 8.2},
            {"name": "Raj Patel", "email": "raj.patel@student.edu", "branch": "Computer Science", "grad_year": 2024, "cgpa": 9.1},
            {"name": "Ananya Gupta", "email": "ananya.gupta@student.edu", "branch": "Electronics", "grad_year": 2025, "cgpa": 7.8},
            {"name": "Kunal Joshi", "email": "kunal.joshi@student.edu", "branch": "Computer Science", "grad_year": 2024, "cgpa": 8.8},
            {"name": "Neha Verma", "email": "neha.verma@student.edu", "branch": "Information Technology", "grad_year": 2025, "cgpa": 7.5},
            {"name": "Saurabh Mishra", "email": "saurabh.mishra@student.edu", "branch": "Mechanical", "grad_year": 2024, "cgpa": 8.0},
            {"name": "Fatima Khan", "email": "fatima.khan@student.edu", "branch": "Computer Science", "grad_year": 2025, "cgpa": 9.3},
            {"name": "Deepak Rao", "email": "deepak.rao@student.edu", "branch": "Electrical", "grad_year": 2024, "cgpa": 7.9},
            {"name": "Ishita Sharma", "email": "ishita.sharma@student.edu", "branch": "Computer Science", "grad_year": 2025, "cgpa": 8.7},
            {"name": "Arjun Nair", "email": "arjun.nair@student.edu", "branch": "Information Technology", "grad_year": 2024, "cgpa": 8.1},
            {"name": "Meera Devi", "email": "meera.devi@student.edu", "branch": "Electronics", "grad_year": 2025, "cgpa": 7.6},
            {"name": "Rohan Khanna", "email": "rohan.khanna@student.edu", "branch": "Computer Science", "grad_year": 2024, "cgpa": 9.0},
            {"name": "Divya Iyer", "email": "divya.iyer@student.edu", "branch": "Chemical", "grad_year": 2025, "cgpa": 7.7},
            {"name": "Aditya Choudhary", "email": "aditya.choudhary@student.edu", "branch": "Civil", "grad_year": 2024, "cgpa": 7.4},
        ]
        
        students = []
        for data in students_data:
            student = Student(**data)
            student.set_password("password123")
            students.append(student)
        
        db.session.add_all(students)
        db.session.commit()
        
        print("Creating Jobs...")
        
        # Create Jobs
        jobs_data = [
            {"hr_id": hr1.id, "title": "Software Developer", "description": "We are looking for a talented software developer to join our dynamic team.", "min_cgpa": 7.0, "branch": "Computer Science", "skills": ["Python", "Java", "React", "SQL", "Git"], "expiry": 30},
            {"hr_id": hr2.id, "title": "Data Analyst", "description": "Join our analytics team to derive insights from data.", "min_cgpa": 6.5, "branch": "Information Technology", "skills": ["Python", "SQL", "Machine Learning", "Tableau", "Excel"], "expiry": 25},
            {"hr_id": hr1.id, "title": "Full Stack Developer", "description": "Looking for a full stack developer proficient in both frontend and backend technologies.", "min_cgpa": 7.5, "branch": "Computer Science", "skills": ["JavaScript", "React", "Node.js", "MongoDB", "Express"], "expiry": 20},
            {"hr_id": hr3.id, "title": "Backend Engineer", "description": "Build scalable backend systems using modern technologies.", "min_cgpa": 7.0, "branch": "Computer Science", "skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"], "expiry": 35},
            {"hr_id": hr4.id, "title": "Machine Learning Engineer", "description": "Work on AI/ML projects. Develop models and algorithms for predictive analytics.", "min_cgpa": 8.0, "branch": "Computer Science", "skills": ["Python", "TensorFlow", "Machine Learning", "Deep Learning", "SQL"], "expiry": 40},
        ]
        
        jobs = []
        for data in jobs_data:
            expiry_days = data.pop('expiry')
            job = Job(
                hr_id=data['hr_id'],
                title=data['title'],
                description=data['description'],
                min_cgpa=data['min_cgpa'],
                branch=data['branch'],
                expiry_date=datetime.utcnow() + timedelta(days=expiry_days),
                is_active=True
            )
            db.session.add(job)
            db.session.flush()
            
            # Add skills
            for skill in data['skills']:
                job_skill = JobSkill(job_id=job.id, skill_name=skill)
                db.session.add(job_skill)
            
            jobs.append(job)
        
        db.session.commit()
        
        print("Creating Internships...")
        
        # Create Internships with skills
        internships_data = [
            {"hr_id": hr1.id, "title": "Summer Intern - Software", "company": "Tech Corp India", "description": "3-month summer internship program for final year students.", "duration": "3 months", "stipend": "₹25,000/month", "skills_list": ["Python", "Java", "Git", "SQL"], "branch": "Computer Science", "expiry": 45},
            {"hr_id": hr2.id, "title": "Data Science Intern", "company": "Digital Solutions", "description": "Internship focused on data analysis and machine learning projects.", "duration": "6 months", "stipend": "₹30,000/month", "skills_list": ["Python", "SQL", "Machine Learning", "Tableau"], "branch": "Information Technology", "expiry": 30},
            {"hr_id": hr3.id, "title": "Web Development Intern", "company": "StartupHub", "description": "Learn modern web development while working on real projects.", "duration": "4 months", "stipend": "₹20,000/month", "skills_list": ["JavaScript", "React", "HTML", "CSS"], "branch": "Computer Science", "expiry": 20},
            {"hr_id": hr4.id, "title": "Cloud Intern", "company": "MNC Technologies", "description": "Get hands-on experience with cloud technologies.", "duration": "6 months", "stipend": "₹28,000/month", "skills_list": ["AWS", "Docker", "Kubernetes", "Python"], "branch": "Computer Science", "expiry": 35},
        ]
        
        internships = []
        for data in internships_data:
            expiry_days = data.pop('expiry')
            skills_list = data.pop('skills_list')
            
            internship = Internship(
                hr_id=data['hr_id'],
                title=data['title'],
                company=data['company'],
                description=data['description'],
                duration=data['duration'],
                stipend=data['stipend'],
                branch=data['branch'],
                expiry_date=datetime.utcnow() + timedelta(days=expiry_days),
                is_active=True
            )
            db.session.add(internship)
            db.session.flush()
            
            # Add internship skills
            for skill in skills_list:
                internship_skill = InternshipSkill(internship_id=internship.id, skill_name=skill)
                db.session.add(internship_skill)
            
            internships.append(internship)
        
        db.session.commit()
        
        print("Creating Business Jobs...")
        
        # Create Business/Non-Tech Jobs
        business_jobs_data = [
            {"hr_id": hr1.id, "title": "Business Development Executive", "company": "Tech Corp India", "description": "Drive new business opportunities.", "job_type": "BD", "salary": "₹6-8 LPA", "skills_required": "Communication,Presentation,Negotiation", "branch": "All", "expiry": 25},
            {"hr_id": hr2.id, "title": "Sales Manager", "company": "Digital Solutions", "description": "Lead sales team and achieve targets.", "job_type": "Sales", "salary": "₹5-7 LPA", "skills_required": "Sales,CRM,Communication", "branch": "All", "expiry": 30},
            {"hr_id": hr3.id, "title": "Marketing Analyst", "company": "StartupHub", "description": "Analyze marketing campaigns.", "job_type": "Marketing", "salary": "₹4-6 LPA", "skills_required": "Digital Marketing,Analytics,SEO", "branch": "All", "expiry": 20},
            {"hr_id": hr5.id, "title": "HR Coordinator", "company": "Cloud Systems Inc", "description": "Manage recruitment and employee relations.", "job_type": "HR", "salary": "₹4-5 LPA", "skills_required": "Communication,Recruitment,MS Office", "branch": "All", "expiry": 35},
        ]
        
        for data in business_jobs_data:
            expiry_days = data.pop('expiry')
            bjob = BusinessJob(
                **data,
                expiry_date=datetime.utcnow() + timedelta(days=expiry_days),
                is_active=True
            )
            db.session.add(bjob)
        
        db.session.commit()
        
        print("Adding Student Skills...")
        
        # Assign random skills to students
        all_skills = ["Python", "Java", "JavaScript", "React", "SQL", "AWS", "Machine Learning", "Node.js", "Docker", "Git", "MongoDB", "TypeScript", "C++", "Data Analysis", "Excel", "Tableau", "TensorFlow", "Django", "Flask", "Kubernetes"]
        
        for student in students:
            num_skills = random.randint(4, 8)
            student_skills = random.sample(all_skills, num_skills)
            for skill in student_skills:
                ss = StudentSkill(student_id=student.id, skill_name=skill)
                db.session.add(ss)
        
        db.session.commit()
        
        print("Creating Applications...")
        
        # Create job applications
        statuses = ["Applied", "Shortlisted", "Rejected", "Applied", "Applied", "Shortlisted", "Applied", "Applied", "Shortlisted", "Applied", "Applied", "Shortlisted", "Rejected", "Applied"]
        
        for i, student in enumerate(students[:14]):
            num_apps = random.randint(2, 3)
            applied_jobs = random.sample(jobs, num_apps)
            
            for j, job in enumerate(applied_jobs):
                status_idx = (i + j) % len(statuses)
                status = statuses[status_idx]
                
                student_skill_names = [s.skill_name for s in student.skills]
                job_skill_names = [s.skill_name for s in job.skills]
                
                if job_skill_names:
                    matched = len(set(student_skill_names) & set(job_skill_names))
                    match_pct = (matched / len(job_skill_names)) * 100
                else:
                    match_pct = 50
                
                app = Application(
                    student_id=student.id,
                    job_id=job.id,
                    status=status,
                    match_percentage=match_pct,
                    applied_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
                )
                db.session.add(app)
        
        db.session.commit()
        
        print("Creating Internship Applications...")
        
        # Create internship applications
        internship_statuses = ["Applied", "Shortlisted", "Applied", "Applied", "Shortlisted", "Applied", "Applied", "Applied", "Shortlisted", "Applied", "Applied", "Shortlisted", "Applied", "Applied", "Applied"]
        
        for i, student in enumerate(students[:10]):
            num_apps = random.randint(1, 2)
            applied_internships = random.sample(internships, num_apps)
            
            for j, internship in enumerate(applied_internships):
                status_idx = (i + j) % len(internship_statuses)
                status = internship_statuses[status_idx]
                
                student_skill_names = [s.skill_name for s in student.skills]
                internship_skills = [s.skill_name for s in internship.skills]
                
                if internship_skills:
                    matched = len(set(student_skill_names) & set(internship_skills))
                    match_pct = (matched / len(internship_skills)) * 100
                else:
                    match_pct = 50
                
                intern_app = InternshipApplication(
                    student_id=student.id,
                    internship_id=internship.id,
                    status=status,
                    match_percentage=match_pct,
                    applied_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                )
                db.session.add(intern_app)
        
        db.session.commit()
        
        print("Creating Saved Jobs...")
        
        # Some students save jobs for later
        for student in students[:5]:
            saved_job = SavedJob(
                student_id=student.id,
                job_id=random.choice(jobs).id
            )
            db.session.add(saved_job)
        
        db.session.commit()
        
        print("Creating Skill Tests...")
        
        # Create MCQ questions
        questions = [
            {"skill_name": "Python", "question": "What is the output of print(type([]))?", "option_a": "<class 'list'>", "option_b": "<class 'dict'>", "option_c": "<class 'tuple'>", "option_d": "<class 'set'>", "correct_answer": "A", "difficulty": "Easy"},
            {"skill_name": "Python", "question": "Which method is used to add an element at the end of a list?", "option_a": "add()", "option_b": "append()", "option_c": "insert()", "option_d": "extend()", "correct_answer": "B", "difficulty": "Easy"},
            {"skill_name": "Python", "question": "What is the correct way to create a dictionary?", "option_a": "{}", "option_b": "[]", "option_c": "()", "option_d": "<>", "correct_answer": "A", "difficulty": "Easy"},
            {"skill_name": "Java", "question": "Which keyword is used to inherit a class in Java?", "option_a": "extends", "option_b": "implements", "option_c": "inherits", "option_d": "super", "correct_answer": "A", "difficulty": "Easy"},
            {"skill_name": "SQL", "question": "Which command is used to retrieve data from a database?", "option_a": "GET", "option_b": "SELECT", "option_c": "FETCH", "option_d": "RETRIEVE", "correct_answer": "B", "difficulty": "Easy"},
            {"skill_name": "JavaScript", "question": "Which method is used to add an element to the end of an array?", "option_a": "push()", "option_b": "pop()", "option_c": "shift()", "option_d": "unshift()", "correct_answer": "A", "difficulty": "Easy"},
            {"skill_name": "Machine Learning", "question": "Which is a supervised learning algorithm?", "option_a": "K-Means", "option_b": "PCA", "option_c": "Linear Regression", "option_d": "DBSCAN", "correct_answer": "C", "difficulty": "Medium"},
            {"skill_name": "Aptitude", "question": "If 2x + 5 = 15, what is x?", "option_a": "5", "option_b": "10", "option_c": "7.5", "option_d": "4", "correct_answer": "A", "difficulty": "Easy"},
            {"skill_name": "Aptitude", "question": "What is 20% of 150?", "option_a": "30", "option_b": "25", "option_c": "35", "option_d": "20", "correct_answer": "A", "difficulty": "Easy"},
        ]
        
        for q in questions:
            test = SkillTest(**q)
            db.session.add(test)
        
        db.session.commit()
        
        print("✅ Demo data seeded successfully!")
        print(f"   - 5 HR accounts")
        print(f"   - {len(students)} Student accounts")
        print(f"   - {len(jobs)} Job postings")
        print(f"   - {len(internships)} Internships")
        print(f"   - 4 Business Jobs")
        print(f"   - {len(questions)} Skill Test Questions")
        
        print("\n📋 Login Credentials:")
        print("   HR: hr@techcorp.com / password123")
        print("   Student: aryan.sharma@student.edu / password123")

if __name__ == "__main__":
    seed_demo_data()
