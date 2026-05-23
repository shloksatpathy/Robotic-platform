import React from 'react';
import './ComponentStyles.css';

/**
 * VideoFeed component displays the live video frame.
 * Props:
 *   - frame: base64 image string or null
 *   - status: connection status string
 *   - mode: operation mode string
 *   - theme: 'dark' | 'light'
 */
export default function VideoFeed({ frame, status, mode, theme }) {
  const darkPlaceholder = 'data:image/svg+xml;base64,' + btoa(`
    <svg width='640' height='480' viewBox='0 0 640 480' xmlns='http://www.w3.org/2000/svg'>
      <defs>
        <radialGradient id='bgGrad' cx='50%' cy='50%' r='75%'>
          <stop offset='0%' stop-color='#0a0e1e' />
          <stop offset='100%' stop-color='#020409' />
        </radialGradient>
        <pattern id='grid' width='40' height='40' patternUnits='userSpaceOnUse'>
          <path d='M 40 0 L 0 0 0 40' fill='none' stroke='rgba(59,130,246,0.06)' stroke-width='1'/>
        </pattern>
      </defs>
      <rect width='640' height='480' fill='url(#bgGrad)'/>
      <rect width='640' height='480' fill='url(#grid)'/>
      <circle cx='320' cy='240' r='100' fill='none' stroke='rgba(59,130,246,0.1)' stroke-width='1.5' stroke-dasharray='4,6'/>
      <circle cx='320' cy='240' r='140' fill='none' stroke='rgba(59,130,246,0.05)' stroke-width='1'/>
      <path d='M 280 240 L 360 240 M 320 200 L 320 280' stroke='rgba(59,130,246,0.25)' stroke-width='1.5'/>
      <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='#3b82f6' font-family='monospace' font-size='16' font-weight='bold' letter-spacing='3'>[ VIDEO SYNC OFFLINE ]</text>
    </svg>`);

  const lightPlaceholder = 'data:image/svg+xml;base64,' + btoa(`
    <svg width='640' height='480' viewBox='0 0 640 480' xmlns='http://www.w3.org/2000/svg'>
      <defs>
        <radialGradient id='bgGradL' cx='50%' cy='50%' r='75%'>
          <stop offset='0%' stop-color='#f8fafc' />
          <stop offset='100%' stop-color='#e2e8f0' />
        </radialGradient>
        <pattern id='gridL' width='40' height='40' patternUnits='userSpaceOnUse'>
          <path d='M 40 0 L 0 0 0 40' fill='none' stroke='rgba(37,99,235,0.08)' stroke-width='1'/>
        </pattern>
      </defs>
      <rect width='640' height='480' fill='url(#bgGradL)'/>
      <rect width='640' height='480' fill='url(#gridL)'/>
      <circle cx='320' cy='240' r='100' fill='none' stroke='rgba(37,99,235,0.15)' stroke-width='1.5' stroke-dasharray='4,6'/>
      <circle cx='320' cy='240' r='140' fill='none' stroke='rgba(37,99,235,0.08)' stroke-width='1'/>
      <path d='M 280 240 L 360 240 M 320 200 L 320 280' stroke='rgba(37,99,235,0.3)' stroke-width='1.5'/>
      <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='#2563eb' font-family='monospace' font-size='16' font-weight='bold' letter-spacing='3'>[ VIDEO SYNC OFFLINE ]</text>
    </svg>`);

  const placeholder = theme === 'light' ? lightPlaceholder : darkPlaceholder;
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
