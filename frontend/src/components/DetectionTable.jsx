import React from "react";

function DetectionTable({ detections = [] }) {
  // Color-coded classification based on YOLO confidence scores
  const getConfidenceLevel = (confidence) => {
    if (confidence >= 0.90) return "high";
    if (confidence >= 0.70) return "med";
    return "low";
  };

  return (
    <div className="table-container glass-panel">
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
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="9" y1="9" x2="15" y2="9"></line>
          <line x1="9" y1="13" x2="15" y2="13"></line>
          <line x1="9" y1="17" x2="15" y2="17"></line>
        </svg>
        Tracked Targets Registry
      </h3>

      <table className="telemetry-table">
        <thead>
          <tr>
            <th className="id-col" style={{ width: "20%" }}>Target ID</th>
            <th className="class-col" style={{ width: "45%" }}>Classification</th>
            <th style={{ width: "35%" }}>Confidence Rating</th>
          </tr>
        </thead>
        <tbody>
          {detections && detections.length > 0 ? (
            detections.map((item) => (
              <tr key={item.id}>
                <td className="id-col">
                  TRK-{String(item.id).padStart(3, "0")}
                </td>
                <td className="class-col">
                  {item.class.toUpperCase()}
                </td>
                <td>
                  <span className={`confidence-badge ${getConfidenceLevel(item.confidence)}`}>
                    {Math.round(item.confidence * 100)}%
                  </span>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="3" className="no-detections">
                SYSTEM SCANNING FOR OBJECTS... NO ACTIVE TARGETS REGISTERED.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default DetectionTable;