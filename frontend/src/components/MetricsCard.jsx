import { Eye, Smile, Compass, Flame, ShieldAlert, Sparkles } from "lucide-react";

function MetricsCard({ metrics = {} }) {
  const ear = Number(metrics?.ear || 0);
  const earThresh = Number(metrics?.earThreshold || 0.20);
  const mar = Number(metrics?.mar || 0);
  const marThresh = Number(metrics?.marThreshold || 0.52);
  const pitch = Number(metrics?.pitch || 0);
  const yaw = Number(metrics?.yaw || 0);
  const roll = Number(metrics?.roll || 0);
  const blinks = Number(metrics?.blinkCount || 0);
  const yawns = Number(metrics?.yawnCount || 0);
  const fatigueScore = Number(metrics?.fatigueScore || 0);

  const earHealth = ear >= earThresh ? "good" : "danger";
  const marHealth = mar <= marThresh ? "good" : "warning";

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
      {/* 1. Eye Aspect Ratio (EAR) */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-bold uppercase tracking-wider">Eye Aperture (EAR)</span>
          <Eye className={`w-4 h-4 ${earHealth === "good" ? "text-emerald-400" : "text-red-400 animate-pulse"}`} />
        </div>
        <div className="flex items-baseline gap-2">
          <span className={`text-2xl font-mono font-black ${earHealth === "good" ? "text-emerald-400" : "text-red-400"}`}>
            {ear.toFixed(2)}
          </span>
          <span className="text-xs font-mono text-slate-500">/ thresh {earThresh.toFixed(2)}</span>
        </div>
        <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div
            className={`h-full transition-all duration-200 ${earHealth === "good" ? "bg-emerald-400" : "bg-red-500"}`}
            style={{ width: `${Math.min(100, Math.max(0, (ear / 0.40) * 100))}%` }}
          />
        </div>
      </div>

      {/* 2. Mouth Aspect Ratio (MAR) */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-bold uppercase tracking-wider">Mouth Opening (MAR)</span>
          <Smile className={`w-4 h-4 ${marHealth === "good" ? "text-cyan-400" : "text-amber-400 animate-bounce"}`} />
        </div>
        <div className="flex items-baseline gap-2">
          <span className={`text-2xl font-mono font-black ${marHealth === "good" ? "text-cyan-400" : "text-amber-400"}`}>
            {mar.toFixed(2)}
          </span>
          <span className="text-xs font-mono text-slate-500">/ thresh {marThresh.toFixed(2)}</span>
        </div>
        <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
          <div
            className={`h-full transition-all duration-200 ${marHealth === "good" ? "bg-cyan-400" : "bg-amber-400"}`}
            style={{ width: `${Math.min(100, Math.max(0, (mar / 0.80) * 100))}%` }}
          />
        </div>
      </div>

      {/* 3. 3D Head Orientation */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-bold uppercase tracking-wider">Head Orientation</span>
          <Compass className="w-4 h-4 text-indigo-400" />
        </div>
        <div className="grid grid-cols-3 gap-1 font-mono text-center">
          <div>
            <div className="text-[10px] text-slate-500">PITCH</div>
            <div className={`text-sm font-bold ${Math.abs(pitch) > 18 ? "text-amber-400" : "text-slate-200"}`}>
              {pitch > 0 ? `+${pitch.toFixed(0)}` : pitch.toFixed(0)}°
            </div>
          </div>
          <div>
            <div className="text-[10px] text-slate-500">YAW</div>
            <div className={`text-sm font-bold ${Math.abs(yaw) > 25 ? "text-amber-400" : "text-slate-200"}`}>
              {yaw > 0 ? `+${yaw.toFixed(0)}` : yaw.toFixed(0)}°
            </div>
          </div>
          <div>
            <div className="text-[10px] text-slate-500">ROLL</div>
            <div className="text-sm font-bold text-slate-200">
              {roll > 0 ? `+${roll.toFixed(0)}` : roll.toFixed(0)}°
            </div>
          </div>
        </div>
        <div className="text-[10px] text-slate-500 mt-1 truncate">
          Posture: {Math.abs(pitch) > 18 ? "Pitch Alert" : "Upright Neutral"}
        </div>
      </div>

      {/* 4. Cumulative Events (Blinks / Yawns) */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-lg">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-[11px] font-bold uppercase tracking-wider">Session Counters</span>
          <Flame className="w-4 h-4 text-orange-400" />
        </div>
        <div className="flex items-center justify-around">
          <div className="text-center">
            <span className="text-xl font-mono font-black text-slate-200">{blinks}</span>
            <div className="text-[10px] uppercase tracking-wider text-slate-500">Blinks</div>
          </div>
          <div className="h-8 w-px bg-slate-800" />
          <div className="text-center">
            <span className={`text-xl font-mono font-black ${yawns > 3 ? "text-amber-400" : "text-slate-200"}`}>
              {yawns}
            </span>
            <div className="text-[10px] uppercase tracking-wider text-slate-500">Yawns</div>
          </div>
        </div>
        <div className="text-[10px] text-slate-500 text-center mt-1">
          Fatigue Score: <span className="font-mono font-bold text-amber-400">{fatigueScore.toFixed(1)}/10</span>
        </div>
      </div>
    </div>
  );
}

export default MetricsCard;
