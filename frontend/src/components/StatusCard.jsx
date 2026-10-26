import {
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  UserX,
  Smartphone,
  Eye,
  Smile,
  Compass,
  Sparkles,
  PauseCircle,
  Loader2,
} from "lucide-react";

function StatusCard({ metrics = {}, running }) {
  const statusConfig = {
    NORMAL: {
      label: "NORMAL & ATTENTIVE",
      subtext: "Driver eyes open, posture upright, road attentive",
      text: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/30",
      progressBg: "bg-emerald-400",
      dot: "bg-emerald-400",
      Icon: CheckCircle2,
    },
    FATIGUE_WARNING: {
      label: "FATIGUE WARNING",
      subtext: "Elevated blinks or yawns detected. Caution recommended",
      text: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/30",
      progressBg: "bg-amber-400",
      dot: "bg-amber-400",
      Icon: AlertTriangle,
    },
    TIRED: {
      label: "FATIGUE / TIRED",
      subtext: "Elevated blinks or yawns detected. Caution recommended",
      text: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/30",
      progressBg: "bg-amber-400",
      dot: "bg-amber-400",
      Icon: AlertTriangle,
    },
    DROWSINESS_WARNING: {
      label: "DROWSINESS WARNING",
      subtext: "Prolonged eye closure detected! Stay alert!",
      text: "text-amber-500",
      bg: "bg-amber-500/15",
      border: "border-amber-500/40",
      progressBg: "bg-amber-500",
      dot: "bg-amber-500",
      Icon: AlertTriangle,
    },
    CRITICAL_DROWSINESS: {
      label: "CRITICAL: SLEEPING / DROWSY",
      subtext: "CRITICAL: Severe eye closure! Wake up immediately!",
      text: "text-red-500",
      bg: "bg-red-500/15",
      border: "border-red-500/40",
      progressBg: "bg-red-500",
      dot: "bg-red-500",
      Icon: AlertOctagon,
    },
    DROWSY: {
      label: "DROWSY / SLEEPING",
      subtext: "CRITICAL: Prolonged eye closure! Audio alarm active!",
      text: "text-red-500",
      bg: "bg-red-500/15",
      border: "border-red-500/40",
      progressBg: "bg-red-500",
      dot: "bg-red-500",
      Icon: AlertOctagon,
    },
    DISTRACTED: {
      label: "DRIVER DISTRACTED",
      subtext: "Eyes off road or distracted posture detected",
      text: "text-orange-400",
      bg: "bg-orange-500/10",
      border: "border-orange-500/30",
      progressBg: "bg-orange-400",
      dot: "bg-orange-400",
      Icon: AlertTriangle,
    },
    DISTRACTED_PHONE: {
      label: "MOBILE DISTRACTION",
      subtext: "Cell phone detected in driver view. Eyes off road",
      text: "text-orange-400",
      bg: "bg-orange-500/10",
      border: "border-orange-500/30",
      progressBg: "bg-orange-400",
      dot: "bg-orange-400",
      Icon: Smartphone,
    },
    DISTRACTED_HEAD_DOWN: {
      label: "HEAD DOWN POSTURE",
      subtext: "Driver head pitched downward for extended period",
      text: "text-orange-400",
      bg: "bg-orange-500/10",
      border: "border-orange-500/30",
      progressBg: "bg-orange-400",
      dot: "bg-orange-400",
      Icon: Compass,
    },
    CALIBRATING: {
      label: "CALIBRATING BASELINE",
      subtext: "Measuring driver resting EAR and head angle (5s)",
      text: "text-cyan-400",
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/30",
      progressBg: "bg-cyan-400",
      dot: "bg-cyan-400",
      Icon: Sparkles,
    },
    INITIALIZING: {
      label: "INITIALIZING SENSORS",
      subtext: "Starting video stream and biometric detection",
      text: "text-cyan-400",
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/30",
      progressBg: "bg-cyan-400",
      dot: "bg-cyan-400",
      Icon: Loader2,
    },
    CAMERA_ERROR: {
      label: "CAMERA ERROR",
      subtext: "Video feed unavailable. Check connection or privacy permissions",
      text: "text-red-400",
      bg: "bg-red-500/10",
      border: "border-red-500/30",
      progressBg: "bg-red-400",
      dot: "bg-red-400",
      Icon: AlertTriangle,
    },
    NO_FACE: {
      label: "NO FACE DETECTED",
      subtext: "Driver face not visible in webcam view",
      text: "text-slate-400",
      bg: "bg-slate-800/40",
      border: "border-slate-700",
      progressBg: "bg-slate-500",
      dot: "bg-slate-500",
      Icon: UserX,
    },
    STOPPED: {
      label: "MONITORING IDLE",
      subtext: "Start the detector to begin real-time safety monitoring",
      text: "text-slate-500",
      bg: "bg-slate-800/20",
      border: "border-slate-800",
      progressBg: "bg-slate-700",
      dot: "bg-slate-600",
      Icon: PauseCircle,
    },
  };

  const statusStr = String(metrics?.status || "NORMAL");
  const rawStatus = running ? (statusStr.startsWith("CALIBRATING") ? "CALIBRATING" : statusStr) : "STOPPED";
  const config = statusConfig[rawStatus] || statusConfig.NORMAL;
  const { label, subtext, text, bg, border, dot, progressBg, Icon } = config;
  const StatusIcon = Icon || CheckCircle2;

  const score = Number(metrics?.fatigueScore || 0);
  const scorePercent = Math.min(100, Math.max(0, (score / 10.0) * 100));

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl p-6 h-full flex flex-col justify-between">
      {/* Card Header */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">
            Driver Safety Status
          </span>
          <span className="relative flex h-3 w-3">
            {running && (
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${dot} opacity-75`} />
            )}
            <span className={`relative inline-flex rounded-full h-3 w-3 ${dot}`} />
          </span>
        </div>

        {/* Status Hero Box */}
        <div className={`rounded-xl border ${border} ${bg} p-4 transition-all duration-300`}>
          <div className="flex items-start gap-3">
            <StatusIcon
              className={`w-7 h-7 ${text} mt-0.5 shrink-0 ${
                rawStatus === "CALIBRATING" || rawStatus === "INITIALIZING"
                  ? "animate-spin"
                  : rawStatus.includes("DROWSY")
                  ? "animate-pulse"
                  : ""
              }`}
            />
            <div>
              <h2 className={`text-base font-black tracking-wider ${text}`}>{label}</h2>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">{subtext}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Fatigue Score Progress Gauge */}
      <div className="mt-5 pt-4 border-t border-slate-800/80">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="font-semibold text-slate-300">Driver Fatigue Level</span>
          <span className="font-mono font-bold text-slate-200">
            {score.toFixed(1)} <span className="text-slate-500 font-normal">/ 10.0</span>
          </span>
        </div>

        {/* Score Bar */}
        <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden p-0.5 border border-slate-700/50">
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              score >= 7.0
                ? "bg-red-500 shadow-red-500/50 shadow-md"
                : score >= 4.0
                ? "bg-amber-400 shadow-amber-400/50 shadow-md"
                : "bg-emerald-400 shadow-emerald-400/50 shadow-md"
            }`}
            style={{ width: `${scorePercent}%` }}
          />
        </div>

        <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1.5">
          <span>0.0 (Alert)</span>
          <span>4.0 (Tired)</span>
          <span>7.0+ (Drowsy)</span>
        </div>
      </div>

      {/* Status Matrix Badges */}
      <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-800/80">
        <div className="bg-slate-950/60 rounded-lg p-2 text-center border border-slate-800">
          <div className="text-[10px] text-slate-500 uppercase font-semibold">Blink State</div>
          <div
            className={`text-xs font-bold font-mono mt-0.5 ${
              metrics?.isEyeClosed ? "text-red-400 animate-pulse" : "text-emerald-400"
            }`}
          >
            {metrics?.isEyeClosed ? "CLOSED" : "OPEN"}
          </div>
        </div>

        <div className="bg-slate-950/60 rounded-lg p-2 text-center border border-slate-800">
          <div className="text-[10px] text-slate-500 uppercase font-semibold">Yawn State</div>
          <div
            className={`text-xs font-bold font-mono mt-0.5 ${
              metrics?.isYawning ? "text-amber-400 animate-bounce" : "text-slate-300"
            }`}
          >
            {metrics?.isYawning ? "YAWNING" : "RESTING"}
          </div>
        </div>

        <div className="bg-slate-950/60 rounded-lg p-2 text-center border border-slate-800">
          <div className="text-[10px] text-slate-500 uppercase font-semibold">Phone AI</div>
          <div
            className={`text-xs font-bold font-mono mt-0.5 ${
              metrics?.isPhoneDistracted ? "text-orange-400 animate-pulse" : "text-slate-300"
            }`}
          >
            {metrics?.isPhoneDistracted ? "DETECTED" : "CLEAR"}
          </div>
        </div>
      </div>
    </div>
  );
}

export default StatusCard;
