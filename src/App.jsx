import React, { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

export default function App() {
  const [url, setUrl] = useState("");
  const [urlResult, setUrlResult] = useState(null);
  const [image, setImage] = useState(null);
  const [imageResult, setImageResult] = useState(null);
  const [file, setFile] = useState(null);
  const [fileResult, setFileResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Automatically use Render URL if deployed
  const backend =
    window.location.hostname === "localhost"
      ? "http://127.0.0.1:5000"
      : "https://your-backend-service.onrender.com"; // ⬅️ Replace with Render URL after deployment

  // ===== URL SCAN =====
  const handleUrlScan = async () => {
    if (!url) return alert("Please enter a URL first!");
    try {
      setLoading(true);
      const res = await axios.post(`${backend}/scan/url`, { url });
      setUrlResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error scanning URL!");
    } finally {
      setLoading(false);
    }
  };

  // ===== IMAGE SCAN =====
  const handleImageScan = async () => {
    if (!image) return alert("Please select an image first!");
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("image", image);
      const res = await axios.post(`${backend}/scan/image`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setImageResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error scanning image!");
    } finally {
      setLoading(false);
    }
  };

  // ===== FILE SCAN =====
  const handleFileScan = async () => {
    if (!file) return alert("Please select a file first!");
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("file", file);
      const res = await axios.post(`${backend}/scan/file`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setFileResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error scanning file!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center p-6 space-y-6">
      <motion.h1
        className="text-4xl font-bold text-center mb-8"
        initial={{ y: -40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        🕵️‍♂️ AI Phishing Detector
      </motion.h1>

      {/* === URL SCANNER === */}
      <motion.div
        className="bg-gray-900 p-6 rounded-2xl shadow-lg w-full max-w-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-xl font-semibold mb-3">🔗 URL Scanner</h2>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter URL..."
          className="w-full p-2 rounded bg-gray-800 text-white mb-3"
        />
        <button
          onClick={handleUrlScan}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded font-semibold"
        >
          {loading ? "Scanning..." : "Scan URL"}
        </button>
        {urlResult && (
          <p className="mt-3 text-center">
            Result:{" "}
            <span
              className={`font-bold ${
                urlResult.phishing ? "text-red-400" : "text-green-400"
              }`}
            >
              {urlResult.phishing ? "Phishing Detected" : "Safe"}
            </span>{" "}
            (Score: {urlResult.score.toFixed(3)})
          </p>
        )}
      </motion.div>

      {/* === IMAGE SCANNER === */}
      <motion.div
        className="bg-gray-900 p-6 rounded-2xl shadow-lg w-full max-w-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-xl font-semibold mb-3">🖼️ Image Scanner</h2>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImage(e.target.files[0])}
          className="w-full mb-3"
        />
        <button
          onClick={handleImageScan}
          disabled={loading}
          className="w-full bg-purple-600 hover:bg-purple-700 py-2 rounded font-semibold"
        >
          {loading ? "Scanning..." : "Scan Image"}
        </button>
        {imageResult && (
          <p className="mt-3 text-center">
            Result:{" "}
            <span
              className={`font-bold ${
                imageResult.phishing ? "text-red-400" : "text-green-400"
              }`}
            >
              {imageResult.phishing ? "Phishing Detected" : "Safe"}
            </span>{" "}
            (Score: {imageResult.score.toFixed(3)})
          </p>
        )}
      </motion.div>

      {/* === FILE SCANNER === */}
      <motion.div
        className="bg-gray-900 p-6 rounded-2xl shadow-lg w-full max-w-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h2 className="text-xl font-semibold mb-3">📁 File Scanner</h2>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
          className="w-full mb-3"
        />
        <button
          onClick={handleFileScan}
          disabled={loading}
          className="w-full bg-green-600 hover:bg-green-700 py-2 rounded font-semibold"
        >
          {loading ? "Scanning..." : "Scan File"}
        </button>
        {fileResult && (
          <p className="mt-3 text-center">
            Result:{" "}
            <span
              className={`font-bold ${
                fileResult.phishing ? "text-red-400" : "text-green-400"
              }`}
            >
              {fileResult.phishing ? "Phishing Detected" : "Safe"}
            </span>{" "}
            (Score: {fileResult.score.toFixed(3)})
          </p>
        )}
      </motion.div>
    </div>
  );
}
