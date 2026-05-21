import React from "react";

function StatsPanel({ stats }) {
  const { fps = 0, objectCount = 0, latency = 0, model = "YOLOv8n" } = stats;

  return (
    <div className="stats-panel glass-panel">
      <h3>
        <svg 
          width="16" 
          height="16" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2.5" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        >
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
        System Status Telemetry
      </h3>

      <div className="stats-panel-container">
        <div className="stat-card fps">
          <h4>Framerate</h4>
          <p>{fps} FPS</p>
        </div>

        <div className="stat-card objects">
          <h4>Active Targets</h4>
          <p>{objectCount}</p>
        </div>

        <div className="stat-card latency">
          <h4>Core Latency</h4>
          <p>{latency} ms</p>
        </div>

        <div className="stat-card model">
          <h4>Active Engine</h4>
          <p>{model}</p>
        </div>
      </div>
    </div>
  );
}

export default StatsPanel;