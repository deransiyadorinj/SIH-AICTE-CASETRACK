import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
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


SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY or SECRET_KEY.startswith('replace-with-'):
    raise RuntimeError('Set SECRET_KEY to a unique random value before starting Flask')


class Config:
    SECRET_KEY = SECRET_KEY
    DATABASE_PATH = os.environ.get('DATABASE_PATH', str(BASE_DIR / 'casetrack.db'))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'txt'}
    
    # Session configuration
    SESSION_COOKIE_NAME = 'casetrack_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = _same_site_setting()
    SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE', False)
    if SESSION_COOKIE_SAMESITE == 'None' and not SESSION_COOKIE_SECURE:
        raise ValueError('SESSION_COOKIE_SECURE must be true when SESSION_COOKIE_SAMESITE is None')
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.environ.get(
            'CORS_ORIGINS',
            'http://localhost:3000,http://127.0.0.1:3000'
        ).split(',')
        if origin.strip()
    ]
