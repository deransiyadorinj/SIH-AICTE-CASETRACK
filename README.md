# AICTE | CASETRACK
### Integrated Dashboard for Monitoring and Tracking Institution-Related Complaint Cases Across AICTE Bureaus/Cells

---

## Architecture Overview

- **Frontend:** React 19 + Vite, Vanilla Enterprise CSS (#090909 dark aesthetic), React Router v7, Recharts, Lucide React
- **Backend:** Python Flask REST API with Blueprints, session-based auth, role-based access control (RBAC), and parameterized SQL operations
- **Database:** Persistent SQLite (`backend/casetrack.db`) with 20 seeded realistic complaints, status history, public updates, private notes, notifications, and audit logs
- **Dev Proxy:** Integrated Vite proxy routing `/api/*` to `http://127.0.0.1:5000`

---

## Quick Start

### 1. Start the Flask Backend (Port 5000)
```powershell
# From workspace root:
python backend/app.py
```
*Backend URL:* `http://127.0.0.1:5000`

### 2. Start the Frontend Dev Server (Port 3000)
```powershell
# In a separate terminal:
npm run dev
```
*Frontend URL:* `http://localhost:3000`

---

## Demo Accounts

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Admin (Cloud Architect)** | `admin@aicte.gov.in` | `admin123` | Full administrative oversight, bureau assignment, status changes, private notes |
| **Institution** | `principal@abcit.edu.in` | `institution123` | Own-institution complaint filing & authorized case tracking |

*(You can also click **"Demo Login (Preview)"** on the sign-in screen to instantly authenticate as the Lead Administrator)*

---

## API Capabilities

- `POST /api/auth/login` — Authenticate and start session
- `POST /api/auth/logout` — Terminate session
- `GET /api/auth/me` — Retrieve active session user
- `GET /api/dashboard/stats` — Live computed KPI counts, resolution rate, and average resolution days
- `GET /api/dashboard/charts` — Dynamic monthly volume trends, status donut, and bureau workload bar charts
- `GET /api/complaints` — Filterable, searchable, and sortable case management records
- `POST /api/complaints` — Register new complaint (generates unique sequential ID: `AIC-2026-XXXX`)
- `GET /api/complaints/<id>` — Detailed case dossier, status history timeline, updates, and confidential notes
- `GET /api/complaints/<id>/tracking` — Public investigation updates & progress timeline
- `PATCH /api/complaints/<id>/status` — Advance complaint workflow status
- `PATCH /api/complaints/<id>/assignment` — Assign or reassign bureau
- `POST /api/complaints/<id>/notes` — Record confidential admin-only investigation notes
- `GET /api/bureaus` — Workload metrics across AICTE administrative bureaus
- `GET /api/reports/analytics` — Multi-dimensional case performance analytics
- `GET /api/reports/export?type=complaints` — Live CSV export download stream
- `GET /api/notifications` — Notification inbox with read/unread updates
- `GET /api/audit-logs` — Immutable audit trail of administrative actions
- `GET /api/users` & `POST /api/users` — User management (passwords never exposed)

---

## Automated Tests

Run backend unit tests verifying all critical workflows:
```powershell
python backend/test_api.py
```
*(All 9 integration suites passing)*
