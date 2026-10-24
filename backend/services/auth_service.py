from functools import wraps
from flask import session, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from backend.database import query_db, execute_db

def authenticate_user(email, password):
    user = query_db("SELECT * FROM users WHERE email = ? AND status = 'Active';", (email,), one=True)
    if not user:
        return None
    if not check_password_hash(user['password_hash'], password):
        return None
    
    # Update last login timestamp
    execute_db("UPDATE users SET last_login = datetime('now', 'localtime') WHERE id = ?;", (user['id'],))
    
    # Return user object without password_hash
    user_dict = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role'],
        'department': user['department'],
        'designation': user['designation'],
        'institution_ref': user['institution_ref'],
        'status': user['status']
    }
    return user_dict

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    user = query_db("SELECT id, name, email, role, department, designation, institution_ref, status FROM users WHERE id = ?;", (user_id,), one=True)
    return user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Authentication required. Please sign in.'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Authentication required. Please sign in.'}), 401
        if user['role'] not in ('Cloud Architect', 'Super Admin', 'Admin', 'Reviewer', 'Analyst'):
            return jsonify({'success': False, 'message': 'Forbidden: Administrative privileges required.'}), 403
        return f(*args, **kwargs)
    return decorated_function
