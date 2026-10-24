from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from backend.database import query_db, execute_db
from backend.services.auth_service import admin_required

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('', methods=['GET'])
def list_users():
    rows = query_db("""
    SELECT id, name, email, role, department, designation, institution_ref, status, last_login as lastLogin, created_at as createdAt
    FROM users
    ORDER BY id ASC;
    """)
    return jsonify({'success': True, 'data': rows})

@user_bp.route('', methods=['POST'])
def add_user():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    role = data.get('role', 'Viewer')
    department = data.get('department', '').strip()
    status = data.get('status', 'Active')
    password = data.get('password', 'password123')

    if not name or not email:
        return jsonify({'success': False, 'message': 'Name and email are required.'}), 400

    existing = query_db("SELECT id FROM users WHERE email = ?;", (email,), one=True)
    if existing:
        return jsonify({'success': False, 'message': f'Email {email} is already in use.'}), 409

    hashed_pw = generate_password_hash(password)
    user_id = execute_db("""
    INSERT INTO users (name, email, password_hash, role, department, status)
    VALUES (?, ?, ?, ?, ?, ?);
    """, (name, email, hashed_pw, role, department, status))

    new_user = query_db("""
    SELECT id, name, email, role, department, status, last_login as lastLogin
    FROM users WHERE id = ?;
    """, (user_id,), one=True)

    return jsonify({'success': True, 'message': 'User created successfully', 'user': new_user}), 201

@user_bp.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    
    existing = query_db("SELECT id FROM users WHERE id = ?;", (user_id,), one=True)
    if not existing:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    updates = []
    params = []

    if 'role' in data:
        updates.append("role = ?")
        params.append(data['role'])
    if 'department' in data:
        updates.append("department = ?")
        params.append(data['department'])
    if 'status' in data:
        updates.append("status = ?")
        params.append(data['status'])
    if 'designation' in data:
        updates.append("designation = ?")
        params.append(data['designation'])

    if not updates:
        return jsonify({'success': False, 'message': 'No fields to update'}), 400

    params.append(user_id)
    execute_db(f"UPDATE users SET {', '.join(updates)} WHERE id = ?;", tuple(params))

    updated_user = query_db("""
    SELECT id, name, email, role, department, designation, status, last_login as lastLogin
    FROM users WHERE id = ?;
    """, (user_id,), one=True)

    return jsonify({'success': True, 'message': 'User updated successfully', 'user': updated_user})
