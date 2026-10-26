import { useState, useEffect } from "react";
import { Activity, TrendingUp } from "lucide-react";

function TelemetryCharts({ metrics = {} }) {
  const [earHistory, setEarHistory] = useState(() => Array(30).fill(0.28));
  const [marHistory, setMarHistory] = useState(() => Array(30).fill(0.12));

  const currentEar = Number(metrics?.ear ?? 0.28);
  const earThreshold = Number(metrics?.earThreshold ?? 0.20);
  const currentMar = Number(metrics?.mar ?? 0.12);
  const marThreshold = Number(metrics?.marThreshold ?? 0.52);

  useEffect(() => {
    if (typeof metrics?.ear === "number" && !isNaN(metrics.ear)) {
      setEarHistory((prev) => [...prev.slice(1), Math.max(0, Math.min(1.0, metrics.ear))]);
    }
    if (typeof metrics?.mar === "number" && !isNaN(metrics.mar)) {
      setMarHistory((prev) => [...prev.slice(1), Math.max(0, Math.min(1.5, metrics.mar))]);
    }
  }, [metrics?.ear, metrics?.mar]);

  // Render SVG Sparkline safely
  const renderSparkline = (data, threshold, maxVal, colorClass, threshColorClass) => {
    const width = 280;
    const height = 55;
    const padding = 4;
    const safeMax = Math.max(0.1, maxVal);

    const points = data
      .map((val, idx) => {
        const safeVal = typeof val === "number" && !isNaN(val) ? val : 0;
        const x = (idx / (data.length - 1)) * width;
        const y = height - (Math.min(safeMax, Math.max(0, safeVal)) / safeMax) * (height - 2 * padding) - padding;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");

    const threshY = (
      height - (Math.min(safeMax, Math.max(0, threshold)) / safeMax) * (height - 2 * padding) - padding
    ).toFixed(1);

    return (
      <svg className="w-full h-14 overflow-visible" viewBox={`0 0 ${width} ${height}`}>
        {/* Background Grid Lines */}
        <line x1="0" y1={height / 2} x2={width} y2={height / 2} stroke="#334155" strokeDasharray="2,2" strokeWidth="0.5" />

        {/* Threshold Reference Line */}
        <line
          x1="0"
          y1={threshY}
          x2={width}
          y2={threshY}
          stroke={threshColorClass}
          strokeDasharray="4,3"
          strokeWidth="1.2"
          opacity="0.8"
        />

        {/* Data Path */}
        <polyline
          fill="none"
          stroke={colorClass}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />
      </svg>
    );
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          <h2 className="text-xs font-bold text-slate-300 uppercase tracking-widest">
            Real-Time Biometric Sparklines
          </h2>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">10Hz Streaming</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* EAR Sparkline */}
        <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] font-bold text-slate-300">EAR Waveform</span>
            <div className="flex items-center gap-2 font-mono text-[11px]">
              <span className="text-emerald-400 font-bold">{currentEar.toFixed(3)}</span>
              <span className="text-slate-500">| limit {earThreshold.toFixed(2)}</span>
            </div>
          </div>
          {renderSparkline(earHistory, earThreshold, 0.40, "#10b981", "#ef4444")}
          <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1">
            <span>Drowsy limit (Red line)</span>
            <span>Current: {currentEar < earThreshold ? "CLOSED" : "OPEN"}</span>
          </div>
        </div>

        {/* MAR Sparkline */}
        <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] font-bold text-slate-300">MAR Waveform</span>
            <div className="flex items-center gap-2 font-mono text-[11px]">
              <span className="text-cyan-400 font-bold">{currentMar.toFixed(3)}</span>
              <span className="text-slate-500">| limit {marThreshold.toFixed(2)}</span>
            </div>
          </div>
          {renderSparkline(marHistory, marThreshold, 0.80, "#06b6d4", "#f59e0b")}
          <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1">
            <span>Yawn threshold (Amber line)</span>
            <span>Current: {currentMar > marThreshold ? "YAWN" : "NORMAL"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TelemetryCharts;
