import { useState, useRef } from "react";
import { Camera, CircleDot, Maximize2, Minimize2, AlertTriangle, ShieldAlert, Sparkles } from "lucide-react";

function CameraFeed({ running, metrics = {}, onRecalibrate }) {
  const [fullscreen, setFullscreen] = useState(false);
  const containerRef = useRef(null);
  const [imgError, setImgError] = useState(false);

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().then(() => setFullscreen(true)).catch(() => {});
    } else {
      document.exitFullscreen().then(() => setFullscreen(false)).catch(() => {});
    }
  };

  const statusStr = String(metrics?.status || "");
  const isCriticalDrowsy = statusStr === "CRITICAL_DROWSINESS" || statusStr === "DROWSY";
  const isDrowsyWarning = statusStr === "DROWSINESS_WARNING";
  const isDistracted = statusStr.startsWith("DISTRACTED") || statusStr === "DISTRACTED";
  const isCalibrating = statusStr.startsWith("CALIBRATING") || Boolean(metrics?.calibrating);
  const cameraStatusStr = String(metrics?.cameraStatus || "ready");

  return (
    <div
      ref={containerRef}
      className={`relative bg-slate-900 border ${
        isCriticalDrowsy
          ? "border-red-500 shadow-red-950/40 shadow-2xl"
          : isDrowsyWarning
          ? "border-amber-500 shadow-amber-950/40 shadow-xl"
          : isDistracted
          ? "border-orange-500 shadow-orange-950/40 shadow-xl"
          : "border-slate-800 shadow-xl"
      } rounded-2xl p-5 flex flex-col transition-all duration-300`}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Camera className="w-4 h-4 text-slate-400" />
          <h2 className="text-xs font-bold text-slate-300 uppercase tracking-widest">
            AI Driver Vision Stream
          </h2>
        </div>

        <div className="flex items-center gap-2">
          {/* Calibrate Pill */}
          {running && (
            <button
              onClick={onRecalibrate}
              title="Recalibrate resting face baseline"
              className="flex items-center gap-1 text-[11px] font-medium text-cyan-400 bg-cyan-950/50 hover:bg-cyan-900/60 border border-cyan-800/60 rounded-lg px-2.5 py-1 transition-colors cursor-pointer"
            >
              <Sparkles className="w-3 h-3" />
              Recalibrate
            </button>
          )}

          {/* Camera Status */}
          {running && (
            <span
              className={`flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-1 rounded-full border ${
                cameraStatusStr === "connected"
                  ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/30"
                  : cameraStatusStr === "reconnecting"
                  ? "text-amber-400 bg-amber-500/10 border-amber-500/30"
                  : "text-red-400 bg-red-500/10 border-red-500/30"
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  cameraStatusStr === "connected" ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
                }`}
              />
              {cameraStatusStr === "connected" ? "CAM ACTIVE" : cameraStatusStr.toUpperCase()}
            </span>
          )}

          {/* Live Badge */}
          {running && (
            <span className="flex items-center gap-1.5 text-[11px] font-bold text-red-400 bg-red-500/10 border border-red-500/30 rounded-full px-2.5 py-1">
              <CircleDot className="w-3 h-3 animate-ping" />
              LIVE {metrics?.fps ? `${Math.round(metrics.fps)} FPS` : ""}
            </span>
          )}

          {/* Fullscreen Toggle */}
          <button
            onClick={toggleFullscreen}
            className="text-slate-400 hover:text-slate-200 p-1.5 hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
            title="Toggle Fullscreen"
          >
            {fullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Video Canvas Container */}
      <div className="relative aspect-video w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-950 flex items-center justify-center">
        {running ? (
          <>
            <img
              src="http://127.0.0.1:8000/video_feed"
              alt="Live Driver Monitoring Feed"
              className="w-full h-full object-contain"
              onError={() => setImgError(true)}
              onLoad={() => setImgError(false)}
            />

            {imgError && (
              <div className="absolute inset-0 bg-slate-950 flex flex-col items-center justify-center gap-2 text-slate-400">
                <AlertTriangle className="w-8 h-8 text-amber-500 animate-bounce" />
                <span className="text-sm font-semibold">Connecting Video Stream...</span>
                <span className="text-xs text-slate-600">Camera feed initializing from backend</span>
              </div>
            )}

            {/* Dynamic Alert Banner */}
            {isCriticalDrowsy && (
              <div className="absolute top-3 left-4 right-4 bg-red-600/90 backdrop-blur-md border border-red-400 text-white px-4 py-2.5 rounded-xl shadow-2xl flex items-center justify-between animate-pulse">
                <div className="flex items-center gap-2.5">
                  <ShieldAlert className="w-5 h-5 text-white" />
                  <div>
                    <div className="text-xs font-black tracking-wider uppercase">
                      CRITICAL ALERT: SLEEPING / DROWSINESS DETECTED
                    </div>
                    <div className="text-[11px] text-red-100 font-hindi">
                      सावधान! आप सो रहे हैं! कृपया तुरंत ध्यान दें!
                    </div>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold bg-white/20 px-2.5 py-1 rounded-lg">
                  EAR: {Number(metrics?.ear || 0).toFixed(2)}
                </span>
              </div>
            )}

            {isDrowsyWarning && !isCriticalDrowsy && (
              <div className="absolute top-3 left-4 right-4 bg-amber-600/90 backdrop-blur-md border border-amber-400 text-white px-4 py-2.5 rounded-xl shadow-2xl flex items-center justify-between animate-pulse">
                <div className="flex items-center gap-2.5">
                  <AlertTriangle className="w-5 h-5 text-white" />
                  <div>
                    <div className="text-xs font-black tracking-wider uppercase">
                      DROWSINESS WARNING: PROLONGED EYE CLOSURE
                    </div>
                    <div className="text-[11px] text-amber-100 font-hindi">
                      चेतावनी! पलकें झपकने में देरी हो रही है!
                    </div>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold bg-white/20 px-2.5 py-1 rounded-lg">
                  EAR: {Number(metrics?.ear || 0).toFixed(2)}
                </span>
              </div>
            )}

            {isDistracted && !isCriticalDrowsy && !isDrowsyWarning && (
              <div className="absolute top-3 left-4 right-4 bg-orange-600/90 backdrop-blur-md border border-orange-400 text-white px-4 py-2.5 rounded-xl shadow-2xl flex items-center justify-between animate-bounce">
                <div className="flex items-center gap-2.5">
                  <AlertTriangle className="w-5 h-5 text-white" />
                  <div>
                    <div className="text-xs font-black tracking-wider uppercase">
                      DISTRACTION DETECTED: {statusStr.replace("DISTRACTED_", "")}
                    </div>
                    <div className="text-[11px] text-orange-100">
                      सावधान! फोन का इस्तेमाल न करें, सामने देखें!
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Calibration Banner */}
            {isCalibrating && (
              <div className="absolute bottom-4 left-4 bg-cyan-950/90 backdrop-blur-md border border-cyan-500/50 text-cyan-300 text-xs px-3.5 py-2 rounded-xl shadow-xl flex items-center gap-2">
                <Sparkles className="w-4 h-4 animate-spin text-cyan-400" />
                <span>Calibrating open-eye resting baseline... Keep looking straight</span>
              </div>
            )}
          </>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 p-8 text-center text-slate-500">
            <div className="w-16 h-16 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center">
              <Camera className="w-8 h-8 text-slate-600" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-300">Live Video Stream Standby</h3>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                Click "Start Safety Monitoring" below to activate camera capture, facial landmark tracking, and real-time fatigue analysis.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Footer Subsystem Status Pill Line */}
      <div className="grid grid-cols-4 gap-2 mt-3 pt-3 border-t border-slate-800/80 text-[11px]">
        <div className="flex items-center gap-1.5 text-slate-400">
          <span className={`w-2 h-2 rounded-full ${metrics?.faceDetected ? "bg-emerald-400" : "bg-slate-600"}`} />
          <span className="truncate">Face: {metrics?.faceDetected ? "Locked" : "Searching"}</span>
        </div>
        <div className="flex items-center gap-1.5 text-slate-400">
          <span className={`w-2 h-2 rounded-full ${!metrics?.isEyeClosed ? "bg-emerald-400" : "bg-red-400"}`} />
          <span className="truncate">Eyes: {metrics?.isEyeClosed ? "Closed" : "Open"}</span>
        </div>
        <div className="flex items-center gap-1.5 text-slate-400">
          <span className={`w-2 h-2 rounded-full ${!metrics?.isYawning ? "bg-emerald-400" : "bg-amber-400"}`} />
          <span className="truncate">Mouth: {metrics?.isYawning ? "Yawning" : "Normal"}</span>
        </div>
        <div className="flex items-center gap-1.5 text-slate-400">
          <span className={`w-2 h-2 rounded-full ${!metrics?.isPhoneDistracted ? "bg-emerald-400" : "bg-orange-400"}`} />
          <span className="truncate">Phone: {metrics?.isPhoneDistracted ? "Detected" : "None"}</span>
        </div>
      </div>
    </div>
  );
}

export default CameraFeed;
