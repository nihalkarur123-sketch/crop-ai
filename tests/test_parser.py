import pytest
from services.diagnosis_parser import parse_diagnosis, DiagnosisParseError

VALID_JSON = """
{
  "disease_name": "Late blight",
  "confidence": 85,
  "severity": "high",
  "symptoms_seen": ["water-soaked lesions", "white mold"],
  "recommended_actions": ["apply copper fungicide", "remove infected leaves"],
  "is_plant_leaf": true
}
"""

def test_valid_json():
    result = parse_diagnosis(VALID_JSON)
    assert result["disease_name"] == "Late blight"
    assert result["confidence"] == 85
    assert result["severity"] == "high"
    assert result["is_plant_leaf"] is True

def test_missing_key():
    bad = VALID_JSON.replace('"severity": "high",', '')
    with pytest.raises(DiagnosisParseError) as exc:
        parse_diagnosis(bad)
    assert "Missing keys" in str(exc.value)

def test_confidence_out_of_range():
    bad = VALID_JSON.replace('"confidence": 85,', '"confidence": 150,')
    with pytest.raises(DiagnosisParseError):
        parse_diagnosis(bad)

def test_invalid_severity():
    bad = VALID_JSON.replace('"severity": "high"', '"severity": "extreme"')
    with pytest.raises(DiagnosisParseError):
        parse_diagnosis(bad)

def test_not_a_leaf_flag():
    bad = VALID_JSON.replace('"is_plant_leaf": true', '"is_plant_leaf": false')
    res = parse_diagnosis(bad)
    assert res["is_plant_leaf"] is False
