import React from 'react';

export default function VisionSystem() {
  return (
    <div className="panel vision-system">
      <h2>Vision System</h2>
      <p>Live video feed with YOLO detections overlay.</p>
      {/* Placeholder for video feed component */}
      <div className="video-placeholder" style={{ backgroundColor: '#222', height: '300px', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        Video Feed Here
      </div>
      <p>Detection data panel (list of objects, confidence, tracking IDs).</p>
    </div>
  );
}
