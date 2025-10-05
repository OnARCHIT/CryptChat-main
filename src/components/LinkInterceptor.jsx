import React from 'react';

export default function LinkInterceptor({ children }) {
  const handleClick = async (e) => {
    const target = e.target.closest('a');
    if (!target) return;
    const href = target.href;
    if (!href.startsWith('http')) return;

    e.preventDefault(); // Stop default browser navigation

    try {
      const res = await fetch(`/api/check-phish?url=${encodeURIComponent(href)}`);
      const json = await res.json();

      if (json.phishing) {
        alert(`⚠️ Phishing detected!\n${json.explanation}`);
      } else {
        window.open(href, '_blank', 'noopener,noreferrer');
      }
    } catch (err) {
      alert('Error checking URL: ' + err.message);
    }
  };

  return (
    <div onClick={handleClick}>
      {children}
    </div>
  );
}
