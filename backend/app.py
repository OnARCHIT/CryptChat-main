# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import numpy as np
import re

# ML imports
import tensorflow as tf

app = Flask(__name__)

# Allowed origins
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:5173",
    "https://webrakshak.vercel.app"
]}})

# ---------------- Load URL Keras model ----------------
URL_MODEL_PATH = "model/url_model.keras"
url_model = None
try:
    if os.path.exists(URL_MODEL_PATH):
        url_model = tf.keras.models.load_model(URL_MODEL_PATH)
except Exception as e:
    print(f"[WARN] Could not load URL Keras model: {e}")
    url_model = None

# ---------------- Load image TFLite model ----------------
IMAGE_MODEL_PATH = "model/image_model_int8.tflite"
image_interpreter = None
try:
    if os.path.exists(IMAGE_MODEL_PATH):
        image_interpreter = tf.lite.Interpreter(model_path=IMAGE_MODEL_PATH)
        image_interpreter.allocate_tensors()
except Exception as e:
    print(f"[WARN] Could not load TFLite image model: {e}")
    image_interpreter = None

# ---------------- Helper functions ----------------
def simple_heuristic_score(url: str) -> float:
    """Fallback score for phishing URL (0-1)."""
    s = url.lower()
    score = 0.0
    tokens = ["login", "secure", "bank", "ebayisapi", "signin", "verify", "account", "update", "free", "confirm"]
    for t in tokens:
        if t in s:
            score += 0.12
    score += min(s.count('.') * 0.02, 0.12)
    score += min(s.count('-') * 0.03, 0.12)
    if re.search(r"https?://\d+\.\d+\.\d+\.\d+", s):
        score += 0.25
    if len(s) > 100:
        score += 0.12
    if '@' in s:
        score += 0.2
    if s.count('?') > 1 or len(s.split('?')[-1]) > 50:
        score += 0.08
    return min(score, 0.99)

def classify_from_score(score: float):
    if score >= 0.70:
        return ("suspicious", "🚨 The link looks suspicious — treat as phishing. Do NOT enter credentials.", "red")
    if score >= 0.40:
        return ("new_phishing_type", "⚠️ This looks unusual and may be a new/unknown phishing pattern — proceed with caution.", "orange")
    return ("safe", "✅ The link appears safe based on current checks.", "green")

# ---------------- Routes ----------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "msg": "CryptChat Backend running"})

@app.route("/scan/url", methods=["POST"])
def scan_url():
    try:
        payload = request.get_json(force=True, silent=True)
        url = (payload.get("url") if payload else "").strip()
        if not url:
            return jsonify({"error": "URL missing"}), 400

        score = None

        # Use Keras model if available
        if url_model is not None:
            try:
                # Simple example: model expects tokenized/embedded input
                # Replace this with your proper preprocessing if needed
                # For demo: predict on length vector
                input_vector = np.array([[len(url)]], dtype=np.float32)
                pred = url_model.predict(input_vector)
                score = float(pred[0][0])  # assume output 0-1
            except Exception:
                score = None

        # fallback
        if score is None:
            score = simple_heuristic_score(url)

        score = float(max(0.0, min(1.0, score)))
        label, message, color = classify_from_score(score)
        return jsonify({
            "url": url,
            "score": round(score*100,2),
            "label": label,
            "message": message,
            "color": color
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/scan/image", methods=["POST"])
def scan_image():
    if "file" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    f = request.files["file"]
    # For demo: not running TFLite inference yet
    return jsonify({"filename": f.filename, "label": "untested", "message": "Image scanning placeholder", "color": "gray"})

@app.route("/scan/email", methods=["POST"])
def scan_email():
    data = request.get_json(force=True, silent=True)
    text = (data.get("data") if data else "").strip()
    if not text:
        return jsonify({"error": "Email content missing"}), 400
    # simple heuristic
    score = 0.0
    for k in ["password", "verify", "account", "login", "bank", "urgent", "confirm"]:
        if k in text.lower():
            score += 0.12
    score = min(score, 0.99)
    label, message, color = classify_from_score(score)
    return jsonify({"score": round(score*100,2), "label": label, "message": message, "color": color})

@app.route("/scan/voice", methods=["POST"])
def scan_voice():
    if "file" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400
    f = request.files["file"]
    return jsonify({"filename": f.filename, "label": "untested", "message": "Voice scanning placeholder", "color": "gray"})

votes = []

@app.route("/api/vote-phish", methods=["POST"])
def vote_phish():
    payload = request.get_json(force=True, silent=True)
    if not payload or "url" not in payload or "vote" not in payload:
        return jsonify({"error": "Missing 'url' or 'vote'"}), 400
    entry = {"url": payload["url"], "vote": payload["vote"]}
    votes.append(entry)
    return jsonify({"message": "Vote recorded", "data": entry})

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(votes[-50:])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
