# 📘 MODEL DIRECTORY

This folder contains placeholders for the **AI models** used by the backend.

⚠️ **Note:** The actual trained models are **not stored in this repository**.  
This ensures the repo remains under **25 MB** and deploys smoothly on **Render**, **GitHub**, or **Hugging Face Spaces**.

---

## ✅ MODEL AUTO-DOWNLOAD FEATURE

When the backend starts (`app.py`), it automatically checks for missing models and downloads them from **Google Drive**.  
You don’t need to upload any large files manually.

---

## 📦 MODEL DETAILS

### 1️⃣ URL MODEL
- **Filename:** `model_compressed.joblib`  
- **Google Drive Link:**  
  [Download model_compressed.joblib](https://drive.google.com/file/d/1SQ9edzHisBtS7KutvRI-14o4vxI3Ref3/view?usp=drive_link)
- **Purpose:** Detects whether a given URL is *phishing* or *safe* using trained ML features.

### 2️⃣ IMAGE MODEL
- **Filename:** `image_model_int8.tflite`  
- **Google Drive Link:**  
  [Download image_model_int8.tflite](https://drive.google.com/file/d/1kuQVSpu_Hx853SHhL4cMtw28gC83-nYl/view?usp=drive_link)
- **Purpose:** Identifies *phishing elements* in webpage or email **screenshots** using a lightweight TensorFlow Lite CNN.

---

## 🧠 HOW IT WORKS

When you send a request to:
- `POST /scan/url` → checks a URL
- `POST /scan/image` → checks an uploaded image
- `POST /update/feedback` → stores user feedback for federated learning

the backend:
1. Checks if the respective model exists under `backend/model/`.
2. If missing, downloads it automatically from Google Drive.
3. Loads it into memory:
   - URL model → via `joblib`
   - Image model → via `tflite_runtime`

---

## 📂 FINAL EXPECTED STRUCTURE

