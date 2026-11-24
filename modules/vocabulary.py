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
    accent = st.session_state.get("tts_accent", "US (Американский)")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("🔊 Озвучить", key=f"{key_prefix}_norm", use_container_width=True):
            audio = get_audio_bytes(text, accent=accent, slow=False)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)
    with c2:
        if st.button("🐢 Медленно", key=f"{key_prefix}_slow", use_container_width=True):
            audio = get_audio_bytes(text, accent=accent, slow=True)
            if audio:
                st.audio(audio, format="audio/mp3", autoplay=True)


def render_vocabulary_study(progress: dict):
    """Раздел 1: Изучение тематического словаря."""
    st.header("📚 Тематический словарь")
    st.caption("Изучи слово, транскрипцию, произношение и пример, затем отметь его для тренировки в карточках и тесте.")

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
    """Раздел 2: Двусторонние переворачиваемые карточки."""
    st.header("🗂 Карточки (переверни и проверь себя)")
    st.caption("Посмотри на слово, вспомни значение и нажми «Перевернуть карточку», чтобы увидеть обратную сторону.")

    words = _load_vocabulary()
    categories = ["Все темы"] + sorted(list({w["category"] for w in words}))

    c1, c2, c3 = st.columns([1.3, 1.3, 1])
    with c1:
        cat_filter = st.selectbox("Тема карточек:", categories, key="fc_cat")
    with c2:
        side_mode = st.selectbox(
            "Лицевая сторона карточки:",
            ["🇬🇧 Английское слово → Русский", "🇷🇺 Русское слово → Английский"],
            key="fc_side_mode",
        )
    with c3:
        accent = st.selectbox("Голос:", ["US (Американский)", "UK (Британский)"], key="fc_accent")

    pool = [w for w in words if cat_filter == "Все темы" or w["category"] == cat_filter]
    if not pool:
        st.warning("В этой теме пока нет слов.")
        return

    # Взвешенный случайный выбор: трудные и невыученные слова выпадают чаще
    def _pick_next_card(exclude_id: str | None = None) -> dict:
        candidates = [w for w in pool if w["id"] != exclude_id] or pool
        weighted = []
        for w in candidates:
            st_data = get_word_state(progress, w["id"])
            status = st_data["status"]
            if status in (STATUS_REPEAT, STATUS_CONFUSED):
                weight = 5
            elif status != STATUS_KNOWN:
                weight = 3
            else:
                weight = 1
            weighted.extend([w] * weight)
        return random.choice(weighted)

    if (
        "fc_card_id" not in st.session_state
        or st.session_state.get("fc_last_cat") != cat_filter
        or not any(w["id"] == st.session_state.fc_card_id for w in pool)
    ):
        st.session_state.fc_last_cat = cat_filter
        st.session_state.fc_card_id = _pick_next_card()["id"]
        st.session_state.fc_flipped = False

    card = next(w for w in pool if w["id"] == st.session_state.fc_card_id)
    w_state = get_word_state(progress, card["id"])
    is_en_front = side_mode.startswith("🇬🇧")

    st.divider()

    # Визуальная двусторонняя карточка
    with st.container(border=True):
        st.caption(f"Тема: {card['category']} | Уровень: {card['level']} | Статус: **{w_state['status']}**")

        if not st.session_state.fc_flipped:
            # ЛИЦЕВАЯ СТОРОНА
            st.markdown("#### Лицевая сторона")
            if is_en_front:
                st.markdown(f"# {card['word']}")
                st.markdown(f"### `{card['ipa']}`")
                a1, a2, _ = st.columns([1, 1, 2])
                with a1:
                    if st.button("🔊 Произнести", key="fc_front_audio", use_container_width=True):
                        audio = get_audio_bytes(card["word"], accent=accent, slow=False)
                        if audio:
                            st.audio(audio, format="audio/mp3", autoplay=True)
                with a2:
                    if st.button("🐢 Медленно", key="fc_front_slow", use_container_width=True):
                        audio = get_audio_bytes(card["word"], accent=accent, slow=True)
                        if audio:
                            st.audio(audio, format="audio/mp3", autoplay=True)
            else:
                st.markdown(f"# 🇷🇺 {card['translation']}")

            st.write("")
            if st.button("🔄 Перевернуть карточку", type="primary", use_container_width=True):
                st.session_state.fc_flipped = True
                record_activity(progress, st.session_state, actions=1)
                st.rerun()

        else:
            # ОБРАТНАЯ СТОРОНА
            st.markdown("#### Обратная сторона")
            st.markdown(f"# {card['word']}  `{card['ipa']}`")
            st.markdown(f"## 🇷🇺 {card['translation']}")

            a1, a2, _ = st.columns([1, 1, 2])
            with a1:
                if st.button("🔊 Произнести слово", key="fc_back_audio", use_container_width=True):
                    audio = get_audio_bytes(card["word"], accent=accent, slow=False)
                    if audio:
                        st.audio(audio, format="audio/mp3", autoplay=True)
            with a2:
                if st.button("🎧 Озвучить пример", key="fc_back_ex_audio", use_container_width=True):
                    audio_ex = get_audio_bytes(card["example"], accent=accent, slow=False)
                    if audio_ex:
                        st.audio(audio_ex, format="audio/mp3", autoplay=True)

            st.info(f"📖 *Пример:* **{card['example']}**\n\n🇷🇺 *Перевод:* {card['example_ru']}")

            if st.button("🔄 Повернуть обратно (лицевая сторона)", use_container_width=True):
                st.session_state.fc_flipped = False
                st.rerun()

    # Кнопки оценки знания и перехода к следующей карточке
    b1, b2, b3 = st.columns([1.2, 1.2, 1])
    with b1:
        if st.button("✅ Знаю это слово", type="primary", use_container_width=True):
            update_word_review(progress, card["id"], True, "flashcard_flip")
            save_progress(progress)
            record_activity(progress, st.session_state, actions=1)
            st.session_state.fc_card_id = _pick_next_card(card["id"])["id"]
            st.session_state.fc_flipped = False
            st.rerun()
    with b2:
        if st.button("❌ Не знаю / Повторить", use_container_width=True):
            update_word_review(progress, card["id"], False, "flashcard_flip")
            save_progress(progress)
            record_activity(progress, st.session_state, actions=1)
            st.session_state.fc_card_id = _pick_next_card(card["id"])["id"]
            st.session_state.fc_flipped = False
            st.rerun()
    with b3:
        if st.button("Следующая ➡️", use_container_width=True):
            st.session_state.fc_card_id = _pick_next_card(card["id"])["id"]
            st.session_state.fc_flipped = False
            st.rerun()


