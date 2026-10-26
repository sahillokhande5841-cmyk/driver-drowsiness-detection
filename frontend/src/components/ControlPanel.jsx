import { Play, Square } from "lucide-react";

function ControlPanel({ startDetector, stopDetector }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-lg p-6">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
        Controls
      </h2>

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          className="flex-1 flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-semibold py-2.5 rounded-lg transition-colors duration-150 shadow-sm"
          onClick={startDetector}
        >
          <Play className="w-4 h-4" />
          Start
        </button>

        <button
          className="flex-1 flex items-center justify-center gap-2 bg-red-600 hover:bg-red-500 active:bg-red-700 text-white font-semibold py-2.5 rounded-lg transition-colors duration-150 shadow-sm"
          onClick={stopDetector}
        >
          <Square className="w-4 h-4" />
          Stop
        </button>
      </div>
    </div>
  );
}

export default ControlPanel;