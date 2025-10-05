# check_phish.py
import os
import json
import math
import traceback
from io import BytesIO

from flask import Flask, request, jsonify
from flask_cors import CORS

# Try to import tensorflow; if missing, return graceful error in responses
try:
    import numpy as np
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from PIL import Image
    TF_AVAILABLE = True
except Exception as e:
    TF_AVAILABLE = False
    _tf_import_error = str(e)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure paths to your saved models
URL_MODEL_PATH = "backend/models/url_model"                 # SavedModel folder or .keras/.h5
IMAGE_MODEL_PATH = "backend/models/image_model/image_model.keras"  # .keras file or folder
# Optional labels mapping for image model (if you saved it)
IMAGE_LABELS_PATH = "backend/models/image_model/labels.json"

# Load models (if available)
url_model = None
image_model = None
image_class_names = None

def safe_load_models():
    global url_model, image_model, image_class_names
    if not TF_AVAILABLE:
        app.logger.warning("TensorFlow not available: %s", _tf_import_error)
        return

    # Load URL model if path exists
    try:
        if os.path.exists(URL_MODEL_PATH):
            app.logger.info("Loading URL model from %s", URL_MODEL_PATH)
            url_model = load_model(URL_MODEL_PATH)
        else:
            app.logger.info("URL model path does not exist: %s", URL_MODEL_PATH)
    except Exception as e:
        app.logger.exception("Failed to load URL model: %s", e)

    # Load image model if path exists
    try:
        if os.path.exists(IMAGE_MODEL_PATH):
            app.logger.info("Loading image model from %s", IMAGE_MODEL_PATH)
            image_model = load_model(IMAGE_MODEL_PATH)
            # try load labels
            if os.path.exists(IMAGE_LABELS_PATH):
                try:
                    with open(IMAGE_LABELS_PATH, "r") as f:
                        image_class_names = json.load(f)
                except Exception:
                    image_class_names = None
        else:
            app.logger.info("Image model path does not exist: %s", IMAGE_MODEL_PATH)
    except Exception as e:
        app.logger.exception("Failed to load image model: %s", e)

# Run model loading at startup
safe_load_models()


# -------------------------
# Utilities
# -------------------------
def heuristic_url_features(url: str, n_features: int):
    """
    Compute a small set of heuristic URL features and pad/truncate to n_features.
    This is a fallback for when you don't have the exact feature extraction used
    to train the URL model. Best practice: replace this with the same preprocessing
    pipeline used at training time.
    """
    url = url.strip()
    length = len(url)
    num_dots = url.count(".")
    num_hyphen = url.count("-")
    num_at = url.count("@")
    num_qm = url.count("?")
    num_equals = url.count("=")
    num_slash = url.count("/")
    num_digits = sum(c.isdigit() for c in url)
    num_letters = sum(c.isalpha() for c in url)
    entropy = 0.0
    try:
        # rough char entropy
        from collections import Counter
        counts = Counter(url)
        probs = [v/length for v in counts.values()] if length>0 else [0]
        import math
        entropy = -sum(p * math.log2(p) for p in probs if p>0)
    except Exception:
        entropy = 0.0

    features = [
        length,
        num_dots,
        num_hyphen,
        num_at,
        num_qm,
        num_equals,
        num_slash,
        num_digits,
        num_letters,
        entropy
    ]

    # normalize / scale with simple transforms to keep numbers reasonable
    features = [float(f) for f in features]
    # pad/truncate to desired length
    if n_features <= len(features):
        return np.array(features[:n_features], dtype=np.float32)
    else:
        pad = [0.0] * (n_features - len(features))
        return np.array(features + pad, dtype=np.float32)


def prepare_image(file_bytes, target_size):
    """
    Open image bytes, convert to RGB, resize to target_size (width, height),
    return float32 numpy array with shape (1, H, W, 3) normalized to [0,1]
    """
    img = Image.open(BytesIO(file_bytes)).convert("RGB")
    img = img.resize((target_size[0], target_size[1]), Image.BICUBIC)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr


