from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)

# ✅ Allow ALL origins, methods & headers
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

def dummy_scan_result():
    return {
        "score": random.randint(60, 95),
        "details": [
            {"reason": "Suspicious domain pattern", "confidence": 0.85},
            {"reason": "Potential phishing indicators", "confidence": 0.72},
        ],
    }

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "✅ WebRakshak Backend is Running Successfully!",
        "endpoints": ["/scan/url", "/scan/email", "/scan/image", "/scan/voice"]
    })

@app.route("/scan/url", methods=["POST"])
def scan_url():
    url = request.json.get("url", "")
    result = dummy_scan_result()
    result["input"] = url
    return jsonify(result)

@app.route("/scan/email", methods=["POST"])
def scan_email():
    email_content = request.json.get("email", "")
    result = dummy_scan_result()
    result["input"] = email_content
    return jsonify(result)

@app.route("/scan/image", methods=["POST"])
def scan_image():
    if "file" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    result = dummy_scan_result()
    result["fileName"] = request.files["file"].filename
    return jsonify(result)

@app.route("/scan/voice", methods=["POST"])
def scan_voice():
    if "file" not in request.files:
        return jsonify({"error": "No audio provided"}), 400
    result = dummy_scan_result()
    result["fileName"] = request.files["file"].filename
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
