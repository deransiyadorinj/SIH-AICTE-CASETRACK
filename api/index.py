import sys
from pathlib import Path

# Add project root and backend to sys.path so backend modules can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

backend_dir = ROOT_DIR / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import the existing Flask app instance
from backend.app import app

# Vercel Serverless Function entry point exposes 'app'
