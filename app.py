import streamlit as st
from services.storage import load_progress
from services.progress_tracker import record_activity
from modules.dashboard import render_dashboard
from modules.diagnostic import render_diagnostic
from modules.vocabulary import (
    render_vocabulary_study,
    render_flashcards,
    render_vocabulary_test,
)

st.set_page_config(
    page_title="MY ENGLISH — Метод Холмата",
    page_icon="🇬🇧",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "progress" not in st.session_state:
    st.session_state.progress = load_progress()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Главная панель"

progress = st.session_state.progress

with st.sidebar:
    st.title("MY ENGLISH")
    st.caption("Метод изучения английского Холмата")
    st.divider()

    menu_items = [
        "Главная панель",
        "Диагностика",
        "Словарь",
        "Карточки",
        "Тест по словарю",
        "Грамматика (Этап 3)",
        "Глаголы (Этап 4)",
        "Жизнь и работа (Этап 5)",
        "Чтение (Этап 6)",
        "Аудирование и речь (Этап 7)",
        "Журнал ошибок",
    ]

    selected = st.radio(
        "Разделы обучения:",
        options=menu_items,
        index=menu_items.index(st.session_state.current_page)
        if st.session_state.current_page in menu_items
        else 0,
    )

    if selected != st.session_state.current_page:
        st.session_state.current_page = selected
        record_activity(progress, st.session_state, actions=1)
        st.rerun()

    st.divider()
    st.caption(f"Пользователь: **{progress.get('user_name', 'Холмат')}**")
    st.caption(f"Уровень: **{progress.get('overall_level', 'Не определён').split(' ')[0]}**")

page = st.session_state.current_page

if page == "Главная панель":
    render_dashboard(progress)

elif page == "Диагностика":
    render_diagnostic(progress)

elif page == "Словарь":
    render_vocabulary_study(progress)

elif page == "Карточки":
    render_flashcards(progress)

elif page == "Тест по словарю":
    render_vocabulary_test(progress)

elif page == "Журнал ошибок":
    st.header("📓 Журнал ошибок")
    mistakes = progress.get("mistakes_log", [])
    if not mistakes:
        st.info("Ошибок пока нет! Они будут автоматически записываться сюда при прохождении диагностики и упражнений.")
    else:
        for idx, m in enumerate(mistakes):
            with st.container(border=True):
                st.markdown(f"**{m['date']} | {m['topic']}**")
                st.write(f"Задание: {m['task']}")
                st.write(f"❌ Ваш ответ: `{m['user_answer']}` → ✅ Правильно: **`{m['correct_answer']}`**")
                st.caption(f"💡 Объяснение: {m['explanation']}")

else:
    st.header(f"🚧 Раздел «{page}»")
    st.info(
        "Этот модуль запланирован на следующий этап разработки. "
        "Сначала убедитесь, что уже готовые разделы работают стабильно."
    )
