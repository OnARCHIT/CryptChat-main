// components/ScanPanel.jsx
import React, { useState } from 'react';

export default function ScanPanel() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleScan(e) {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await fetch(`/api/check-phish?url=${encodeURIComponent(url)}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-4 rounded-xl bg-slate-900/40 backdrop-blur-md relative z-10">
      <h3 className="text-lg font-bold mb-3 text-white">🔍 URL Phishing Scanner</h3>

      <form onSubmit={handleScan} className="flex gap-2">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste a link to scan..."
          className="flex-1 p-2 rounded bg-slate-800 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold"
        >
          {loading ? 'Scanning...' : 'Scan'}
        </button>
      </form>

      {/* Results */}
      <div className="mt-4">
        {loading && <p className="text-yellow-400">⏳ Scanning in progress...</p>}
        {error && <p className="text-red-500">❌ Error: {error}</p>}
        {result && (
          <div className="p-3 rounded bg-slate-800 mt-2 text-sm text-white">
            <p>
              Result:{' '}
              {result.phishing ? (
                <span className="text-red-400 font-bold">⚠️ Phishing Detected</span>
              ) : (
                <span className="text-green-400 font-bold">✅ Safe</span>
              )}
            </p>
            {result.explanation && (
              <p className="text-gray-400 mt-1">ℹ️ {result.explanation}</p>
            )}
            {result.preview && (
              <details className="mt-2">
                <summary className="cursor-pointer text-blue-400">Show raw response</summary>
                <pre className="bg-black p-2 mt-1 rounded text-xs overflow-x-auto">
                  {result.preview}
                </pre>
              </details>
            )}
          </div>
        )}
      </div>

      {/* Quick Test Links */}
      <div className="mt-6">
        <h4 className="text-gray-300 text-sm mb-2">⚡ Quick Test Links:</h4>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setUrl('https://testsafebrowsing.appspot.com/s/phishing.html')}
            className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
          >
            Phishing Test
          </button>
          <button
            onClick={() => setUrl('https://testsafebrowsing.appspot.com/s/malware.html')}
            className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
          >
            Malware Test
          </button>
          <button
            onClick={() => setUrl('https://example.com')}
            className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-xs text-white"
          >
            Safe Link
          </button>
        </div>
      </div>
    </div>
  );
}
