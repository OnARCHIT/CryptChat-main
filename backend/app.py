from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from PIL import Image
import io
import tflite_runtime.interpreter as tflite

app = Flask(__name__)

# ✅ Allow CORS only for specific origins
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "https://webrakshak.vercel.app"]}})

# ---------------- Lazy load URL model ----------------
url_model = None
def get_url_model():
    global url_model
    if url_model is None:
        url_model = joblib.load("backend/model/model_compressed.joblib")
    return url_model

# ---------------- Lazy load Image model ----------------
image_interpreter = None
def get_image_model():
    global image_interpreter
    if image_interpreter is None:
        image_interpreter = tflite.Interpreter(model_path="backend/model/image_model/image_model_int8.tflite")
        image_interpreter.allocate_tensors()
    return image_interpreter

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
        pred = int(model.predict([data])[0])

        # Color-coded message
        if pred == 0:
            result_msg = {"message": "Safe ✅", "color": "green"}
        elif pred == 1:
            result_msg = {"message": "Phishing ❌", "color": "red"}
        else:
            result_msg = {"message": "New type ⚠️", "color": "yellow"}

        return jsonify({"url": data, **result_msg})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Image Scanner ----------------
@app.route("/scan/image", methods=["POST"])
def scan_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        file = request.files["file"]
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB").resize((224,224))

        # Prepare TFLite input
        interpreter = get_image_model()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        input_data = np.expand_dims(np.array(img, dtype=np.uint8), axis=0)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])[0]
        pred_class = int(np.argmax(output_data))

        # Color-coded message
        if pred_class == 0:
            result_msg = {"message": "Safe ✅", "color": "green"}
        elif pred_class == 1:
            result_msg = {"message": "Phishing ❌", "color": "red"}
        else:
            result_msg = {"message": "New type ⚠️", "color": "yellow"}

        return jsonify({"filename": file.filename, **result_msg})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Email Scanner ----------------
@app.route("/scan/email", methods=["POST"])
def scan_email():
    email_text = request.json.get("data", "")
    if not email_text:
        return jsonify({"error": "Email content missing"}), 400
    score = np.random.uniform(0.4, 0.95)
    result_msg = {"message": "Phishing ❌", "color": "red"} if score>0.65 else {"message": "Safe ✅", "color": "green"}
    return jsonify({"score": round(score,3), **result_msg})

# ---------------- Voice Scanner ----------------
@app.route("/scan/voice", methods=["POST"])
def scan_voice():
    if "file" not in request.files:
        return jsonify({"error": "No audio uploaded"}), 400
    file = request.files["file"]
    return jsonify({"filename": file.filename, "message": "Voice suspicious ❌", "color": "red"})

# ---------------- Vote Phish Section ----------------
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

# ---------------- Main ----------------
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
