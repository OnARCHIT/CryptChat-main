import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Components
import ChatBox from "./components/ChatBox.jsx";
import FileInterceptor from "./components/FileInterceptor.jsx";
import HeadlineTicker from "./components/HeadlineTicker.jsx";
import LinkInterceptor from "./components/LinkInterceptor.jsx";
import MediaPanel from "./components/MediaPanel.jsx";
import NewsFeed from "./components/NewsFeed.jsx";
import PhishingChallenges from "./components/PhishingChallenge.jsx";
import PhishingRadar from "./components/PhishRadar.jsx";
import ScanPanel from "./components/ScanPanel.jsx";

import { startClipboardMonitor } from "./utils/clipboardMonitor.js";

gsap.registerPlugin(ScrollTrigger);

export default function App() {
  const [url, setUrl] = useState("");
  const [urlResult, setUrlResult] = useState(null);
  const [image, setImage] = useState(null);
  const [imageResult, setImageResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState("dark");

  const scrollRef = useRef(null);
  const backend = "https://cryptchat2.onrender.com";

  // === Theme Toggle ===
  const toggleTheme = () => setTheme(theme === "dark" ? "light" : "dark");

  // === Scroll animations ===
  useEffect(() => {
    const sections = scrollRef.current?.querySelectorAll(".section");
    sections?.forEach((sec) => {
      gsap.from(sec, {
        opacity: 0,
        y: 50,
        duration: 1,
        scrollTrigger: {
          trigger: sec,
          start: "top 85%",
          toggleActions: "play none none none",
        },
      });
    });
  }, []);

  // === Clipboard Monitoring ===
  useEffect(() => {
    startClipboardMonitor((text) => {
      console.log("Clipboard content detected:", text);
    });
  }, []);

  // === URL Scan ===
  const handleUrlScan = async () => {
    if (!url) return alert("Please enter a URL!");
    try {
      setLoading(true);
      const res = await axios.post(`${backend}/scan/url`, { url });
      setUrlResult(res.data);
    } catch {
      alert("Error scanning URL!");
    } finally {
      setLoading(false);
    }
  };

  // === Image Scan ===
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
    } catch {
      alert("Error scanning image!");
    } finally {
      setLoading(false);
    }
  };

  // === THEME COLORS ===
  const isDark = theme === "dark";
  const bgGradient = isDark
    ? "from-gray-950 via-gray-900 to-black"
    : "from-blue-50 via-white to-gray-100";
  const textColor = isDark ? "text-white" : "text-gray-900";

  return (
    <div
      ref={scrollRef}
      className={`relative min-h-screen w-full overflow-x-hidden transition-colors duration-500 bg-gradient-to-b ${bgGradient} ${textColor}`}
    >
      {/* Background Glow */}
      {isDark && (
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(56,189,248,0.15),transparent_60%)] pointer-events-none" />
      )}

      {/* Header */}
      <header className="flex justify-between items-center p-6 sticky top-0 z-50 backdrop-blur-xl bg-black/30 border-b border-gray-800">
        <h1 className="text-2xl font-extrabold tracking-tight">
          🔐 CryptChat
        </h1>
        <button
          onClick={toggleTheme}
          className={`px-4 py-2 rounded-full font-semibold transition-all ${
            isDark
              ? "bg-blue-600 hover:bg-blue-700 text-white"
              : "bg-yellow-400 hover:bg-yellow-500 text-gray-900"
          }`}
        >
          {isDark ? "☀️ Daylight Mode" : "🌙 Night Mode"}
        </button>
      </header>

      {/* Hero */}
      <section className="section text-center py-20 space-y-6">
        <motion.h1
          className="text-6xl font-extrabold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-transparent drop-shadow-lg"
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
        >
          AI-Driven Phishing Defense Agent
        </motion.h1>
        <motion.p
          className={`max-w-2xl mx-auto text-lg ${
            isDark ? "text-gray-300" : "text-gray-700"
          }`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, transition: { delay: 0.5 } }}
        >
          Real-time interception, adaptive threat learning, and explainable AI —
          integrated into your daily communication.
        </motion.p>
      </section>

      {/* URL Scanner */}
      <section className="section flex justify-center py-12">
        <div
          className={`p-6 rounded-2xl backdrop-blur-lg border shadow-lg w-full max-w-xl transition-all ${
            isDark
              ? "bg-gray-900/70 border-gray-800"
              : "bg-white/70 border-gray-200"
          }`}
        >
          <h2 className="text-2xl font-semibold mb-3">🔗 URL Scanner</h2>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL..."
            className={`w-full p-3 rounded-lg mb-3 outline-none border transition ${
              isDark
                ? "bg-gray-800 text-white border-gray-700 focus:border-blue-500"
                : "bg-white text-gray-900 border-gray-300 focus:border-blue-500"
            }`}
          />
          <button
            onClick={handleUrlScan}
            disabled={loading}
            className={`w-full py-3 rounded-lg font-semibold transition-all ${
              isDark
                ? "bg-blue-600 hover:bg-blue-700"
                : "bg-blue-500 hover:bg-blue-600 text-white"
            }`}
          >
            {loading ? "Scanning..." : "Scan URL"}
          </button>

          {urlResult && (
            <p className="mt-3 text-center text-lg">
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
      </section>

      {/* Image Scanner */}
      <section className="section flex justify-center py-12">
        <div
          className={`p-6 rounded-2xl backdrop-blur-lg border shadow-lg w-full max-w-xl transition-all ${
            isDark
              ? "bg-gray-900/70 border-gray-800"
              : "bg-white/70 border-gray-200"
          }`}
        >
          <h2 className="text-2xl font-semibold mb-3">🖼️ Image Scanner</h2>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setImage(e.target.files[0])}
            className="w-full mb-3 text-gray-400"
          />
          <button
            onClick={handleImageScan}
            disabled={loading}
            className={`w-full py-3 rounded-lg font-semibold transition-all ${
              isDark
                ? "bg-purple-600 hover:bg-purple-700"
                : "bg-purple-500 hover:bg-purple-600 text-white"
            }`}
          >
            {loading ? "Scanning..." : "Scan Image"}
          </button>

          {imageResult && (
            <p className="mt-3 text-center text-lg">
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
      </section>

      {/* AI Modules */}
      <section className="section w-full max-w-6xl mx-auto space-y-16 py-20 px-6">
        <HeadlineTicker />
        <MediaPanel />
        <NewsFeed />
        <PhishingChallenges />
        <PhishingRadar />
        <ScanPanel />
        <ChatBox />
        <LinkInterceptor />
        <FileInterceptor />
      </section>

      {/* Footer */}
      <footer
        className={`py-8 text-center border-t transition ${
          isDark ? "border-gray-800 text-gray-500" : "border-gray-200 text-gray-600"
        }`}
      >
        © {new Date().getFullYear()} CryptChat | AI Phishing Defense Agent
      </footer>
    </div>
  );
}
