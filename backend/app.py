from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
import os
import requests
import zipfile
import tensorflow as tf
from tensorflow.keras.preprocessing import image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://webrakshak.vercel.app"}})

@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://webrakshak.vercel.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response


# === Google Drive zip file IDs (replace with your actual zip IDs) ===
URL_MODEL_ID = "1SQ9edzHisBtS7KutvRI-14o4vxI3Ref3"     # zipped URL model
IMAGE_MODEL_ID = "1kuQVSpu_Hx853SHhL4cMtw28gC83-nYl"    # zipped image model

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)


def download_and_unzip(file_id, zip_path, extract_dir):
    """Downloads and unzips model from Google Drive if not already done"""
    if not os.path.exists(extract_dir):
        print(f"⬇️ Downloading zip from Google Drive ID: {file_id}")
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        r = requests.get(url)
        if r.status_code == 200:
            with open(zip_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Downloaded {zip_path}")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"✅ Extracted to {extract_dir}")
        else:
            print(f"❌ Download failed: {r.status_code}")
    else:
        print(f"✅ Already exists at {extract_dir}")


# --- Download + extract models ---
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


# === URL scan ===
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

    try:
        x = preprocess_url(url)
        score = float(url_model.predict_proba(x)[0][1])
    except Exception:
        score = 0.5
    phishing = score > 0.5
    return jsonify({"score": score, "phishing": phishing})


# === Image scan ===
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

    try:
        interpreter.set_tensor(input_details[0]['index'], x)
        interpreter.invoke()
        score = float(interpreter.get_tensor(output_details[0]['index'])[0][0])
    except Exception:
        score = 0.5
    phishing = score > 0.5
    return jsonify({"score": score, "phishing": phishing})


# === Health check ===
@app.route("/")
def home():
    return jsonify({"status": "running", "message": "Backend live & CORS-enabled"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
