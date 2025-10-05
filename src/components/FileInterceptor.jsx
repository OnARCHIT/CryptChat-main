// FileInterceptor.jsx
import React, { useState } from "react";
import { checkFileWithApi } from "../utils/checkApi";
import { predictImageLocal } from "../utils/tfImagePredict"; // optional local TFJS
// If you don't have local model, skip predictImageLocal

export default function FileInterceptor({ apiEndpoint, onSafeFile }) {
  const [modal, setModal] = useState({ open: false, loading: false, result: null, fileName: "" });

  async function handleFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setModal({ open: true, loading: true, result: null, fileName: file.name });

    // Fast client-side image check (optional)
    if (file.type.startsWith("image/")) {
      try {
        const img = new Image();
        img.src = URL.createObjectURL(file);
        img.onload = async () => {
          // optional: local prediction
          let localScore = null;
          try {
            localScore = await predictImageLocal(img, "/models/image_phish/model.json");
          } catch (err) { /* ignore if no model */ }

          // always still send to server for more robust checks
          const serverRes = await checkFileWithApi(apiEndpoint, file);
          const final = mergeResults(serverRes, localScore);
          setModal({ open: true, loading: false, result: final, fileName: file.name });
        };
      } catch (err) {
        const serverRes = await checkFileWithApi(apiEndpoint, file);
        setModal({ open: true, loading: false, result: serverRes, fileName: file.name });
      }
    } else {
      // Non-image: send to server for deep analysis
      const res = await checkFileWithApi(apiEndpoint, file);
      setModal({ open: true, loading: false, result: res, fileName: file.name });
    }
  }

  function mergeResults(serverRes, localScore) {
    if (!serverRes || serverRes.error) {
      // if server failed, rely on local
      return localScore ? { phishing: localScore > 0.5, scores: { image_score: localScore }, explanation: "Local model only", details: {} } : serverRes;
    }
    // combine scores: simple ensemble (you can tune weights)
    let image_score = serverRes.scores?.image_score ?? null;
    if (localScore != null) {
      image_score = image_score != null ? (image_score + localScore) / 2 : localScore;
    }
    const phishing = serverRes.phishing || (image_score != null && image_score > 0.6);
    return { ...serverRes, scores: {...(serverRes.scores||{}), image_score }, phishing };
  }

  function acceptFile() {
    onSafeFile && onSafeFile(modal.result);
    setModal({ open: false, loading: false, result: null, fileName: "" });
  }
  function rejectFile() {
    setModal({ open: false, loading: false, result: null, fileName: "" });
  }

  return (
    <>
      <input type="file" onChange={handleFile} />
      {modal.open && (
        <div className="fixed inset-0 z-60 flex items-center justify-center">
          <div className="absolute inset-0 bg-black/60" onClick={rejectFile}></div>
          <div className="relative w-full max-w-lg mx-4 bg-slate-900 rounded-xl p-6">
            <div className="text-sm text-gray-300">File: {modal.fileName}</div>
            <div className="mt-4">
              {modal.loading ? (
                <div className="flex items-center gap-3"><div className="w-8 h-8 border-4 border-green-400 border-t-transparent rounded-full animate-spin"></div><div className="text-sm">Scanning file…</div></div>
              ) : modal.result ? (
                <div>
                  <div className={`font-semibold ${modal.result.phishing ? 'text-red-400' : 'text-green-300'}`}>{modal.result.phishing ? '⚠️ Potential phishing' : '✅ Looks safe'}</div>
                  <div className="text-xs text-gray-400 mt-2">{modal.result.explanation}</div>
                </div>
              ) : <div className="text-sm text-gray-300">No result</div>}
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button onClick={rejectFile} className="px-3 py-1 rounded bg-gray-700 text-gray-200">Cancel</button>
              <button onClick={acceptFile} className="px-3 py-1 rounded bg-cyan-500 text-black font-semibold">Use Anyway</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
