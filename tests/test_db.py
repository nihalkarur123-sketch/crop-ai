import os
import tempfile
from services import db

def test_save_and_list():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_path = path
    try:
        db.init_db(db_path)
        id1 = db.save_diagnosis(
            db_path,
            crop="tomato",
            disease_name="Early blight",
            confidence=70,
            severity="medium",
            symptoms=["leaf spots"],
            actions=["remove affected leaves"],
            image_path="img1.jpg",
        )
        id2 = db.save_diagnosis(
            db_path,
            crop="potato",
            disease_name="Late blight",
            confidence=90,
            severity="high",
            symptoms=["wilting"],
            actions=["apply fungicide"],
            image_path="img2.jpg",
        )
        rows = db.list_diagnoses(db_path)
        assert len(rows) == 2
        assert rows[0]["id"] == id2
        assert rows[1]["id"] == id1
    finally:
        os.remove(db_path)
