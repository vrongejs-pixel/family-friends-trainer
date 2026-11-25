import streamlit as st
from services.storage import load_progress, save_progress
from services.progress_tracker import record_activity
from services.gemini_coach import render_gemini_practice_lab, ask_gemini
from services.speech import get_audio_bytes
from modules.dashboard import render_dashboard
from modules.diagnostic import render_diagnostic
from modules.vocabulary import (
    render_vocabulary_study,
    render_flashcards,
    render_vocabulary_test,
)
from modules.grammar import render_grammar

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


def _render_verbs_stage(prog: dict):
    st.header("⚡ Глаголы (Этап 4)")
    st.caption("Отрабатывай формы глаголов, времена и неправильные глаголы в готовом плане и безлимитно через Gemini.")

    base_verbs = [
        {"base": "go", "past": "went", "participle": "gone", "ru": "идти / ехать"},
        {"base": "come", "past": "came", "participle": "come", "ru": "приходить / приезжать"},
        {"base": "get", "past": "got", "participle": "got / gotten", "ru": "получать / добираться"},
        {"base": "take", "past": "took", "participle": "taken", "ru": "брать / занимать (время)"},
        {"base": "make", "past": "made", "participle": "made", "ru": "делать / создавать"},
        {"base": "do", "past": "did", "participle": "done", "ru": "делать / выполнять"},
        {"base": "say", "past": "said", "participle": "said", "ru": "сказать"},
        {"base": "tell", "past": "told", "participle": "told", "ru": "рассказать / сказать кому-то"},
        {"base": "find", "past": "found", "participle": "found", "ru": "находить"},
        {"base": "work", "past": "worked", "participle": "worked", "ru": "работать"},
    ]

    with st.expander("📋 Базовая таблица частых глаголов (опора)", expanded=True):
        st.table(
            [
                {
                    "Начальная (V1)": v["base"],
                    "Прошедшее (V2)": v["past"],
                    "Причастие (V3)": v["participle"],
                    "Перевод": v["ru"],
                }
                for v in base_verbs
            ]
        )

    st.divider()
    render_gemini_practice_lab(
        prog,
        scope_key="stage4_verbs",
        default_topic="Формы глаголов, времена и неправильные глаголы",
    )


def _render_life_work_stage(prog: dict):
    st.header("🏢 Жизнь и работа (Этап 5)")
    st.caption("Практикуй английский для реальных жизненных моментов: работа, документы, жильё, поездки и общение.")

    preset_situations = [
        "Собеседование и первый рабочий день",
        "Работа на складе / стройке / смены и график",
        "Аренда жилья и общение с хозяином квартиры",
        "Врач, аптека и самочувствие",
        "Банк, документы, полиция и бытовые вопросы",
    ]
    chosen_sit = st.selectbox("Быстрый выбор жизненного момента:", preset_situations, key="life_work_preset")
    render_gemini_practice_lab(
        prog,
        scope_key="stage5_life_work",
        default_topic=chosen_sit,
    )


def _render_reading_stage(prog: dict):
    st.header("📖 Чтение (Этап 6)")
    st.caption("Читай короткие жизненные истории, переводи и генерируй бесконечные тексты под свой уровень.")

    sample_texts = {
        "Первый день на новой смене (A1–A2)": (
            "My name is Timur. Today is my first day at the new logistics center. "
            "My shift starts at eight o'clock in the morning. The supervisor shows me where the boxes are "
            "and explains the safety rules. I can understand most instructions, and when something is not clear, "
            "I ask my colleague to repeat it slowly.",
            "Меня зовут Тимур. Сегодня мой первый день в новом логистическом центре. "
            "Моя смена начинается в восемь утра. Руководитель показывает мне, где находятся коробки, "
            "и объясняет правила безопасности. Я понимаю большую часть инструкций, а когда что-то непонятно, "
            "прошу коллегу повторить медленнее.",
        ),
        "Поиск квартиры и договор (A2–B1)": (
            "We arrived in the city last week and stayed in a small hotel for three days. "
            "Yesterday we visited two apartments near the metro station. The second flat is bright and quiet, "
            "and the rent includes water and heating. Before signing the agreement, we checked all bills "
            "and asked about the deposit.",
            "Мы приехали в город на прошлой неделе и три дня жили в небольшом отеле. "
            "Вчера мы посмотрели две квартиры рядом со станцией метро. Вторая квартира светлая и тихая, "
            "и в арендную плату входят вода и отопление. Перед подписанием договора мы проверили все счета "
            "и спросили про залог.",
        ),
    }

    title = st.selectbox("Выберите готовый текст для разбора:", list(sample_texts.keys()), key="read_sample_title")
    en_text, ru_text = sample_texts[title]

    with st.container(border=True):
        st.markdown(f"### {title}")
        st.write(en_text)
        if st.button("🔊 Озвучить текст", key="read_sample_tts"):
            audio = get_audio_bytes(en_text, accent="US (Американский)", slow=False)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)
        if st.checkbox("Показать перевод на русский", key="read_show_ru"):
            st.info(ru_text)

    st.divider()
    render_gemini_practice_lab(
        prog,
        scope_key="stage6_reading",
        default_topic=f"Чтение и разбор текста: {title}",
    )


