from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import HR, Student

def role_required(allowed_roles):
    """
    Decorator to check if user has required role
    Usage: @role_required(['hr']) or @role_required(['student'])
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            claims = get_jwt()
            
            user_role = claims.get('role')
            user_id = claims.get('user_id')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Access denied. You do not have permission to access this resource.',
                    'required_role': allowed_roles,
                    'your_role': user_role
                }), 403
            
            # Verify user still exists
            if user_role == 'hr':
                user = HR.query.get(user_id)
                if not user:
                    return jsonify({'error': 'HR account not found'}), 401
            elif user_role == 'student':
                user = Student.query.get(user_id)
                if not user:
                    return jsonify({'error': 'Student account not found'}), 401
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def hr_required(fn):
    """Decorator to require HR role"""
    return role_required(['hr'])(fn)

def student_required(fn):
    """Decorator to require Student role"""
    return role_required(['student'])(fn)

def get_current_user():
    """
    Get current user from JWT token
    Returns tuple: (user_object, role)
    """
    verify_jwt_in_request()
    claims = get_jwt()
    user_id = claims.get('user_id')
    user_role = claims.get('role')
    
    if user_role == 'hr':
        return HR.query.get(user_id), 'hr'
    elif user_role == 'student':
        return Student.query.get(user_id), 'student'
    return None, None

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Password validation - min 6 characters"""
    return len(password) >= 6
