function EventLog() {

  const events = [
    "Person detected",
    "Bottle detected",
    "Chair detected"
  ];

  return (
    <div className="event-log">

      <h3>Event Log</h3>

      {events.map((event, index) => (
        <p key={index}>{event}</p>
      ))}

    </div>
  );
}

export default EventLog;