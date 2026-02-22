import re
import json

# Common skills database
COMMON_SKILLS = [
    # Programming Languages
    'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'typescript', 'php', 'swift', 'kotlin',
    # Web Technologies
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'bootstrap',
    'jquery', 'ajax', 'rest api', 'graphql', 'webpack', 'sass', 'less',
    # Database
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'firebase', 'elasticsearch',
    # Data Science & ML
    'machine learning', 'deep learning', 'data science', 'data analysis', 'numpy', 'pandas', 'scikit-learn',
    'tensorflow', 'pytorch', 'keras', 'nlp', 'computer vision', 'data visualization',
    # DevOps & Cloud
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'ci/cd',
    'devops', 'linux', 'unix', 'bash', 'terraform', 'ansible',
    # Tools
    'jira', 'confluence', 'figma', 'photoshop', 'illustrator', 'postman', 'selenium',
    # Soft Skills
    'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
    # Other
    'agile', 'scrum', 'oops', 'dsa', 'algorithm', 'testing', 'unit testing', 'debugging'
]

# Education keywords
EDUCATION_KEYWORDS = [
    'bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'b.e', 'm.e', 'bca', 'mca',
    'bsc', 'msc', 'diploma', 'degree', 'university', 'institute', 'college'
]

# Experience keywords
EXPERIENCE_KEYWORDS = [
    'experience', 'internship', 'project', 'work', 'employment', 'role', 'responsibility',
    'achievement', 'company', 'organization', 'team'
]

def extract_text_from_file(file_path):
    """
    Extract text from PDF or DOCX file
    """
    import os
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.pdf':
            return extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return extract_text_from_docx(file_path)
        else:
            return ""
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_text_from_pdf(file_path):
    """Extract text from PDF using PyPDF2"""
    try:
        import PyPDF2
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return extract_text_simple(file_path)

def extract_text_from_docx(file_path):
    """Extract text from DOCX using python-docx"""
    try:
        from docx import Document
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return ""

def extract_text_simple(file_path):
    """Simple text extraction fallback"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ""

def extract_skills(text):
    """
    Extract skills from resume text using keyword matching
    """
    text_lower = text.lower()
    found_skills = []
    
    for skill in COMMON_SKILLS:
        if skill in text_lower:
            # Capitalize skill name for display
            found_skills.append(skill.title())
    
    # Remove duplicates and return
    return list(set(found_skills))

def extract_education(text):
    """
    Extract education information from resume text
    """
    text_lower = text.lower()
    education_info = []
    
    # Find education section
    lines = text.split('\n')
    in_education_section = False
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        
        # Check if we're in education section
        if 'education' in line_lower or 'academic' in line_lower:
            in_education_section = True
            continue
        
        if in_education_section:
            # Check for education keywords
            for keyword in EDUCATION_KEYWORDS:
                if keyword in line_lower and len(line.strip()) > 5:
                    education_info.append(line.strip())
                    break
        
        # Stop if we hit another section
        if in_education_section and any(x in line_lower for x in ['experience', 'skills', 'projects']):
            break
    
    # If no structured education found, extract using patterns
    if not education_info:
        # Pattern for degree/year
        degree_patterns = [
            r'(b\.?tech|m\.?tech|b\.?e|m\.?e|b\.?sc|m\.?sc|b\.?ca|m\.?ca)\s*[-–]?\s*(\d{4})?',
            r'(bachelor|master|phd)\s*(of|degree)?\s*(\w+)?\s*[-–]?\s*(\d{4})?',
            r'(\d{4})\s*[-–]\s*(\d{4})?'
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    edu = ' '.join([m for m in match if m])
                    if edu:
                        education_info.append(edu)
                else:
                    education_info.append(match)
    
    return ' | '.join(education_info[:3]) if education_info else "Not found"

def extract_experience(text):
    """
    Extract experience information from resume text
    """
    lines = text.split('\n')
    experience_info = []
    in_experience_section = False
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if we're in experience section
        if 'experience' in line_lower or 'work history' in line_lower:
            in_experience_section = True
            continue
        
        if in_experience_section:
            if len(line.strip()) > 10:
                experience_info.append(line.strip())
        
        # Stop if we hit another section
        if in_experience_section and any(x in line_lower for x in ['skills', 'education', 'projects', 'achievements']):
            break
    
    return ' | '.join(experience_info[:5]) if experience_info else "Fresher"

def parse_resume(text):
    """
    Main function to parse resume text
    Returns JSON with skills, education, experience
    """
    skills = extract_skills(text)
    education = extract_education(text)
    experience = extract_experience(text)
    
    return {
        'skills': skills,
        'education': education,
        'experience': experience
    }

def calculate_resume_score(resume_data, job_requirements=None):
    """
    Calculate resume score out of 100
    
    Factors:
    - Skills count (max 25 points)
    - Keywords match with job (max 25 points)
    - Education details (max 15 points)
    - Experience section (max 15 points)
    - Formatting keywords (max 20 points)
    """
    score = 0
    suggestions = []
    
    # Skills score (max 25)
    skills = resume_data.get('skills', [])
    skills_count = len(skills)
    if skills_count >= 10:
        score += 25
        suggestions.append("Great skill set!")
    elif skills_count >= 5:
        score += 15
        suggestions.append("Add more technical skills")
    else:
        score += 5
        suggestions.append("Add more skills to improve visibility")
    
    # Job requirements match (max 25)
    if job_requirements:
        job_skills = [s.lower() for s in job_requirements]
        matched_skills = [s for s in skills if s.lower() in job_skills]
        match_ratio = len(matched_skills) / len(job_skills) if job_skills else 0
        score += int(match_ratio * 25)
        if match_ratio < 0.5:
            suggestions.append(f"Add these skills: {', '.join([s for s in job_skills if s.lower() not in [x.lower() for x in skills]][:5])}")
    
    # Education score (max 15)
    education = resume_data.get('education', '')
    if education and education != 'Not found':
        score += 15
    else:
        suggestions.append("Add education details")
    
    # Experience score (max 15)
    experience = resume_data.get('experience', '')
    if experience and experience != 'Fresher':
        score += 15
    else:
        suggestions.append("Add project/internship experience")
    
    # Formatting keywords (max 20)
    formatting_keywords = ['project', 'achievement', 'responsibility', 'technology', 'framework']
    text = f"{education} {experience}".lower()
    keyword_count = sum(1 for kw in formatting_keywords if kw in text)
    score += min(keyword_count * 4, 20)
    
    return min(score, 100), suggestions
