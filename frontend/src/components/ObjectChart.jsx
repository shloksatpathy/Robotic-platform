import React from 'react';
import './ComponentStyles.css';

/**
 * ObjectChart displays a premium telemetry chart representation for tracking detections.
 * Props:
 *   - detections: array of detection objects
 */
export default function ObjectChart({ detections = [] }) {
  const safeDetections = detections || [];
  const total = safeDetections.length;
  const classes = safeDetections.reduce((acc, d) => {
    acc[d.class] = (acc[d.class] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="object-chart glass">
      <h2>TRACKING OVERVIEW</h2>
      <p className="total-indicator">TOTAL TARGETS IN FRAME: {total}</p>
      <ul className="chart-list">
        {total === 0 ? (
          <li className="chart-empty">NO ACTIVE TARGETS IN SECTOR</li>
        ) : (
          Object.entries(classes).map(([cls, count]) => (
            <li key={cls} className="chart-row">
              <div className="chart-info">
                <span className="chart-class">{cls.toUpperCase()}</span>
                <span className="chart-count">{count}</span>
              </div>
              <div className="bar-container">
                <div className="bar" style={{ width: `${(count / total) * 100}%` }} />
              </div>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
