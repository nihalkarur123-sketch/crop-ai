import uuid
import re
import os
import json
from datetime import datetime, timezone
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, abort, jsonify
)

import config
from config import UPLOAD_DIR, DB_PATH, MAX_UPLOAD_MB
from services import db, gemini_client, diagnosis_parser

ALLOWED_EXT = {".jpg", ".jpeg", ".png"}
ALLOWED_CROPS = {"auto", "tomato", "potato", "rice", "maize", "chilli"}
PRIMARY_CROPS = ["tomato", "potato", "rice", "maize", "chilli"]
UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}\.(jpg|jpeg|png)$")


def create_app():
    base_path = Path(__file__).resolve().parent
    app = Flask(
        __name__,
        static_folder=str(base_path / "static"),
        template_folder=str(base_path / "templates")
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "plantcare-ai-dev-secret-key-2026")
    db.init_db(DB_PATH)

    @app.context_processor
    def inject_global_data():
        return {
            "now": datetime.now(timezone.utc),
            "allowed_crops": PRIMARY_CROPS,
            "config": config,
            "max_upload_mb": MAX_UPLOAD_MB,
        }

    # 1. Landing Page
    @app.route("/")
    def landing():
        records = db.list_diagnoses(DB_PATH, limit=100)
        total_scans = len(records)
        healthy_count = sum(1 for r in records if (r.get("severity") or "").lower() == "low" or (r.get("disease_name") or "").lower() == "healthy")
        return render_template(
            "landing.html",
            total_scans=total_scans,
            healthy_count=healthy_count,
            allowed_crops=PRIMARY_CROPS
        )

    # 2. Scanner Page (routes for both /scan and /index)
    @app.route("/scan", endpoint="scan")
    @app.route("/index", endpoint="index")
    def scan_page():
        selected_crop = request.args.get("crop", "auto").lower()
        if selected_crop not in ALLOWED_CROPS:
            selected_crop = "auto"
        return render_template("index.html", crops=PRIMARY_CROPS, selected_crop=selected_crop)

    # 3. Farmer Dashboard
    @app.route("/dashboard")
    def dashboard():
        records = db.list_diagnoses(DB_PATH, limit=1000)
        total = len(records)
        healthy = sum(1 for r in records if (r.get("severity") or "").lower() == "low" or (r.get("disease_name") or "").lower() == "healthy")
        diseased = total - healthy
        
        # Calculate crop distribution
        crop_counts = {c: 0 for c in PRIMARY_CROPS}
        avg_conf = 0
        if total > 0:
            total_conf = sum(int(r.get("confidence") or 0) for r in records)
            avg_conf = round(total_conf / total)
            for r in records:
                c = (r.get("crop") or "").lower()
                if c in crop_counts:
                    crop_counts[c] += 1
                else:
                    crop_counts[c] = 1

        recent = records[:8]
        return render_template(
            "dashboard.html",
            total=total,
            healthy=healthy,
            diseased=diseased,
            avg_conf=avg_conf,
            crop_counts=crop_counts,
            recent=recent,
        )

    # 4. Leaf Diagnosis Endpoint
    @app.route("/diagnose", methods=["POST"])
    def diagnose():
        crop = request.form.get("crop", "auto").lower()
        if crop not in ALLOWED_CROPS:
            crop = "auto"

        # Check if an uploaded file or sample is provided
        if "image" not in request.files:
            flash("No image file uploaded.", "error")
            return redirect(url_for("scan"))

        file = request.files["image"]
        if file.filename == "":
            flash("Please select or drop a leaf image to diagnose.", "error")
            return redirect(url_for("scan"))

        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXT:
            flash("Unsupported file format. Please upload JPG, JPEG, or PNG.", "error")
            return redirect(url_for("scan"))

        # Check file size
        file.seek(0, 2)
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)
        if size_mb > MAX_UPLOAD_MB:
            flash(f"File exceeds the maximum limit of {MAX_UPLOAD_MB} MB.", "error")
            return redirect(url_for("scan"))

        uuid_name = f"{uuid.uuid4()}{ext}"
        save_path = UPLOAD_DIR / uuid_name
        file.save(save_path)

        # Verify image using Pillow
        try:
            from PIL import Image
            im = Image.open(save_path)
            im.verify()
        except Exception:
            save_path.unlink(missing_ok=True)
            flash("Uploaded file is corrupted or not a valid image.", "error")
            return redirect(url_for("scan"))

        # Call Gemini Vision Pipeline / Local Vision Engine
        try:
            raw = gemini_client.analyze_image(str(save_path), crop, original_filename=file.filename)
            diag = diagnosis_parser.parse_diagnosis(raw)
        except diagnosis_parser.DiagnosisParseError as e:
            flash(f"Diagnosis parsing error: {e}", "error")
            return redirect(url_for("scan"))
        except Exception as e:
            flash(f"AI Engine error: {e}", "error")
            return redirect(url_for("scan"))

        # Extract crop: User's explicit choice is authoritative!
        if crop and crop.lower() not in {"auto", ""}:
            final_crop = crop.lower()
        else:
            final_crop = "chilli"
            try:
                raw_dict = json.loads(raw)
                if raw_dict.get("crop") and raw_dict.get("crop") != "auto":
                    final_crop = raw_dict.get("crop").lower()
            except Exception:
                pass
            if final_crop == "auto":
                final_crop = "chilli"

        if not diag.get("is_plant_leaf", True):
            flash("Visual verification notice: The uploaded image does not appear to be a recognizable plant leaf.", "warning")
            diag_obj = {
                "id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "crop": final_crop,
                "disease_name": "Non-Leaf Detected",
                "confidence": diag.get("confidence", 0),
                "severity": "low",
                "symptoms": diag.get("symptoms_seen", ["Subject is not identifiable as a botanical leaf specimen."]),
                "actions": diag.get("recommended_actions", ["Please upload a well-lit, close-up photograph of a single plant leaf."]),
                "image_path": uuid_name,
                "is_plant_leaf": False,
            }
            return render_template("result.html", diagnosis=diag_obj, image_url=url_for("uploaded_file", name=uuid_name))

        # Save to database
        rec_id = db.save_diagnosis(
            DB_PATH,
            crop=final_crop,
            disease_name=diag["disease_name"],
            confidence=diag["confidence"],
            severity=diag["severity"],
            symptoms=diag["symptoms_seen"],
            actions=diag["recommended_actions"],
            image_path=uuid_name,
        )
        return redirect(url_for("result", diag_id=rec_id))
        return redirect(url_for("result", diag_id=rec_id))

    # 5. Result Detail View
    @app.route("/result/<int:diag_id>")
    def result(diag_id):
        record = next((r for r in db.list_diagnoses(DB_PATH, limit=1000) if r["id"] == diag_id), None)
        if not record:
            abort(404)
        return render_template("result.html", diagnosis=record, image_url=url_for("uploaded_file", name=record["image_path"]))

    # 6. History View
    @app.route("/history")
    def history():
        diagnoses = db.list_diagnoses(DB_PATH, limit=500)
        return render_template("history.html", diagnoses=diagnoses)

    # 7. Uploaded File Access
    @app.route("/uploads/<name>")
    def uploaded_file(name):
        if not UUID_RE.fullmatch(name):
            abort(404)
        return send_from_directory(UPLOAD_DIR, name)

    # 8. API endpoints for live interactivity
    @app.route("/api/stats")
    def api_stats():
        records = db.list_diagnoses(DB_PATH, limit=1000)
        total = len(records)
        healthy = sum(1 for r in records if (r.get("severity") or "").lower() == "low" or (r.get("disease_name") or "").lower() == "healthy")
        return jsonify({
            "total": total,
            "healthy": healthy,
            "diseased": total - healthy,
            "crops": sorted(ALLOWED_CROPS)
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