# -------------------------
# Main endpoint
# -------------------------
@app.route("/check-phish", methods=["POST"])
def check_phish():
    """
    Accepts:
      - form field 'url' (plain text)
      - multipart file field 'image' or 'file'
    Returns JSON:
      {
        phishing: bool,
        scores: { url_score, image_score, file_score },
        explanation: "...",
        details: {...}
      }
    """
    if not TF_AVAILABLE:
        return jsonify({"error": "TensorFlow not installed on backend", "details": _tf_import_error}), 500

    try:
        result = {
            "phishing": False,
            "scores": {"url_score": None, "image_score": None, "file_score": None},
            "explanation": None,
            "details": {}
        }

        # 1) URL flow
        url = request.form.get("url") or request.args.get("url")
        if url:
            if url_model is None:
                return jsonify({"error": "URL model not loaded on server"}), 500

            # determine required input size for model
            try:
                input_shape = url_model.input_shape  # e.g. (None, N)
                # find feature length
                if isinstance(input_shape, (list, tuple)):
                    # handle nested models
                    if isinstance(input_shape[0], (list, tuple)):
                        n_in = int(input_shape[0][-1])
                    else:
                        n_in = int(input_shape[-1])
                else:
                    n_in = int(input_shape[-1])
            except Exception:
                n_in = 24  # fallback

            # build heuristic features (replace with your real preprocess)
            feats = heuristic_url_features(url, n_in).reshape(1, -1)

            try:
                url_pred = url_model.predict(feats)
                # model may return a single score or vector
                if isinstance(url_pred, (list, tuple)):
                    url_score = float(url_pred[0].ravel()[0])
                else:
                    url_score = float(np.asarray(url_pred).ravel()[0])
                phishing = bool(url_score > 0.5)
                result["scores"]["url_score"] = url_score
                result["phishing"] = phishing
                result["explanation"] = f"URL score >0.5 => phishing" if phishing else "URL looks safe by model threshold"
                result["details"]["url_features_used"] = feats.tolist()
                return jsonify(result)
            except Exception as e:
                app.logger.exception("URL model inference failed")
                return jsonify({"error": "URL model inference failed", "details": str(e)}), 500

        # 2) Image/file flow
        if "image" in request.files or "file" in request.files:
            key = "image" if "image" in request.files else "file"
            f = request.files[key]
            if f.filename == "":
                return jsonify({"error": "Empty filename"}), 400

            if image_model is None:
                return jsonify({"error": "Image model not loaded on server"}), 500

            # get target input shape from model
            try:
                in_shape = image_model.input_shape  # e.g. (None, H, W, C)
                if isinstance(in_shape, (list, tuple)):
                    # if a list, choose first; then deduce H,W
                    s = in_shape[0] if isinstance(in_shape[0], (list, tuple)) else in_shape
                else:
                    s = in_shape
                # find spatial dims
                if len(s) == 4:
                    _, H, W, C = s
                elif len(s) == 3:
                    H, W, C = s
                else:
                    H, W = 224, 224
                H = int(H) if H is not None else 224
                W = int(W) if W is not None else 224
            except Exception:
                H, W = 224, 224

            # read bytes and prepare
            file_bytes = f.read()
            try:
                img_arr = prepare_image(file_bytes, (W, H))
            except Exception as e:
                app.logger.exception("Failed to process image")
                return jsonify({"error": "Failed to process image", "details": str(e)}), 400

            try:
                pred = image_model.predict(img_arr)
                # If multi-class, return probabilities; if binary, take single score
                arr = np.asarray(pred).ravel()
                if arr.size == 1:
                    score = float(arr[0])
                    phishing = bool(score > 0.5)
                    result["scores"]["image_score"] = score
                    result["phishing"] = phishing
                    result["explanation"] = "Binary image model score"
                else:
                    # multi-class - pick top predicted class
                    top_idx = int(arr.argmax())
                    top_prob = float(arr[top_idx])
                    label = None
                    if image_class_names:
                        # if labels mapping is dict of index->name
                        try:
                            label = image_class_names.get(str(top_idx)) or image_class_names[top_idx]
                        except Exception:
                            label = str(top_idx)
                    else:
                        # fallback to index name
                        label = str(top_idx)
                    result["scores"]["image_score"] = {"top_index": top_idx, "top_prob": top_prob, "label": label}
                    # heuristic: if top label is in known brand login_pages list mark suspicious (this is domain-specific)
                    suspicious_labels = ["login_pages", "phishing", "phish"]  # customize
                    result["phishing"] = any(s in str(label).lower() for s in suspicious_labels) and top_prob > 0.6
                    result["explanation"] = f"Multi-class image model predicted {label} with prob {top_prob:.3f}"
                result["details"]["raw_prediction"] = arr.tolist()
                return jsonify(result)
            except Exception as e:
                app.logger.exception("Image model inference failed")
                return jsonify({"error": "Image model inference failed", "details": str(e)}), 500

        # 3) No input provided
        return jsonify({"error": "No 'url' or 'image/file' provided in request"}), 400

    except Exception as e:
        app.logger.exception("Unexpected error in check_phish")
        return jsonify({"error": "Unexpected server error", "details": traceback.format_exc()}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
