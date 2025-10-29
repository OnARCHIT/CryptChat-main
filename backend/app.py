from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os
import requests
import zipfile
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://webrakshak.vercel.app"}})

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://webrakshak.vercel.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# === Google Drive zip file IDs (replace with your actual zip IDs) ===
URL_MODEL_ID = "1SQ9edzHisBtS7KutvRI-14o4vxI3Ref3"
IMAGE_MODEL_ID = "1kuQVSpu_Hx853SHhL4cMtw28gC83-nYl"

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)
REWARD_FILE = os.path.join(MODEL_DIR, "reward_memory.json")

# ============================================================
# Helper: download + unzip Google Drive files
# ============================================================
def download_and_unzip(file_id, zip_path, extract_dir):
    if not os.path.exists(extract_dir):
        print(f"⬇️ Downloading zip from Google Drive ID: {file_id}")
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        r = requests.get(url)
        if r.status_code == 200:
            with open(zip_path, "wb") as f:
                f.write(r.content)
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"✅ Extracted to {extract_dir}")
        else:
            print(f"❌ Download failed: {r.status_code}")
    else:
        print(f"✅ Already exists at {extract_dir}")

# --- Download and extract models ---
url_extract_dir = os.path.join(MODEL_DIR, "url_model")
image_extract_dir = os.path.join(MODEL_DIR, "image_model")
download_and_unzip(URL_MODEL_ID, os.path.join(MODEL_DIR, "url_model.zip"), url_extract_dir)
download_and_unzip(IMAGE_MODEL_ID, os.path.join(MODEL_DIR, "image_model.zip"), image_extract_dir)

# --- Load models ---
url_model_path = os.path.join(url_extract_dir, "url_model.joblib")
image_model_path = os.path.join(image_extract_dir, "image_model.tflite")

print("🔹 Loading models into memory...")
try:
    url_model = joblib.load(url_model_path)
    print("✅ URL model loaded")
except Exception as e:
    print("⚠️ URL model load failed:", e)
    url_model = None

try:
    interpreter = tf.lite.Interpreter(model_path=image_model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print("✅ Image model loaded")
except Exception as e:
    print("⚠️ Image model load failed:", e)
    interpreter = None
    input_details = output_details = None

# ============================================================
#  Federated Reinforcement Feedback Logic
# ============================================================

def save_reward(data):
    """Store reinforcement feedback from user votes"""
    try:
        if os.path.exists(REWARD_FILE):
            with open(REWARD_FILE, "r") as f:
                memory = json.load(f)
        else:
            memory = []
        memory.append(data)
        with open(REWARD_FILE, "w") as f:
            json.dump(memory, f, indent=2)
        print("🧠 Feedback stored:", data)
    except Exception as e:
        print("⚠️ Could not save reward:", e)

def apply_reinforcement():
    """Lightweight self-adjustment based on feedback"""
    if not os.path.exists(REWARD_FILE) or url_model is None:
        return
    try:
        with open(REWARD_FILE, "r") as f:
            memory = json.load(f)
        if not memory:
            return
        X = []
        y = []
        for entry in memory:
            X.append(entry["features"])
            y.append(1 if entry["phish"] else 0)
        url_model.fit(np.array(X), np.array(y))
        joblib.dump(url_model, url_model_path)
        print(f"✅ Reinforcement update applied on {len(memory)} samples.")
        os.remove(REWARD_FILE)
    except Exception as e:
        print("⚠️ Reinforcement failed:", e)

# ============================================================
# Prediction Routes
# ============================================================

def preprocess_url(url):
    url = url.lower()
    max_len = 200
    x = [ord(c) for c in url[:max_len]]
    if len(x) < max_len:
        x += [0] * (max_len - len(x))
    return np.array([x])

@app.route("/scan/url", methods=["POST"])
def scan_url():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    if url_model is None:
        return jsonify({"error": "URL model not loaded"}), 500

    x = preprocess_url(url)
    score = float(url_model.predict_proba(x)[0][1])
    phishing = score > 0.5
    return jsonify({"score": score, "phishing": phishing})

@app.route("/feedback/url", methods=["POST"])
def feedback_url():
    """User feedback: store as reinforcement reward"""
    data = request.get_json()
    url = data.get("url")
    correct_label = data.get("phish")
    if url is None or correct_label is None:
        return jsonify({"error": "Missing parameters"}), 400
    features = preprocess_url(url).tolist()[0]
    save_reward({"features": features, "phish": correct_label})
    apply_reinforcement()
    return jsonify({"message": "Feedback received and applied"})

@app.route("/scan/image", methods=["POST"])
def scan_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    if interpreter is None:
        return jsonify({"error": "Image model not loaded"}), 500

    img_file = request.files["image"]
    img = image.load_img(img_file, target_size=(224, 224))
    x = image.img_to_array(img) / 255.0
    x = np.expand_dims(x, axis=0).astype(np.float32)

    interpreter.set_tensor(input_details[0]['index'], x)
    interpreter.invoke()
    score = float(interpreter.get_tensor(output_details[0]['index'])[0][0])
    phishing = score > 0.5
    return jsonify({"score": score, "phishing": phishing})

@app.route("/")
def home():
    return jsonify({"status": "running", "message": "Backend live & self-learning enabled"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
