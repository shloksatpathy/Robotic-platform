import React from 'react';

export default function SystemHealth() {
  return (
    <div className="panel system-health">
      <h2>System Health</h2>
      <ul>
        <li>CPU utilization</li>
        <li>RAM utilization</li>
        <li>GPU utilization</li>
        <li>Temperature</li>
        <li>Disk usage</li>
        <li>Network latency</li>
        <li>Battery voltage / percentage</li>
        <li>Current consumption</li>
      </ul>
    </div>
  );
}
