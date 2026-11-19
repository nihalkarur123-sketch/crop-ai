import json
from typing import Any, Dict, List

class DiagnosisParseError(ValueError):
    """Raised when Gemini output cannot be parsed or validated."""

def _ensure_keys(data: Dict[str, Any], required: List[str]) -> None:
    missing = [k for k in required if k not in data]
    if missing:
        raise DiagnosisParseError(f"Missing keys: {', '.join(missing)}")

def _validate_and_normalise(raw: Dict[str, Any]) -> Dict[str, Any]:
    required = [
        "disease_name",
        "confidence",
        "severity",
        "symptoms_seen",
        "recommended_actions",
        "is_plant_leaf",
    ]
    _ensure_keys(raw, required)

    if not isinstance(raw["disease_name"], str):
        raise DiagnosisParseError("disease_name must be a string")
    if not isinstance(raw["confidence"], int):
        raise DiagnosisParseError("confidence must be an integer")
    if not (0 <= raw["confidence"] <= 100):
        raise DiagnosisParseError("confidence must be between 0 and 100")
    if not isinstance(raw["severity"], str):
        raise DiagnosisParseError("severity must be a string")
    severity = raw["severity"].lower()
    if severity not in {"low", "medium", "high"}:
        raise DiagnosisParseError("severity must be low, medium, or high")
    if not isinstance(raw["symptoms_seen"], list) or not all(isinstance(i, str) for i in raw["symptoms_seen"]):
        raise DiagnosisParseError("symptoms_seen must be a list of strings")
    if not isinstance(raw["recommended_actions"], list) or not all(isinstance(i, str) for i in raw["recommended_actions"]):
        raise DiagnosisParseError("recommended_actions must be a list of strings")
    if not isinstance(raw["is_plant_leaf"], bool):
        raise DiagnosisParseError("is_plant_leaf must be a boolean")

    # Clamp lists to max 6 items
    symptoms = raw["symptoms_seen"][:6]
    actions = raw["recommended_actions"][:6]
    return {
        "disease_name": raw["disease_name"],
        "confidence": raw["confidence"],
        "severity": severity,
        "symptoms_seen": symptoms,
        "recommended_actions": actions,
        "is_plant_leaf": raw["is_plant_leaf"],
    }

def parse_diagnosis(json_str: str) -> Dict[str, Any]:
    """Parse raw JSON from Gemini, validate and normalise it."""
    cleaned = json_str.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise DiagnosisParseError(f"Invalid JSON: {e}") from e
    return _validate_and_normalise(data)
