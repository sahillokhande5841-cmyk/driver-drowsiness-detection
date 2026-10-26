import { CheckCircle2, AlertTriangle, AlertOctagon, Loader2 } from "lucide-react";

function StatusCard({ metrics }) {
  const statusConfig = {
    NORMAL: {
      text: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/30",
      dot: "bg-emerald-400",
      Icon: CheckCircle2,
    },
    TIRED: {
      text: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/30",
      dot: "bg-amber-400",
      Icon: AlertTriangle,
    },
    DROWSY: {
      text: "text-red-500",
      bg: "bg-red-500/10",
      border: "border-red-500/30",
      dot: "bg-red-500",
      Icon: AlertOctagon,
    },
    INITIALIZING: {
      text: "text-slate-400",
      bg: "bg-slate-500/10",
      border: "border-slate-500/30",
      dot: "bg-slate-400",
      Icon: Loader2,
    },
  };

  const config = statusConfig[metrics.status] || statusConfig.INITIALIZING;
  const { text, bg, border, dot, Icon } = config;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-lg p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
          Driver Status
        </h2>
        <span className="relative flex h-2.5 w-2.5">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${dot} opacity-75`}></span>
          <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${dot}`}></span>
        </span>
      </div>

      <div className={`flex items-center gap-3 rounded-lg border ${border} ${bg} px-4 py-3 mt-auto`}>
        <Icon className={`w-6 h-6 ${text} ${metrics.status === "INITIALIZING" ? "animate-spin" : ""}`} />
        <span className={`text-2xl font-bold tracking-tight ${text}`}>
          {metrics.status}
        </span>
      </div>

      <p className="text-slate-500 text-sm mt-4 font-mono">
        Fatigue Score{" "}
        <span className="text-slate-300 font-semibold">
          {(metrics.fatigueScore ?? 0).toFixed(1)}
        </span>
      </p>
    </div>
  );
}

export default StatusCard;