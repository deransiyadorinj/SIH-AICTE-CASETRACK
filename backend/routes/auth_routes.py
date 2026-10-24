from flask import Blueprint, request, jsonify, session
from backend.services.auth_service import authenticate_user, get_current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

    user = authenticate_user(email, password)
    if not user:
        return jsonify({'success': False, 'message': 'Invalid credentials. Please verify email and password.'}), 401

    session['user_id'] = user['id']
    session.permanent = True

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': user,
        'token': f"session-{user['id']}"
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/me', methods=['GET'])
def me():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'user': None}), 401
    return jsonify({'success': True, 'user': user})
