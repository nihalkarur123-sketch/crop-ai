import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

def _connect(db_path: Path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path) -> None:
    """Create the diagnoses table if it doesn't exist."""
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                crop TEXT NOT NULL,
                disease_name TEXT,
                confidence INTEGER,
                severity TEXT,
                symptoms TEXT,
                actions TEXT,
                image_path TEXT NOT NULL
            )
            """
        )
        conn.commit()

def save_diagnosis(
    db_path: Path,
    *,
    crop: str,
    disease_name: str,
    confidence: int,
    severity: str,
    symptoms: List[str],
    actions: List[str],
    image_path: str,
) -> int:
    """Insert a diagnosis record and return its ID."""
    created_at = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO diagnoses (
                created_at, crop, disease_name,
                confidence, severity, symptoms, actions, image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                crop,
                disease_name,
                confidence,
                severity,
                json.dumps(symptoms, ensure_ascii=False),
                json.dumps(actions, ensure_ascii=False),
                image_path,
            ),
        )
        conn.commit()
        return cur.lastrowid

def list_diagnoses(db_path: Path, limit: int = 100) -> List[Dict[str, Any]]:
    """Return the newest diagnoses up to *limit* (newest first)."""
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT * FROM diagnoses
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        result = []
        for r in rows:
            result.append(
                {
                    "id": r["id"],
                    "created_at": r["created_at"],
                    "crop": r["crop"],
                    "disease_name": r["disease_name"],
                    "confidence": r["confidence"],
                    "severity": r["severity"],
                    "symptoms": json.loads(r["symptoms"]),
                    "actions": json.loads(r["actions"]),
                    "image_path": r["image_path"],
                }
            )
        return result
