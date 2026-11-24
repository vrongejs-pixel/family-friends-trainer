import json
import os
import random
import re
import streamlit as st
from datetime import datetime
from services.storage import save_progress
from services.progress_tracker import record_activity
from services.speech import get_audio_bytes
from services.spaced_repetition import (
    get_word_state,
    mark_word_studied,
    update_word_review,
    is_due_for_review,
    STATUS_NEW,
    STATUS_REPEAT,
    STATUS_CONFUSED,
    STATUS_KNOWN,
)


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[.,!?;:'\"()\-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _load_vocabulary() -> list[dict]:
    path = os.path.join("curriculum", "vocabulary.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("words", [])


def _render_audio_controls(text: str, key_prefix: str):
    """Отображает кнопки озвучивания: обычная и медленная скорость."""
    accent = st.session_state.get("tts_accent", "US (Американский)")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🔊 Озвучить", key=f"{key_prefix}_norm", use_container_width=True):
            audio = get_audio_bytes(text, accent=accent, slow=False)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)
            else:
                st.warning("Не удалось загрузить озвучку. Проверьте интернет.")
    with c2:
        if st.button("🐢 Медленно", key=f"{key_prefix}_slow", use_container_width=True):
            audio = get_audio_bytes(text, accent=accent, slow=True)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)


def render_vocabulary_study(progress: dict):
    """Раздел 1: Изучение тематического словаря (Сначала понимание и перевод, затем практика)."""
    st.header("📚 Тематический словарь")
    st.caption("Принцип метода Холмата: сначала изучи слово, транскрипцию, произношение и пример, затем переходи к карточкам.")

    words = _load_vocabulary()
    categories = ["Все темы"] + sorted(list({w["category"] for w in words}))
    statuses = ["Все статусы", STATUS_NEW, "Знакомое слово", STATUS_REPEAT, STATUS_CONFUSED, STATUS_KNOWN]

    col_f1, col_f2, col_f3 = st.columns([1.4, 1.2, 1.2])
    with col_f1:
        selected_cat = st.selectbox("Выберите тему:", categories)
    with col_f2:
        selected_status = st.selectbox("Фильтр по статусу:", statuses)
    with col_f3:
        accent = st.selectbox("Произношение:", ["US (Американский)", "UK (Британский)"], key="tts_accent")

    filtered = []
    for w in words:
        w_state = get_word_state(progress, w["id"])
        if selected_cat != "Все темы" and w["category"] != selected_cat:
            continue
        if selected_status != "Все статусы" and w_state["status"] != selected_status:
            continue
        filtered.append((w, w_state))

    st.write(f"Найдено слов: **{len(filtered)}**")
    st.divider()

    for w, w_state in filtered:
        with st.container(border=True):
            top_l, top_r = st.columns([2, 1])
            with top_l:
                st.markdown(f"### {w['word']}  `{w['ipa']}`  —  **{w['translation']}**")
                st.caption(f"Тема: {w['category']} | Уровень: {w['level']} | Статус: **{w_state['status']}**")
            with top_r:
                _render_audio_controls(w["word"], key_prefix=f"vocab_{w['id']}")

            st.markdown(f"📝 *Пример:* **{w['example']}**")
            st.write(f"🇷🇺 *Перевод:* {w['example_ru']}")

            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                if st.button("🎧 Озвучить пример", key=f"ex_{w['id']}", use_container_width=True):
                    audio_ex = get_audio_bytes(w["example"], accent=accent, slow=False)
                    if audio_ex:
                        st.audio(audio_ex, format="audio/mp3", autoplay=True)
            with btn_col2:
                if w_state["status"] == STATUS_NEW:
                    if st.button("✅ Я ознакомился со словом", key=f"learn_{w['id']}", type="primary", use_container_width=True):
                        mark_word_studied(progress, w["id"])
                        save_progress(progress)
                        record_activity(progress, st.session_state, actions=1)
                        st.rerun()
                else:
                    st.button(
                        f"Статус: {w_state['status']} (верно: {w_state['total_correct']})",
                        key=f"done_{w['id']}",
                        disabled=True,
                        use_container_width=True,
                    )