def _render_listening_speaking_stage(prog: dict):
    st.header("🎧 Аудирование и речь (Этап 7)")
    st.caption("Слушай фразы на английском, тренируй устные/письменные ответы и получай разбор от Gemini.")

    practice_phrases = [
        ("Could you repeat that more slowly, please?", "Не могли бы вы повторить это помедленнее, пожалуйста?"),
        ("Excuse me, where is the nearest train station?", "Извините, где находится ближайшая железнодорожная станция?"),
        ("I can start work tomorrow morning.", "Я могу выйти на работу завтра утром."),
        ("How much is the monthly rent, and is heating included?", "Сколько стоит аренда в месяц и входит ли отопление?"),
    ]

    phrase_en, phrase_ru = st.selectbox(
        "Выберите фразу для аудирования и речи:",
        practice_phrases,
        format_func=lambda pair: f"{pair[0]} — {pair[1]}",
        key="ls_phrase_select",
    )

    c_tts1, c_tts2 = st.columns(2)
    with c_tts1:
        if st.button("🔊 Озвучить (обычный темп)", key="ls_tts_norm", use_container_width=True):
            audio = get_audio_bytes(phrase_en, accent="US (Американский)", slow=False)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)
    with c_tts2:
        if st.button("🐢 Озвучить медленно", key="ls_tts_slow", use_container_width=True):
            audio = get_audio_bytes(phrase_en, accent="US (Американский)", slow=True)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)

    user_reply = st.text_input(
        "Напишите ваш ответ или похожую фразу на английском для проверки:",
        key="ls_user_reply",
    )
    if st.button("Проверить речь/ответ с Gemini", key="ls_check_btn", type="primary"):
        if not user_reply.strip():
            st.info("Введите фразу на английском для проверки.")
        else:
            prompt = (
                f"Фраза для тренировки: '{phrase_en}' ({phrase_ru}).\n"
                f"Ответ/фраза ученика: '{user_reply}'.\n"
                "Проверь на русском языке: грамматику, естественность звучания и дай 1-2 более живых варианта."
            )
            with st.spinner("Gemini проверяет вашу фразу..."):
                ok, ans = ask_gemini(prompt)
            if ok:
                st.markdown(ans)
                record_activity(prog, st.session_state, actions=1)
                save_progress(prog)
            else:
                st.error(ans)

    st.divider()
    render_gemini_practice_lab(
        prog,
        scope_key="stage7_listening_speaking",
        default_topic="Разговорная речь, вопросы и ответы в жизни",
    )


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
        "AI-практика (Gemini)",
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
elif page in ("Грамматика", "Грамматика (Этап 3)"):
    render_grammar(progress)
elif page == "AI-практика (Gemini)":
    render_gemini_practice_lab(progress, scope_key="main_ai_lab", default_topic="Работа, повседневная речь и грамматика")
elif page == "Глаголы (Этап 4)":
    _render_verbs_stage(progress)
elif page == "Жизнь и работа (Этап 5)":
    _render_life_work_stage(progress)
elif page == "Чтение (Этап 6)":
    _render_reading_stage(progress)
elif page == "Аудирование и речь (Этап 7)":
    _render_listening_speaking_stage(progress)
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
