import React from 'react';

export default function CameraGimbalControl() {
  return (
    <div className="panel camera-gimbal">
      <h2>Camera & Gimbal Control</h2>
      <ul>
        <li>Pan control</li>
        <li>Tilt control</li>
        <li>Home position / Calibration</li>
        <li>Current angles</li>
        <li>Tracking enable/disable</li>
        <li>Manual override</li>
      </ul>
    </div>
  );
}
