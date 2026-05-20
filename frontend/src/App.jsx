import "./App.css";

import VideoFeed from "./components/VideoFeed";
import StatsPanel from "./components/StatsPanel";
import DetectionTable from "./components/DetectionTable";
import EventLog from "./components/EventLog";
import ObjectChart from "./components/ObjectChart";

const [frame, SetFrame] = useState(null);
function App() {
  return (
    <div className="dashboard">

      <header>
        <h1>AI Robotics Dashboard</h1>
      </header>

      <div className="top-section">

        <VideoFeed frame={frame} />

        <StatsPanel />

      </div>

      <DetectionTable />

      <div className="bottom-section">

        <ObjectChart />

        <EventLog />

      </div>

    </div>
  );
}

export default App;