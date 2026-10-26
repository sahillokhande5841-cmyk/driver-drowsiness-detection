import StatusCard from "../components/StatusCard";
import CameraFeed from "../components/CameraFeed";
import MetricsCard from "../components/MetricsCard";
import ControlPanel from "../components/ControlPanel";
import { useState, useEffect } from "react";
import api from "../services/api";


function Dashboard() {
  const [metrics, setMetrics] = useState({
    status: "INITIALIZING",
    fatigueScore: 0,
    ear: 0,
    mar: 0,
    pitch: 0,
    blinkCount: 0,
    yawnCount: 0,
  });

  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (!running) return;

    const ws = new WebSocket("ws://127.0.0.1:8000/ws");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log(data);
      setMetrics(data);
    };

    ws.onerror = (err) => {
      console.error("WebSocket Error:", err);
    };

    ws.onclose = () => {
      console.log("WebSocket Closed");
  };

    return () => {
      ws.close();
    };

  }, [running]);

  const startDetector = async () => {
    try {
      const res = await api.post("/start");
      console.log(res.data);
      setRunning(true);
    } catch (err) {
      console.error(err);
    }
  };

  const stopDetector = async () => {
    try {
        setRunning(false);

        setMetrics({
            status: "INITIALIZING",
            fatigueScore: 0,
            ear: 0,
            mar: 0,
            pitch: 0,
            blinkCount: 0,
            yawnCount: 0,
        });

        const res = await api.post("/stop");
        console.log(res.data);
    } catch (err) {
        console.error(err);
    }
};

  return (
    <div className="min-h-screen bg-slate-950 px-4 py-8 sm:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 tracking-tight">
              Driver Drowsiness Dashboard
            </h1>
            <p className="text-slate-500 text-sm mt-1">
              Real-time fatigue monitoring
            </p>
          </div>

          <span
            className={`flex items-center gap-2 text-xs font-semibold px-3 py-1.5 rounded-full border ${
              running
                ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/30"
                : "text-slate-500 bg-slate-800/50 border-slate-700"
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                running ? "bg-emerald-400 animate-pulse" : "bg-slate-500"
              }`}
            />
            {running ? "Monitoring" : "Idle"}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-4">
            <StatusCard metrics={metrics} />
          </div>

          <div className="lg:col-span-8">
            <CameraFeed running={running} />
          </div>

          <div className="lg:col-span-8">
            <MetricsCard metrics={metrics} />
          </div>

          <div className="lg:col-span-4">
            <ControlPanel startDetector={startDetector} stopDetector={stopDetector} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;