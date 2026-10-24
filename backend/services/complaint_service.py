import re
from datetime import datetime
from backend.database import query_db, execute_db, get_db

def normalize_complaint_id(comp_id):
    if not comp_id:
        return comp_id
    clean = comp_id.strip()
    clean = re.sub(r'^AICTE-', 'AIC-', clean, flags=re.IGNORECASE)
    clean = re.sub(r'AIC-(\d+)-0+(\d+)', lambda m: f"AIC-{m.group(1)}-{int(m.group(2)):04d}", clean)
    return clean

def generate_complaint_id():
    """Generates next unique complaint ID e.g. AIC-2026-0021"""
    row = query_db("SELECT id FROM complaints ORDER BY ROWID DESC LIMIT 1;", one=True)
    year = datetime.now().year
    if not row or not row['id']:
        return f"AIC-{year}-0001"
    
    last_id = row['id']
    match = re.search(r'AIC-\d+-(\d+)', last_id)
    if match:
        next_num = int(match.group(1)) + 1
        return f"AIC-{year}-{next_num:04d}"
    
    count_row = query_db("SELECT COUNT(*) as c FROM complaints;", one=True)
    next_num = (count_row['c'] if count_row else 0) + 1
    return f"AIC-{year}-{next_num:04d}"

def get_complaints(filters=None, user=None):
    filters = filters or {}
    query = """
    SELECT 
        c.id, c.institution, c.institution_id, c.institution_type,
        c.state, c.district, c.contact_person, c.email, c.phone,
        c.category, c.bureau_id, b.name as bureau,
        c.priority, c.status, c.subject, c.description,
        c.submission_date as submissionDate, c.last_updated as lastUpdated,
        c.resolution_details, c.created_at
    FROM complaints c
    LEFT JOIN bureaus b ON c.bureau_id = b.id
    WHERE 1=1
    """
    params = []

    # Institution authorization check
    if user and user.get('role') == 'Institution':
        query += " AND (c.institution_id = ? OR c.created_by_user_id = ?)"
        params.extend([user.get('institution_ref', ''), user['id']])

    # Filters
    if filters.get('search'):
        q = f"%{filters['search'].strip()}%"
        query += " AND (c.id LIKE ? OR c.subject LIKE ? OR c.institution LIKE ?)"
        params.extend([q, q, q])

    if filters.get('status'):
        query += " AND c.status = ?"
        params.append(filters['status'])

    if filters.get('priority'):
        query += " AND c.priority = ?"
        params.append(filters['priority'])

    if filters.get('category'):
        query += " AND c.category = ?"
        params.append(filters['category'])

    if filters.get('bureau'):
        # Allow filtering by bureau name or bureau id
        query += " AND (b.name = ? OR c.bureau_id = ?)"
        params.extend([filters['bureau'], filters['bureau']])

    # Sorting
    sort_by = filters.get('sortBy', 'submissionDate')
    sort_dir = 'ASC' if str(filters.get('sortDir', 'desc')).lower() == 'asc' else 'DESC'
    
    col_map = {
        'id': 'c.id',
        'subject': 'c.subject',
        'priority': 'c.priority',
        'status': 'c.status',
        'submissionDate': 'c.submission_date',
        'lastUpdated': 'c.last_updated'
    }
    db_sort_col = col_map.get(sort_by, 'c.submission_date')
    query += f" ORDER BY {db_sort_col} {sort_dir}"

    rows = query_db(query, tuple(params))

    # Format bureau fallback
    for r in rows:
        if not r.get('bureau'):
            r['bureau'] = 'Unassigned'
    return rows

