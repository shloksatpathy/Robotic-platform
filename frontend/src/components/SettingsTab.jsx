import React, { useState } from 'react';
import './ComponentStyles.css';

/**
 * SettingsTab provides UI controls for camera gimbal orientation,
 * sensor calibration, and telemetry on/off toggle.
 */
export default function SettingsTab() {
  const [tilt, setTilt] = useState(0);
  const [pan, setPan] = useState(0);
  const [telemetryOn, setTelemetryOn] = useState(true);

  const handleRecalibrate = () => {
    // Placeholder: send recalibration command to backend
    console.log('Sensor recalibration requested');
  };

  return (
    <div className="settings-tab glass">
      <h2 className="section-title">Camera Gimbal Control</h2>
      <div className="slider-group">
        <label className="slider-label">Tilt: {tilt}°</label>
        <input
          type="range"
          min="-90"
          max="90"
          value={tilt}
          onChange={e => setTilt(parseInt(e.target.value, 10))}
          className="slider"
        />
      </div>
      <div className="slider-group">
        <label className="slider-label">Pan: {pan}°</label>
        <input
          type="range"
          min="-180"
          max="180"
          value={pan}
          onChange={e => setPan(parseInt(e.target.value, 10))}
          className="slider"
        />
      </div>

      <h2 className="section-title">System Controls</h2>
      <button className="btn primary" onClick={handleRecalibrate}>Sensor Recalibration</button>

      <h2 className="section-title">Telemetry</h2>
      <div className="toggle-group">
        <label className="toggle-label">Telemetry Stream</label>
        <input
          type="checkbox"
          checked={telemetryOn}
          onChange={e => setTelemetryOn(e.target.checked)}
          className="toggle"
        />
      </div>
    </div>
  );
}
