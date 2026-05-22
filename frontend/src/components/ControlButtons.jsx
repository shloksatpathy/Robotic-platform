import React, { useEffect, useCallback } from 'react';
import './ComponentStyles.css';

/**
 * ControlButtons component – provides control panel with:
 *  - Start / Stop / Snapshot action buttons
 *  - Navigation D-pad (Forward / Back / Left / Right)
 *  - Emergency Stop
 *  - Keyboard arrow key instructions
 */
export default function ControlButtons() {
  const handleAction = (action) => {
    console.log(`Control action: ${action}`);
    // In a full implementation this would emit events to the backend.
  };

  const handleKeyDown = useCallback((e) => {
    switch (e.key) {
      case 'ArrowUp':    handleAction('forward'); break;
      case 'ArrowDown':  handleAction('backward'); break;
      case 'ArrowLeft':  handleAction('left'); break;
      case 'ArrowRight': handleAction('right'); break;
      default: return;
    }
    e.preventDefault();
  }, []);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className="control-buttons glass">
      {/* Action buttons */}
      <div className="ctrl-actions">
        <button className="ctrl-btn small" onClick={() => handleAction('start')}>Start</button>
        <button className="ctrl-btn small" onClick={() => handleAction('stop')}>Stop</button>
        <button className="ctrl-btn small" onClick={() => handleAction('snapshot')}>Snap</button>
      </div>

      {/* Navigation D-pad */}
      <div className="ctrl-nav">
        <div className="nav-label">NAVIGATION</div>
        <div className="nav-dpad">
          <button className="nav-btn up" onClick={() => handleAction('forward')}>▲</button>
          <div className="nav-middle-row">
            <button className="nav-btn left" onClick={() => handleAction('left')}>◀</button>
            <div className="nav-center-dot" />
            <button className="nav-btn right" onClick={() => handleAction('right')}>▶</button>
          </div>
          <button className="nav-btn down" onClick={() => handleAction('backward')}>▼</button>
        </div>
        <div className="nav-hint">Use ↑ ↓ ← → arrow keys</div>
      </div>

      {/* Emergency Stop */}
      <button className="ctrl-btn emergency" onClick={() => handleAction('emergency')}>Emergency Stop</button>
    </div>
  );
}
