import React, { useEffect, useImperativeHandle, forwardRef, useState } from 'react'

const ChatBox = forwardRef(({ refProp }, ref) => {
  const [messages, setMessages] = useState([
    { from: 'bot', text: 'Hi! Ask me about links or report suspicious items.' }
  ])
  const [input, setInput] = useState('')
  const [badges, setBadges] = useState([])

  useImperativeHandle(ref, () => ({}))

  useEffect(() => {
    const b = JSON.parse(localStorage.getItem('cryptchat_badges') || '[]')
    setBadges(b)
  }, [])

  const send = () => {
    if (!input.trim()) return
    const userMsg = { from: 'user', text: input, ts: Date.now() }
    setMessages(m => [...m, userMsg])
    setInput('')
    setTimeout(() => {
      const reply = {
        from: 'bot',
        text: 'Thanks — I logged that. You can mark suspicious items after a scan.'
      }
      setMessages(m => [...m, reply])
    }, 700)
  }

  return (
    <aside
      ref={refProp}
      className="fixed bottom-6 right-6 w-80 max-w-full h-96 bg-gray-900 bg-opacity-90 rounded-xl p-3 text-white shadow-xl backdrop-blur-lg flex flex-col z-50"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-bold">CryptChat Assistant</h4>
        <div className="text-xs text-gray-400">Local demo</div>
      </div>

      {/* Badges */}
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        <div className="text-xs text-gray-300">Badges:</div>
        <div className="flex gap-1 flex-wrap max-w-[calc(100%-40px)] overflow-x-auto">
          {badges.length === 0 ? (
            <div className="text-xs text-gray-500">—</div>
          ) : (
            badges.map((b, i) => (
              <div
                key={i}
                className="px-2 py-1 bg-yellow-500 text-black rounded text-xs whitespace-nowrap"
              >
                {b.name}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-grow bg-gray-800 rounded p-2 mb-3 overflow-auto text-sm scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
        {messages.map((m, i) => (
          <div
            key={i}
            className={
              m.from === 'bot' ? 'mb-2 text-gray-200' : 'mb-2 text-cyanCustom'
            }
          >
            <strong>{m.from}:</strong> {m.text}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          placeholder="Ask about phishing..."
          className="flex-grow px-2 py-1 rounded bg-gray-700 bg-opacity-60 placeholder-gray-400 text-white focus:outline-none border border-gray-600"
        />
        <button
          onClick={send}
          className="px-3 py-1 rounded bg-cyanCustom text-black font-semibold"
        >
          Send
        </button>
      </div>
    </aside>
  )
})

export default ChatBox
