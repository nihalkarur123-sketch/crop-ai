import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "5"))

# On Vercel / serverless environments, root filesystem is read-only.
# Writable storage is available in /tmp
IS_SERVERLESS = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

if IS_SERVERLESS:
    UPLOAD_DIR = Path("/tmp/uploads").resolve()
    DB_PATH = Path("/tmp/diagnoses.db").resolve()
else:
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads")).resolve()
    DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "diagnoses.db")).resolve()

# Ensure upload directory exists safely
try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
