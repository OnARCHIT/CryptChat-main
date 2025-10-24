from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import os
import uvicorn

# ------------------- FastAPI App -------------------
app = FastAPI(title="CryptChat Security API")

# ------------------- CORS Setup -------------------
origins = ["*"]  # You can restrict to your frontend domain if needed

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------- Request Models -------------------
class URLScanRequest(BaseModel):
    url: str

class EmailScanRequest(BaseModel):
    data: str  # email content

# ------------------- Helper Function (Dummy) -------------------
def dummy_scan_result() -> Dict:
    """
    Returns a dummy scan result.
    Replace this logic with real ML or rule-based scanning.
    """
    return {
        "score": 85,
        "details": [
            {"reason": "Suspicious domain pattern", "confidence": 0.9},
            {"reason": "Blacklisted IP", "confidence": 0.75},
        ],
    }

# ------------------- URL Scan -------------------
@app.post("/scan/url")
async def scan_url(request: URLScanRequest):
    result = dummy_scan_result()
    return result

# ------------------- Email Scan -------------------
@app.post("/scan/email")
async def scan_email(request: EmailScanRequest):
    result = dummy_scan_result()
    return result

# ------------------- Image Scan -------------------
@app.post("/scan/image")
async def scan_image(file: UploadFile = File(...)):
    contents = await file.read()  # You can process the uploaded image
    result = dummy_scan_result()
    return result

# ------------------- Voice Scan -------------------
@app.post("/scan/voice")
async def scan_voice(file: UploadFile = File(...)):
    contents = await file.read()  # You can process the uploaded audio
    result = dummy_scan_result()
    return result

# ------------------- Run Server (Render / Local) -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
