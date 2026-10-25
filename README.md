# AICTE | CASETRACK
### Integrated Dashboard for Monitoring and Tracking Institution-Related Complaint Cases Across AICTE Bureaus/Cells

---

## Architecture Overview

- **Frontend:** React 19 + Vite, Vanilla Enterprise CSS (#090909 dark aesthetic), React Router v7, Recharts, Lucide React
- **Backend:** Python Flask REST API with Blueprints, session-based auth, role-based access control (RBAC), and parameterized SQL operations
- **Database:** SQLite (`backend/casetrack.db` locally) with 20 seeded realistic complaints, status history, public updates, private notes, notifications, and audit logs; hosted deployments need persistent storage for durability
- **Dev Proxy:** Integrated Vite proxy routing `/api/*` to `http://127.0.0.1:5000`

---

## Quick Start

### 0. Configure the environment
```powershell
# From the workspace root:
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```
Set `SECRET_KEY` and the three `INITIAL_*_PASSWORD` values in `.env` to unique random development values. These seed passwords are backend-only; never put them in frontend variables or deploy the example values.

### 1. Start the Flask Backend (Port 5000)
```powershell
# From workspace root:
python -m pip install -r backend/requirements.txt
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

## Initial Accounts

On an empty database, the backend seeds the administrator, institution, and other sample accounts with passwords supplied through `INITIAL_ADMIN_PASSWORD`, `INITIAL_INSTITUTION_PASSWORD`, and `INITIAL_USER_PASSWORD`. Set unique values of at least 16 characters in the backend environment, then distribute account credentials through a secure channel. The application does not display or prefill demo credentials.

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

---

## Deployment Environment

### Vercel frontend
- Set the project root to the repository root, build command to `npm run build`, and output directory to `dist`.
- Configure `VITE_API_BASE_URL` in the Vercel project environment settings to the deployed Flask API base URL, including `/api` (for example, the actual backend origin followed by `/api`). This is public frontend configuration, not a secret.
- Redeploy after changing this variable. Do not put backend secrets in any `VITE_` variable.

### Render Flask backend
- Create a Python web service from this repository, install dependencies with `pip install -r backend/requirements.txt`, and use `gunicorn --bind 0.0.0.0:$PORT backend.app:app` as the start command.
- Configure these values in the Render service environment dashboard; do not copy local `.env` values as production secrets:
  - `SECRET_KEY`: generate a unique, random production secret.
  - `INITIAL_ADMIN_PASSWORD`, `INITIAL_INSTITUTION_PASSWORD`, `INITIAL_USER_PASSWORD`: set unique random passwords of at least 16 characters. They are only used when seeding an empty database.
  - `CORS_ORIGINS`: the exact Vercel site origin(s), comma-separated, without paths.
  - `SESSION_COOKIE_SAMESITE`: `None` when the frontend and backend are on separate sites.
  - `SESSION_COOKIE_SECURE`: `true` when serving over HTTPS; required with `SESSION_COOKIE_SAMESITE=None`.
  - `DATABASE_PATH`: use a path on an attached persistent disk, such as `/var/data/casetrack.db`.
  - `UPLOAD_FOLDER`: use a path on that same persistent disk, such as `/var/data/uploads`.
  - `PORT` is supplied by Render; the application also defaults to `5000` for local development.
- `DATABASE_PATH` and `UPLOAD_FOLDER` are optional if the platform's defaults are acceptable, but the defaults are not durable on an ephemeral service filesystem.

SQLite remains the configured database. Its files are not durable across deployments/restarts on an ephemeral serverless or hosted filesystem; attach persistent storage and point both paths to it to retain records and uploads. Do not use SQLite as a shared database across multiple service instances. The repository currently tracks a pre-seeded SQLite database; use a fresh database path for deployment, since seed-password environment values do not reset accounts in an already populated database. If you reuse existing data, reset all existing account passwords before exposing the service. Cross-site session cookies can also be restricted by browsers; a same-site custom domain/reverse proxy may be needed if sessions are blocked.