def render_flashcards(progress: dict):
    """Раздел 2: Карточки и 6 режимов проверки с интервальным повторением."""
    st.header("🗂 Карточки и проверка слов")

    words = _load_vocabulary()
    modes = [
        "1. Английское слово → вспомнить перевод",
        "2. Русское слово → вспомнить английское слово",
        "3. Услышать слово → написать его",
        "4. Увидеть слово → составить предложение",
        "5. Вспомнить слово без подсказки",
        "6. Повторить сложные и забываемые слова",
    ]

    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        selected_mode = st.selectbox("Режим тренировки:", modes)
    with col_m2:
        accent = st.selectbox("Голос озвучки:", ["US (Американский)", "UK (Британский)"], key="fc_accent")

    # Формируем список слов для текущего режима
    pool = []
    for w in words:
        st_data = get_word_state(progress, w["id"])
        if selected_mode.startswith("6."):
            if st_data["status"] in (STATUS_REPEAT, STATUS_CONFUSED) or is_due_for_review(st_data):
                pool.append(w)
        else:
            # В основных режимах берём слова, которые пользователь уже начал учить, либо все если изученных мало
            if st_data["status"] != STATUS_NEW:
                pool.append(w)

    if not pool:
        if selected_mode.startswith("6."):
            st.success("🎉 На сегодня сложных или просроченных слов для повторения нет! Отличная работа.")
            return
        else:
            st.info("Вы ещё не отметили ни одного слова как изученное в разделе «Словарь». Сейчас тренируемся на общем списке слов.")
            pool = words

    # Перемешивание и выбор текущей карточки
    if "fc_current_word_id" not in st.session_state or st.session_state.get("fc_last_mode") != selected_mode:
        st.session_state.fc_last_mode = selected_mode
        st.session_state.fc_current_word_id = random.choice(pool)["id"]
        st.session_state.fc_checked = False
        st.session_state.fc_revealed = False

    current_word = next((w for w in pool if w["id"] == st.session_state.fc_current_word_id), pool[0])
    w_state = get_word_state(progress, current_word["id"])

    st.divider()
    with st.container(border=True):
        st.caption(f"Тема: {current_word['category']} | Уровень: {current_word['level']} | Текущий статус: **{w_state['status']}**")

        # РЕЖИМ 1: Английское слово -> вспомнить перевод
        if selected_mode.startswith("1."):
            st.markdown(f"## {current_word['word']}  `{current_word['ipa']}`")
            if st.button("🔊 Произнести слово", key="m1_audio"):
                audio = get_audio_bytes(current_word["word"], accent=accent)
                if audio:
                    st.audio(audio, format="audio/mp3", autoplay=True)

            user_ans = st.text_input("Напишите перевод на русском языке:", key="fc_input_1")
            if st.button("Проверить ответ", type="primary", key="m1_check"):
                st.session_state.fc_checked = True
                record_activity(progress, st.session_state, actions=1)
                expected_variants = [_normalize(x) for x in current_word["translation"].split("/")]
                is_ok = bool(_normalize(user_ans)) and any(
                    _normalize(user_ans) in exp or exp in _normalize(user_ans) for exp in expected_variants
                )
                update_word_review(progress, current_word["id"], is_ok, "en_to_ru")
                if not is_ok:
                    progress["mistakes_log"].append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "topic": f"Словарь ({current_word['category']})",
                        "task": f"Перевод слова «{current_word['word']}»",
                        "user_answer": user_ans or "Пусто",
                        "correct_answer": current_word["translation"],
                        "explanation": f"{current_word['word']} {current_word['ipa']} — {current_word['translation']}. Пример: {current_word['example']}",
                        "status": "Не исправлено",
                    })
                save_progress(progress)
                st.session_state.fc_last_ok = is_ok

        # РЕЖИМ 2: Русское слово -> вспомнить английское слово
        elif selected_mode.startswith("2."):
            st.markdown(f"## 🇷🇺 {current_word['translation']}")
            user_ans = st.text_input("Напишите это слово по-английски:", key="fc_input_2")
            if st.button("Проверить ответ", type="primary", key="m2_check"):
                st.session_state.fc_checked = True
                record_activity(progress, st.session_state, actions=1)
                is_ok = _normalize(user_ans) == _normalize(current_word["word"])
                update_word_review(progress, current_word["id"], is_ok, "ru_to_en")
                if not is_ok:
                    progress["mistakes_log"].append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "topic": f"Словарь ({current_word['category']})",
                        "task": f"Написать по-английски: «{current_word['translation']}»",
                        "user_answer": user_ans or "Пусто",
                        "correct_answer": current_word["word"],
                        "explanation": f"Правильное написание: {current_word['word']} {current_word['ipa']}.",
                        "status": "Не исправлено",
                    })
                save_progress(progress)
                st.session_state.fc_last_ok = is_ok

        # РЕЖИМ 3: Услышать слово -> написать его
        elif selected_mode.startswith("3."):
            st.markdown("### 🎧 Прослушайте слово и напишите его по-английски")
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                if st.button("🔊 Слушать (обычно)", key="m3_norm", use_container_width=True):
                    audio = get_audio_bytes(current_word["word"], accent=accent, slow=False)
                    if audio:
                        st.audio(audio, format="audio/mp3", autoplay=True)
            with c_a2:
                if st.button("🐢 Слушать (медленно)", key="m3_slow", use_container_width=True):
                    audio = get_audio_bytes(current_word["word"], accent=accent, slow=True)
                    if audio:
                        st.audio(audio, format="audio/mp3", autoplay=True)

            user_ans = st.text_input("Напишите услышанное слово:", key="fc_input_3")
            if st.button("Проверить написание", type="primary", key="m3_check"):
                st.session_state.fc_checked = True
                record_activity(progress, st.session_state, actions=1)
                is_ok = _normalize(user_ans) == _normalize(current_word["word"])
                update_word_review(progress, current_word["id"], is_ok, "dictation")
                if not is_ok:
                    progress["mistakes_log"].append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "topic": "Аудирование слов (диктант)",
                        "task": f"Написать слово на слух ({current_word['translation']})",
                        "user_answer": user_ans or "Пусто",
                        "correct_answer": current_word["word"],
                        "explanation": f"Слово пишется так: {current_word['word']} {current_word['ipa']} ({current_word['translation']}).",
                        "status": "Не исправлено",
                    })
                save_progress(progress)
                st.session_state.fc_last_ok = is_ok

        # РЕЖИМ 4: Увидеть слово -> составить предложение
        elif selected_mode.startswith("4."):
            st.markdown(f"## {current_word['word']} — {current_word['translation']}")
            st.write("Составьте своё короткое предложение на английском языке, используя это слово:")
            user_sent = st.text_input("Ваше предложение:", key="fc_input_4", placeholder="Например: I work in a warehouse...")
            if st.button("Проверить предложение", type="primary", key="m4_check"):
                st.session_state.fc_checked = True
                record_activity(progress, st.session_state, actions=1)
                norm_s = _normalize(user_sent)
                target_w = _normalize(current_word["word"])
                has_word = target_w in norm_s and len(norm_s.split()) >= 2
                update_word_review(progress, current_word["id"], has_word, "sentence")
                save_progress(progress)
                st.session_state.fc_last_ok = has_word

        # РЕЖИМ 5 и 6: Вспомнить слово без подсказки / Повторение трудных слов
        else:
            st.markdown(f"### Вспомните английское слово и его написание:")
            st.markdown(f"## 🇷🇺 {current_word['translation']}")
            st.caption(f"Подсказка контекста: {current_word['example_ru']}")
            user_ans = st.text_input("Введите английское слово без подсказок:", key="fc_input_56")
            if st.button("Проверить", type="primary", key="m56_check"):
                st.session_state.fc_checked = True
                record_activity(progress, st.session_state, actions=1)
                is_ok = _normalize(user_ans) == _normalize(current_word["word"])
                update_word_review(progress, current_word["id"], is_ok, "recall_hard")
                if not is_ok:
                    progress["mistakes_log"].append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "topic": "Повторение сложных слов",
                        "task": f"Вспомнить слово: «{current_word['translation']}»",
                        "user_answer": user_ans or "Пусто",
                        "correct_answer": current_word["word"],
                        "explanation": f"Правильно: {current_word['word']} {current_word['ipa']}. Пример: {current_word['example']}",
                        "status": "Не исправлено",
                    })
                save_progress(progress)
                st.session_state.fc_last_ok = is_ok

        # Показ результата и подробного разбора после проверки
        if st.session_state.get("fc_checked"):
            st.divider()
            if st.session_state.get("fc_last_ok"):
                st.success(f"✅ Верно! **{current_word['word']}** `{current_word['ipa']}` — {current_word['translation']}")
            else:
                st.error(f"❌ Ошибка! Правильно: **{current_word['word']}** `{current_word['ipa']}` — {current_word['translation']}")

            st.info(f"📖 Пример использования:\n**{current_word['example']}**\n🇷🇺 {current_word['example_ru']}")

    # Кнопка перехода к следующему слову
    if st.button("Следующее слово ➡️", type="primary"):
        other_words = [w for w in pool if w["id"] != current_word["id"]]
        next_w = random.choice(other_words) if other_words else current_word
        st.session_state.fc_current_word_id = next_w["id"]
        st.session_state.fc_checked = False
        st.rerun()
