from flask import Blueprint, jsonify, request
from backend.database import query_db, execute_db

notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notification_bp.route('', methods=['GET'])
def list_notifications():
    rows = query_db("""
    SELECT id, type, title, message, complaint_id as complaintId, is_read as read, created_at as time
    FROM notifications
    ORDER BY id DESC;
    """)
    # Convert read from 0/1 to boolean
    for r in rows:
        r['read'] = bool(r['read'])
    return jsonify({'success': True, 'data': rows})

@notification_bp.route('/<int:notif_id>/read', methods=['PATCH'])
def mark_read(notif_id):
    execute_db("UPDATE notifications SET is_read = 1 WHERE id = ?;", (notif_id,))
    return jsonify({'success': True, 'message': 'Notification marked as read'})

@notification_bp.route('/read-all', methods=['POST'])
def mark_all_read():
    execute_db("UPDATE notifications SET is_read = 1;")
    return jsonify({'success': True, 'message': 'All notifications marked as read'})
