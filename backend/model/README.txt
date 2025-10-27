📘 MODEL DIRECTORY

This folder contains placeholders for the AI models used by the backend.

⚠️ The actual trained models are NOT stored here to keep the repository under 25MB
and ensure smooth deployment on Render and GitHub.

✅ When the backend starts, it automatically downloads the required models
from Google Drive if they are missing.

------------------------------------------------------------
MODEL DETAILS
------------------------------------------------------------

1️⃣ URL MODEL
   - File: model_compressed.joblib
   - Google Drive Link:
     https://drive.google.com/file/d/1SQ9edzHisBtS7KutvRI-14o4vxI3Ref3/view?usp=drive_link
   - Purpose: Detects whether a given URL is phishing or safe.

2️⃣ IMAGE MODEL
   - File: image_model_int8.tflite
   - Google Drive Link:
     https://drive.google.com/file/d/1kuQVSpu_Hx853SHhL4cMtw28gC83-nYl/view?usp=drive_link
   - Purpose: Identifies phishing content in webpage or email screenshots.

------------------------------------------------------------
🧠 HOW IT WORKS
------------------------------------------------------------

- When you send a `/scan/url` or `/scan/image` request, the backend:
  1. Checks if the model file exists locally under `backend/model/`.
  2. If missing, it automatically downloads the model from Google Drive.
  3. Loads it into memory (URL: via joblib, Image: via tflite runtime).

------------------------------------------------------------
📂 FINAL EXPECTED STRUCTURE
------------------------------------------------------------

backend/
 ├── app.py
 └── model/
     ├── __init__.py
     ├── README.txt
     ├── model_compressed.joblib        (auto-downloaded at runtime)
     └── image_model_int8.tflite        (auto-downloaded at runtime)

------------------------------------------------------------
👨‍💻 AUTHOR NOTE
------------------------------------------------------------
You can modify the Google Drive file IDs in app.py if you retrain or replace the models.
Ensure that the new links are *public (anyone with link can view)* for Render to fetch them.

