import React from "react";
import { AlertOctagon, RotateCcw } from "lucide-react";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("[Dashboard ErrorBoundary]", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-slate-900 border border-red-500/30 rounded-2xl p-6 shadow-2xl text-center">
            <div className="w-14 h-14 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center mx-auto mb-4">
              <AlertOctagon className="w-8 h-8 text-red-500" />
            </div>
            <h2 className="text-lg font-bold text-slate-100 mb-2">
              Dashboard Render Recovery
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              An unexpected render issue occurred while processing telemetry data. The system has safely contained the error.
            </p>
            <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-left font-mono text-[11px] text-red-400 mb-5 overflow-x-auto max-h-32">
              {this.state.error?.message || "Unknown client error"}
            </div>
            <button
              onClick={this.handleReset}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white text-xs font-bold px-4 py-2.5 rounded-xl shadow-lg cursor-pointer transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              Reload Dashboard
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
