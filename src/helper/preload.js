// Preload script for browser extension sandbox
import { monitorClipboard } from './utils/clipboardMonitor.js';

window.addEventListener("DOMContentLoaded", () => {
  // Start clipboard monitor
  monitorClipboard();
});
