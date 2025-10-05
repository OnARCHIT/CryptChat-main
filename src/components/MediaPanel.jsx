import React, { useRef, useState } from 'react';
import { BsExclamationTriangleFill } from 'react-icons/bs';

export default function MediaPanel() {
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(true);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (videoRef.current.paused) {
      videoRef.current.play();
      setIsPlaying(true);
    } else {
      videoRef.current.pause();
      setIsPlaying(false);
    }
  };

  return (
    <div className="p-4 rounded-xl bg-slate-800/50 backdrop-blur-md relative z-10 shadow-lg">
      <div className="flex items-center space-x-2 mb-3">
        <BsExclamationTriangleFill className="text-yellow-400 text-xl animate-pulse" />
        <h4 className="font-semibold text-gray-100 text-lg">Recent Phishing Attack Highlight</h4>
      </div>

      <div className="relative rounded overflow-hidden shadow-sm bg-black/30 group">
        <video
          ref={videoRef}
          loop
          muted
          autoPlay
          className="w-full h-56 object-cover transition-transform duration-500 group-hover:scale-105"
        >
          <source src="/assets/phising-highlight.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-80 transition-opacity duration-300 flex items-center justify-center text-white text-center p-4">
          ⚠️ Always verify URLs and certificates before clicking links.
        </div>
        <button
          onClick={togglePlay}
          className="absolute bottom-2 right-2 bg-cyanCustom text-black px-3 py-1 rounded font-semibold text-sm"
        >
          {isPlaying ? 'Pause' : 'Play'}
        </button>
      </div>

      <div className="text-xs text-gray-400 mt-3">
        Tip: Hover the video for extra warning info and observe the attack highlights carefully.
      </div>
    </div>
  );
}