def get_complaint_details(complaint_id, user=None):
    cid = normalize_complaint_id(complaint_id)
    query = """
    SELECT 
        c.id, c.institution, c.institution_id as institutionId, c.institution_type as institutionType,
        c.state, c.district, c.contact_person as contactPerson, c.email, c.phone,
        c.category, c.bureau_id, b.name as bureau,
        c.priority, c.status, c.subject, c.description,
        c.submission_date as submissionDate, c.last_updated as lastUpdated,
        c.resolution_details, c.created_by_user_id, c.created_at
    FROM complaints c
    LEFT JOIN bureaus b ON c.bureau_id = b.id
    WHERE c.id = ?
    """
    comp = query_db(query, (cid,), one=True)
    if not comp:
        return None

    # Role-based ownership check for Institution users
    if user and user.get('role') == 'Institution':
        if comp.get('institutionId') != user.get('institution_ref') and comp.get('created_by_user_id') != user.get('id'):
            return None

    comp['bureau'] = comp['bureau'] or 'Unassigned'

    # Get Timeline
    hist_rows = query_db("""
    SELECT status, note, created_at as date, created_by as createdBy
    FROM complaint_history
    WHERE complaint_id = ?
    ORDER BY id ASC;
    """, (cid,))
    comp['timeline'] = hist_rows

    # Get Public Updates
    update_rows = query_db("""
    SELECT update_text, created_at as date, created_by as createdBy
    FROM investigation_updates
    WHERE complaint_id = ? AND is_public = 1
    ORDER BY id ASC;
    """, (cid,))
    comp['updates'] = [u['update_text'] for u in update_rows]
    comp['updatesDetail'] = update_rows

    # Get Private Investigation Notes ONLY if user is admin
    if user and user.get('role') in ('Cloud Architect', 'Super Admin', 'Admin', 'Reviewer', 'Analyst'):
        notes_rows = query_db("""
        SELECT id, note_text, created_by as createdBy, created_at as date
        FROM investigation_notes
        WHERE complaint_id = ?
        ORDER BY id ASC;
        """, (cid,))
        comp['privateNotes'] = notes_rows
    else:
        comp['privateNotes'] = []

    return comp

def get_public_tracking(complaint_id):
    """Clean public tracking endpoint without sensitive contact info or private notes"""
    cid = normalize_complaint_id(complaint_id)
    comp = query_db("""
    SELECT 
        c.id, c.institution, c.category, b.name as bureau,
        c.priority, c.status, c.subject, c.description,
        c.submission_date as submissionDate, c.last_updated as lastUpdated,
        c.resolution_details
    FROM complaints c
    LEFT JOIN bureaus b ON c.bureau_id = b.id
    WHERE c.id = ?
    """, (cid,), one=True)
    
    if not comp:
        return None

    comp['bureau'] = comp['bureau'] or 'Unassigned'

    # Timeline
    hist_rows = query_db("""
    SELECT status, note, created_at as date
    FROM complaint_history
    WHERE complaint_id = ?
    ORDER BY id ASC;
    """, (cid,))
    comp['timeline'] = hist_rows

    # Public updates only
    update_rows = query_db("""
    SELECT update_text as text, created_at as date
    FROM investigation_updates
    WHERE complaint_id = ? AND is_public = 1
    ORDER BY id ASC;
    """, (cid,))
    comp['updates'] = [u['text'] for u in update_rows]

    return comp

def create_complaint(data, user=None):
    complaint_id = generate_complaint_id()
    now_date = datetime.now().strftime('%Y-%m-%d')
    now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    bureau_id = data.get('bureau_id')
    # If bureau name is passed instead of id, resolve it
    if bureau_id and not bureau_id.startswith('bureau-'):
        b_row = query_db("SELECT id FROM bureaus WHERE name = ?;", (bureau_id,), one=True)
        bureau_id = b_row['id'] if b_row else None

    user_id = user['id'] if user else None
    user_name = user['name'] if user else data.get('contactPerson', 'Anonymous Portal User')

    db = get_db()
    with db:
        db.execute("""
        INSERT INTO complaints (
            id, institution, institution_id, institution_type, state, district,
            contact_person, email, phone, category, bureau_id, priority, status,
            subject, description, consent, created_by_user_id, submission_date, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'New', ?, ?, ?, ?, ?, ?);
        """, (
            complaint_id,
            data.get('institution', '').strip(),
            data.get('institutionId', '').strip(),
            data.get('institutionType', 'Other'),
            data.get('state', '').strip(),
            data.get('district', '').strip(),
            data.get('contactPerson', '').strip(),
            data.get('email', '').strip(),
            data.get('phone', '').strip(),
            data.get('category', 'Other'),
            bureau_id,
            data.get('priority', 'Medium'),
            data.get('subject', '').strip(),
            data.get('description', '').strip(),
            1 if data.get('consent') else 0,
            user_id,
            now_date,
            now_date
        ))

        # Initial History Entry
        db.execute("""
        INSERT INTO complaint_history (complaint_id, status, note, created_by, created_at)
        VALUES (?, 'Submitted', 'Complaint registered successfully.', ?, ?);
        """, (complaint_id, user_name, now_datetime))

        # Audit Log
        db.execute("""
        INSERT INTO audit_logs (user_name, action, complaint_id, details, created_at)
        VALUES (?, 'Complaint Received', ?, ?, ?);
        """, (user_name, complaint_id, f"New complaint filed for {data.get('institution', '')}: {data.get('subject', '')}", now_datetime))

        # Admin Notification
        admin_row = query_db("SELECT id FROM users WHERE role IN ('Cloud Architect', 'Super Admin') LIMIT 1;", one=True)
        admin_id = admin_row['id'] if admin_row else 1
        db.execute("""
        INSERT INTO notifications (user_id, type, title, message, complaint_id, is_read, created_at)
        VALUES (?, 'new', 'New complaint received', ?, ?, 0, ?);
        """, (admin_id, f"Complaint {complaint_id} received for {data.get('institution')}.", complaint_id, now_datetime))

    return complaint_id

