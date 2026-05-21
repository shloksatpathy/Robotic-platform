import React from "react";

function ObjectChart({ detections = [] }) {
  // Aggregate detection counts per class class name
  const distribution = detections.reduce((acc, current) => {
    acc[current.class] = (acc[current.class] || 0) + 1;
    return acc;
  }, {});

  // Convert aggregation to sorted list (highest counts first)
  const distributionArray = Object.entries(distribution).map(([className, count]) => ({
    className,
    count
  })).sort((a, b) => b.count - a.count);

  // Get max count to normalize widths relative to the largest item
  const maxCount = distributionArray.length > 0 
    ? Math.max(...distributionArray.map(item => item.count)) 
    : 1;

  return (
    <div className="object-chart glass-panel">
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
          <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
          <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
        </svg>
        Object Distribution Profile
      </h3>

      <div className="chart-container">
        {distributionArray.length > 0 ? (
          distributionArray.map((item, index) => {
            const widthPct = (item.count / maxCount) * 100;
            return (
              <div className="chart-bar-row" key={index}>
                <div className="chart-bar-info">
                  <span className="chart-bar-class">
                    {item.className.toUpperCase()}
                  </span>
                  <span className="chart-bar-count">
                    {item.count} unit{item.count > 1 ? "s" : ""}
                  </span>
                </div>
                <div className="chart-bar-outer">
                  <div 
                    className="chart-bar-inner" 
                    style={{ width: `${widthPct}%` }}
                  ></div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="chart-empty">
            AWAITING TARGET CLASSIFICATION SCHEMATICS...
          </div>
        )}
      </div>
    </div>
  );
}

export default ObjectChart;