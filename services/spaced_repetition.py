from datetime import datetime, timedelta


STATUS_NEW = "Новое слово"
STATUS_FAMILIAR = "Знакомое слово"
STATUS_REPEAT = "Нужно повторить"
STATUS_CONFUSED = "Часто путаю"
STATUS_KNOWN = "Хорошо знаю"


def get_word_state(progress: dict, word_id: str) -> dict:
    """Возвращает текущее состояние изучения слова из профиля пользователя."""
    vocab_prog = progress.setdefault("vocabulary_progress", {})
    if word_id not in vocab_prog:
        vocab_prog[word_id] = {
            "status": STATUS_NEW,
            "correct_streak": 0,
            "total_correct": 0,
            "total_wrong": 0,
            "interval_days": 0,
            "next_review": datetime.now().strftime("%Y-%m-%d"),
            "last_practiced": None,
            "modes_passed": [],
        }
    return vocab_prog[word_id]


def mark_word_studied(progress: dict, word_id: str):
    """Переводит слово из 'Новое слово' в 'Знакомое слово' после первичного изучения."""
    state = get_word_state(progress, word_id)
    if state["status"] == STATUS_NEW:
        state["status"] = STATUS_FAMILIAR
        state["last_practiced"] = datetime.now().strftime("%Y-%m-%d %H:%M")


def update_word_review(progress: dict, word_id: str, is_correct: bool, mode_name: str) -> dict:
    """
    Обновляет статистику слова по правилам метода Холмата:
    - не считает слово выученным после 1 правильного ответа;
    - учитывает успешные вспоминания в разных режимах и интервалы.
    """
    state = get_word_state(progress, word_id)
    now = datetime.now()
    state["last_practiced"] = now.strftime("%Y-%m-%d %H:%M")

    if is_correct:
        state["total_correct"] += 1
        state["correct_streak"] += 1

        modes = set(state.get("modes_passed", []))
        modes.add(mode_name)
        state["modes_passed"] = list(modes)

        # Рассчитываем следующий интервал повторения (в днях)
        streak = state["correct_streak"]
        if streak == 1:
            interval = 1
        elif streak == 2:
            interval = 3
        elif streak == 3:
            interval = 7
        else:
            interval = min(state.get("interval_days", 7) * 2, 60)

        state["interval_days"] = interval
        state["next_review"] = (now + timedelta(days=interval)).strftime("%Y-%m-%d")

        # Статус 'Хорошо знаю' даётся только после 3+ верных ответов подряд и минимум в 2 разных режимах
        if streak >= 3 and len(state["modes_passed"]) >= 2:
            state["status"] = STATUS_KNOWN
        else:
            state["status"] = STATUS_FAMILIAR
    else:
        state["total_wrong"] += 1
        state["correct_streak"] = 0
        state["interval_days"] = 0
        state["next_review"] = now.strftime("%Y-%m-%d")

        if state["total_wrong"] >= 2:
            state["status"] = STATUS_CONFUSED
        else:
            state["status"] = STATUS_REPEAT

    return state


def is_due_for_review(state: dict) -> bool:
    """Проверяет, пора ли повторять слово сегодня."""
    if state.get("status") == STATUS_NEW:
        return False
    next_rev = state.get("next_review")
    if not next_rev:
        return True
    today_str = datetime.now().strftime("%Y-%m-%d")
    return next_rev <= today_str
