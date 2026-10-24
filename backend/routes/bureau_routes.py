from flask import Blueprint, jsonify
from backend.database import query_db

bureau_bp = Blueprint('bureaus', __name__, url_prefix='/api/bureaus')

@bureau_bp.route('', methods=['GET'])
def list_bureaus():
    rows = query_db("""
    SELECT 
        b.id, b.name, b.head, b.email, b.description,
        COUNT(c.id) as totalComplaints,
        SUM(CASE WHEN c.status IN ('New', 'Under Review', 'In Progress', 'Overdue') THEN 1 ELSE 0 END) as pendingCases,
        SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolvedCases
    FROM bureaus b
    LEFT JOIN complaints c ON b.id = c.bureau_id
    GROUP BY b.id, b.name, b.head, b.email, b.description;
    """)
    for r in rows:
        r['totalComplaints'] = r['totalComplaints'] or 0
        r['pendingCases'] = r['pendingCases'] or 0
        r['resolvedCases'] = r['resolvedCases'] or 0
    return jsonify({'success': True, 'data': rows})

@bureau_bp.route('/<bureau_id>/complaints', methods=['GET'])
def bureau_complaints(bureau_id):
    rows = query_db("""
    SELECT c.*, b.name as bureau
    FROM complaints c
    JOIN bureaus b ON c.bureau_id = b.id
    WHERE b.id = ? OR b.name = ?;
    """, (bureau_id, bureau_id))
    return jsonify({'success': True, 'data': rows})
