import React, { useEffect, useState } from 'react'
import gsap from 'gsap'

export default function NewsFeed() {
  const [articles, setArticles] = useState([])

  useEffect(() => {
    // fetch via your server proxy
    fetch('/api/news', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ q: 'phishing OR deepfake OR "phishing attack"' }),
    })
      .then(r => r.json())
      .then(json => {
        const items = (json.articles || []).slice(0, 6)
        setArticles(items)
        gsap.from('.news-card', {
          opacity: 0,
          y: 20,
          stagger: 0.12,
          duration: 0.6,
          ease: 'power2.out',
        })
      })
      .catch(() => {
        /* handle errors */
      })
  }, [])

  return (
    <aside className="p-4 rounded-xl bg-slate-800/40 backdrop-blur-md relative z-10">
      <h4 className="font-semibold mb-3 text-gray-100">Latest Phishing & Threat News</h4>
      <div className="space-y-3">
        {articles.length === 0 && (
          <div className="text-sm text-gray-400">Loading...</div>
        )}
        {articles.map((a, i) => (
          <a
            key={i}
            className="news-card block p-3 bg-black/30 rounded hover:scale-[1.01] transition-transform"
            href={a.url}
            target="_blank"
            rel="noreferrer"
          >
            <div className="text-sm font-medium text-gray-100">{a.title}</div>
            <div className="text-xs text-gray-300 mt-1 line-clamp-2">{a.description}</div>
            <div className="text-xs text-gray-500 mt-1">{new Date(a.publishedAt).toLocaleString()}</div>
          </a>
        ))}
      </div>
    </aside>
  )
}
