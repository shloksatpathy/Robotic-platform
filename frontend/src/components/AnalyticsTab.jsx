import React from 'react';
import TelemetryTab from './TelemetryTab';
import EventLog from './EventLog';
import ObjectChart from './ObjectChart';
import './AnalyticsTab.css';

/**
 * AnalyticsTab — Unified view of telemetry graphs, event log, and object tracking.
 * Props:
 *   - stats: telemetry stats object
 *   - events: array of system events
 *   - detections: array of detection objects
 *   - theme: 'dark' | 'light'
 */
export default function AnalyticsTab({ stats, events, detections, theme }) {
  return (
    <div className="analytics-tab">
      {/* Header */}
      <div className="analytics-header">
        <h1>Analytics &amp; Telemetry</h1>
      </div>

      {/* Charts section */}
      <div className="analytics-charts">
        <TelemetryTab stats={stats} theme={theme} />
      </div>

      {/* Bottom: Event log + Object chart */}
      <div className="analytics-bottom">
        <div className="analytics-log-wrapper">
          <EventLog events={events} />
        </div>
        <div className="analytics-chart-wrapper glass">
          <ObjectChart detections={detections} />
        </div>
      </div>
    </div>
  );
}
