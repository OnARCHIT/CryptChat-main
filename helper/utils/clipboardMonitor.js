// src/utils/clipboardMonitor.js
import { sendClipboardData } from "../helper/helper.js";

export function startClipboardMonitor(callback) {
  // Poll clipboard every 2 seconds (example)
  setInterval(async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        callback(text);
        sendClipboardData(text);
      }
    } catch (err) {
      console.warn("Clipboard access denied or unavailable", err);
    }
  }, 2000);
}
