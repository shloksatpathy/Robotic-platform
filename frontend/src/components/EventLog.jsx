import React from "react";

function EventLog({ events = [] }) {
  return (
    <div className="event-log glass-panel">
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
          <polyline points="4 17 10 11 4 5"></polyline>
          <line x1="12" y1="19" x2="20" y2="19"></line>
        </svg>
        System Log & Event Terminal
      </h3>

      <div className="event-terminal">
        {events && events.length > 0 ? (
          events.map((event, index) => (
            <div className="terminal-line" key={index}>
              <span className="line-time">[{event.timestamp}]</span>
              <span className={`line-type ${event.type.toLowerCase()}`}>
                {event.type.toUpperCase()}:
              </span>
              <span className="line-message">{event.message}</span>
            </div>
          ))
        ) : (
          <div className="terminal-line">
            <span className="line-time">
              [{new Date().toLocaleTimeString()}]
            </span>
            <span className="line-type system">SYSTEM:</span>
            <span className="line-message">
              TELEMETRY INTERFACE SYSTEM CONNECTED. LISTENING FOR BROADCASTS...
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

export default EventLog;