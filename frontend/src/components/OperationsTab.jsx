import React from 'react';
import VideoFeed from './VideoFeed';
import LidarMap from './LidarMap';
import ControlButtons from './ControlButtons';
import DetectionTable from './DetectionTable';
import './OperationsTab.css';

/**
 * OperationsTab — Video feed + Lidar map + Controls + Detection table.
 * Reuses existing components in a split layout.
 * Props:
 *   - frame: base64 video frame
 *   - stats: telemetry stats object
 *   - detections: array of detection objects
 *   - theme: 'dark' | 'light'
 */
export default function OperationsTab({ frame, stats, detections, theme }) {
  return (
    <div className="operations-tab">
      {/* Left column: Video + Lidar */}
      <div className="ops-main-left">
        <div className="ops-video-wrapper">
          <VideoFeed
            frame={frame}
            status={stats?.status || 'OFFLINE'}
            mode={stats?.mode || 'OFFLINE'}
            theme={theme}
          />
        </div>
        <div className="ops-lidar-wrapper">
          <LidarMap />
        </div>
      </div>

      {/* Right column: Controls + Detection Table */}
      <div className="ops-main-right">
        <div className="ops-controls-wrapper">
          <ControlButtons />
        </div>
        <div className="ops-detection-wrapper">
          <DetectionTable detections={detections} />
        </div>
      </div>

      {/* Status bar */}
      <div className="ops-status-bar">
        <div className="ops-status-item">
          <strong>FPS:</strong>
          <span className="ops-status-value">{stats?.fps || 0}</span>
        </div>
        <div className="ops-status-item">
          <strong>Latency:</strong>
          <span className="ops-status-value">{stats?.latency || 0} ms</span>
        </div>
        <div className="ops-status-item">
          <strong>Mode:</strong>
          <span className="ops-status-value">{(stats?.mode || 'Offline').toUpperCase()}</span>
        </div>
        <div className="ops-status-item">
          <strong>Objects:</strong>
          <span className="ops-status-value">{stats?.objectCount || 0}</span>
        </div>
        <div className="ops-status-item">
          <strong>Model:</strong>
          <span className="ops-status-value">{stats?.model || 'N/A'}</span>
        </div>
      </div>
    </div>
  );
}
