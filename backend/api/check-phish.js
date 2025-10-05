// /api/check-phish.js
import fetch from 'node-fetch';

export default async function handler(req, res) {
  const { url } = req.query;

  if (!url) {
    return res.status(400).json({ error: 'Missing URL' });
  }

  try {
    const googleScriptUrl =
      'https://script.google.com/macros/s/AKfycbzf4hJEElGbpCjGq6KyMkNbFiH6ds1yufgZ4epni839YtBiMEgfWNN5lspS0pccRRhS/exec';
    const response = await fetch(`${googleScriptUrl}?url=${encodeURIComponent(url)}`);

    const text = await response.text();
    let json;

    try {
      json = JSON.parse(text);
    } catch {
      // Always fallback with safe JSON
      json = {
        phishing: text.toLowerCase().includes('malware') || text.toLowerCase().includes('phishing'),
        explanation: 'Parsed HTML response, heuristic applied',
        preview: text.slice(0, 200) // just the first 200 chars
      };
    }

    res.status(200).json(json);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
