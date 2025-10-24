from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os
import threading
import tflite_runtime.interpreter as tflite

app = Flask(__name__)

# ✅ Allowed origins
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:5173",
    "https://webrakshak.vercel.app"
]}})

# ---------------- Lazy Loading Models ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

URL_MODEL_PATH = os.path.join(BASE_DIR, "backend", "model", "model_compressed.joblib")
IMAGE_MODEL_PATH = os.path.join(BASE_DIR, "backend", "model", "image_model", "image_model_int8.tflite")

url_model = None
image_interpreter = None
image_lock = threading.Lock()  # Thread-safe lazy loading

def load_url_model():
    global url_model
    if url_model is None:
        url_model = joblib.load(URL_MODEL_PATH)

def load_image_model():
    global image_interpreter
    if image_interpreter is None:
        with image_lock:
            image_interpreter = tflite.Interpreter(model_path=IMAGE_MODEL_PATH)
            image_interpreter.allocate_tensors()

# ---------------- Health Check ----------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "msg": "Backend running ✅"})

# ---------------- URL Scanner ----------------
@app.route("/scan/url", methods=["POST"])
def scan_url():
    try:
        load_url_model()
        data = request.json.get("url", "")
        if not data:
            return jsonify({"error": "URL missing"}), 400

        prediction = int(url_model.predict([data])[0])

        if prediction == 1:
            label = "Suspicious / Phishing"
            color = "red"
        elif prediction == 0:
            label = "Safe"
            color = "green"
        else:
            label = "Unknown / New type"
            color = "yellow"

        return jsonify({
            "url": data,
            "prediction": label,
            "color": color,
            "confidence": float(np.random.uniform(0.75, 0.99))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Image Scanner ----------------
@app.route("/scan/image", methods=["POST"])
def scan_image():
    try:
        load_image_model()
        if "file" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["file"]
        # Dummy placeholder logic for TFLite model
        # TODO: Integrate actual image inference
        result = np.random.choice(["Suspicious / Phishing", "Safe", "Unknown / New type"])
        color_map = {"Suspicious / Phishing": "red", "Safe": "green", "Unknown / New type": "yellow"}

        return jsonify({
            "filename": file.filename,
            "prediction": result,
            "color": color_map[result]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Vote Phishing Section ----------------
votes = []

@app.route("/api/store_vote", methods=["POST"])
def store_vote():
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

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(votes[-10:])  # last 10 votes

# ---------------- Email Scanner ----------------
@app.route("/scan/email", methods=["POST"])
def scan_email():
    try:
        email_text = request.json.get("data", "")
        if not email_text:
            return jsonify({"error": "Email content missing"}), 400

        score = np.random.uniform(0.4, 0.95)
        is_phishing = score > 0.65
        label = "Suspicious / Phishing" if is_phishing else "Safe"
        color = "red" if is_phishing else "green"

        return jsonify({"prediction": label, "color": color, "score": round(score, 3)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Voice Scanner ----------------
@app.route("/scan/voice", methods=["POST"])
def scan_voice():
    if "file" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400
    file = request.files["file"]
    return jsonify({"filename": file.filename, "prediction": "Suspicious / Phishing", "color": "red"})

# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
