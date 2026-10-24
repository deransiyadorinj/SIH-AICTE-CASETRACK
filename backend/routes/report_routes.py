import io
import csv
from flask import Blueprint, jsonify, request, Response
from backend.services.stats_service import get_dashboard_charts
from backend.services.complaint_service import get_complaints
from backend.services.auth_service import get_current_user

report_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@report_bp.route('/analytics', methods=['GET'])
def analytics():
    data = get_dashboard_charts()
    return jsonify({'success': True, 'data': data})

@report_bp.route('/export', methods=['GET'])
def export_csv():
    report_type = request.args.get('type', 'complaints')
    user = get_current_user()

    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'complaints':
        complaints = get_complaints({}, user)
        writer.writerow(['Complaint ID', 'Subject', 'Institution', 'Institution ID', 'Category', 'Bureau', 'Priority', 'Status', 'Submission Date', 'Last Updated', 'Resolution Details'])
        for c in complaints:
            writer.writerow([
                c.get('id', ''),
                c.get('subject', ''),
                c.get('institution', ''),
                c.get('institution_id', ''),
                c.get('category', ''),
                c.get('bureau', 'Unassigned'),
                c.get('priority', ''),
                c.get('status', ''),
                c.get('submissionDate', ''),
                c.get('lastUpdated', ''),
                c.get('resolution_details', '')
            ])
        filename = "aicte_complaints_report.csv"
    else:
        charts = get_dashboard_charts()
        writer.writerow(['Month', 'Filed Complaints', 'Resolved Complaints'])
        for m in charts['monthlyTrends']:
            writer.writerow([m['month'], m['complaints'], m['resolved']])
        filename = "aicte_analytics_report.csv"

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )
