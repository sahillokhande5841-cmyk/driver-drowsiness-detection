import { Play, Square, Sparkles, SlidersHorizontal, BellRing, Volume2, VolumeX } from "lucide-react";

function ControlPanel({
  running,
  onStart,
  onStop,
  onRecalibrate,
  onOpenSettings,
  onTriggerTestAlert,
  audioMuted,
  onToggleMute,
}) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl p-5 flex flex-col gap-4">
      {/* Primary Execution Controls */}
      <div className="grid grid-cols-2 gap-3">
        {!running ? (
          <button
            onClick={onStart}
            className="col-span-2 flex items-center justify-center gap-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-sm py-3.5 px-4 rounded-xl shadow-lg shadow-emerald-950/50 cursor-pointer transition-all duration-200 active:scale-[0.98]"
          >
            <Play className="w-4 h-4 fill-white" />
            START SAFETY MONITORING
          </button>
        ) : (
          <button
            onClick={onStop}
            className="col-span-2 flex items-center justify-center gap-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-sm py-3.5 px-4 rounded-xl shadow-lg shadow-red-950/50 cursor-pointer transition-all duration-200 active:scale-[0.98]"
          >
            <Square className="w-4 h-4 fill-white" />
            STOP MONITORING
          </button>
        )}
      </div>

      {/* Auxiliary Action Buttons */}
      <div className="grid grid-cols-3 gap-2.5">
        {/* Recalibrate */}
        <button
          onClick={onRecalibrate}
          disabled={!running}
          className={`flex items-center justify-center gap-1.5 text-xs font-semibold py-2.5 px-3 rounded-xl border transition-all ${
            running
              ? "bg-slate-800/80 hover:bg-slate-700/80 text-cyan-400 border-cyan-500/30 cursor-pointer"
              : "bg-slate-950/40 text-slate-600 border-slate-800 cursor-not-allowed"
          }`}
          title="Recalibrate open-eye resting baseline"
        >
          <Sparkles className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">Calibrate</span>
        </button>

        {/* Audio Mute Toggle */}
        <button
          onClick={onToggleMute}
          className={`flex items-center justify-center gap-1.5 text-xs font-semibold py-2.5 px-3 rounded-xl border cursor-pointer transition-all ${
            audioMuted
              ? "bg-rose-500/10 border-rose-500/30 text-rose-400 hover:bg-rose-500/20"
              : "bg-slate-800/80 border-slate-700 text-slate-300 hover:bg-slate-700/80"
          }`}
          title={audioMuted ? "Unmute Voice Alarms" : "Mute Voice Alarms"}
        >
          {audioMuted ? (
            <>
              <VolumeX className="w-3.5 h-3.5 shrink-0" />
              <span>Muted</span>
            </>
          ) : (
            <>
              <Volume2 className="w-3.5 h-3.5 shrink-0" />
              <span>Voice ON</span>
            </>
          )}
        </button>

        {/* Test Alert */}
        <button
          onClick={onTriggerTestAlert}
          className="flex items-center justify-center gap-1.5 text-xs font-semibold py-2.5 px-3 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-amber-400 border border-amber-500/30 cursor-pointer transition-all"
          title="Test audio alert synthesis"
        >
          <BellRing className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">Test Alarm</span>
        </button>
      </div>

      {/* Settings Drawer Button */}
      <button
        onClick={onOpenSettings}
        className="w-full flex items-center justify-center gap-2 text-xs font-semibold py-2 px-3 rounded-xl bg-slate-950/60 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
      >
        <SlidersHorizontal className="w-3.5 h-3.5" />
        Configure Sensor Sensitivity & Audio
      </button>
    </div>
  );
}

export default ControlPanel;
