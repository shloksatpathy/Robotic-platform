import React from 'react';
import RoverScene from './RoverScene';
import './LandingPage.css';

/**
 * LandingPage — Immersive 3D landing page with a rotating rover.
 * Displays project title, status, and live stats on glassmorphism overlays.
 * Props:
 *   - stats: telemetry stats object { fps, latency, objectCount, model, mode, status }
 */
export default function LandingPage({ stats }) {
  const statusKey = (stats?.status || 'Disconnected').toLowerCase().replace('...', '');

  return (
    <div className="landing-page">
      {/* Gradient background */}
      <div className="landing-bg-gradient" />

      {/* 3D Rover Scene */}
      <div className="landing-scene">
        <RoverScene />
      </div>

      {/* Scanline overlay for CRT effect */}
      <div className="landing-scanlines" />

      {/* Content overlay */}
      <div className="landing-overlay">
        {/* Top: Title & Status */}
        <div className="landing-top">
          <div className="landing-title-block">
            <h1 className="landing-title">Kristellar</h1>
            <p className="landing-subtitle">Autonomous Robotics Platform</p>
          </div>
          <div className="landing-status">
            <div className={`landing-status-dot ${statusKey}`} />
            <span className="landing-status-text">
              {(stats?.status || 'Offline').toUpperCase()}
            </span>
          </div>
        </div>

        {/* Bottom: Stat cards */}
        <div className="landing-bottom">
          <div className="landing-stat-card">
            <p className="landing-stat-label">FPS</p>
            <p className="landing-stat-value fps">{stats?.fps || 0}</p>
          </div>
          <div className="landing-stat-card">
            <p className="landing-stat-label">Latency</p>
            <p className="landing-stat-value latency">{stats?.latency || 0} ms</p>
          </div>
          <div className="landing-stat-card">
            <p className="landing-stat-label">Objects</p>
            <p className="landing-stat-value objects">{stats?.objectCount || 0}</p>
          </div>
          <div className="landing-stat-card">
            <p className="landing-stat-label">Model</p>
            <p className="landing-stat-value model">{stats?.model || 'N/A'}</p>
          </div>
        </div>
      </div>

      {/* Interaction hint */}
      <div className="landing-center-hint">
        <span className="landing-hint-text">Drag to explore</span>
        <div className="landing-hint-arrow" />
      </div>
    </div>
  );
}
