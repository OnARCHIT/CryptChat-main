// src/helper/helper.js

// Backend URL
const BACKEND_URL = "https://cryptchat2.onrender.com";

// ===== URL Scanner =====
export async function checkUrl(url) {
  try {
    const res = await fetch(`${BACKEND_URL}/scan/url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    return await res.json();
  } catch (err) {
    console.error("checkUrl error:", err);
    return { score: 0, phishing: false };
  }
}

// ===== Image Scanner =====
export async function checkImage(file) {
  try {
    const formData = new FormData();
    formData.append("image", file);
    const res = await fetch(`${BACKEND_URL}/scan/image`, {
      method: "POST",
      body: formData,
    });
    return await res.json();
  } catch (err) {
    console.error("checkImage error:", err);
    return { score: 0, phishing: false };
  }
}

// ===== Zone Classification =====
export function classifyZone(score, phishing) {
  if (phishing) return "red";
  if (score > 0.3) return "yellow";
  return "green";
}

// ===== Alert System =====
export function showAlert(zone, type) {
  if (zone === "red") alert(`⚠️ ${type} Red Zone: Phishing detected!`);
  else if (zone === "yellow")
    alert(`⚠️ ${type} Yellow Zone: Possible phishing. Proceed with caution.`);
  else if (zone === "green") alert(`✅ ${type} Green Zone: Safe to open.`);
}
