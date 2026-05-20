function StatsPanel() {
  return (
    <div className="stats-panel">

      <div className="stat-card">
        <h4>FPS</h4>
        <p>30</p>
      </div>

      <div className="stat-card">
        <h4>Objects</h4>
        <p>4</p>
      </div>

      <div className="stat-card">
        <h4>Latency</h4>
        <p>28 ms</p>
      </div>

      <div className="stat-card">
        <h4>Model</h4>
        <p>YOLO</p>
      </div>

    </div>
  );
}

export default StatsPanel;