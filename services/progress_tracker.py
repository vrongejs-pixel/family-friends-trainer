import time
from datetime import datetime
from services.storage import save_progress

MAX_IDLE_SECONDS = 300  # Пауза более 5 минут не засчитывается как активная учёба


def record_activity(progress: dict, session_state, actions: int = 1):
    """Фиксирует реальное активное время занятия без накрутки за открытую вкладку."""
    now = time.time()
    today_str = datetime.now().strftime("%Y-%m-%d")

    last_ts = getattr(session_state, "last_activity_ts", None)
    elapsed = 0
    if last_ts is not None:
        diff = now - last_ts
        if 0 < diff <= MAX_IDLE_SECONDS:
            elapsed = int(diff)

    session_state.last_activity_ts = now

    sessions = progress.setdefault("study_sessions", [])
    today_entry = next((s for s in sessions if s["date"] == today_str), None)

    if today_entry is None:
        today_entry = {
            "date": today_str,
            "started_at": datetime.now().strftime("%H:%M"),
            "last_active_at": datetime.now().strftime("%H:%M"),
            "active_seconds": elapsed,
            "actions_count": actions,
        }
        sessions.append(today_entry)
    else:
        today_entry["last_active_at"] = datetime.now().strftime("%H:%M")
        today_entry["active_seconds"] += elapsed
        today_entry["actions_count"] += actions

    save_progress(progress)


def get_today_minutes(progress: dict) -> int:
    """Возвращает количество активных минут занятий за сегодня."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    for s in progress.get("study_sessions", []):
        if s["date"] == today_str:
            return round(s.get("active_seconds", 0) / 60)
    return 0
