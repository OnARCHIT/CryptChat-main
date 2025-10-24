from flask import Flask, request, jsonify
from flask_cors import CORS

# ------------------- Flask App -------------------
app = Flask(__name__)
CORS(app)  # Allow all origins, you can restrict to your frontend domain

# ------------------- Helper Function (Dummy) -------------------
def dummy_scan_result():
    """
    Returns a dummy scan result.
    Replace this with real ML or rule-based scanning logic.
    """
    return {
        "score": 85,
        "details": [
            {"reason": "Suspicious domain pattern", "confidence": 0.9},
            {"reason": "Blacklisted IP", "confidence": 0.75},
        ],
    }

# ------------------- Routes -------------------
@app.route("/scan/url", methods=["POST"])
def scan_url():
    data = request.get_json()
    url = data.get("url", "")
    # Add real URL scanning logic here
    return jsonify(dummy_scan_result())

@app.route("/scan/email", methods=["POST"])
def scan_email():
    data = request.get_json()
    email_content = data.get("data", "")
    # Add real email scanning logic here
    return jsonify(dummy_scan_result())

@app.route("/scan/image", methods=["POST"])
def scan_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    # Add real image scanning logic here
    return jsonify(dummy_scan_result())

@app.route("/scan/voice", methods=["POST"])
def scan_voice():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    # Add real voice scanning logic here
    return jsonify(dummy_scan_result())

# ------------------- Main -------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
