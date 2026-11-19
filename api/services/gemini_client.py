import os
import json
import logging
from pathlib import Path
try:
    from services.leaf_vision import analyze_leaf_image
except ImportError:
    from leaf_vision import analyze_leaf_image

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None

# Load API key from environment
API_KEY = os.getenv("GEMINI_API_KEY")
# Valid Gemini keys start with AIzaSy... If it's a dummy or invalid prefix, treat as unconfigured
IS_VALID_KEY_FORMAT = bool(API_KEY and API_KEY.startswith("AIzaSy") and len(API_KEY) >= 35)

if genai is not None and IS_VALID_KEY_FORMAT:
    try:
        genai.configure(api_key=API_KEY)
        _MODEL = "gemini-2.5-flash"
    except Exception as e:
        logger.warning(f"Could not configure genai: {e}")
        IS_VALID_KEY_FORMAT = False


def _build_prompt(crop: str) -> str:
    crop_instruction = (
        "Identify the crop / plant species automatically from the leaf morphology (e.g. tomato, potato, rice, maize, chilli, etc.)."
        if crop == "auto" or not crop else
        f"The user indicated this is a {crop} leaf. Verify this crop or correct it if another plant species is obvious."
    )
    return (
        f"You are an expert plant pathologist and agronomist. {crop_instruction} "
        "Carefully examine the leaf image for any disease, pest damage, fungal lesions, or nutrient deficiency. "
        "Return ONLY a valid JSON object with these exact keys: "
        "crop (string: lowercase crop name, e.g. 'tomato', 'potato', 'rice', 'maize', 'chilli'), "
        "disease_name (string: specific disease name like 'Early Blight (Alternaria solani)' or 'Healthy Tomato Foliage' if completely healthy), "
        "confidence (integer between 0 and 100), "
        "severity (string: strictly one of 'low', 'medium', or 'high'), "
        "symptoms_seen (list of 2-5 strings describing observed visual signs on the foliage), "
        "recommended_actions (list of 2-5 strings with actionable organic/agronomic management steps), "
        "is_plant_leaf (boolean: true if image contains a plant leaf, false if non-leaf/non-plant). "
        "If the image is not a plant leaf, set is_plant_leaf to false, disease_name to 'Non-Leaf Object', and empty lists. "
        "Do not invent fake diseases if the leaf is healthy. Return only raw JSON without markdown formatting."
    )


def analyze_image(image_path: str, crop: str = "auto", original_filename: str = None) -> str:
    """
    Sends the leaf image to Gemini 2.5 Flash Vision if configured with a valid key.
    Falls back gracefully to the local computer vision leaf pathology engine.
    """
    if genai is not None and IS_VALID_KEY_FORMAT:
        try:
            prompt = _build_prompt(crop)
            generation_config = genai.GenerationConfig(
                temperature=0.2,
                max_output_tokens=600,
                top_p=0.8,
            )
            uploaded_file = genai.upload_file(path=image_path)
            model = genai.GenerativeModel(_MODEL)
            response = model.generate_content(
                [prompt, uploaded_file],
                generation_config=generation_config,
                request_options={"timeout": 25.0},
            )
            text = (response.text or "").strip()

            def _clean(txt: str) -> str:
                if txt.startswith("```json"):
                    txt = txt[len("```json"):].strip()
                elif txt.startswith("```"):
                    txt = txt[len("```"):].strip()
                if txt.endswith("```"):
                    txt = txt[:-3].strip()
                return txt

            cleaned = _clean(text)
            # Validate JSON
            parsed = json.loads(cleaned)
            if "disease_name" in parsed and "is_plant_leaf" in parsed:
                return cleaned
        except Exception as e:
            logger.warning(f"Gemini Vision call failed, falling back to local vision engine: {e}")

    # Local Computer Vision Pathology Engine (analyzes actual pixels, necrosis, chlorosis, and shape)
    result = analyze_leaf_image(image_path, crop_hint=crop, original_filename=original_filename)
    return json.dumps(result)
