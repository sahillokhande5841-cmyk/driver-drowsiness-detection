import { Eye, Smile, Compass, RotateCcw, MessageCircle } from "lucide-react";

function MetricsCard({ metrics }) {
  const items = [
    { label: "EAR", value: (metrics.ear ?? 0).toFixed(2), Icon: Eye },
    { label: "MAR", value: (metrics.mar ?? 0).toFixed(2), Icon: Smile },
    { label: "Pitch", value: `${(metrics.pitch ?? 0).toFixed(1)}°`, Icon: Compass },
    { label: "Blinks", value: metrics.blinkCount ?? 0, Icon: RotateCcw },
    { label: "Yawns", value: metrics.yawnCount ?? 0, Icon: MessageCircle },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-lg p-6 h-full">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
        Live Metrics
      </h2>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {items.map(({ label, value, Icon }) => (
          <div
            key={label}
            className="flex flex-col gap-1 rounded-lg border border-slate-800 bg-slate-800/40 px-3 py-3 hover:border-slate-700 transition-colors duration-150"
          >
            <div className="flex items-center gap-1.5 text-slate-500">
              <Icon className="w-3.5 h-3.5" />
              <span className="text-xs uppercase tracking-wide">{label}</span>
            </div>
            <span className="text-lg font-mono font-semibold text-slate-100">
              {value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MetricsCard;