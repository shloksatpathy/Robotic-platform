import React from 'react';
import './ComponentStyles.css';

/**
 * StatsPanel displays system statistics.
 * Props:
 *   - stats: object containing fps, latency, objectCount, mode, model, status
 */
export default function StatsPanel({ stats }) {
  const { fps, latency, objectCount, mode, model, status } = stats;
  return (
    <div className="stats-panel glass">
      <h2>System Stats</h2>
      <ul>
        <li><strong>FPS:</strong> {fps}</li>
        <li><strong>Latency:</strong> {latency} ms</li>
        <li><strong>Objects:</strong> {objectCount}</li>
        <li><strong>Mode:</strong> {mode}</li>
        <li><strong>Model:</strong> {model}</li>
        <li><strong>Status:</strong> {status}</li>
      </ul>
    </div>
  );
}
