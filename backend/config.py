import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')
load_dotenv(BASE_DIR.parent / '.env')


def _env_bool(name, default):
    value = os.environ.get(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {'1', 'true', 'yes', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'off'}:
        return False
    raise ValueError(f'{name} must be a boolean value')


def _same_site_setting():
    value = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax').strip().lower()
    settings = {'lax': 'Lax', 'strict': 'Strict', 'none': 'None'}
    if value not in settings:
        raise ValueError('SESSION_COOKIE_SAMESITE must be Lax, Strict, or None')
    return settings[value]


def _parse_cors_origins():
    import re
    raw = os.environ.get(
        'CORS_ORIGINS',
        'http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173'
    )
    origins = []
    for item in raw.split(','):
        origin = item.strip()
        if not origin:
            continue
        if '*' in origin:
            # Convert glob wildcard to regex pattern (e.g., https://*.vercel.app -> ^https://.*\.vercel\.app$)
            escaped = re.escape(origin).replace(r'\*', '.*')
            origins.append(re.compile(f'^{escaped}$'))
        else:
            origins.append(origin)
    return origins


SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY or SECRET_KEY.startswith('replace-with-'):
    raise RuntimeError('Set SECRET_KEY to a unique random value before starting Flask')


IS_VERCEL = os.environ.get('VERCEL') == '1'


def _resolve_database_path():
    env_db = os.environ.get('DATABASE_PATH')
    if IS_VERCEL:
        if not env_db or env_db in ('backend/casetrack.db', str(BASE_DIR / 'casetrack.db')):
            tmp_db = Path('/tmp/casetrack.db')
            src_db = BASE_DIR / 'casetrack.db'
            if not tmp_db.exists() and src_db.exists():
                try:
                    import shutil
                    shutil.copyfile(src_db, tmp_db)
                except Exception:
                    pass
            return str(tmp_db)
        return env_db
    return env_db or str(BASE_DIR / 'casetrack.db')


def _resolve_upload_folder():
    env_upload = os.environ.get('UPLOAD_FOLDER')
    if IS_VERCEL:
        if not env_upload or env_upload in ('backend/uploads', str(BASE_DIR / 'uploads')):
            return '/tmp/uploads'
        return env_upload
    return env_upload or str(BASE_DIR / 'uploads')


class Config:
    SECRET_KEY = SECRET_KEY
    DATABASE_PATH = _resolve_database_path()
    UPLOAD_FOLDER = _resolve_upload_folder()
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'txt'}
    
    # Session configuration
    SESSION_COOKIE_NAME = 'casetrack_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = _same_site_setting()
    SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', IS_VERCEL)
    if SESSION_COOKIE_SAMESITE == 'None' and not SESSION_COOKIE_SECURE:
        raise ValueError('SESSION_COOKIE_SECURE must be true when SESSION_COOKIE_SAMESITE is None')
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS = _parse_cors_origins()