def render_vocabulary_test(progress: dict):
    """Раздел 3: Письменный тест по словарю (Русский -> Английский) с умным закреплением ошибок."""
    st.header("✍️ Тест по словарю (Русский → Английский)")
    st.caption(
        "Система показывает русское слово — вы пишете его на английском. "
        "Все слова, где допущена ошибка, автоматически фиксируются и повторно выдаются в случайном порядке для закрепления."
    )

    words = _load_vocabulary()
    categories = ["Все изученные и сложные", "Все слова из базы"] + sorted(list({w["category"] for w in words}))

    col1, col2 = st.columns([1.5, 1])
    with col1:
        scope = st.selectbox("Какие слова проверять:", categories, key="vtest_scope")
    with col2:
        accent = st.selectbox("Озвучка при проверке:", ["US (Американский)", "UK (Британский)"], key="vtest_accent")

    # Формируем пул слов
    if scope == "Все изученные и сложные":
        pool = [
            w for w in words
            if get_word_state(progress, w["id"])["status"] != STATUS_NEW
        ]
        if not pool:
            st.info("Вы ещё не отметили изученные слова в разделе «Словарь», поэтому тест запущен по всем словам базы.")
            pool = words
    elif scope == "Все слова из базы":
        pool = words
    else:
        pool = [w for w in words if w["category"] == scope]

    # Статистика проблемных слов пользователя
    weak_words = [
        w for w in pool
        if get_word_state(progress, w["id"])["status"] in (STATUS_REPEAT, STATUS_CONFUSED)
    ]
    known_words = [
        w for w in pool
        if get_word_state(progress, w["id"])["status"] == STATUS_KNOWN
    ]

    m1, m2, m3 = st.columns(3)
    m1.metric("Слов в тесте", len(pool))
    m2.metric("Закреплено (Хорошо знаю)", len(known_words))
    m3.metric("На повтор (Ошибки)", len(weak_words))

    # Функция умного случайного выбора: приоритет у слов с ошибками (очередь закрепления + высокий вес)
    def _select_test_word(exclude_id: str | None = None) -> dict:
        retry_queue = st.session_state.setdefault("vtest_retry_queue", [])
        # Если в очереди закрепления есть слова и выпал шанс (или других мало) — достаём оттуда
        valid_queue = [wid for wid in retry_queue if wid != exclude_id and any(w["id"] == wid for w in pool)]
        if valid_queue and random.random() < 0.65:
            chosen_id = random.choice(valid_queue)
            return next(w for w in pool if w["id"] == chosen_id)

        candidates = [w for w in pool if w["id"] != exclude_id] or pool
        weighted = []
        for w in candidates:
            st_data = get_word_state(progress, w["id"])
            status = st_data["status"]
            if status == STATUS_CONFUSED:
                weight = 6
            elif status == STATUS_REPEAT:
                weight = 5
            elif is_due_for_review(st_data):
                weight = 3
            elif status != STATUS_KNOWN:
                weight = 2
            else:
                weight = 1
            weighted.extend([w] * weight)
        return random.choice(weighted)

    if (
        "vtest_word_id" not in st.session_state
        or st.session_state.get("vtest_last_scope") != scope
        or not any(w["id"] == st.session_state.vtest_word_id for w in pool)
    ):
        st.session_state.vtest_last_scope = scope
        st.session_state.vtest_word_id = _select_test_word()["id"]
        st.session_state.vtest_answered = False
        st.session_state.vtest_user_input = ""

    current_w = next(w for w in pool if w["id"] == st.session_state.vtest_word_id)
    w_state = get_word_state(progress, current_w["id"])
    is_retry = current_w["id"] in st.session_state.get("vtest_retry_queue", []) or w_state["status"] in (
        STATUS_REPEAT,
        STATUS_CONFUSED,
    )

    st.divider()
    with st.container(border=True):
        if is_retry:
            st.warning("🔁 **Повторное закрепление:** ранее в этом слове была ошибка.")
        st.caption(f"Тема: {current_w['category']} | Уровень: {current_w['level']} | Статус: **{w_state['status']}**")
        st.markdown(f"### Переведите и напишите по-английски:")
        st.markdown(f"# 🇷🇺 {current_w['translation']}")

        with st.form(key=f"vtest_form_{current_w['id']}"):
            user_text = st.text_input(
                "Введите английское слово:",
                placeholder="Напишите слово на английском и нажмите «Проверить»...",
            )
            submitted = st.form_submit_button("Проверить ответ ✅", type="primary", use_container_width=True)

        if submitted and not st.session_state.vtest_answered:
            st.session_state.vtest_answered = True
            st.session_state.vtest_user_input = user_text
            record_activity(progress, st.session_state, actions=1)

            is_correct = _normalize(user_text) == _normalize(current_w["word"])
            st.session_state.vtest_last_correct = is_correct

            update_word_review(progress, current_w["id"], is_correct, "written_test_ru_en")
            retry_queue = st.session_state.setdefault("vtest_retry_queue", [])

            if is_correct:
                # Если слово было в очереди на закрепление, убираем только после уверенного ответа
                if current_w["id"] in retry_queue and w_state["correct_streak"] >= 2:
                    retry_queue.remove(current_w["id"])
            else:
                # Фиксируем слово в очереди случайного повторения и в журнале ошибок
                if current_w["id"] not in retry_queue:
                    retry_queue.append(current_w["id"])
                progress["mistakes_log"].append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "topic": f"Тест по словарю ({current_w['category']})",
                    "task": f"Написать по-английски: «{current_w['translation']}»",
                    "user_answer": user_text.strip() or "Пусто",
                    "correct_answer": current_w["word"],
                    "explanation": f"Правильное написание: {current_w['word']} {current_w['ipa']}. Пример: {current_w['example']}",
                    "status": "Не исправлено",
                })

            save_progress(progress)

        if st.session_state.vtest_answered:
            st.divider()
            if st.session_state.get("vtest_last_correct"):
                st.success(
                    f"✅ **Правильно!** `{current_w['word']}` {current_w['ipa']} — {current_w['translation']}"
                )
            else:
                st.error(
                    f"❌ **Ошибка!** Вы написали: `{st.session_state.vtest_user_input or 'Пусто'}`\n\n"
                    f"✅ Правильно: **`{current_w['word']}`** `{current_w['ipa']}`"
                )

            if st.button("🔊 Послушать правильное произношение", key="vtest_listen"):
                audio = get_audio_bytes(current_w["word"], accent=accent, slow=False)
                if audio:
                    st.audio(audio, format="audio/mp3", autoplay=True)

            st.info(f"📖 *Пример:* **{current_w['example']}**\n\n🇷🇺 {current_w['example_ru']}")

    if st.button("Следующее слово в тесте ➡️", type="primary", use_container_width=True):
        st.session_state.vtest_word_id = _select_test_word(current_w["id"])["id"]
        st.session_state.vtest_answered = False
        st.session_state.vtest_user_input = ""
        st.rerun()

    # Блок анализа ошибок прямо под тестом
    if weak_words:
        with st.expander(f"📊 Анализ проблемных слов ({len(weak_words)} шт. на закрепление)"):
            st.write("Система автоматически будет давать эти слова чаще в случайном порядке, пока вы не напишете их без ошибок:")
            for ww in weak_words:
                st_w = get_word_state(progress, ww["id"])
                st.write(
                    f"• **{ww['translation']}** → `{ww['word']}` {ww['ipa']} "
                    f"*(ошибок: {st_w['total_wrong']}, серия верных: {st_w['correct_streak']})*"
                )
