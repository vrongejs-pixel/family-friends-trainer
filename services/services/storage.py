import json
import os
from datetime import datetime
from copy import deepcopy

DATA_DIR = "data"
PROGRESS_FILE = os.path.join(DATA_DIR, "user_progress.json")

DEFAULT_PROGRESS = {
    "user_name": "Холмат",
    "created_at": "",
    "diagnostic_completed": False,
    "diagnostic_date": None,
    "diagnostic_raw_scores": {},
    "skill_levels": {
        "vocabulary": "Не определён",
        "grammar": "Не определён",
        "reading": "Не определён",
        "listening": "Не определён",
        "writing": "Не определён",
        "speaking": "Не определён",
    },
    "overall_level": "Не определён",
    "focus_areas": [],
    "vocabulary_progress": {},
    "grammar_progress": {},
    "mistakes_log": [],
    "study_sessions": [],
    "daily_plan_minutes": 45,
}


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_progress() -> dict:
    """Загружает прогресс пользователя или создаёт чистый профиль."""
    ensure_data_dir()
    if not os.path.exists(PROGRESS_FILE):
        data = deepcopy(DEFAULT_PROGRESS)
        data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_progress(data)
        return data

    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        merged = deepcopy(DEFAULT_PROGRESS)
        for key, value in loaded.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key].update(value)
            else:
                merged[key] = value
        return merged
    except Exception:
        backup = deepcopy(DEFAULT_PROGRESS)
        backup["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return backup


def save_progress(data: dict) -> bool:
    """Сохраняет прогресс в локальный JSON."""
    ensure_data_dir()
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения прогресса: {e}")
        return False


def export_progress_json(data: dict) -> str:
    """Возвращает строку JSON для скачивания резервной копии."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def import_progress_json(json_str: str) -> tuple[bool, str, dict | None]:
    """Проверняет и загружает резервную копию из JSON-строки."""
    try:
        parsed = json.loads(json_str)
        if not isinstance(parsed, dict) or "skill_levels" not in parsed:
            return False, "Файл не соответствует формату MY ENGLISH.", None
        merged = deepcopy(DEFAULT_PROGRESS)
        merged.update(parsed)
        save_progress(merged)
        return True, "Резервная копия успешно восстановлена!", merged
    except json.JSONDecodeError:
        return False, "Ошибка чтения файла: повреждённый JSON.", None
