import { useState, useEffect, useRef } from "react";
import {
  Shield,
  Activity,
  Sliders,
  Volume2,
  VolumeX,
  Sparkles,
  Play,
  Square,
  RefreshCw,
  Bell,
  Eye,
  Smile,
  Compass,
} from "lucide-react";

import CameraFeed from "../components/CameraFeed";
import StatusCard from "../components/StatusCard";
import MetricsCard from "../components/MetricsCard";
import TelemetryCharts from "../components/TelemetryCharts";
import ControlPanel from "../components/ControlPanel";
import EventLogCard from "../components/EventLogCard";
import SettingsModal from "../components/SettingsModal";
import VoiceAlertHandler from "../components/VoiceAlertHandler";

import {
  getStatus,
  startDetector,
  stopDetector,
  recalibrate,
  setSettings,
  triggerTestAlert,
} from "../services/api";

const WS_URL = "ws://127.0.0.1:8000/ws";

const INITIAL_METRICS = {
  status: "NORMAL",
  cameraStatus: "ready",
  faceDetected: false,
  fatigueScore: 0.0,
  ear: 0.28,
  earThreshold: 0.20,
  mar: 0.12,
  marThreshold: 0.52,
  pitch: 0.0,
  yaw: 0.0,
  roll: 0.0,
  blinkCount: 0,
  yawnCount: 0,
  isEyeClosed: false,
  isYawning: false,
  isHeadDown: false,
  isPhoneDistracted: false,
  fps: 0.0,
  running: false,
  activeAlert: null,
  recentEvents: [],
  calibrating: false,
};

