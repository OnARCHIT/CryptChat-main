import React, { useEffect, useState } from 'react'

export default function PhishRadar(){
  const [points, setPoints] = useState([])

  useEffect(()=>{
    const mock = []
    for(let i=0;i<30;i++){
      mock.push({lat: 20 + Math.random()*40, lng: -140 + Math.random()*280, intensity: Math.random()})
    }
    setPoints(mock)
  },[])

  return (
    <div className="p-4 rounded-xl bg-slate-800/30">
      <div className="text-sm text-gray-300 mb-2">PhishRadar (mock data) — demo heatmap. Swap to real map (Leaflet/Mapbox) in production.</div>
      <div className="h-56 bg-gradient-to-br from-slate-900 to-slate-800 rounded relative overflow-hidden">
        {points.map((p,i)=> (
          <div key={i} title={`intensity:${p.intensity.toFixed(2)}`} style={{
            position:'absolute',
            left: (i * 7) % 100 + '%',
            top: (i * 13) % 100 + '%',
            transform: 'translate(-50%,-50%)'
          }} className="w-3 h-3 rounded-full" >
            <div style={{width: '12px', height: '12px', background: `rgba(255,80,80,${0.4 + p.intensity*0.6})`, borderRadius: '9999px'}}></div>
          </div>
        ))}
      </div>
    </div>
  )
}
