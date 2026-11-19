import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads")).absolute()
DB_PATH = Path(os.getenv("DB_PATH", "diagnoses.db")).absolute()

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
