import time
import os
import threading
from typing import Optional, Dict, Any, List
from app.config import (
    ALARM_SOUND,
    ALERT_MP3,
    WAKE_UP_MP3,
    ALERT_COOLDOWN_DROWSY,
    ALERT_COOLDOWN_YAWN,
    ALERT_COOLDOWN_PHONE,
    ALERT_COOLDOWN_HEAD
)

class AlertManager:
    """
    Manages alarm sounds, voice alerts (Hindi & English), alert cooldowns,
    and structured deduplicated event logs.
    """

    COOLDOWNS = {
        "CRITICAL_DROWSINESS": ALERT_COOLDOWN_DROWSY,
        "DROWSINESS_WARNING": ALERT_COOLDOWN_DROWSY,
        "YAWNING": ALERT_COOLDOWN_YAWN,
        "PHONE_DISTRACTION": ALERT_COOLDOWN_PHONE,
        "HEAD_DOWN": ALERT_COOLDOWN_HEAD,
    }

    MESSAGES = {
        "CRITICAL_DROWSINESS": {
            "hi": "सावधान! आप सो रहे हैं! तुरंत जागें!",
            "en": "Warning! Drowsiness detected! Wake up immediately!",
            "severity": "danger",
            "sound": WAKE_UP_MP3 if os.path.exists(WAKE_UP_MP3) else ALARM_SOUND
        },
        "DROWSINESS_WARNING": {
            "hi": "चेतावनी! पलकें झपकने में देरी हो रही है!",
            "en": "Caution! Prolonged eye closure detected!",
            "severity": "warning",
            "sound": ALERT_MP3 if os.path.exists(ALERT_MP3) else ALARM_SOUND
        },
        "YAWNING": {
            "hi": "चेतावनी! लगातार जम्हाई आ रही है! कृपया आराम करें!",
            "en": "Warning! Frequent yawning detected. Please take a break.",
            "severity": "warning",
            "sound": ALERT_MP3 if os.path.exists(ALERT_MP3) else ALARM_SOUND
        },
        "PHONE_DISTRACTION": {
            "hi": "सावधान! गाड़ी चलाते समय मोबाइल फोन का उपयोग न करें!",
            "en": "Warning! Mobile phone distraction detected! Eyes on the road!",
            "severity": "danger",
            "sound": ALERT_MP3 if os.path.exists(ALERT_MP3) else ALARM_SOUND
        },
        "HEAD_DOWN": {
            "hi": "सावधान! कृपया सामने देखें, सिर ऊपर रखें!",
            "en": "Warning! Head down posture detected! Look at the road!",
            "severity": "warning",
            "sound": ALERT_MP3 if os.path.exists(ALERT_MP3) else ALARM_SOUND
        }
    }

    def __init__(self):
        self.last_alert_times = {}
        self.active_alert: Optional[Dict[str, Any]] = None
        self.event_log: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.audio_enabled = True
        self.language = "hi"
        self._init_audio()

    def _init_audio(self):
        """Attempts to initialize local sound system."""
        self.pygame_available = False
        try:
            import pygame
            pygame.mixer.init()
            self.pygame_available = True
        except Exception:
            self.pygame_available = False

    def can_trigger(self, alert_type: str) -> bool:
        """Checks if cooldown period has elapsed for the given alert type."""
        now = time.time()
        last_time = self.last_alert_times.get(alert_type, 0.0)
        cooldown = self.COOLDOWNS.get(alert_type, 4.0)
        return (now - last_time) >= cooldown

    def trigger(self, alert_type: str, details: str = "") -> Optional[Dict[str, Any]]:
        """
        Triggers an alert if cooldown permits.
        Updates active_alert, logs deduplicated event, and plays audio.
        """
        if not self.can_trigger(alert_type):
            return None

        now = time.time()
        self.last_alert_times[alert_type] = now

        msg_info = self.MESSAGES.get(alert_type, {
            "hi": f"चेतावनी: {alert_type}",
            "en": f"Warning: {alert_type}",
            "severity": "warning",
            "sound": ALARM_SOUND
        })

        alert_data = {
            "id": f"{int(now * 1000)}",
            "type": alert_type,
            "severity": msg_info["severity"],
            "messageHindi": msg_info["hi"],
            "messageEnglish": msg_info["en"],
            "message": msg_info.get(self.language, msg_info["en"]),
            "details": details,
            "timestamp": now,
            "timeFormatted": time.strftime("%H:%M:%S")
        }

        with self.lock:
            self.active_alert = alert_data
            # Deduplicate and append to log
            self.event_log.insert(0, alert_data)
            if len(self.event_log) > 50:
                self.event_log.pop()

        if self.audio_enabled:
            threading.Thread(target=self._play_sound, args=(msg_info.get("sound"),), daemon=True).start()

        return alert_data

    def clear_active_alert(self):
        """Immediately clears active alert upon driver recovery."""
        with self.lock:
            self.active_alert = None

    def _play_sound(self, sound_path: Optional[str]):
        """Plays audio file locally using pygame or Windows native audio."""
        if not sound_path or not os.path.exists(sound_path):
            return

        try:
            if self.pygame_available:
                import pygame
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play()
            elif os.name == 'nt':
                import winsound
                if sound_path.endswith('.wav'):
                    winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"[AlertManager] Audio playback error: {e}")

    def get_active_alert(self) -> Optional[Dict[str, Any]]:
        """Returns the active alert if it occurred within the last 3.5 seconds."""
        with self.lock:
            if self.active_alert:
                if time.time() - self.active_alert["timestamp"] < 3.5:
                    return self.active_alert
                else:
                    self.active_alert = None
            return None

    def get_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns recent event log items."""
        with self.lock:
            return self.event_log[:limit]

    def set_language(self, lang: str):
        if lang in ("hi", "en"):
            self.language = lang

    def set_audio_enabled(self, enabled: bool):
        self.audio_enabled = enabled
