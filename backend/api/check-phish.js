import fetch from 'node-fetch';

export default async function handler(req, res) {
  const { url } = req.query;

  if (!url) {
    return res.status(400).json({ error: 'Missing URL parameter' });
  }

  try {
    const googleScriptUrl =
      'https://script.google.com/macros/s/AKfycbzf4hJEElGbpCjGq6KyMkNbFiH6ds1yufgZ4epni839YtBiMEgfWNN5lspS0pccRRhS/exec';

    const response = await fetch(`${googleScriptUrl}?url=${encodeURIComponent(url)}`);

    const text = await response.text();

    // Attempt to parse JSON, fallback to heuristic
    let json;
    try {
      json = JSON.parse(text);
    } catch (err) {
      json = {
        phishing:
          text.toLowerCase().includes('malware') ||
          text.toLowerCase().includes('phishing'),
        explanation: 'Fallback: parsed as text and applied heuristic',
        preview: text.slice(0, 200) // first 200 characters
      };
    }

    res.status(200).json(json);
  } catch (err) {
    console.error('Error in /api/check-phish:', err);
    res.status(500).json({ error: 'Internal Server Error', details: err.message });
  }
}
