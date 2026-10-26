import { useEffect, useRef } from "react";

function VoiceAlertHandler({ activeAlert, audioMuted, language = "hi" }) {
  const lastAlertIdRef = useRef(null);

  useEffect(() => {
    if (!activeAlert || audioMuted) return;

    // Deduplicate against the same alert instance
    if (activeAlert.id === lastAlertIdRef.current) return;
    lastAlertIdRef.current = activeAlert.id;

    // Speak message using Web Speech API synthesis
    try {
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel(); // Stop ongoing speech

        const utteranceText =
          language === "hi" && activeAlert.messageHindi
            ? activeAlert.messageHindi
            : activeAlert.messageEnglish || activeAlert.message || "Warning";

        const utterance = new SpeechSynthesisUtterance(utteranceText);
        utterance.rate = 1.05;
        utterance.pitch = 1.1;
        utterance.lang = language === "hi" ? "hi-IN" : "en-US";

        // Try to pick an appropriate Hindi/English voice if available
        const voices = window.speechSynthesis.getVoices();
        const preferredVoice = voices.find(
          (v) =>
            v.lang.startsWith(language === "hi" ? "hi" : "en") &&
            (v.name.includes("Google") || v.name.includes("Natural") || v.default)
        );
        if (preferredVoice) {
          utterance.voice = preferredVoice;
        }

        window.speechSynthesis.speak(utterance);
      } else {
        // Fallback Web Audio synth beep
        playSynthesizerBeep();
      }
    } catch (err) {
      console.warn("[VoiceAlertHandler] Audio synthesis failed:", err);
    }
  }, [activeAlert, audioMuted, language]);

  return null; // Headless component
}

function playSynthesizerBeep() {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(880, audioCtx.currentTime); // A5 note
    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + 0.4);
  } catch (e) {
    // AudioContext blocked
  }
}

export default VoiceAlertHandler;
