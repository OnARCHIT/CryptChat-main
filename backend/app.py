# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os
import numpy as np
import re

app = Flask(__name__)

# Allowed origins
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:5173",
    "https://webrakshak.vercel.app"
]}})

# ---------------- Load Models ----------------
URL_MODEL_PATH = "model/model_compressed.joblib"
IMAGE_MODEL_PATH = "model/image_model/image_model_int8.tflite"

url_model = None
if os.path.exists(URL_MODEL_PATH):
    try:
        url_model = joblib.load(URL_MODEL_PATH)
    except Exception as e:
        print("Failed to load URL model:", e)

# For now, image_model placeholder
image_model_loaded = os.path.exists(IMAGE_MODEL_PATH)

# ---------------- Helper Functions ----------------
def heuristic_score(url: str) -> float:
    """Fallback heuristic score if URL model fails."""
    s = url.lower()
    score = 0.0
    tokens = ["login","secure","bank","signin","verify","account","update","free","confirm"]
    for t in tokens:
        if t in s: score += 0.12
    score += min(s.count('.')*0.02,0.12)
    score += min(s.count('-')*0.03,0.12)
    if re.search(r"https?://\d+\.\d+\.\d+\.\d+",s):
        score += 0.25
    if len(s)>100: score += 0.12
    if '@' in s: score += 0.2
    if s.count('?')>1 or len(s.split('?')[-1])>50:
        score += 0.08
    return min(score,0.99)

def classify(score: float):
    if score>=0.70:
        return "suspicious", "🚨 The link looks suspicious — treat as phishing. Do NOT enter credentials.", "red"
    if score>=0.40:
        return "new_phishing_type", "⚠️ This looks unusual and may be a new/unknown phishing pattern — proceed with caution.", "orange"
    return "safe", "✅ The link appears safe based on current checks.", "green"

# ---------------- Routes ----------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status":"OK","msg":"Backend running ✅"})

@app.route("/scan/url", methods=["POST"])
def scan_url():
    data = request.get_json(force=True)
    url = str(data.get("url","")).strip()
    if url=="":
        return jsonify({"error":"URL missing"}),400

    score = None
    if url_model:
        try:
            if hasattr(url_model,"predict_proba"):
                probs = url_model.predict_proba([url])
                score = float(probs[0][1])
            else:
                pred = url_model.predict([url])
                score = 0.9 if int(pred[0])==1 else 0.1
        except:
            score = None

    if score is None:
        score = heuristic_score(url)

    score = max(0.0,min(1.0,score))
    label,message,color = classify(score)
    return jsonify({
        "url": url,
        "score": round(score*100,2),
        "label": label,
        "message": message,
        "color": color
    })

@app.route("/scan/image", methods=["POST"])
def scan_image():
    if "file" not in request.files:
        return jsonify({"error":"No image uploaded"}),400
    file = request.files["file"]
    # Placeholder: can integrate TFLite model later
    result = {
        "filename": file.filename,
        "label": "untested",
        "message": "Image scanning not implemented yet",
        "color": "gray"
    }
    return jsonify(result)

@app.route("/scan/email", methods=["POST"])
def scan_email():
    data = request.get_json(force=True)
    text = (data.get("data") if data else "") or ""
    if text.strip()=="":
        return jsonify({"error":"Email missing"}),400
    # simple heuristic
    score = 0.0
    for k in ["password","verify","account","login","bank","ssn","urgent","confirm"]:
        if k in text.lower(): score+=0.12
    score = min(score,0.99)
    label,message,color = classify(score)
    return jsonify({"score": round(score*100,2),"label":label,"message":message,"color":color})

@app.route("/scan/voice", methods=["POST"])
def scan_voice():
    if "file" not in request.files:
        return jsonify({"error":"No audio uploaded"}),400
    file = request.files["file"]
    return jsonify({"filename": file.filename,"label":"untested","message":"Voice scanning not implemented","color":"gray"})

votes = []
@app.route("/api/vote-phish", methods=["POST"])
def vote_phish():
    data = request.get_json(force=True)
    url = data.get("url")
    vote = data.get("vote")
    if not url or not vote:
        return jsonify({"error":"URL & vote required"}),400
    entry = {"url":url,"vote":vote}
    votes.append(entry)
    return jsonify({"message":"Vote recorded ✅","data":entry})

@app.route("/api/history", methods=["GET"])
def get_history():
    return jsonify(votes[-10:])

if __name__=="__main__":
    app.run(debug=False,host="0.0.0.0",port=5000)
