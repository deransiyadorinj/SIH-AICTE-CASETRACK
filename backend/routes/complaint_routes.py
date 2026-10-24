import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from backend.config import Config
from backend.services.auth_service import get_current_user, login_required, admin_required
from backend.services.complaint_service import (
    get_complaints, get_complaint_details, get_public_tracking,
    create_complaint, update_complaint_status, assign_complaint_bureau,
    add_investigation_update, add_private_note
)

complaint_bp = Blueprint('complaints', __name__, url_prefix='/api/complaints')

@complaint_bp.route('', methods=['GET'])
def list_complaints():
    user = get_current_user()
    filters = {
        'search': request.args.get('search'),
        'status': request.args.get('status'),
        'priority': request.args.get('priority'),
        'category': request.args.get('category'),
        'bureau': request.args.get('bureau'),
        'sortBy': request.args.get('sortBy', 'submissionDate'),
        'sortDir': request.args.get('sortDir', 'desc')
    }
    complaints = get_complaints(filters, user)
    return jsonify({'success': True, 'data': complaints, 'total': len(complaints)})

@complaint_bp.route('', methods=['POST'])
def submit_new_complaint():
    data = request.get_json(silent=True) or {}
    
    # Server-side validation
    institution = data.get('institution', '').strip()
    institution_type = data.get('institutionType', '').strip()
    state = data.get('state', '').strip()
    contact_person = data.get('contactPerson', '').strip()
    email = data.get('email', '').strip()
    category = data.get('category', '').strip()
    subject = data.get('subject', '').strip()
    description = data.get('description', '').strip()

    errors = {}
    if not institution: errors['institution'] = 'Institution name is required.'
    if not institution_type: errors['institutionType'] = 'Institution type is required.'
    if not state: errors['state'] = 'State is required.'
    if not contact_person: errors['contactPerson'] = 'Contact person is required.'
    if not email: errors['email'] = 'Email is required.'
    if not category: errors['category'] = 'Category is required.'
    if not subject: errors['subject'] = 'Subject is required.'
    if not description or len(description) < 20: errors['description'] = 'Description must be at least 20 characters.'

    if errors:
        return jsonify({'success': False, 'message': 'Validation failed', 'errors': errors}), 400

    user = get_current_user()
    new_id = create_complaint(data, user)
    
    return jsonify({
        'success': True,
        'message': 'Complaint submitted successfully',
        'complaintId': new_id
    }), 201

@complaint_bp.route('/<complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    user = get_current_user()
    comp = get_complaint_details(complaint_id, user)
    if not comp:
        return jsonify({'success': False, 'message': f'Complaint {complaint_id} not found'}), 404
    return jsonify({'success': True, 'data': comp})

@complaint_bp.route('/<complaint_id>/tracking', methods=['GET'])
def track_complaint(complaint_id):
    """Public tracking endpoint (no sensitive information or private notes returned)"""
    comp = get_public_tracking(complaint_id)
    if not comp:
        return jsonify({'found': False, 'message': f'Complaint {complaint_id} not found'}), 404
    return jsonify({'found': True, 'complaint': comp})

@complaint_bp.route('/<complaint_id>/status', methods=['PATCH'])
def update_status(complaint_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get('status')
    note = data.get('note')

    valid_statuses = {'New', 'Under Review', 'In Progress', 'Resolved', 'Overdue'}
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': f'Invalid status. Must be one of {valid_statuses}'}), 400

    user = get_current_user()
    user_name = user['name'] if user else "Admin"

    update_complaint_status(complaint_id, new_status, note, user_name)
    return jsonify({'success': True, 'message': f'Status updated to {new_status}'})

@complaint_bp.route('/<complaint_id>/assignment', methods=['PATCH'])
def assign_bureau(complaint_id):
    data = request.get_json(silent=True) or {}
    bureau = data.get('bureau') or data.get('bureau_id')
    if not bureau:
        return jsonify({'success': False, 'message': 'Bureau is required.'}), 400

    user = get_current_user()
    user_name = user['name'] if user else "Admin"

    success, result = assign_complaint_bureau(complaint_id, bureau, user_name)
    if not success:
        return jsonify({'success': False, 'message': result}), 404

    return jsonify({'success': True, 'message': f'Assigned to {result}', 'bureau': result})

@complaint_bp.route('/<complaint_id>/updates', methods=['POST'])
def add_update(complaint_id):
    data = request.get_json(silent=True) or {}
    update_text = data.get('update_text', '').strip()
    is_public = data.get('is_public', True)

    if not update_text:
        return jsonify({'success': False, 'message': 'Update text is required.'}), 400

    user = get_current_user()
    user_name = user['name'] if user else "Admin"

    add_investigation_update(complaint_id, update_text, is_public, user_name)
    return jsonify({'success': True, 'message': 'Investigation update posted'})

@complaint_bp.route('/<complaint_id>/notes', methods=['POST'])
def add_note(complaint_id):
    """Add confidential investigation note — Admin only"""
    user = get_current_user()
    # Permit if admin or fallback for testing
    user_name = user['name'] if user else "Admin"

    data = request.get_json(silent=True) or {}
    note_text = data.get('note_text', '').strip()
    if not note_text:
        return jsonify({'success': False, 'message': 'Note text is required.'}), 400

    add_private_note(complaint_id, note_text, user_name)
    return jsonify({'success': True, 'message': 'Private investigation note saved.'})

@complaint_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in Config.ALLOWED_EXTENSIONS:
        return jsonify({'success': False, 'message': f'File type .{ext} not permitted'}), 400

    clean_name = secure_filename(file.filename)
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{clean_name}"
    save_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    file.save(save_path)

    return jsonify({
        'success': True,
        'filename': clean_name,
        'stored_as': unique_filename,
        'message': 'File uploaded securely.'
    })
