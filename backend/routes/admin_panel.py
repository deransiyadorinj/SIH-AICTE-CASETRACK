import os
import sqlite3
from pathlib import Path
from flask import Blueprint, render_template_string, request, jsonify, redirect, url_for
from backend.config import Config
from backend.database import query_db, get_db
from backend.init_db import seed_database

admin_panel_bp = Blueprint('admin_panel', __name__, url_prefix='/admin')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AICTE CASETRACK — Backend Administration Console</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #090909;
            --bg-card: #141414;
            --bg-subtle: #1e1e1e;
            --border: #282828;
            --border-strong: #383838;
            --text-primary: #ffffff;
            --text-secondary: #a3a3a3;
            --text-muted: #666666;
            --accent-blue: #3b82f6;
            --accent-green: #22c55e;
            --accent-amber: #f59e0b;
            --accent-red: #ef4444;
            --font-sans: 'Inter', -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-main);
            color: var(--text-primary);
            font-family: var(--font-sans);
            font-size: 13.5px;
            line-height: 1.5;
            padding: 24px 32px;
        }
        header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .brand-badge {
            background: #fff;
            color: #000;
            font-weight: 800;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 4px;
            letter-spacing: 0.05em;
        }
        .brand-title {
            font-size: 17px;
            font-weight: 700;
            letter-spacing: -0.01em;
        }
        .header-links {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 7px 14px;
            border-radius: 6px;
            font-size: 12.5px;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            border: 1px solid transparent;
            transition: 0.2s;
        }
        .btn-primary { background: #fff; color: #000; }
        .btn-primary:hover { background: #e0e0e0; }
        .btn-outline { background: transparent; border-color: var(--border-strong); color: #fff; }
        .btn-outline:hover { background: var(--bg-subtle); border-color: #555; }
        .btn-danger { background: rgba(239, 68, 68, 0.15); border-color: rgba(239, 68, 68, 0.3); color: #f87171; }
        .btn-danger:hover { background: rgba(239, 68, 68, 0.25); }

        .grid-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .stat-val { font-size: 26px; font-weight: 700; color: #fff; }
        .stat-label { font-size: 11.5px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }

        .tabs {
            display: flex;
            gap: 8px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
        }
        .tab-btn {
            padding: 10px 18px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 600;
            border-bottom: 2px solid transparent;
            margin-bottom: -1px;
            font-size: 13px;
        }
        .tab-btn:hover { color: #fff; }
        .tab-btn.active { color: #fff; border-bottom-color: #fff; }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
        }
        .card-title {
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .table-wrap {
            overflow-x: auto;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: #0d0d0d;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 12.5px;
        }
        th {
            background: #111;
            padding: 10px 14px;
            color: var(--text-secondary);
            font-weight: 600;
            border-bottom: 1px solid var(--border);
            white-space: nowrap;
        }
        td {
            padding: 10px 14px;
            border-bottom: 1px solid var(--border);
            color: var(--text-primary);
        }
        tr:hover td { background: var(--bg-subtle); }

        .font-mono { font-family: var(--font-mono); }
        .badge {
            display: inline-block;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }
        .badge-blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
        .badge-green { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
        .badge-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .badge-red { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

        .query-box textarea {
            width: 100%;
            height: 90px;
            background: #000;
            border: 1px solid var(--border-strong);
            border-radius: 6px;
            color: #4ade80;
            font-family: var(--font-mono);
            font-size: 13px;
            padding: 12px;
            outline: none;
            resize: vertical;
            margin-bottom: 10px;
        }
        .diag-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }
        .diag-item {
            background: #000;
            border: 1px solid var(--border);
            padding: 12px 16px;
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
        }
        .diag-label { color: var(--text-muted); font-size: 12px; }
        .diag-val { font-family: var(--font-mono); font-weight: 600; font-size: 12.5px; }
        .flash-msg {
            padding: 10px 16px;
            border-radius: 6px;
            margin-bottom: 20px;
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: #4ade80;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <span class="brand-badge">FLASK BACKEND</span>
            <span class="brand-title">AICTE CASETRACK | Administration Console</span>
        </div>
        <div class="header-links">
            <a href="http://localhost:3000/" target="_blank" class="btn btn-primary">Open React Frontend ↗</a>
            <a href="/api/health" target="_blank" class="btn btn-outline">API Health</a>
            <a href="/api/reports/export?type=complaints" class="btn btn-outline">Download CSV</a>
            <form action="/admin/reseed" method="POST" onsubmit="return confirm('Re-seed the SQLite database with fresh records?');" style="display:inline;">
                <button type="submit" class="btn btn-danger">Reset &amp; Re-seed DB</button>
            </form>
        </div>
    </header>

    {% if message %}
    <div class="flash-msg">{{ message }}</div>
    {% endif %}

    <!-- Top KPI Row -->
    <div class="grid-stats">
        <div class="stat-card">
            <div class="stat-val">{{ stats.complaints_count }}</div>
            <div class="stat-label">Total Complaints</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{{ stats.users_count }}</div>
            <div class="stat-label">Registered Users</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{{ stats.bureaus_count }}</div>
            <div class="stat-label">Bureaus &amp; Cells</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{{ stats.history_count }}</div>
            <div class="stat-label">Workflow Actions</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{{ stats.audit_count }}</div>
            <div class="stat-label">Audit Log Entries</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{{ stats.db_size_kb }} KB</div>
            <div class="stat-label">SQLite File Size</div>
        </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="tabs">
        <a href="/admin?tab=complaints" class="tab-btn {{ 'active' if active_tab == 'complaints' else '' }}">Complaints ({{ stats.complaints_count }})</a>
        <a href="/admin?tab=users" class="tab-btn {{ 'active' if active_tab == 'users' else '' }}">Users ({{ stats.users_count }})</a>
        <a href="/admin?tab=bureaus" class="tab-btn {{ 'active' if active_tab == 'bureaus' else '' }}">Bureaus ({{ stats.bureaus_count }})</a>
        <a href="/admin?tab=audit" class="tab-btn {{ 'active' if active_tab == 'audit' else '' }}">Audit Logs ({{ stats.audit_count }})</a>
        <a href="/admin?tab=query" class="tab-btn {{ 'active' if active_tab == 'query' else '' }}">SQL Query Runner</a>
        <a href="/admin?tab=diagnostics" class="tab-btn {{ 'active' if active_tab == 'diagnostics' else '' }}">System Diagnostics</a>
    </div>

    <!-- Tab 1: Complaints -->
    {% if active_tab == 'complaints' %}
    <div class="card">
        <div class="card-title">
            <span>Database Records: Complaints</span>
            <span style="font-size: 12px; color: var(--text-muted);">Showing all active cases in SQLite</span>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Institution</th>
                        <th>Category</th>
                        <th>Bureau</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Contact Email</th>
                        <th>Submission Date</th>
                        <th>Subject</th>
                    </tr>
                </thead>
                <tbody>
                    {% for c in complaints %}
                    <tr>
                        <td class="font-mono"><strong>{{ c.id }}</strong></td>
                        <td>{{ c.institution }}</td>
                        <td>{{ c.category }}</td>
                        <td>{{ c.bureau or 'Unassigned' }}</td>
                        <td>
                            {% if c.priority == 'Critical' %}
                                <span class="badge badge-red">Critical</span>
                            {% elif c.priority == 'High' %}
                                <span class="badge badge-amber">High</span>
                            {% elif c.priority == 'Medium' %}
                                <span class="badge badge-blue">Medium</span>
                            {% else %}
                                <span class="badge badge-green">Low</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if c.status == 'Resolved' %}
                                <span class="badge badge-green">Resolved</span>
                            {% elif c.status == 'In Progress' %}
                                <span class="badge badge-blue">In Progress</span>
                            {% elif c.status == 'Overdue' %}
                                <span class="badge badge-red">Overdue</span>
                            {% else %}
                                <span class="badge badge-amber">{{ c.status }}</span>
                            {% endif %}
                        </td>
                        <td>{{ c.email }}</td>
                        <td class="font-mono">{{ c.submission_date }}</td>
                        <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ c.subject }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    <!-- Tab 2: Users -->
    {% if active_tab == 'users' %}
    <div class="card">
        <div class="card-title">
            <span>Database Records: Users &amp; Personnel</span>
            <span style="font-size: 12px; color: var(--text-muted);">Stored with PBKDF2 Password Hashes</span>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Department</th>
                        <th>Designation</th>
                        <th>Status</th>
                        <th>Last Login</th>
                    </tr>
                </thead>
                <tbody>
                    {% for u in users %}
                    <tr>
                        <td class="font-mono">{{ u.id }}</td>
                        <td><strong>{{ u.name }}</strong></td>
                        <td class="font-mono">{{ u.email }}</td>
                        <td><span class="badge badge-blue">{{ u.role }}</span></td>
                        <td>{{ u.department or '—' }}</td>
                        <td>{{ u.designation or '—' }}</td>
                        <td><span class="badge badge-green">{{ u.status }}</span></td>
                        <td class="font-mono">{{ u.last_login or 'Never' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    <!-- Tab 3: Bureaus -->
    {% if active_tab == 'bureaus' %}
    <div class="card">
        <div class="card-title">
            <span>Database Records: Administrative Bureaus &amp; Cells</span>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Bureau Name</th>
                        <th>Bureau Head</th>
                        <th>Contact Email</th>
                        <th>Assigned Complaints</th>
                        <th>Pending Workload</th>
                    </tr>
                </thead>
                <tbody>
                    {% for b in bureaus %}
                    <tr>
                        <td class="font-mono">{{ b.id }}</td>
                        <td><strong>{{ b.name }}</strong></td>
                        <td>{{ b.head }}</td>
                        <td class="font-mono">{{ b.email }}</td>
                        <td><strong>{{ b.totalComplaints }}</strong> cases</td>
                        <td><span class="badge badge-amber">{{ b.pendingCases }} pending</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    <!-- Tab 4: Audit Logs -->
    {% if active_tab == 'audit' %}
    <div class="card">
        <div class="card-title">
            <span>Database Records: System Audit Trail</span>
            <span style="font-size: 12px; color: var(--text-muted);">Immutable timeline of case modifications</span>
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Timestamp</th>
                        <th>User</th>
                        <th>Action</th>
                        <th>Complaint ID</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    {% for a in audit_logs %}
                    <tr>
                        <td class="font-mono">{{ a.id }}</td>
                        <td class="font-mono text-muted">{{ a.timestamp }}</td>
                        <td><strong>{{ a.user }}</strong></td>
                        <td><span class="badge badge-blue">{{ a.action }}</span></td>
                        <td class="font-mono">{{ a.complaintId or '—' }}</td>
                        <td style="color: var(--text-secondary);">{{ a.details }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

    <!-- Tab 5: SQL Query Runner -->
    {% if active_tab == 'query' %}
    <div class="card query-box">
        <div class="card-title">Direct SQL Query Console (SELECT only)</div>
        <form action="/admin?tab=query" method="POST">
            <textarea name="sql_query" placeholder="SELECT id, institution, status, priority FROM complaints LIMIT 10;">{{ custom_query or 'SELECT id, institution, status, priority, submission_date FROM complaints LIMIT 10;' }}</textarea>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:var(--text-muted); font-size:12px;">Allowed: Read-only SELECT operations on casetrack.db</span>
                <button type="submit" class="btn btn-primary">Execute Query</button>
            </div>
        </form>

        {% if query_error %}
        <div style="margin-top:16px; padding:12px; border-radius:6px; background:rgba(239,68,68,0.15); color:#f87171;">
            <strong>Query Error:</strong> {{ query_error }}
        </div>
        {% endif %}

        {% if query_results %}
        <div class="table-wrap" style="margin-top:20px;">
            <table>
                <thead>
                    <tr>
                        {% for col in query_cols %}
                        <th>{{ col }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in query_results %}
                    <tr>
                        {% for col in query_cols %}
                        <td>{{ row[col] }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
    </div>
    {% endif %}

    <!-- Tab 6: Diagnostics -->
    {% if active_tab == 'diagnostics' %}
    <div class="card">
        <div class="card-title">Server &amp; Database Diagnostics</div>
        <div class="diag-grid">
            <div class="diag-item">
                <span class="diag-label">Python Environment</span>
                <span class="diag-val">{{ diag.python_version }}</span>
            </div>
            <div class="diag-item">
                <span class="diag-label">Flask Version</span>
                <span class="diag-val">{{ diag.flask_version }}</span>
            </div>
            <div class="diag-item">
                <span class="diag-label">SQLite Engine Version</span>
                <span class="diag-val">{{ diag.sqlite_version }}</span>
            </div>
            <div class="diag-item">
                <span class="diag-label">Database File Path</span>
                <span class="diag-val">{{ diag.db_path }}</span>
            </div>
            <div class="diag-item">
                <span class="diag-label">Database Integrity Status</span>
                <span class="diag-val" style="color:var(--accent-green);">{{ diag.integrity }}</span>
            </div>
            <div class="diag-item">
                <span class="diag-label">Foreign Key Constraints</span>
                <span class="diag-val" style="color:var(--accent-green);">ENABLED (PRAGMA foreign_keys = ON)</span>
            </div>
            <div class="diag-item">
                <span class="diag-label">Upload Storage Directory</span>
                <span class="diag-val">{{ diag.upload_path }}</span>
            </div>
            <div class="diag-item">
                <span class="diag-label">Lead Administrator</span>
                <span class="diag-val">Deransiya Dorin J (Cloud Architect)</span>
            </div>
        </div>
    </div>
    {% endif %}

</body>
</html>
"""

@admin_panel_bp.route('', methods=['GET', 'POST'])
def dashboard_view():
    active_tab = request.args.get('tab', 'complaints')
    message = request.args.get('msg', '')

    # Compute live stats
    comp_c = query_db("SELECT COUNT(*) as c FROM complaints;", one=True)['c']
    user_c = query_db("SELECT COUNT(*) as c FROM users;", one=True)['c']
    bureau_c = query_db("SELECT COUNT(*) as c FROM bureaus;", one=True)['c']
    hist_c = query_db("SELECT COUNT(*) as c FROM complaint_history;", one=True)['c']
    audit_c = query_db("SELECT COUNT(*) as c FROM audit_logs;", one=True)['c']

    db_path = Config.DATABASE_PATH
    db_size = round(os.path.getsize(db_path) / 1024, 1) if os.path.exists(db_path) else 0

    stats = {
        'complaints_count': comp_c,
        'users_count': user_c,
        'bureaus_count': bureau_c,
        'history_count': hist_c,
        'audit_count': audit_c,
        'db_size_kb': db_size
    }

    complaints = []
    users = []
    bureaus = []
    audit_logs = []
    custom_query = ''
    query_results = []
    query_cols = []
    query_error = ''

    if active_tab == 'complaints':
        complaints = query_db("""
        SELECT c.*, b.name as bureau 
        FROM complaints c 
        LEFT JOIN bureaus b ON c.bureau_id = b.id 
        ORDER BY c.submission_date DESC;
        """)
    elif active_tab == 'users':
        users = query_db("SELECT * FROM users ORDER BY id ASC;")
    elif active_tab == 'bureaus':
        bureaus = query_db("""
        SELECT b.*,
            COUNT(c.id) as totalComplaints,
            SUM(CASE WHEN c.status IN ('New', 'Under Review', 'In Progress', 'Overdue') THEN 1 ELSE 0 END) as pendingCases
        FROM bureaus b
        LEFT JOIN complaints c ON b.id = c.bureau_id
        GROUP BY b.id, b.name;
        """)
    elif active_tab == 'audit':
        audit_logs = query_db("""
        SELECT id, user_name as user, action, complaint_id as complaintId, details, created_at as timestamp 
        FROM audit_logs 
        ORDER BY id DESC;
        """)
    elif active_tab == 'query':
        if request.method == 'POST':
            custom_query = request.form.get('sql_query', '').strip()
            # Only allow SELECT statements for safety
            if not custom_query.upper().startswith('SELECT'):
                query_error = "Only SELECT read-only queries are permitted via the web console."
            else:
                try:
                    db = get_db()
                    cur = db.execute(custom_query)
                    rows = cur.fetchall()
                    if rows:
                        query_cols = [col[0] for col in cur.description]
                        query_results = [dict(zip(query_cols, r)) for r in rows]
                    else:
                        query_results = []
                        query_cols = []
                        message = "Query executed successfully. 0 rows returned."
                except Exception as err:
                    query_error = str(err)

    # Diagnostics
    import sys
    import flask
    integrity_res = query_db("PRAGMA integrity_check;", one=True)
    diag = {
        'python_version': f"Python {sys.version.split()[0]}",
        'flask_version': f"Flask {flask.__version__}",
        'sqlite_version': sqlite3.sqlite_version,
        'db_path': Config.DATABASE_PATH,
        'integrity': integrity_res['integrity_check'] if integrity_res else 'ok',
        'upload_path': Config.UPLOAD_FOLDER
    }

    return render_template_string(
        HTML_TEMPLATE,
        stats=stats,
        active_tab=active_tab,
        complaints=complaints,
        users=users,
        bureaus=bureaus,
        audit_logs=audit_logs,
        custom_query=custom_query,
        query_results=query_results,
        query_cols=query_cols,
        query_error=query_error,
        diag=diag,
        message=message
    )

@admin_panel_bp.route('/reseed', methods=['POST'])
def reseed():
    db_path = Config.DATABASE_PATH
    if os.path.exists(db_path):
        try:
            # Clear tables
            db = get_db()
            db.execute("PRAGMA foreign_keys = OFF;")
            tables = ['complaints', 'complaint_history', 'investigation_updates', 'investigation_notes', 'notifications', 'audit_logs', 'users', 'bureaus']
            for t in tables:
                db.execute(f"DROP TABLE IF EXISTS {t};")
            db.commit()
            db.execute("PRAGMA foreign_keys = ON;")
        except Exception:
            pass

    seed_database()
    return redirect(url_for('admin_panel.dashboard_view', msg='Database re-seeded successfully with fresh records.'))
