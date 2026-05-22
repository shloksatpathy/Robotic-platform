import React from 'react';
import './ComponentStyles.css';

function EventLog({ events }) {
  return (
    <div className="event-log">
      <h3>Event Log</h3>
      <ul>
        {events.map((ev, idx) => (
          <li key={idx} className={`event-${ev.type.toLowerCase()}`}>
            [{ev.timestamp}] <strong>{ev.type}:</strong> {ev.message}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default EventLog;
