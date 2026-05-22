import React from 'react';
import './ComponentStyles.css';

/**
 * VideoFeed component displays the live video frame.
 * Props:
 *   - frame: base64 image string or null
 *   - status: connection status string
 *   - mode: operation mode string
 */
export default function VideoFeed({ frame, status, mode }) {
  const placeholder = 'data:image/svg+xml;base64,' + btoa(`
    <svg width='640' height='480' xmlns='http://www.w3.org/2000/svg'>
      <rect width='640' height='480' fill='hsl(210,10%,20%)'/>
      <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='white' font-size='24'>No Video Feed</text>
    </svg>`);
  const src = frame ? `data:image/jpeg;base64,${frame}` : placeholder;
  return (
    <div className='video-feed glass'>
      <img src={src} alt='Video Feed' className='video-img' />
      <div className='overlay'>
        <span className='status'>{status}</span>
        <span className='mode'>{mode}</span>
      </div>
    </div>
  );
}
