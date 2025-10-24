from flask import Flask, request, jsonify, send_from_directory
import tensorflow as tf
import keras
import numpy as np
from tensorflow.keras.preprocessing import image
import os
from flask_cors import CORS  # <--- Enable CORS

# ==== Enable unsafe deserialization for Lambda layers ====
keras.config.enable_unsafe_deserialization()

app = Flask(__name__)
CORS(app)  # <--- Allow frontend to access backend

# ==== Paths ====
URL_MODEL_PATH = "model/url_model.keras"
IMAGE_MODEL_PATH = "model/image_model/image_model_int8.tflite"
EMAIL_MODEL_PATH = "model/email_model.keras"  # optional email model if exists

# ==== Load Models ====
url_model = tf.keras.models.load_model(URL_MODEL_PATH, compile=False)

image_interpreter = tf.lite.Interpreter(model_path=IMAGE_MODEL_PATH)
image_interpreter.allocate_tensors()
image_input = image_interpreter.get_input_details()[0]
image_output = image_interpreter.get_output_details()[0]
input_index = image_input["index"]
output_index = image_output["index"]
input_scale, input_zero_point = image_input["quantization"]
output_scale, output_zero_point = image_output["quantization"]

# Optional: Email model
try:
    email_model = tf.keras.models.load_model(EMAIL_MODEL_PATH, compile=False)
except:
    email_model = None

# ==== Helper Functions ====
def preprocess_url(url):
    url = url.lower()
    max_len = 200
    x = [ord(c) for c in url[:max_len]]
    if len(x) < max_len:
        x += [0] * (max_len - len(x))
    return np.array([x])

def preprocess_email(email):
    if email_model is None:
        return None
    email = email.lower()
    max_len = 200
    x = [ord(c) for c in email[:max_len]]
    if len(x) < max_len:
        x += [0] * (max_len - len(x))
    return np.array([x])

def predict_image(img_file):
    img = image.load_img(img_file, target_size=(224, 224))
    x = image.img_to_array(img) / 255.0
    x = np.expand_dims(x, axis=0).astype(np.float32)
    if input_scale > 0:
        x_q = (x / input_scale + input_zero_point).astype(np.uint8)
    else:
        x_q = x.astype(np.uint8)
    image_interpreter.set_tensor(input_index, x_q)
    image_interpreter.invoke()
    output = image_interpreter.get_tensor(output_index)
    score = (output[0][0] - output_zero_point) * output_scale
    return float(score)

# ==== API Endpoints ====
@app.route("/")
def home():
    return "✅ PhisingSheild Backend is Running! API endpoints: /scan_url, /scan_image, /scan_email"

@app.route("/scan_url", methods=["POST"])
def scan_url():
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing URL"}), 400
    x = preprocess_url(data["url"])
    score = float(url_model.predict(x)[0][0])
    phishing = score > 0.5
    return jsonify({
        "score": score,
        "phishing": phishing,
        "details":[{"reason":"URL check","confidence":score}]
    })

@app.route("/scan_image", methods=["POST"])
def scan_image():
    if "file" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    score = predict_image(request.files["file"])
    phishing = score > 0.5
    return jsonify({
        "score": score,
        "phishing": phishing,
        "details":[{"reason":"Image check","confidence":score}]
    })

@app.route("/scan_email", methods=["POST"])
def scan_email():
    if email_model is None:
        return jsonify({"error": "Email model not available"}), 501
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Missing email"}), 400
    x = preprocess_email(data["email"])
    score = float(email_model.predict(x)[0][0])
    phishing = score > 0.5
    return jsonify({
        "score": score,
        "phishing": phishing,
        "details":[{"reason":"Email check","confidence":score}]
    })

# ==== Serve TFJS Model Files ====
@app.route("/tfjs/<path:filename>")
def serve_tfjs(filename):
    return send_from_directory('.', filename)

# ==== Main ====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
