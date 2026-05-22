import React from 'react';
import './ComponentStyles.css';

function EventLog({ events = [] }) {
  const safeEvents = events || [];
  return (
    <div className="event-log">
      <h3>Event Log</h3>
      <ul>
        {safeEvents.length === 0 ? (
          <li className="event-system">No events recorded.</li>
        ) : (
          safeEvents.map((ev, idx) => (
            <li key={idx} className={`event-${(ev.type || 'system').toLowerCase()}`}>
              [{ev.timestamp || ''}] <strong>{(ev.type || 'SYSTEM')}:</strong> {ev.message || ''}
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default EventLog;
