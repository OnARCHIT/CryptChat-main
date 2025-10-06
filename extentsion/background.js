// Handles extension-wide messaging
chrome.runtime.onMessage.addListener(async (msg, sender, sendResponse) => {
  if (msg.type === "CHECK_PHISHING_URL") {
    const backend = "https://cryptchat2.onrender.com";
    try {
      const response = await fetch(`${backend}/scan/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: msg.url })
      });
      const data = await response.json();
      sendResponse({ success: true, data });
    } catch (err) {
      console.error("Backend error:", err);
      sendResponse({ success: false });
    }
    return true; // keep connection open for async response
  }

  if (msg.type === "CHECK_PHISHING_IMAGE") {
    const backend = "https://cryptchat2.onrender.com";
    try {
      const formData = new FormData();
      formData.append("image", msg.file);
      const response = await fetch(`${backend}/scan/image`, {
        method: "POST",
        body: formData
      });
      const data = await response.json();
      sendResponse({ success: true, data });
    } catch (err) {
      console.error("Backend error:", err);
      sendResponse({ success: false });
    }
    return true;
  }
});
