import React from 'react';

export default function SensorTelemetry() {
  return (
    <div className="panel sensor-telemetry">
      <h2>Sensor Telemetry</h2>
      <ul>
        <li>IMU – Roll, Pitch, Yaw, Acceleration</li>
        <li>GPS – Coordinates (if used)</li>
        <li>LiDAR – Point cloud overview</li>
        <li>Ultrasonic sensors – Distance readings</li>
        <li>ToF sensors – Precise range data</li>
        <li>Encoders – Wheel rotations</li>
        <li>Health status – Operational flags</li>
      </ul>
    </div>
  );
}
