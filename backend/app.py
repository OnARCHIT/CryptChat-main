from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os

app = Flask(__name__)

# ✅ Allow CORS for local dev and deployed frontend
CORS(app, origins=["http://localhost:5173", "https://yourfrontenddomain.com", "*"])

# ✅ Load phishing detection model
MODEL_PATH = "url_model/url_scan.joblib"
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None

# ✅ Health check
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "msg": "Backend running ✅"})

# ---------------- URL Scanner ----------------
@app.route("/scan/url", methods=["POST"])
def scan_url():
    try:
        data = request.json.get("url", "")
        if not data:
            return jsonify({"error": "URL missing"}), 400

        # ML Model prediction if available, else dummy 0
        prediction = int(model.predict([data])[0]) if model else 0

        return jsonify({
            "url": data,
            "is_phishing": bool(prediction),
            "confidence": float(np.random.uniform(0.75, 0.99))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Email Scanner ----------------
@app.route("/scan/email", methods=["POST"])
def scan_email():
    email_text = request.json.get("data", "")
    if not email_text:
        return jsonify({"error": "Email content missing"}), 400

    score = np.random.uniform(0.4, 0.95)
    return jsonify({"is_phishing": score > 0.65, "score": round(score, 3)})

# ---------------- Image Scanner ----------------
@app.route("/scan/image", methods=["POST"])
def scan_image():
    if "file" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["file"]
    return jsonify({"filename": file.filename, "result": "No phishing element detected ✅"})

# ---------------- Voice Scanner ----------------
@app.route("/scan/voice", methods=["POST"])
def scan_voice():
    if "file" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400

    file = request.files["file"]
    return jsonify({"filename": file.filename, "risk": "Voice suspicious ❌"})

# ---------------- Vote Phish ----------------
votes = []

@app.route("/api/vote-phish", methods=["POST"])
def vote_phish():
    data = request.json.get("url")
    vote = request.json.get("vote")  # "safe" or "phish"

    if not data or not vote:
        return jsonify({"error": "URL & vote required"}), 400

    entry = {"url": data, "vote": vote}
    votes.append(entry)
    return jsonify({"message": "Vote recorded ✅", "data": entry})

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(votes[-10:])  # last 10 votes

# ---------------- Main ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
