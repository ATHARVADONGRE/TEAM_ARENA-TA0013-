from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db, Student, StudentSkill, Job, JobSkill, Application, Resume
from utils.auth import student_required, hr_required
from utils.ai_engine import get_missing_skills, get_learning_paths_for_missing_skills
import json
import random

feature_bp = Blueprint('features', __name__)

# ==================== AI GAP ANALYSER ====================

@feature_bp.route('/gap-analysis/<int:job_id>', methods=['GET'])
@student_required
def get_gap_analysis(job_id):
    """Analyze skill gaps for a specific job"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    # Get student
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get job
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Get student skills
    student_skills = [skill.skill_name for skill in student.skills]
    
    # Get job required skills
    job_skills = [skill.skill_name for skill in job.skills]
    
    # Find gaps
    missing_skills = get_missing_skills(student_skills, job_skills)
    
    # Get learning paths for missing skills
    learning_paths = get_learning_paths_for_missing_skills(missing_skills)
    
    # Calculate match percentage
    match_percentage = 0
    if job_skills:
        match_percentage = ((len(job_skills) - len(missing_skills)) / len(job_skills)) * 100
    
    # Determine gap severity
    if match_percentage >= 70:
        severity = "Low"
    elif match_percentage >= 40:
        severity = "Medium"
    else:
        severity = "High"
    
    # Generate analysis
    analysis = {
        'student_name': student.name,
        'job_title': job.title,
        'company': job.hr.company_name if job.hr else 'Company',
        'current_skills_count': len(student_skills),
        'required_skills_count': len(job_skills),
        'matched_skills': [s for s in job_skills if s.lower() in [sk.lower() for sk in student_skills]],
        'missing_skills': missing_skills,
        'match_percentage': round(match_percentage, 2),
        'gap_severity': severity,
        'learning_paths': learning_paths,
        'recommendations': []
    }
    
    # Add recommendations
    if missing_skills:
        analysis['recommendations'].append(f"Learn {len(missing_skills)} missing skills to improve your chances")
    if match_percentage < 50:
        analysis['recommendations'].append("Consider adding more technical skills from job requirements")
    
    return jsonify({
        'success': True,
        'gap_analysis': analysis
    })

@feature_bp.route('/gap-analysis/all', methods=['GET'])
@student_required
def get_all_gap_analysis():
    """Get gap analysis for all recommended jobs"""
    claims = get_jwt()
    student_id = claims.get('user_id')
    
    # Get recommended jobs
    from utils.ai_engine import get_recommended_jobs
    recommended = get_recommended_jobs(student_id, limit=10)
    
    analyses = []
    for rec in recommended:
        job = rec['job']
        job_skills = job.get('required_skills_list', [])
        student = Student.query.get(student_id)
        student_skills = [s.skill_name for s in student.skills]
        
        missing = get_missing_skills(student_skills, job_skills)
        
        # Calculate severity
        match = rec['match_score']
        if match >= 70:
            severity = "Low"
        elif match >= 40:
            severity = "Medium"
        else:
            severity = "High"
        
        analyses.append({
            'job_id': job['id'],
            'job_title': job['title'],
            'match_score': rec['match_score'],
            'missing_skills_count': len(missing),
            'missing_skills': missing[:5],
            'gap_severity': severity
        })
    
    # Sort by match score
    analyses.sort(key=lambda x: x['match_score'], reverse=True)
    
    return jsonify({
        'success': True,
        'gap_analyses': analyses
    })

# ==================== AI MOCK TEST SIMULATOR ====================

# MCQ Questions Database
MOCK_QUESTIONS = {
    'Python': [
        {'id': 1, 'question': 'What is the output of print(type([]))?', 'options': ['list', 'tuple', 'dict', 'set'], 'answer': 'list', 'difficulty': 'Easy', 'topic': 'Data Types'},
        {'id': 2, 'question': 'Which method is used to add an element at the end of a list?', 'options': ['append()', 'add()', 'insert()', 'extend()'], 'answer': 'append()', 'difficulty': 'Easy', 'topic': 'Lists'},
        {'id': 3, 'question': 'What is the time complexity of accessing an element in a list by index?', 'options': ['O(1)', 'O(n)', 'O(log n)', 'O(n log n)'], 'answer': 'O(1)', 'difficulty': 'Medium', 'topic': 'Complexity'},
        {'id': 4, 'question': 'Which keyword is used to define a function in Python?', 'options': ['function', 'def', 'func', 'lambda'], 'answer': 'def', 'difficulty': 'Easy', 'topic': 'Functions'},
        {'id': 5, 'question': 'What is a lambda function?', 'options': ['Anonymous function', 'Named function', 'Recursive function', 'Generator'], 'answer': 'Anonymous function', 'difficulty': 'Medium', 'topic': 'Functions'},
        {'id': 6, 'question': 'Which Python library is used for data analysis?', 'options': ['NumPy', 'Django', 'Flask', 'Pygame'], 'answer': 'NumPy', 'difficulty': 'Easy', 'topic': 'Libraries'},
        {'id': 7, 'question': 'What is the output of 2**3 in Python?', 'options': ['6', '8', '9', '5'], 'answer': '8', 'difficulty': 'Easy', 'topic': 'Operators'},
        {'id': 8, 'question': 'Which method is used to read a file in Python?', 'options': ['read()', 'open()', 'file()', 'load()'], 'answer': 'open()', 'difficulty': 'Medium', 'topic': 'File Handling'},
        {'id': 9, 'question': 'What is a dictionary in Python?', 'options': ['Ordered collection', 'Key-value pair', 'Sequence', 'Set'], 'answer': 'Key-value pair', 'difficulty': 'Easy', 'topic': 'Data Types'},
        {'id': 10, 'question': 'Which exception is raised when division by zero occurs?', 'options': ['ValueError', 'TypeError', 'ZeroDivisionError', 'RuntimeError'], 'answer': 'ZeroDivisionError', 'difficulty': 'Medium', 'topic': 'Exception Handling'}
    ],
    'JavaScript': [
        {'id': 1, 'question': 'Which keyword declares a constant in JavaScript?', 'options': ['var', 'let', 'const', 'constant'], 'answer': 'const', 'difficulty': 'Easy', 'topic': 'Variables'},
        {'id': 2, 'question': 'What is the result of typeof null?', 'options': ['null', 'undefined', 'object', 'boolean'], 'answer': 'object', 'difficulty': 'Medium', 'topic': 'Data Types'},
        {'id': 3, 'question': 'Which method adds an element to the end of an array?', 'options': ['push()', 'pop()', 'shift()', 'unshift()'], 'answer': 'push()', 'difficulty': 'Easy', 'topic': 'Arrays'},
        {'id': 4, 'question': 'What does === compare?', 'options': ['Value only', 'Type only', 'Value and Type', 'Reference'], 'answer': 'Value and Type', 'difficulty': 'Easy', 'topic': 'Operators'},
        {'id': 5, 'question': 'Which is NOT a JavaScript data type?', 'options': ['Number', 'Boolean', 'Character', 'Undefined'], 'answer': 'Character', 'difficulty': 'Easy', 'topic': 'Data Types'},
        {'id': 6, 'question': 'What is a closure?', 'options': ['A function with variables', 'A function returning function with access to outer scope', 'A loop', 'An object'], 'answer': 'A function returning function with access to outer scope', 'difficulty': 'Hard', 'topic': 'Functions'},
        {'id': 7, 'question': 'Which event occurs when user clicks on an element?', 'options': ['onmouseover', 'onclick', 'onchange', 'onsubmit'], 'answer': 'onclick', 'difficulty': 'Easy', 'topic': 'Events'},
        {'id': 8, 'question': 'What is the correct way to create an object?', 'options': ['var obj = {}', 'var obj = []', 'var obj = ()', 'var obj = object()'], 'answer': 'var obj = {}', 'difficulty': 'Easy', 'topic': 'Objects'},
        {'id': 9, 'question': 'Which method converts JSON string to object?', 'options': ['JSON.stringify()', 'JSON.parse()', 'JSON.convert()', 'JSON.toObject()'], 'answer': 'JSON.parse()', 'difficulty': 'Easy', 'topic': 'JSON'},
        {'id': 10, 'question': 'What is Promise used for?', 'options': ['Async operations', 'Looping', 'Error handling', 'DOM manipulation'], 'answer': 'Async operations', 'difficulty': 'Medium', 'topic': 'Async'}
    ],
    'SQL': [
        {'id': 1, 'question': 'Which command is used to extract data from a database?', 'options': ['EXTRACT', 'SELECT', 'GET', 'FIND'], 'answer': 'SELECT', 'difficulty': 'Easy', 'topic': 'Queries'},
        {'id': 2, 'question': 'Which clause is used to filter grouped results?', 'options': ['WHERE', 'HAVING', 'FILTER', 'GROUP BY'], 'answer': 'HAVING', 'difficulty': 'Medium', 'topic': 'Clauses'},
        {'id': 3, 'question': 'What is a primary key?', 'options': ['First column', 'Unique identifier', 'Foreign key', 'Index'], 'answer': 'Unique identifier', 'difficulty': 'Easy', 'topic': 'Keys'},
        {'id': 4, 'question': 'Which join returns matching rows from both tables?', 'options': ['LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'FULL JOIN'], 'answer': 'INNER JOIN', 'difficulty': 'Easy', 'topic': 'Joins'},
        {'id': 5, 'question': 'What does COUNT(*) return?', 'options': ['Sum of values', 'Number of rows', 'Average', 'Maximum'], 'answer': 'Number of rows', 'difficulty': 'Easy', 'topic': 'Functions'},
        {'id': 6, 'question': 'Which is used to remove duplicate values?', 'options': ['UNIQUE', 'DISTINCT', 'DIFFERENT', 'REMOVE'], 'answer': 'DISTINCT', 'difficulty': 'Easy', 'topic': 'Queries'},
        {'id': 7, 'question': 'What is a foreign key?', 'options': ['Primary key in another table', 'Unique key', 'Index key', 'Composite key'], 'answer': 'Primary key in another table', 'difficulty': 'Easy', 'topic': 'Keys'},
        {'id': 8, 'question': 'Which normal form removes transitive dependencies?', 'options': ['1NF', '2NF', '3NF', 'BCNF'], 'answer': '3NF', 'difficulty': 'Hard', 'topic': 'Normalization'},
        {'id': 9, 'question': 'What is the default order of ORDER BY?', 'options': ['Descending', 'Ascending', 'Random', 'No default'], 'answer': 'Ascending', 'difficulty': 'Easy', 'topic': 'Clauses'},
        {'id': 10, 'question': 'Which command modifies existing data?', 'options': ['INSERT', 'UPDATE', 'CREATE', 'ALTER'], 'answer': 'UPDATE', 'difficulty': 'Easy', 'topic': 'Commands'}
    ],
    'Aptitude': [
        {'id': 1, 'question': 'If 3x = 27, what is x?', 'options': ['6', '9', '12', '3'], 'answer': '9', 'difficulty': 'Easy', 'topic': 'Algebra'},
        {'id': 2, 'question': 'What is 20% of 150?', 'options': ['25', '30', '35', '40'], 'answer': '30', 'difficulty': 'Easy', 'topic': 'Percentage'},
        {'id': 3, 'question': 'A train travels 300km in 5 hours. What is its speed?', 'options': ['50 km/h', '60 km/h', '70 km/h', '80 km/h'], 'answer': '60 km/h', 'difficulty': 'Easy', 'topic': 'Speed'},
        {'id': 4, 'question': 'What is the square root of 144?', 'options': ['10', '11', '12', '14'], 'answer': '12', 'difficulty': 'Easy', 'topic': 'Numbers'},
        {'id': 5, 'question': 'If 5 workers complete a task in 10 days, how many days for 10 workers?', 'options': ['3 days', '4 days', '5 days', '6 days'], 'answer': '5 days', 'difficulty': 'Medium', 'topic': 'Work'},
        {'id': 6, 'question': 'What comes next: 2, 6, 12, 20, ?', 'options': ['28', '30', '32', '36'], 'answer': '30', 'difficulty': 'Medium', 'topic': 'Series'},
        {'id': 7, 'question': 'A person buys for 500 and sells for 550. What is profit %?', 'options': ['8%', '10%', '12%', '15%'], 'answer': '10%', 'difficulty': 'Easy', 'topic': 'Profit Loss'},
        {'id': 8, 'question': 'What is the average of 10, 20, 30, 40?', 'options': ['20', '25', '30', '35'], 'answer': '25', 'difficulty': 'Easy', 'topic': 'Average'},
        {'id': 9, 'question': 'If 40% of a number is 80, what is the number?', 'options': ['150', '180', '200', '250'], 'answer': '200', 'difficulty': 'Medium', 'topic': 'Percentage'},
        {'id': 10, 'question': 'What is 15% of 200?', 'options': ['25', '30', '35', '40'], 'answer': '30', 'difficulty': 'Easy', 'topic': 'Percentage'}
    ],
    'React': [
        {'id': 1, 'question': 'What is JSX?', 'options': ['JavaScript XML', 'Java Syntax Extension', 'JSON Extra', 'JavaScript Extra'], 'answer': 'JavaScript XML', 'difficulty': 'Easy', 'topic': 'Basics'},
        {'id': 2, 'question': 'Which hook is used for side effects?', 'options': ['useState', 'useEffect', 'useContext', 'useReducer'], 'answer': 'useEffect', 'difficulty': 'Easy', 'topic': 'Hooks'},
        {'id': 3, 'question': 'What is the virtual DOM?', 'options': ['Direct DOM manipulation', 'Lightweight copy of DOM', 'Browser DOM', 'Server DOM'], 'answer': 'Lightweight copy of DOM', 'difficulty': 'Medium', 'topic': 'Core'},
        {'id': 4, 'question': 'Which method is used to update state?', 'options': ['updateState()', 'setState()', 'changeState()', 'modifyState()'], 'answer': 'setState()', 'difficulty': 'Easy', 'topic': 'State'},
        {'id': 5, 'question': 'What is a component?', 'options': ['Function only', 'Class only', 'Function or Class returning JSX', 'HTML element'], 'answer': 'Function or Class returning JSX', 'difficulty': 'Easy', 'topic': 'Basics'},
        {'id': 6, 'question': 'What is props?', 'options': ['Internal data', 'Read-only data passed from parent', 'State', 'Method'], 'answer': 'Read-only data passed from parent', 'difficulty': 'Easy', 'topic': 'Props'},
        {'id': 7, 'question': 'Which is NOT a React hook?', 'options': ['useMemo', 'useCallback', 'useHTTP', 'useRef'], 'answer': 'useHTTP', 'difficulty': 'Medium', 'topic': 'Hooks'},
        {'id': 8, 'question': 'What is conditional rendering?', 'options': ['Showing elements based on condition', 'Loop rendering', 'Error rendering', 'Style rendering'], 'answer': 'Showing elements based on condition', 'difficulty': 'Easy', 'topic': 'Rendering'},
        {'id': 9, 'question': 'What is Redux?', 'options': ['Database', 'State management library', 'Router', 'Testing library'], 'answer': 'State management library', 'difficulty': 'Medium', 'topic': 'State Management'},
        {'id': 10, 'question': 'What is React Router used for?', 'options': ['Database', 'Routing', 'HTTP requests', 'Animations'], 'answer': 'Routing', 'difficulty': 'Easy', 'topic': 'Routing'}
    ],
    'Java': [
        {'id': 1, 'question': 'What is the size of int in Java?', 'options': ['8 bits', '16 bits', '32 bits', '64 bits'], 'answer': '32 bits', 'difficulty': 'Easy', 'topic': 'Data Types'},
        {'id': 2, 'question': 'Which keyword is used to inherit a class?', 'options': ['implements', 'extends', 'inherits', 'derives'], 'answer': 'extends', 'difficulty': 'Easy', 'topic': 'OOP'},
        {'id': 3, 'question': 'What is polymorphism?', 'options': ['Multiple forms', 'Data hiding', 'Code reuse', 'Inheritance'], 'answer': 'Multiple forms', 'difficulty': 'Medium', 'topic': 'OOP'},
        {'id': 4, 'question': 'Which is not a primitive type?', 'options': ['int', 'float', 'String', 'boolean'], 'answer': 'String', 'difficulty': 'Easy', 'topic': 'Data Types'},
        {'id': 5, 'question': 'What is encapsulation?', 'options': ['Hiding data', 'Inheritance', 'Polymorphism', 'Abstraction'], 'answer': 'Hiding data', 'difficulty': 'Medium', 'topic': 'OOP'},
        {'id': 6, 'question': 'Which collection allows duplicate elements?', 'options': ['Set', 'List', 'Map', 'Queue'], 'answer': 'List', 'difficulty': 'Easy', 'topic': 'Collections'},
        {'id': 7, 'question': 'What is the entry point of a Java program?', 'options': ['start()', 'main()', 'run()', 'init()'], 'answer': 'main()', 'difficulty': 'Easy', 'topic': 'Basics'},
        {'id': 8, 'question': 'Which keyword prevents inheritance?', 'options': ['final', 'static', 'private', 'protected'], 'answer': 'final', 'difficulty': 'Easy', 'topic': 'OOP'},
        {'id': 9, 'question': 'What is an interface?', 'options': ['Class', 'Contract with abstract methods', 'Object', 'Package'], 'answer': 'Contract with abstract methods', 'difficulty': 'Medium', 'topic': 'OOP'},
        {'id': 10, 'question': 'What is exception handling?', 'options': ['Error prevention', 'Handling runtime errors', 'Compiling code', 'Testing'], 'answer': 'Handling runtime errors', 'difficulty': 'Medium', 'topic': 'Exception Handling'}
    ]
}

@feature_bp.route('/mock-test/<skill>', methods=['GET'])
@student_required
def get_mock_test(skill):
    """Get mock test questions for a skill"""
    questions = MOCK_QUESTIONS.get(skill, [])
    
    if not questions:
        return jsonify({
            'success': False,
            'error': f'No questions available for {skill}',
            'available_skills': list(MOCK_QUESTIONS.keys())
        }), 404
    
    # Return 5 random questions
    selected = random.sample(questions, min(5, len(questions)))
    
    # Remove answers from response
    questions_list = []
    for q in selected:
        q_copy = q.copy()
        q_copy.pop('answer', None)
        questions_list.append(q_copy)
    
    return jsonify({
        'success': True,
        'skill': skill,
        'total_questions': len(questions),
        'questions': questions_list
    })

@feature_bp.route('/mock-test/submit', methods=['POST'])
@student_required
def submit_mock_test():
    """Submit mock test answers and get score"""
    data = request.get_json()
    
    skill = data.get('skill')
    answers = data.get('answers', {})
    
    if not skill or not answers:
        return jsonify({'error': 'Skill and answers required'}), 400
    
    questions = MOCK_QUESTIONS.get(skill, [])
    
    if not questions:
        return jsonify({'error': 'Invalid skill'}), 404
    
    # Calculate score
    correct = 0
    incorrect = 0
    results = []
    
    for q in questions:
        q_id = str(q['id'])
        user_answer = answers.get(q_id)
        correct_answer = q['answer']
        
        is_correct = user_answer == correct_answer
        if is_correct:
            correct += 1
        else:
            incorrect += 1
        
        results.append({
            'question': q['question'],
            'options': q['options'],
            'your_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'difficulty': q['difficulty'],
            'topic': q['topic']
        })
    
    total = 5
    score_percentage = (correct / total) * 100
    
    # Generate improvement suggestions
    suggestions = []
    if score_percentage < 60:
        suggestions.append(f"Practice more {skill} fundamentals")
        suggestions.append("Review the topics you got wrong")
    if score_percentage >= 60 and score_percentage < 80:
        suggestions.append("Good progress! Keep practicing")
    if score_percentage >= 80:
        suggestions.append("Excellent! You have strong fundamentals")
    
    return jsonify({
        'success': True,
        'skill': skill,
        'score': correct,
        'total': total,
        'percentage': score_percentage,
        'correct': correct,
        'incorrect': incorrect,
        'results': results,
        'suggestions': suggestions
    })

@feature_bp.route('/mock-test/skills', methods=['GET'])
@student_required
def get_mock_test_skills():
    """Get available skills for mock tests"""
    return jsonify({
        'success': True,
        'skills': list(MOCK_QUESTIONS.keys())
    })

# ==================== SKILL DEMAND ANALYTICS ====================

@feature_bp.route('/analytics/skill-demand', methods=['GET'])
def get_skill_demand():
    """Get skill demand analytics from all job postings"""
    # Get all job skills
    job_skills = JobSkill.query.all()
    
    # Count skill occurrences
    skill_counts = {}
    for js in job_skills:
        skill = js.skill_name.lower()
        if skill in skill_counts:
            skill_counts[skill] += 1
        else:
            skill_counts[skill] = 1
    
    # Sort by count
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Categorize skills
    high_demand = []
    medium_demand = []
    low_demand = []
    
    max_count = sorted_skills[0][1] if sorted_skills else 1
    
    for skill, count in sorted_skills:
        percentage = (count / max_count) * 100
        
        skill_data = {
            'skill': skill.title(),
            'count': count,
            'percentage': round(percentage, 2)
        }
        
        if percentage >= 60:
            high_demand.append(skill_data)
        elif percentage >= 30:
            medium_demand.append(skill_data)
        else:
            low_demand.append(skill_data)
    
    # Get total jobs
    total_jobs = Job.query.count()
    
    return jsonify({
        'success': True,
        'total_jobs': total_jobs,
        'total_unique_skills': len(sorted_skills),
        'high_demand_skills': high_demand[:15],
        'medium_demand_skills': medium_demand[:10],
        'low_demand_skills': low_demand[:10],
        'all_skills': [{'skill': s[0].title(), 'count': s[1]} for s in sorted_skills[:30]]
    })

@feature_bp.route('/analytics/skill-demand/hr', methods=['GET'])
@hr_required
def get_skill_demand_for_hr():
    """Get skill demand analytics for HR's own jobs"""
    claims = get_jwt()
    hr_id = claims.get('user_id')
    
    # Get HR's jobs
    hr_jobs = Job.query.filter_by(hr_id=hr_id).all()
    job_ids = [j.id for j in hr_jobs]
    
    if not job_ids:
        return jsonify({
            'success': True,
            'message': 'No jobs posted yet',
            'total_jobs': 0,
            'high_demand_skills': [],
            'medium_demand_skills': [],
            'low_demand_skills': []
        })
    
    # Get skills for HR's jobs only
    job_skills = JobSkill.query.filter(JobSkill.job_id.in_(job_ids)).all()
    
    skill_counts = {}
    for js in job_skills:
        skill = js.skill_name.lower()
        if skill in skill_counts:
            skill_counts[skill] += 1
        else:
            skill_counts[skill] = 1
    
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    
    high_demand = [{'skill': s[0].title(), 'count': s[1]} for s in sorted_skills if s[1] >= 2]
    medium_demand = [{'skill': s[0].title(), 'count': s[1]} for s in sorted_skills if s[1] == 1]
    low_demand = []
    
    return jsonify({
        'success': True,
        'total_jobs': len(hr_jobs),
        'high_demand_skills': high_demand,
        'medium_demand_skills': medium_demand,
        'low_demand_skills': low_demand
    })