function Dashboard() {
  const [running, setRunning] = useState(false);
  const [metrics, setMetrics] = useState(INITIAL_METRICS);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [audioMuted, setAudioMuted] = useState(false);
  const [language, setLanguage] = useState("hi");

  const wsRef = useRef(null);

  // Sync initial status from REST API
  useEffect(() => {
    getStatus()
      .then((data) => {
        if (data) {
          setRunning(Boolean(data.running));
          setMetrics((prev) => ({ ...prev, ...data }));
        }
      })
      .catch((err) => console.log("[Dashboard] Initial status sync standby:", err.message));
  }, []);

  // Connect WebSocket for real-time 10Hz streaming
  useEffect(() => {
    let shouldReconnect = true;

    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("[WebSocket] Connected to backend telemetry stream.");
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data && typeof data === "object") {
              setMetrics((prev) => ({
                ...prev,
                ...data,
                // Ensure array fields remain defined
                recentEvents: Array.isArray(data.recentEvents) ? data.recentEvents : prev.recentEvents,
              }));
              if (typeof data.running === "boolean") {
                setRunning(data.running);
              }
            }
          } catch (e) {
            console.error("[WebSocket] JSON parse error:", e);
          }
        };

        ws.onclose = () => {
          if (shouldReconnect) {
            setTimeout(connectWebSocket, 1500);
          }
        };

        ws.onerror = (err) => {
          ws.close();
        };
      } catch (e) {
        if (shouldReconnect) {
          setTimeout(connectWebSocket, 2000);
        }
      }
    };

    connectWebSocket();

    return () => {
      shouldReconnect = false;
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const handleStart = async () => {
    try {
      await startDetector();
      setRunning(true);
    } catch (e) {
      console.error("[Dashboard] Start failed:", e);
    }
  };

  const handleStop = async () => {
    try {
      await stopDetector();
      setRunning(false);
      setMetrics((prev) => ({ ...prev, running: false, status: "NORMAL" }));
    } catch (e) {
      console.error("[Dashboard] Stop failed:", e);
    }
  };

  const handleRecalibrate = async () => {
    try {
      await recalibrate();
    } catch (e) {
      console.error("[Dashboard] Recalibrate failed:", e);
    }
  };

  const handleApplySettings = async (newSettings) => {
    try {
      if (newSettings.language) setLanguage(newSettings.language);
      await setSettings(newSettings);
    } catch (e) {
      console.error("[Dashboard] Settings apply failed:", e);
    }
  };

  const handleTriggerTestAlert = async () => {
    try {
      await triggerTestAlert("DROWSINESS");
    } catch (e) {
      console.error("[Dashboard] Test alert failed:", e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-white">
      {/* Background Radial Glow */}
      <div className="fixed inset-0 pointer-events-none bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(14,165,233,0.12),rgba(255,255,255,0))]" />

      {/* Headless Voice Alert Handler */}
      <VoiceAlertHandler
        activeAlert={metrics.activeAlert}
        audioMuted={audioMuted}
        language={language}
      />

      {/* Navigation Header */}
      <header className="relative z-10 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-950/50">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-black tracking-wider uppercase text-slate-100 flex items-center gap-2">
              AI Driver Safety Cockpit
              <span className="text-[10px] font-mono font-bold bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 px-2 py-0.5 rounded-full">
                v2.0 PRO
              </span>
            </h1>
            <p className="text-[11px] text-slate-500">
              Real-time Computer Vision Fatigue, Microsleep & Distraction Detection
            </p>
          </div>
        </div>

        {/* Global Toolbar Quick Actions */}
        <div className="flex items-center gap-3">
          {/* Language Switcher */}
          <button
            onClick={() => setLanguage((prev) => (prev === "hi" ? "en" : "hi"))}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 transition-colors cursor-pointer"
            title="Switch Voice Alert Language"
          >
            <span>{language === "hi" ? "🇮🇳 Hindi" : "🇺🇸 English"}</span>
          </button>

          {/* Mute Audio */}
          <button
            onClick={() => setAudioMuted((prev) => !prev)}
            className={`p-2 rounded-xl border transition-colors cursor-pointer ${
              audioMuted
                ? "bg-rose-500/10 border-rose-500/30 text-rose-400"
                : "bg-slate-900 border-slate-800 text-slate-300 hover:text-white"
            }`}
            title={audioMuted ? "Unmute Voice Alarms" : "Mute Voice Alarms"}
          >
            {audioMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </button>

          {/* Settings Trigger */}
          <button
            onClick={() => setIsSettingsOpen(true)}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white transition-colors cursor-pointer"
          >
            <Sliders className="w-3.5 h-3.5" />
            Settings
          </button>
        </div>
      </header>

      {/* Main Cockpit Content Grid */}
      <main className="relative z-10 flex-1 p-6 space-y-6 max-w-7xl mx-auto w-full">
        {/* Top Biometric Metrics Ribbon */}
        <MetricsCard metrics={metrics} />

        {/* Center Grid: Left = Video Stream (8 cols), Right = Status Hero & Controls (4 cols) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Live Camera Feed */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            <CameraFeed
              running={running}
              metrics={metrics}
              onRecalibrate={handleRecalibrate}
            />

            {/* Sparkline Charts Strip */}
            <TelemetryCharts metrics={metrics} />
          </div>

          {/* Right Control & Status Column */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            {/* Status Hero Card */}
            <StatusCard metrics={metrics} running={running} />

            {/* Controls Panel */}
            <ControlPanel
              running={running}
              onStart={handleStart}
              onStop={handleStop}
              onRecalibrate={handleRecalibrate}
              onOpenSettings={() => setIsSettingsOpen(true)}
              onTriggerTestAlert={handleTriggerTestAlert}
              audioMuted={audioMuted}
              onToggleMute={() => setAudioMuted((prev) => !prev)}
            />

            {/* Event Audit Log Card */}
            <EventLogCard events={metrics.recentEvents || []} />
          </div>
        </div>
      </main>

      {/* Modal Settings Drawer */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={{
          earThreshold: metrics.earThreshold,
          marThreshold: metrics.marThreshold,
          language,
        }}
        onSave={handleApplySettings}
        onTriggerTestAlert={handleTriggerTestAlert}
      />
    </div>
  );
}

export default Dashboard;
