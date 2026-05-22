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
    <svg width='640' height='480' viewBox='0 0 640 480' xmlns='http://www.w3.org/2000/svg'>
      <defs>
        <radialGradient id='bgGrad' cx='50%' cy='50%' r='75%'>
          <stop offset='0%' stop-color='#0a0e1e' />
          <stop offset='100%' stop-color='#020409' />
        </radialGradient>
        <pattern id='grid' width='40' height='40' patternUnits='userSpaceOnUse'>
          <path d='M 40 0 L 0 0 0 40' fill='none' stroke='rgba(0, 240, 255, 0.04)' stroke-width='1'/>
        </pattern>
      </defs>
      <rect width='640' height='480' fill='url(#bgGrad)'/>
      <rect width='640' height='480' fill='url(#grid)'/>
      <circle cx='320' cy='240' r='100' fill='none' stroke='rgba(0, 240, 255, 0.08)' stroke-width='1.5' stroke-dasharray='4,6'/>
      <circle cx='320' cy='240' r='140' fill='none' stroke='rgba(0, 240, 255, 0.04)' stroke-width='1'/>
      <path d='M 280 240 L 360 240 M 320 200 L 320 280' stroke='rgba(0, 240, 255, 0.2)' stroke-width='1.5'/>
      <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='#00f0ff' font-family='monospace' font-size='16' font-weight='bold' letter-spacing='3'>[ VIDEO SYNC OFFLINE ]</text>
    </svg>`);
    
  const src = frame ? `data:image/jpeg;base64,${frame}` : placeholder;
  
  return (
    <div className='video-feed glass'>
      <img src={src} alt='Video Feed' className='video-img' />
      <div className='overlay'>
        <span className='status-hud-pill'>{status.toUpperCase()}</span>
        <span className='mode-hud-pill'>{mode.toUpperCase()}</span>
      </div>
    </div>
  );
}
