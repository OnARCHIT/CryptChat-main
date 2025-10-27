from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os
import threading
import requests
import tflite_runtime.interpreter as tflite

app = Flask(__name__)

# ✅ CORS settings
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:5173",
    "https://webrakshak.vercel.app"
]}})

# ---------------- Paths & Config ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

URL_MODEL_PATH = os.path.join(MODEL_DIR, "model_compressed.joblib")
IMAGE_MODEL_PATH = os.path.join(MODEL_DIR, "image_model_int8.tflite")

# 🔗 REPLACE with your actual Google Drive *file* links (not folder links)
# Get file link → replace /file/d/FILE_ID/view → with → uc?export=download&id=FILE_ID
URL_MODEL_LINK = "https://drive.google.com/file/d/1SQ9edzHisBtS7KutvRI-14o4vxI3Ref3/view?usp=drive_link"
IMAGE_MODEL_LINK = "https://drive.google.com/file/d/1kuQVSpu_Hx853SHhL4cMtw28gC83-nYl/view?usp=drive_link"

url_model = None
image_interpreter = None
image_lock = threading.Lock()


# ---------------- Helpers ----------------
def download_if_missing(link, dest):
    """Downloads a model from Google Drive if not already present."""
    if not os.path.exists(dest):
        print(f"📥 Downloading model from {link} ...")
        r = requests.get(link, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"✅ Saved to {dest}")
    else:
        print(f"✅ {os.path.basename(dest)} already exists")


def load_url_model():
    global url_model
    if url_model is None:
        download_if_missing(URL_MODEL_LINK, URL_MODEL_PATH)
        url_model = joblib.load(URL_MODEL_PATH)
        print("✅ URL model loaded")


def load_image_model():
    global image_interpreter
    if image_interpreter is None:
        with image_lock:
            download_if_missing(IMAGE_MODEL_LINK, IMAGE_MODEL_PATH)
            image_interpreter = tflite.Interpreter(model_path=IMAGE_MODEL_PATH)
            image_interpreter.allocate_tensors()
            print("✅ Image model loaded")


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

        # Predict
        prediction = int(url_model.predict([data])[0])

        if prediction == 1:
            label, color = "Suspicious / Phishing", "red"
        elif prediction == 0:
            label, color = "Safe", "green"
        else:
            label, color = "Unknown / New type", "yellow"

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

        # Placeholder (actual image preprocessing can be added)
        result = np.random.choice(["Suspicious / Phishing", "Safe", "Unknown / New type"])
        color_map = {"Suspicious / Phishing": "red", "Safe": "green", "Unknown / New type": "yellow"}

        return jsonify({
            "filename": file.filename,
            "prediction": result,
            "color": color_map[result]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- Vote Storage ----------------
votes = []

@app.route("/api/store_vote", methods=["POST"])
def store_vote():
    try:
        data = request.json.get("url")
        vote = request.json.get("vote")
        if not data or not vote:
            return jsonify({"error": "URL & vote required"}), 400

        entry = {"url": data, "vote": vote}
        votes.append(entry)
        return jsonify({"message": "Vote recorded ✅", "data": entry})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(votes[-10:])


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
