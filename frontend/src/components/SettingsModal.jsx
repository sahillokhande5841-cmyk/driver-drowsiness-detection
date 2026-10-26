import { useState } from "react";
import { X, Sliders, Volume2, Globe, Sparkles } from "lucide-react";

function SettingsModal({
  isOpen,
  onClose,
  settings = {},
  onSave,
  onTriggerTestAlert,
}) {
  if (!isOpen) return null;

  const [earThresh, setEarThresh] = useState(settings.earThreshold ?? 0.20);
  const [marThresh, setMarThresh] = useState(settings.marThreshold ?? 0.52);
  const [closureDuration, setClosureDuration] = useState(settings.closureDuration ?? 1.2);
  const [language, setLanguage] = useState(settings.language ?? "hi");
  const [volume, setVolume] = useState(settings.volume ?? 80);

  const handleSave = () => {
    if (onSave) {
      onSave({
        earThreshold: Number(earThresh),
        marThreshold: Number(marThresh),
        closureDuration: Number(closureDuration),
        language,
        volume: Number(volume),
      });
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6 text-slate-200">
        {/* Header */}
        <div className="flex items-center justify-between mb-5 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-cyan-400" />
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-100">
              Detector Sensitivity & Voice
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Sliders */}
        <div className="space-y-4 text-xs">
          {/* EAR Threshold */}
          <div>
            <div className="flex justify-between font-semibold mb-1">
              <span className="text-slate-300">Eye Closure Threshold (EAR)</span>
              <span className="font-mono text-cyan-400">{Number(earThresh).toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.14"
              max="0.28"
              step="0.01"
              value={earThresh}
              onChange={(e) => setEarThresh(e.target.value)}
              className="w-full accent-cyan-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
              <span>0.14 (Low sensitivity)</span>
              <span>0.28 (High sensitivity)</span>
            </div>
          </div>

          {/* MAR Threshold */}
          <div>
            <div className="flex justify-between font-semibold mb-1">
              <span className="text-slate-300">Yawn Ratio Threshold (MAR)</span>
              <span className="font-mono text-cyan-400">{Number(marThresh).toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.40"
              max="0.70"
              step="0.02"
              value={marThresh}
              onChange={(e) => setMarThresh(e.target.value)}
              className="w-full accent-cyan-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
              <span>0.40 (Sensitive)</span>
              <span>0.70 (Deep yawns only)</span>
            </div>
          </div>

          {/* Eye Closure Duration */}
          <div>
            <div className="flex justify-between font-semibold mb-1">
              <span className="text-slate-300">Drowsiness Warning Time</span>
              <span className="font-mono text-cyan-400">{Number(closureDuration).toFixed(1)}s</span>
            </div>
            <input
              type="range"
              min="0.8"
              max="2.5"
              step="0.1"
              value={closureDuration}
              onChange={(e) => setClosureDuration(e.target.value)}
              className="w-full accent-cyan-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
              <span>0.8s (Fast alarm)</span>
              <span>2.5s (Tolerant)</span>
            </div>
          </div>

          {/* Language Selection */}
          <div className="pt-2 border-t border-slate-800">
            <span className="font-semibold text-slate-300 block mb-2">Voice Alert Language</span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setLanguage("hi")}
                className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
                  language === "hi"
                    ? "bg-cyan-500/10 border-cyan-500/50 text-cyan-300"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-800"
                }`}
              >
                🇮🇳 Hindi (हिंदी)
              </button>
              <button
                type="button"
                onClick={() => setLanguage("en")}
                className={`py-2 px-3 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
                  language === "en"
                    ? "bg-cyan-500/10 border-cyan-500/50 text-cyan-300"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:bg-slate-800"
                }`}
              >
                🇺🇸 English
              </button>
            </div>
          </div>

          {/* Volume Slider */}
          <div>
            <div className="flex justify-between font-semibold mb-1">
              <span className="text-slate-300">Alarm Audio Volume</span>
              <span className="font-mono text-cyan-400">{volume}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={(e) => setVolume(e.target.value)}
              className="w-full accent-cyan-500 cursor-pointer"
            />
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between gap-3 mt-6 pt-4 border-t border-slate-800">
          <button
            type="button"
            onClick={onTriggerTestAlert}
            className="text-xs font-semibold text-amber-400 hover:text-amber-300 underline cursor-pointer"
          >
            Play Test Alarm
          </button>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-950/50 transition-colors cursor-pointer"
            >
              Apply Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsModal;
