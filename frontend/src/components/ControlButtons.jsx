import React from 'react';
import './ComponentStyles.css';

/**
 * ControlButtons component – provides bottom control panel buttons.
 * Includes Start, Stop, and Snapshot actions.
 */
export default function ControlButtons() {
  const handleAction = (action) => {
    console.log(`Control action: ${action}`);
    // In a full implementation this would emit events to the backend.
  };
  return (
    <div className="control-buttons glass">
      <button className="ctrl-btn" onClick={() => handleAction('start')}>Start</button>
      <button className="ctrl-btn" onClick={() => handleAction('stop')}>Stop</button>
      <button className="ctrl-btn" onClick={() => handleAction('snapshot')}>Snapshot</button>
    </div>
  );
}
