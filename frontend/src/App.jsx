import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import TabDock from "./components/TabDock";
import LandingPage from "./components/LandingPage";
import OperationsTab from "./components/OperationsTab";
import AnalyticsTab from "./components/AnalyticsTab";
import PathPlanningTab from "./components/PathPlanningTab";

function App() {
  const [frame, setFrame] = useState(null);
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
  const [theme, setTheme] = useState(() => localStorage.getItem('gcs-theme') || 'dark');
  const [activeTab, setActiveTab] = useState('home');
  const wsRef = useRef(null);
  const lastFrameTimeRef = useRef(performance.now());
  const prevClassesRef = useRef(new Set());

  // Persist theme preference and toggle class on <html>
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'light') {
      root.classList.add('theme-light');
    } else {
      root.classList.remove('theme-light');
    }
    localStorage.setItem('gcs-theme', theme);
  }, [theme]);

  // Function to add system logs with precision timestamps
  const addEvent = (type, message) => {
    const timestamp = new Date().toLocaleTimeString();
    setEvents((prev) => [
      { timestamp, type, message },
      ...prev.slice(0, 49) // Maintain last 50 events to optimize performance
    ]);
  };

  useEffect(() => {
    let reconnectTimeout;
    // Log initial platform bootstrap
    addEvent("System", "Booting AI Robotics Telemetry Platform...");
    addEvent("System", "Loading YOLOv8n tracking layers...");
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
          // Calculate actual arrival FPS on frontend
          const now = performance.now();
          const delta = now - lastFrameTimeRef.current;
          lastFrameTimeRef.current = now;
          const calculatedFps = delta > 0 ? Math.round(1000 / delta) : 30;
          if (data.frame) {
            setFrame(data.frame);
          } else {
            setFrame(null);
          }
          if (data.detections) {
            const formatted = data.detections.map((d, idx) => ({
              id: d.id != null ? d.id : idx + 1,
              class: d.class,
              confidence: d.confidence
            }));
            setDetections(formatted);
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
            // Merge stats from backend and local FPS calculation
            setStats((prev) => ({
              ...prev,
              status: "Connected",
              fps: calculatedFps,
              latency: data.stats?.latency || 0,
              objectCount: formatted.length,
              mode: data.stats?.mode || "Webcam",
              model: data.stats?.model || "YOLOv8n"
            }));
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
        setFrame(null);
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
    };
  }, []);

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'home':
        return <LandingPage stats={stats} />;
      case 'operations':
        return (
          <OperationsTab
            frame={frame}
            stats={stats}
            detections={detections}
            theme={theme}
          />
        );
      case 'analytics':
        return (
          <AnalyticsTab
            stats={stats}
            events={events}
            detections={detections}
            theme={theme}
          />
        );
      case 'pathplanning':
        return <PathPlanningTab />;
      default:
        return <LandingPage stats={stats} />;
    }
  };

  return (
    <>
      {renderActiveTab()}
      <TabDock activeTab={activeTab} onTabChange={setActiveTab} />
    </>
  );
}

export default App;