def update_complaint_status(complaint_id, new_status, note=None, user_name="Admin"):
    now_date = datetime.now().strftime('%Y-%m-%d')
    now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    note_text = note or f"Status changed to {new_status}."

    db = get_db()
    with db:
        db.execute("""
        UPDATE complaints 
        SET status = ?, last_updated = ?, updated_at = ?
        WHERE id = ?;
        """, (new_status, now_date, now_datetime, complaint_id))

        db.execute("""
        INSERT INTO complaint_history (complaint_id, status, note, created_by, created_at)
        VALUES (?, ?, ?, ?, ?);
        """, (complaint_id, new_status, note_text, user_name, now_datetime))

        action_name = 'Case Resolved' if new_status == 'Resolved' else 'Status Updated'
        db.execute("""
        INSERT INTO audit_logs (user_name, action, complaint_id, details, created_at)
        VALUES (?, ?, ?, ?, ?);
        """, (user_name, action_name, complaint_id, f"Status updated to {new_status}. {note_text}", now_datetime))

        # Notification
        db.execute("""
        INSERT INTO notifications (type, title, message, complaint_id, is_read, created_at)
        VALUES ('status', 'Status updated', ?, ?, 0, ?);
        """, (f"Complaint {complaint_id} status changed to {new_status}.", complaint_id, now_datetime))

    return True

def assign_complaint_bureau(complaint_id, bureau_identifier, user_name="Admin"):
    now_date = datetime.now().strftime('%Y-%m-%d')
    now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    b_row = query_db("SELECT id, name FROM bureaus WHERE id = ? OR name = ?;", (bureau_identifier, bureau_identifier), one=True)
    if not b_row:
        return False, "Bureau not found"

    db = get_db()
    with db:
        db.execute("""
        UPDATE complaints 
        SET bureau_id = ?, last_updated = ?, updated_at = ?
        WHERE id = ?;
        """, (b_row['id'], now_date, now_datetime, complaint_id))

        db.execute("""
        INSERT INTO audit_logs (user_name, action, complaint_id, details, created_at)
        VALUES (?, 'Bureau Reassigned', ?, ?, ?);
        """, (user_name, complaint_id, f"Assigned to {b_row['name']}", now_datetime))

        db.execute("""
        INSERT INTO notifications (type, title, message, complaint_id, is_read, created_at)
        VALUES ('assigned', 'Case assigned', ?, ?, 0, ?);
        """, (f"Complaint {complaint_id} assigned to {b_row['name']}.", complaint_id, now_datetime))

    return True, b_row['name']

def add_investigation_update(complaint_id, update_text, is_public=True, user_name="Admin"):
    now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    with db:
        db.execute("""
        INSERT INTO investigation_updates (complaint_id, update_text, is_public, created_by, created_at)
        VALUES (?, ?, ?, ?, ?);
        """, (complaint_id, update_text, 1 if is_public else 0, user_name, now_datetime))

        db.execute("""
        INSERT INTO audit_logs (user_name, action, complaint_id, details, created_at)
        VALUES (?, 'Investigation Update', ?, ?, ?);
        """, (user_name, complaint_id, update_text, now_datetime))
    return True

def add_private_note(complaint_id, note_text, user_name="Admin"):
    now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    with db:
        db.execute("""
        INSERT INTO investigation_notes (complaint_id, note_text, created_by, created_at)
        VALUES (?, ?, ?, ?);
        """, (complaint_id, note_text, user_name, now_datetime))

        db.execute("""
        INSERT INTO audit_logs (user_name, action, complaint_id, details, created_at)
        VALUES (?, 'Private Note Added', ?, 'Confidential investigation note added by administrator.', ?);
        """, (user_name, complaint_id, now_datetime))
    return True
