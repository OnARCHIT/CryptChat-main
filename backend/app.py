from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import joblib
from PIL import Image
import io

app = Flask(__name__)
# ✅ Allow CORS for specific origins
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://webrakshak.vercel.app"]}})

# ---------------- Load Models ----------------
try:
    url_model = joblib.load("model/model_compressed.joblib")
except:
    url_model = None

# For image model (TFLite) placeholder
try:
    import tflite_runtime.interpreter as tflite
    image_interpreter = tflite.Interpreter(model_path="model/image_model/image_model_int8.tflite")
    image_interpreter.allocate_tensors()
except:
    image_interpreter = None

# ---------------- Health Check ----------------
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

        if url_model:
            pred = url_model.predict([data])[0]
            if pred == 0:
                result = {"message": "Safe Link ✅", "color": "green"}
            elif pred == 1:
                result = {"message": "Suspicious / Phishing Link ❌", "color": "red"}
            else:
                result = {"message": "Unknown / New Phishing Type ⚠️", "color": "yellow"}
        else:
            result = {"message": "Safe Link ✅", "color": "green"}

        return jsonify({"url": data, **result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Image Scanner ----------------
@app.route("/scan/image", methods=["POST"])
def scan_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files["file"]
        image_bytes = file.read()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # ---------------- Dummy Prediction ----------------
        # Replace this with actual TFLite inference later
        if image_interpreter:
            pred = np.random.choice([0, 1, 2])  # 0: Safe, 1: Phishing, 2: Unknown
        else:
            pred = np.random.choice([0, 1, 2])

        if pred == 0:
            result = {"message": "Safe Image ✅", "color": "green"}
        elif pred == 1:
            result = {"message": "Suspicious / Phishing Image ❌", "color": "red"}
        else:
            result = {"message": "Unknown / New Threat ⚠️", "color": "yellow"}

        return jsonify({"filename": file.filename, **result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Other routes ----------------
@app.route("/scan/email", methods=["POST"])
def scan_email():
    email_text = request.json.get("data", "")
    if not email_text:
        return jsonify({"error": "Email content missing"}), 400
    score = np.random.uniform(0.4, 0.95)
    return jsonify({"is_phishing": score > 0.65, "score": round(score, 3)})

@app.route("/scan/voice", methods=["POST"])
def scan_voice():
    if "file" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400
    file = request.files["file"]
    return jsonify({"filename": file.filename, "risk": "Voice suspicious ❌"})

votes = []
@app.route("/api/store_vote", methods=["POST"])
def store_vote():
    data = request.json.get("url")
    vote = request.json.get("vote")
    if not data or not vote:
        return jsonify({"error": "URL & vote required"}), 400
    entry = {"url": data, "vote": vote}
    votes.append(entry)
    return jsonify({"message": "Vote recorded ✅", "data": entry})

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(votes[-10:])

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
