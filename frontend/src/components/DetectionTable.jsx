import React from 'react';
import './ComponentStyles.css';

/**
 * DetectionTable displays a list of detection objects.
 * Props:
 *   - detections: array of {id, class, confidence}
 */
export default function DetectionTable({ detections }) {
  return (
    <div className="detection-table glass">
      <h2>Detections</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Class</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {detections.map((d) => (
            <tr key={d.id}>
              <td>{d.id}</td>
              <td>{d.class}</td>
              <td>{(d.confidence * 100).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
