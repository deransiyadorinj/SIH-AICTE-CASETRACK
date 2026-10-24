from flask import Blueprint, jsonify
from backend.services.stats_service import get_dashboard_stats, get_dashboard_charts

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
def stats():
    data = get_dashboard_stats()
    return jsonify({'success': True, 'data': data})

@dashboard_bp.route('/charts', methods=['GET'])
def charts():
    data = get_dashboard_charts()
    return jsonify({'success': True, 'data': data})
