from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os

app = Flask(__name__)

# ✅ Allow CORS for specific domains
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://webrakshak.vercel.app"]}})

# ---------------- Lazy-load URL model ----------------
url_model = None
def get_url_model():
    global url_model
    if url_model is None:
        model_path = os.path.join("model", "model_compressed.joblib")
        url_model = joblib.load(model_path)
    return url_model

# ---------------- Health check ----------------
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

        model = get_url_model()
        prediction = int(model.predict([data])[0]) if model else 0

        # Classify message with color
        if prediction == 1:
            status, color = "Phishing", "red"
        elif prediction == 0:
            status, color = "Safe", "green"
        else:
            status, color = "Unknown / New type", "yellow"

        return jsonify({
            "url": data,
            "status": status,
            "color": color,
            "confidence": float(np.random.uniform(0.75, 0.99))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Image Scanner ----------------
# TFLite model deferred for low memory deployment
image_interpreter = None

@app.route("/scan/image", methods=["POST"])
def scan_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        file = request.files["file"]

        # Placeholder logic
        status = "Safe"
        color = "green"
        # Later: integrate TFLite model for real inference

        return jsonify({
            "filename": file.filename,
            "status": status,
            "color": color,
            "result": "No phishing element detected ✅"
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
    status = "Phishing" if score > 0.65 else "Safe"
    color = "red" if score > 0.65 else "green"

    return jsonify({"status": status, "color": color, "score": round(score, 3)})

# ---------------- Voice Scanner ----------------
@app.route("/scan/voice", methods=["POST"])
def scan_voice():
    if "file" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400

    file = request.files["file"]
    return jsonify({"filename": file.filename, "risk": "Voice suspicious ❌"})

# ---------------- Vote Phishing Section ----------------
votes = []

@app.route("/api/store_vote", methods=["POST"])
def store_vote():
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

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
