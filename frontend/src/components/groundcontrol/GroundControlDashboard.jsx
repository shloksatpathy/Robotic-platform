import React, { useState } from 'react';
import '../ComponentStyles.css';
import VideoFeed from '../VideoFeed';
import ObjectChart from '../ObjectChart';
import EventLog from '../EventLog';

import ControlButtons from '../ControlButtons';
import TelemetryTab from '../TelemetryTab';
import SettingsTab from '../SettingsTab';
import './GroundControlDashboard.css';

/**
 * GroundControlDashboard component
 * Props:
 *  - frame: current video frame image source
 *  - stats: telemetry statistics object
 *  - detections: array of detection objects
 *  - events: array of system events
 */
export default function GroundControlDashboard({ frame, stats, detections, events, theme, setTheme }) {
  const [activeTab, setActiveTab] = useState('video');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'video':
        return (
          <div className="video-tab-grid">
            <div className="video-left-col">
              <div className="video-feed-wrapper">
                <VideoFeed frame={frame} status={stats?.status || 'OFFLINE'} mode={stats?.mode || 'OFFLINE'} theme={theme} />
              </div>
              <div className="video-controls-chart-wrapper">
                <div className="chart-section">
                  <ObjectChart detections={detections} />
                </div>
                <div className="control-section">
                  <ControlButtons />
                </div>
              </div>
            </div>
            <div className="video-right-col">
              <div className="lidar-map-wrapper">
                <div className="lidar-map glass">
                  <div className="lidar-header">
                    <h3>LIDAR Mapping</h3>
                    <span className="live-tag">WAITING</span>
                  </div>
                  <div className="lidar-canvas-container">
                    <div className="lidar-placeholder">
                      <span>No LIDAR data</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="event-log-wrapper">
                <EventLog events={events} />
              </div>
            </div>
          </div>
        );
      case 'telemetry':
        return <TelemetryTab stats={stats} theme={theme} />;
      case 'settings':
        return <SettingsTab />;
      default:
        return null;
    }
  };

  const systemStatus = stats?.status || 'OFFLINE';

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-logo">
          <div className="logo-pulse" />
          <h1>KRISTELLAR'S DASHBOARD</h1>
        </div>
        <div className="header-status">
          <span className="status-label">SYSTEM STATE:</span>
          <span className={`status-value ${systemStatus.toLowerCase().replace('...', '')}`}>{systemStatus.toUpperCase()}</span>
        </div>
        <div className="header-right-controls">
          <div className="theme-selector">
            <button
              className={`theme-pill${theme === 'dark' ? ' active' : ''}`}
              onClick={() => setTheme('dark')}
            >TACTICAL</button>
            <button
              className={`theme-pill${theme === 'light' ? ' active' : ''}`}
              onClick={() => setTheme('light')}
            >ENTERPRISE</button>
          </div>
          <nav className="tab-nav">
            <button className={activeTab === 'video' ? 'active' : ''} onClick={() => setActiveTab('video')}>Video</button>
            <button className={activeTab === 'telemetry' ? 'active' : ''} onClick={() => setActiveTab('telemetry')}>Telemetry</button>
            <button className={activeTab === 'settings' ? 'active' : ''} onClick={() => setActiveTab('settings')}>Settings</button>
          </nav>
        </div>
      </header>
      {renderTabContent()}
    </div>
  );
}

