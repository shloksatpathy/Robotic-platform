import React from 'react';
import './ComponentStyles.css';

/**
 * ObjectChart displays a simple placeholder chart for detections.
 * Props:
 *   - detections: array of detection objects
 */
export default function ObjectChart({ detections }) {
  // For demonstration, we'll just show a count and a simple bar representation.
  const total = detections.length;
  const classes = detections.reduce((acc, d) => {
    acc[d.class] = (acc[d.class] || 0) + 1;
    return acc;
  }, {});
  return (
    <div className="object-chart glass">
      <h2>Detection Overview</h2>
      <p>Total objects: {total}</p>
      <ul>
        {Object.entries(classes).map(([cls, count]) => (
          <li key={cls}>
            {cls}: {count}
            <div className="bar" style={{ width: `${(count / total) * 100}%` }} />
          </li>
        ))}
      </ul>
    </div>
  );
}
