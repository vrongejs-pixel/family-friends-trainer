import streamlit as st
from datetime import datetime
from services.progress_tracker import get_today_minutes
from services.storage import export_progress_json, import_progress_json


def render_dashboard(progress: dict):
    st.title("🇬🇧 MY ENGLISH — Метод Холмата")
    st.caption("Персональная система изучения английского для жизни и работы за границей")

    today_min = get_today_minutes(progress)
    goal_min = progress.get("daily_plan_minutes", 45)
    mistakes_open = sum(1 for m in progress.get("mistakes_log", []) if m.get("status") != "Исправлено")
    words_learned = sum(
        1 for w in progress.get("vocabulary_progress", {}).values() if w.get("status") == "Хорошо знаю"
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Текущий уровень", progress.get("overall_level", "Не определён").split(" ")[0])
    col2.metric("Сегодня занято", f"{today_min} / {goal_min} мин")
    col3.metric("Выучено слов", f"{words_learned}")
    col4.metric("Ошибки на разбор", f"{mistakes_open}")

    st.divider()

    if not progress.get("diagnostic_completed"):
        st.warning(
            "👋 **Первый шаг:** Вы ещё не прошли стартовую диагностику знаний. "
            "Пройдите её сейчас, чтобы система определила ваш уровень по навыкам и настроила программу."
        )
        if st.button("Начать диагностику знаний 🚀", type="primary"):
            st.session_state.current_page = "Диагностика"
            st.rerun()
    else:
        st.success(f"✅ Стартовая диагностика пройдена ({progress.get('diagnostic_date')}).")

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.subheader("📈 Уровень по 6 навыкам")
        skills = progress.get("skill_levels", {})
        labels = {
            "vocabulary": "Словарный запас",
            "grammar": "Грамматика",
            "reading": "Чтение",
            "listening": "Аудирование",
            "writing": "Письмо",
            "speaking": "Разговорная практика",
        }
        for key, title in labels.items():
            st.write(f"**{title}:** {skills.get(key, 'Не определён')}")

    with right_col:
        st.subheader("⏱ Рекомендуемый план на 45 минут")
        st.markdown(
            """
            * **10 мин** — Словарь (новые слова и перевод)
            * **10 мин** — Грамматика (теория и примеры)
            * **10 мин** — Упражнения и конструктор фраз
            * **10 мин** — Ситуации «Жизнь и работа» / Аудирование
            * **5 мин** — Работа над ошибками и повторение
            """
        )

    st.divider()

    with st.expander("💾 Резервное копирование и восстановление прогресса"):
        st.write(
            "Все результаты сохраняются автоматически. Чтобы гарантированно не потерять прогресс "
            "при обновлении сервера, периодически скачивайте резервную копию."
        )
        dl_col, ul_col = st.columns(2)
        with dl_col:
            backup_str = export_progress_json(progress)
            file_name = f"my_english_backup_{datetime.now().strftime('%Y%m%d')}.json"
            st.download_button(
                label="⬇️ Скачать резервную копию (.json)",
                data=backup_str,
                file_name=file_name,
                mime="application/json",
                use_container_width=True,
            )
        with ul_col:
            uploaded = st.file_uploader("⬆️ Восстановить из файла (.json)", type=["json"])
            if uploaded is not None:
                content = uploaded.read().decode("utf-8")
                ok, msg, restored = import_progress_json(content)
                if ok and restored:
                    st.session_state.progress = restored
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
