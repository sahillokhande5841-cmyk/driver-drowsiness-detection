import { ShieldAlert, AlertTriangle, Smartphone, Compass, Clock, CheckCircle2 } from "lucide-react";

function EventLogCard({ events = [] }) {
  const getIcon = (type = "") => {
    switch (type) {
      case "CRITICAL_DROWSINESS":
      case "DROWSINESS":
        return <ShieldAlert className="w-4 h-4 text-red-400 shrink-0" />;
      case "DROWSINESS_WARNING":
      case "YAWNING":
        return <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />;
      case "PHONE_DISTRACTION":
        return <Smartphone className="w-4 h-4 text-orange-400 shrink-0" />;
      case "HEAD_DOWN":
        return <Compass className="w-4 h-4 text-orange-400 shrink-0" />;
      default:
        return <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />;
    }
  };

  const getBadgeStyle = (severity = "") => {
    switch (severity) {
      case "danger":
        return "bg-red-500/10 border-red-500/30 text-red-400";
      case "warning":
        return "bg-amber-500/10 border-amber-500/30 text-amber-400";
      default:
        return "bg-slate-800 border-slate-700 text-slate-300";
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl p-5 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-400" />
          <h2 className="text-xs font-bold text-slate-300 uppercase tracking-widest">
            Safety Event Audit Log
          </h2>
        </div>
        <span className="text-[11px] font-mono text-slate-500">
          {events.length} Recorded
        </span>
      </div>

      {/* Events List */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 max-h-[360px] custom-scrollbar">
        {events.length === 0 ? (
          <div className="h-44 flex flex-col items-center justify-center text-slate-600 gap-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-600/50" />
            <span className="text-xs font-medium">No safety alerts triggered yet</span>
            <span className="text-[11px] text-slate-600">Events will record automatically</span>
          </div>
        ) : (
          events.map((evt, idx) => (
            <div
              key={evt.id || idx}
              className="bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 rounded-xl p-3 flex items-start gap-3 transition-colors"
            >
              <div className="mt-0.5">{getIcon(evt.type)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2 mb-0.5">
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider ${getBadgeStyle(
                      evt.severity
                    )}`}
                  >
                    {evt.type?.replace("_", " ")}
                  </span>
                  <span className="text-[10px] font-mono text-slate-500">
                    {evt.timeFormatted || new Date(evt.timestamp * 1000).toLocaleTimeString()}
                  </span>
                </div>
                <div className="text-xs font-semibold text-slate-200 truncate">
                  {evt.messageEnglish || evt.message}
                </div>
                {evt.messageHindi && (
                  <div className="text-[11px] text-amber-300/80 font-hindi truncate">
                    {evt.messageHindi}
                  </div>
                )}
                {evt.details && (
                  <div className="text-[10px] text-slate-500 mt-0.5 truncate">
                    {evt.details}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default EventLogCard;
