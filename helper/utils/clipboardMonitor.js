import { checkUrl, classifyZone, showAlert } from '../helper/helper.js';

export function monitorClipboard() {
  let lastText = "";
  setInterval(async () => {
    const text = await navigator.clipboard.readText().catch(() => "");
    if (text && text !== lastText && text.startsWith("http")) {
      lastText = text;
      const res = await checkUrl(text);
      const zone = classifyZone(res.score, res.phishing);
      showAlert(zone, "Clipboard URL");
    }
  }, 2000); // check every 2 seconds
}
