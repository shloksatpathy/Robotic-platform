import React from "react";

function VideoFeed({ frame, status, mode }) {
  const isConnected = status === "Connected";

  return (
    <div className="video-feed glass-panel">
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
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
          <circle cx="12" cy="13" r="4"></circle>
        </svg>
        Live Telemetry Feed
      </h3>

      <div className="video-container">
        {isConnected && frame ? (
          <>
            <img
              src={`data:image/jpeg;base64,${frame}`}
              alt="Live Robotic Platform Feed"
              className="video-stream"
            />
            <div className="video-overlay-hud">
              <div className="hud-pill live">LIVE</div>
              <div className="hud-pill">{mode.toUpperCase()} MODE</div>
              <div className="hud-pill">640 × 480 px</div>
            </div>
          </>
        ) : (
          <div className="video-placeholder">
            <div className="placeholder-spinner"></div>
            <span>
              {status === "Connecting..."
                ? "BOOTING SYSTEM INTERFACE..."
                : status === "Disconnected"
                ? "TELEMETRY LINK SEVERED. RECONNECTING..."
                : status === "Error"
                ? "INTERFACE ERROR. CHECKING STATUS..."
                : status === "Connected" && !frame
                ? "WEBCAM OFFLINE. RETRYING CAMERA CONNECTION..."
                : "WAITING FOR ACTIVE TELEMETRY LINK..."}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export default VideoFeed;