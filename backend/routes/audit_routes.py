from flask import Blueprint, jsonify, request
from backend.database import query_db

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit-logs')

@audit_bp.route('', methods=['GET'])
def list_audit_logs():
    search = request.args.get('search', '').strip()
    action = request.args.get('action', '').strip()

    query = """
    SELECT id, user_name as user, action, complaint_id as complaintId, details, created_at as timestamp
    FROM audit_logs
    WHERE 1=1
    """
    params = []
    if search:
        q = f"%{search}%"
        query += " AND (user_name LIKE ? OR complaint_id LIKE ? OR details LIKE ?)"
        params.extend([q, q, q])
    if action:
        query += " AND action = ?"
        params.append(action)

    query += " ORDER BY id DESC LIMIT 100;"
    rows = query_db(query, tuple(params))
    return jsonify({'success': True, 'data': rows})
