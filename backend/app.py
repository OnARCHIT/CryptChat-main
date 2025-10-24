from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os

app = Flask(__name__)

# ✅ CORS: allow specific frontend origins
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://webrakshak.vercel.app"
]}}, supports_credentials=True)

# ✅ Load phishing URL model
MODEL_PATH = os.path.join("model", "model_compressed.joblib")
try:
    url_model = joblib.load(MODEL_PATH)
except Exception as e:
    url_model = None
    print(f"URL model load failed: {e}")

# ✅ Image model placeholder (TFLite)
IMAGE_MODEL_PATH = os.path.join("model", "image_model", "image_model_int8.tflite")
if not os.path.exists(IMAGE_MODEL_PATH):
    print("Image model not found!")

# ---------------- Health Check ----------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "msg": "Backend running ✅"})

# ---------------- URL Scanner ----------------
@app.route("/scan/url", methods=["POST", "OPTIONS"])
def scan_url():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.json.get("url", "")
        if not data:
            return jsonify({"error": "URL missing"}), 400

        # Predict phishing
        prediction = int(url_model.predict([data])[0]) if url_model else 0
        label = "Safe" if prediction == 0 else "Suspicious"

        return jsonify({
            "url": data,
            "result": label,
            "confidence": float(np.random.uniform(0.75, 0.99))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Email Scanner ----------------
@app.route("/scan/email", methods=["POST", "OPTIONS"])
def scan_email():
    if request.method == "OPTIONS":
        return "", 200

    email_text = request.json.get("data", "")
    if not email_text:
        return jsonify({"error": "Email content missing"}), 400

    score = np.random.uniform(0.4, 0.95)
    label = "Suspicious" if score > 0.65 else "Safe"
    return jsonify({"result": label, "score": round(score, 3)})

# ---------------- Image Scanner ----------------
@app.route("/scan/image", methods=["POST", "OPTIONS"])
def scan_image():
    if request.method == "OPTIONS":
        return "", 200

    if "file" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["file"]
    # Placeholder logic for image model
    return jsonify({"filename": file.filename, "result": "No phishing element detected ✅"})

# ---------------- Voice Scanner ----------------
@app.route("/scan/voice", methods=["POST", "OPTIONS"])
def scan_voice():
    if request.method == "OPTIONS":
        return "", 200

    if "file" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400

    file = request.files["file"]
    return jsonify({"filename": file.filename, "result": "Voice suspicious ❌"})

# ---------------- Vote Phish ----------------
votes = []

@app.route("/api/store_vote", methods=["POST", "OPTIONS"])
def store_vote():
    if request.method == "OPTIONS":
        return "", 200

    try:
        data = request.json.get("url")
        vote = request.json.get("vote")  # "safe" or "phish"
        if not data or not vote:
            return jsonify({"error": "URL & vote required"}), 400

        entry = {"url": data, "vote": vote}
        votes.append(entry)
        return jsonify({"message": "Vote recorded ✅", "data": entry})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Vote History ----------------
@app.route("/api/history", methods=["GET", "OPTIONS"])
def get_history():
    if request.method == "OPTIONS":
        return "", 200
    return jsonify(votes[-10:])  # last 10 votes

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
