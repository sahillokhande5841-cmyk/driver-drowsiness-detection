import { Camera, CircleDot } from "lucide-react";

function CameraFeed({ running }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-lg p-6 h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
          Camera Feed
        </h2>
        {running && (
          <span className="flex items-center gap-1.5 text-xs font-semibold text-red-400 bg-red-500/10 border border-red-500/30 rounded-full px-2.5 py-1">
            <CircleDot className="w-3 h-3 animate-pulse" />
            LIVE
          </span>
        )}
      </div>

      <div className="aspect-video w-full overflow-hidden rounded-lg border border-slate-800 bg-slate-950">
        {running ? (
          <img
            src="http://127.0.0.1:8000/video_feed"
            alt="Camera Feed"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="h-full flex flex-col items-center justify-center gap-2 text-slate-600">
            <Camera className="w-10 h-10" />
            <span className="text-sm font-medium">Camera Stopped</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default CameraFeed;