import React, { useState, useEffect, useRef, useCallback } from "react";
import "./App.css";
import VideoFeed from "./components/VideoFeed";
import StatsPanel from "./components/StatsPanel";
import DetectionTable from "./components/DetectionTable";
import EventLog from "./components/EventLog";
import ObjectChart from "./components/ObjectChart";

function App() {
  const [detections, setDetections] = useState([]);
  const [stats, setStats] = useState({
    fps: 0,
    latency: 0,
    objectCount: 0,
    model: "YOLOv8n",
    mode: "Offline",
    status: "Connecting..."
  });
  const [events, setEvents] = useState([]);
  const wsRef = useRef(null);
  const lastFrameTimeRef = useRef(performance.now());
  const prevClassesRef = useRef(new Set());

  // Direct DOM ref for the <img> element — bypasses React reconciliation entirely
  const imgRef = useRef(null);

  // Throttle refs: avoid updating React state on every single frame
  const pendingStatsRef = useRef(null);
  const pendingDetectionsRef = useRef(null);
  const throttleTimerRef = useRef(null);

  // FPS smoothing: use rolling average instead of per-frame jitter
  const fpsHistoryRef = useRef([]);

  // Function to add system logs with precision timestamps
  const addEvent = useCallback((type, message) => {
    const timestamp = new Date().toLocaleTimeString();
    setEvents((prev) => [
      { timestamp, type, message },
      ...prev.slice(0, 49) // Maintain last 50 events to optimize performance
    ]);
  }, []);

  // Flush pending stats/detections to React state at a throttled rate (~10 Hz)
  // This lets child components (StatsPanel, DetectionTable, etc.) update at 10 FPS
  // while the video <img> stays at a full 30 FPS via direct DOM writes.
  const flushPendingUpdates = useCallback(() => {
    if (pendingStatsRef.current) {
      setStats(pendingStatsRef.current);
      pendingStatsRef.current = null;
    }
    if (pendingDetectionsRef.current) {
      setDetections(pendingDetectionsRef.current);
      pendingDetectionsRef.current = null;
    }
  }, []);

  useEffect(() => {
    let reconnectTimeout;
    // Log initial platform bootstrap
    addEvent("System", "Booting AI Robotics Telemetry Platform...");
    addEvent("System", "Loading YOLOv8n tracking layers...");

    // Start throttled flush timer: updates React state at ~10 Hz (every 100ms)
    throttleTimerRef.current = setInterval(flushPendingUpdates, 100);

    function connect() {
      setStats((prev) => ({ ...prev, status: "Connecting..." }));
      // Establish WebSocket connection to backend
      const socketUrl = "ws://localhost:8000/ws";
      const ws = new WebSocket(socketUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setStats((prev) => ({ ...prev, status: "Connected" }));
        addEvent("System", "Telemetry interface linked successfully.");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Calculate actual arrival FPS on frontend (smoothed rolling average)
          const now = performance.now();
          const delta = now - lastFrameTimeRef.current;
          lastFrameTimeRef.current = now;
          const instantFps = delta > 0 ? 1000 / delta : 30;

          // Rolling average over last 10 frames for stable FPS display
          const history = fpsHistoryRef.current;
          history.push(instantFps);
          if (history.length > 10) history.shift();
          const smoothedFps = Math.round(
            history.reduce((a, b) => a + b, 0) / history.length
          );

          // CRITICAL PERF: Write frame directly to DOM, bypassing React state.
          // This is the single biggest perf win — avoids triggering a full
          // React reconciliation + browser layout/paint cycle on every frame.
          if (data.frame && imgRef.current) {
            imgRef.current.src = `data:image/jpeg;base64,${data.frame}`;
          }

          if (data.detections) {
            const formatted = data.detections.map((d, idx) => ({
              id: d.id != null ? d.id : idx + 1,
              class: d.class,
              confidence: d.confidence
            }));

            // Stage detection + stats updates for throttled flush (not immediate)
            pendingDetectionsRef.current = formatted;

            // Dynamic event generation based on changes in tracked object classes
            const currentClasses = new Set(formatted.map((d) => d.class));
            formatted.forEach((d) => {
              if (!prevClassesRef.current.has(d.class)) {
                addEvent("Detected", `Acquired target tracking: [${d.class.toUpperCase()}] (${Math.round(d.confidence * 100)}% confidence)`);
              }
            });
            prevClassesRef.current.forEach((cls) => {
              if (!currentClasses.has(cls)) {
                addEvent("System", `Lost tracking on target: [${cls.toUpperCase()}]`);
              }
            });
            prevClassesRef.current = currentClasses;

            // Stage stats for throttled flush
            pendingStatsRef.current = {
              status: "Connected",
              fps: smoothedFps,
              latency: data.stats?.latency || 0,
              objectCount: formatted.length,
              mode: data.stats?.mode || "Webcam",
              model: data.stats?.model || "YOLOv8n"
            };
          }
        } catch (err) {
          console.error("Error parsing websocket frame", err);
        }
      };

      ws.onerror = () => {
        setStats((prev) => ({ ...prev, status: "Error" }));
        addEvent("Error", "Telemetry interface encountered an interface error.");
      };

      ws.onclose = () => {
        setDetections([]);
        prevClassesRef.current.clear();
        setStats((prev) => ({ ...prev, status: "Disconnected", mode: "Offline", fps: 0, latency: 0, objectCount: 0 }));
        addEvent("Warning", "Telemetry connection closed. Attempting auto-reconnect...");
        reconnectTimeout = setTimeout(connect, 3000);
      };
    }
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      clearTimeout(reconnectTimeout);
      if (throttleTimerRef.current) {
        clearInterval(throttleTimerRef.current);
      }
    };
  }, [addEvent, flushPendingUpdates]);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-logo">
          <div className="logo-pulse"></div>
          <h1>KRISTELLAR'S DASHBOARD</h1>
        </div>
        <div className="header-status">
          <span className="status-label">SYSTEM STATE:</span>
          <span className={`status-value ${stats.status.toLowerCase().replace("...", "")}`}>
            {stats.status.toUpperCase()}
          </span>
        </div>
      </header>
      <div className="top-section">
        <VideoFeed imgRef={imgRef} status={stats.status} mode={stats.mode} />
        <StatsPanel stats={stats} />
      </div>
      <div className="table-section">
        <DetectionTable detections={detections} />
      </div>
      <div className="bottom-section">
        <ObjectChart detections={detections} />
        <EventLog events={events} />
      </div>
    </div>
  );
}

export default App;