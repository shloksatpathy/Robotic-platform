// GroundControlDashboard with tabbed interface
import React, { useState } from 'react';
import '../../styles/groundcontrol.css';
import MissionControl from './MissionControl';
import SensorTelemetry from './SensorTelemetry';
import VisionSystem from './VisionSystem';
import CameraGimbalControl from './CameraGimbalControl';
import SystemHealth from './SystemHealth';
import EventLogs from './EventLogs';

const tabs = [
  { name: 'Mission Control', component: <MissionControl /> },
  { name: 'Sensor Telemetry', component: <SensorTelemetry /> },
  { name: 'Vision System', component: <VisionSystem /> },
  { name: 'Camera & Gimbal', component: <CameraGimbalControl /> },
  { name: 'System Health', component: <SystemHealth /> },
  { name: 'Event Logs', component: <EventLogs /> },
];

export default function GroundControlDashboard() {
  const [activeTab, setActiveTab] = useState(tabs[0].name);
  const renderActive = tabs.find(t => t.name === activeTab)?.component;
  return (
    <div className="groundcontrol-dashboard">
      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab.name}
            className={tab.name === activeTab ? 'active' : ''}
            onClick={() => setActiveTab(tab.name)}
          >
            {tab.name}
          </button>
        ))}
      </div>
      <div className="tab-content">
        {renderActive}
      </div>
    </div>
  );
}
