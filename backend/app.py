from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os
import requests
import tempfile
import tensorflow as tf
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

# ✅ Enable CORS for your frontend origin
CORS(app, resources={r"/*": {"origins": "https://webrakshak.vercel.app"}})

# ✅ Optional: Add CORS headers manually (for strict browsers)
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://webrakshak.vercel.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


# === GOOGLE DRIVE MODEL LINKS (Direct downloadable) ===
URL_MODEL_ID = "1SQ9edzHisBtS7KutvRI-14o4vxI3Ref3"
IMAGE_MODEL_ID = "1kuQVSpu_Hx853SHhL4cMtw28gC83-nYl"

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

url_model_path = os.path.join(MODEL_DIR, "url_model.joblib")
image_model_path = os.path.join(MODEL_DIR, "image_model.keras")

def download_from_gdrive(file_id, dest_path):
    """Downloads file from Google Drive if not already cached"""
    if os.path.exists(dest_path):
        print(f"✅ Model already exists at {dest_path}")
        return dest_path
    print(f"⬇️ Downloading model from Google Drive ID: {file_id}")
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(dest_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Model saved at {dest_path}")
    else:
        print(f"❌ Failed to download model: {response.status_code}")
    return dest_path


# === LOAD MODELS ===
print("🔹 Preparing models...")
download_from_gdrive(URL_MODEL_ID, url_model_path)
download_from_gdrive(IMAGE_MODEL_ID, image_model_path)

print("🔹 Loading models into memory...")
try:
    url_model = joblib.load(url_model_path)
except Exception as e:
    print("⚠️ Could not load URL model:", e)
    url_model = None

try:
    image_model = tf.keras.models.load_model(image_model_path)
except Exception as e:
    print("⚠️ Could not load image model:", e)
    image_model = None


# === URL SCAN ===
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
    try:
        score = float(url_model.predict_proba(x)[0][1])
    except Exception:
        score = 0.5  # neutral fallback
    phishing = score > 0.5
    return jsonify({"score": score, "phishing": phishing})


# === IMAGE SCAN ===
@app.route("/scan/image", methods=["POST"])
def scan_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    if image_model is None:
        return jsonify({"error": "Image model not loaded"}), 500

    img_file = request.files["image"]
    img = image.load_img(img_file, target_size=(224, 224))
    x = image.img_to_array(img) / 255.0
    x = np.expand_dims(x, axis=0)

    try:
        score = float(image_model.predict(x)[0][0])
    except Exception:
        score = 0.5
    phishing = score > 0.5
    return jsonify({"score": score, "phishing": phishing})


# === HEALTH CHECK ===
@app.route("/")
def home():
    return jsonify({"status": "running", "message": "Backend is live and CORS-enabled"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
