import React, { useState, useEffect } from 'react'

const sampleItems = [
  { id: 1, text: 'Your bank account will be closed. Click here to verify.', label: 'phish' },
  { id: 2, text: 'Update to the latest version of AppName from official site.', label: 'legit' },
  { id: 3, text: 'You won a gift card! Claim now.', label: 'phish' },
  { id: 4, text: 'Team meeting rescheduled to 3 PM today (calendar invite).', label: 'legit' }
]

export default function PhishingChallenge() {
  const [queue, setQueue] = useState([])
  const [score, setScore] = useState(0)
  const [index, setIndex] = useState(0)

  useEffect(() => {
    setQueue(sampleItems.sort(() => Math.random() - 0.5))
  }, [])

  const choose = (choice) => {
    const current = queue[index]
    const correct = current.label === choice
    setScore(s => s + (correct ? 10 : -5))
    setIndex(i => i + 1)
    if (index + 1 >= queue.length) {
      const final = score + (correct ? 10 : -5)
      alert('Challenge finished! Your score: ' + final)
      const badges = JSON.parse(localStorage.getItem('cryptchat_badges') || '[]')
      if (final > 20) {
        badges.push({ name: 'Phish Finder', ts: Date.now() })
        localStorage.setItem('cryptchat_badges', JSON.stringify(badges))
      }
      setIndex(0)
      setScore(0)
    }
  }

  if (queue.length === 0) return null
  const item = queue[index]

  return (
    <div className="p-4 rounded-xl bg-slate-800/40 backdrop-blur-md relative z-10">
      <div className="text-sm text-gray-200 mb-2">
        Identify whether the following post is Legit or Phishing:
      </div>
      <div className="p-4 bg-black/30 rounded mb-3 text-gray-100">{item.text}</div>
      <div className="flex gap-3">
        <button
          onClick={() => choose('phish')}
          className="px-3 py-2 rounded bg-red-600 text-white hover:bg-red-500 transition-colors"
        >
          Phish
        </button>
        <button
          onClick={() => choose('legit')}
          className="px-3 py-2 rounded bg-green-600 text-white hover:bg-green-500 transition-colors"
        >
          Legit
        </button>
      </div>
      <div className="mt-3 text-sm text-gray-200">Score: {score}</div>
    </div>
  )
}
