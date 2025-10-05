import React, { useEffect, useRef } from 'react'
import gsap from 'gsap'

export default function HeadlineTicker({ items = [] }) {
  const wrap = useRef()
  if (items.length === 0)
    items = [
      'AI deepfake scams rising',
      'OAuth phishing campaigns found',
      'DigiCert acquires Valimail for email auth'
    ]

  useEffect(() => {
    const el = wrap.current
    if (!el) return

    const anim = gsap.to(el, { xPercent: -50, duration: 18, repeat: -1, ease: 'none' })

    el.addEventListener('mouseenter', () => anim.pause())
    el.addEventListener('mouseleave', () => anim.resume())

    return () => anim.kill()
  }, [])

  return (
    <div className="overflow-hidden whitespace-nowrap py-2 px-3 rounded bg-gradient-to-r from-slate-900/50 to-slate-800/30 relative z-20">
      <div ref={wrap} className="inline-flex gap-6">
        {items.concat(items).map((it, i) => (
          <div key={i} className="text-sm text-gray-200 px-4">
            {it}
          </div>
        ))}
      </div>
    </div>
  )
}
