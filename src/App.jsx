import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Import your custom components
import ChatBox from "./ChatBox.jsx";
import FileInterceptor from ".components/FileInterceptor.jsx";
import HeadlineTicker from ".components/HeadlineTicker.jsx";
import LinkInterceptor from ".components/LinkInterceptor.jsx";
import MediaPanel from ".components/MediaPanel.jsx";
import NewsFeed from ".components/NewsFeed.jsx";
import PhishingChallenges from ".components/PhishingChallenges.jsx";
import PhishingRadar from ".components/PhishingRadar.jsx";
import ScanPanel from ".components/ScanPanel.jsx";

gsap.registerPlugin(ScrollTrigger);

export default function App() {
  const [url, setUrl] = useState("");
  const [urlResult, setUrlResult] = useState(null);
  const [image, setImage] = useState(null);
  const [imageResult, setImageResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const backend = "https://cryptchat2.onrender.com/";

  const scrollRef = useRef(null);

  // ScrollTrigger animation for sections
  useEffect(() => {
    const sections = scrollRef.current?.querySelectorAll(".section");
    if (sections) {
      sections.forEach((sec) => {
        gsap.from(sec, {
          opacity: 0,
          y: 50,
          duration: 1,
          scrollTrigger: {
            trigger: sec,
            start: "top 80%",
            toggleActions: "play none none none",
          },
        });
      });
    }
  }, []);

  // ===== URL Scan =====
  const handleUrlScan = async () => {
    if (!url) return alert("Please enter a URL!");
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

  // ===== Image Scan =====
  const handleImageScan = async () => {
    if (!image) return alert("Please select an image!");
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

  return (
    <div
      ref={scrollRef}
      className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-start p-6 space-y-16"
    >
      <motion.h1
        className="text-5xl font-bold text-center mt-8"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        🕵️‍♂️ CryptChat — AI Phishing Protection
      </motion.h1>

      <motion.p
        className="max-w-3xl text-center text-gray-300"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1, transition: { delay: 0.5 } }}
      >
        Proactive in-app interception, explainable alerts, and continuous adaptive AI learning — all integrated seamlessly into your daily chat and browser workflow.
      </motion.p>

      {/* === URL Scanner Section === */}
      <div className="section bg-gray-900 p-6 rounded-2xl shadow-lg w-full max-w-xl">
        <h2 className="text-2xl font-semibold mb-3">🔗 URL Scanner</h2>
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
            (Score: {urlResult.score?.toFixed(3) || "N/A"})
          </p>
        )}
      </div>

      {/* === Image Scanner Section === */}
      <div className="section bg-gray-900 p-6 rounded-2xl shadow-lg w-full max-w-xl">
        <h2 className="text-2xl font-semibold mb-3">🖼️ Image Scanner</h2>
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
            (Score: {imageResult.score?.toFixed(3) || "N/A"})
          </p>
        )}
      </div>

        {/* === Game & Interactive Modules === */}
      <div className="section w-full max-w-4xl space-y-12">
        <HeadlineTicker />
        <MediaPanel />
        <NewsFeed />
        <PhishingChallenges />
        <PhishingRadar />
        <ScanPanel />
        <ChatBox />
        <LinkInterceptor />
        <FileInterceptor />
      </div>
    </div>
  );
}
