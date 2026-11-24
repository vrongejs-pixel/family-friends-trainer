import glob
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


@st.cache_data(ttl=60)
def _load_vocabulary() -> list[dict]:
    words = []
    seen_ids = set()
    for path in sorted(glob.glob(os.path.join("curriculum", "*.json"))):
        if os.path.basename(path) == "diagnostic_questions.json":
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("words", []) if isinstance(data, dict) else []
            for w in items:
                if w.get("id") and w["id"] not in seen_ids:
                    seen_ids.add(w["id"])
                    if not w.get("pos"):
                        w["pos"] = "Существительные"
                    if not w.get("category"):
                        w["category"] = "Без темы"
                    words.append(w)
        except Exception:
            continue
    return words


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
    """Раздел 1: Тематический словарь с группировкой по частям речи и темам."""
    st.header("📚 Тематический словарь")
    st.caption("Изучай слова по частям речи и жизненным темам: смотри транскрипцию, слушай произношение и отмечай изученные.")

    words = _load_vocabulary()
    pos_list = ["Все части речи"] + sorted(list({w.get("pos") or "Без части речи" for w in words}))
    categories = ["Все темы"] + sorted(list({w.get("category") or "Без темы" for w in words}))
    statuses = ["Все статусы", STATUS_NEW, "Знакомое слово", STATUS_REPEAT, STATUS_CONFUSED, STATUS_KNOWN]

    col_f1, col_f2, col_f3, col_f4 = st.columns([1.2, 1.2, 1.1, 1.1])
    with col_f1:
        selected_pos = st.selectbox("Часть речи:", pos_list)
    with col_f2:
        selected_cat = st.selectbox("Тема:", categories)
    with col_f3:
        selected_status = st.selectbox("Статус:", statuses)
    with col_f4:
        accent = st.selectbox("Произношение:", ["US (Американский)", "UK (Британский)"], key="tts_accent")

    search_q = st.text_input("🔍 Поиск слова (на английском или русском):", placeholder="Например: work, shift, работать...")

    filtered = []
    for w in words:
        w_state = get_word_state(progress, w["id"])
        w_pos = w.get("pos") or "Без части речи"
        w_cat = w.get("category") or "Без темы"
        if selected_pos != "Все части речи" and w_pos != selected_pos:
            continue
        if selected_cat != "Все темы" and w_cat != selected_cat:
            continue
        if selected_status != "Все статусы" and w_state["status"] != selected_status:
            continue
        if search_q.strip():
            q = search_q.strip().lower()
            if q not in w.get("word", "").lower() and q not in w.get("translation", "").lower():
                continue
        filtered.append((w, w_state))

    m1, m2, m3 = st.columns(3)
    m1.metric("Всего слов в базе", len(words))
    m2.metric("Показано по фильтру", len(filtered))
    learned_cnt = sum(1 for w in words if get_word_state(progress, w["id"])["status"] != STATUS_NEW)
    m3.metric("Изучено / в работе", learned_cnt)

    st.divider()

    page_size = 25
    total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
    if total_pages > 1:
        page_num = st.number_input(f"Страница (всего {total_pages}):", min_value=1, max_value=total_pages, value=1)
    else:
        page_num = 1

    start_idx = (page_num - 1) * page_size
    page_items = filtered[start_idx : start_idx + page_size]

    for w, w_state in page_items:
        w_pos = w.get("pos") or "Без части речи"
        w_cat = w.get("category") or "Без темы"
        with st.container(border=True):
            top_l, top_r = st.columns([2, 1])
            with top_l:
                st.markdown(f"### {w.get('word', '')}  `{w.get('ipa', '')}`  —  **{w.get('translation', '')}**")
                st.caption(
                    f"Часть речи: **{w_pos}** | Тема: {w_cat} | Уровень: {w.get('level', 'A1')} | Статус: **{w_state['status']}**"
                )
            with top_r:
                _render_audio_controls(w.get("word", ""), key_prefix=f"vocab_{w['id']}")

            st.markdown(f"📝 *Пример:* **{w.get('example', '')}**")
            st.write(f"🇷🇺 *Перевод:* {w.get('example_ru', '')}")

            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                if st.button("🎧 Озвучить пример", key=f"ex_{w['id']}", use_container_width=True):
                    audio_ex = get_audio_bytes(w.get("example", ""), accent=accent, slow=False)
                    if audio_ex:
                        st.audio(audio_ex, format="audio/mp3", autoplay=True)
            with btn_col2:
                if w_state["status"] == STATUS_NEW:
                    if st.button("✅ Отметить как изученное", key=f"learn_{w['id']}", type="primary", use_container_width=True):
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
    pos_list = ["Все части речи"] + sorted(list({w.get("pos") or "Без части речи" for w in words}))
    categories = ["Все темы"] + sorted(list({w.get("category") or "Без темы" for w in words}))

    c1, c2, c3, c4 = st.columns([1.1, 1.2, 1.3, 1])
    with c1:
        pos_filter = st.selectbox("Часть речи:", pos_list, key="fc_pos")
    with c2:
        cat_filter = st.selectbox("Тема:", categories, key="fc_cat")
    with c3:
        side_mode = st.selectbox(
            "Лицевая сторона:",
            ["🇬🇧 Английское слово → Русский", "🇷🇺 Русское слово → Английский"],
            key="fc_side_mode",
        )
    with c4:
        accent = st.selectbox("Голос:", ["US (Американский)", "UK (Британский)"], key="fc_accent")

    pool = [
        w for w in words
        if (pos_filter == "Все части речи" or (w.get("pos") or "Без части речи") == pos_filter)
        and (cat_filter == "Все темы" or (w.get("category") or "Без темы") == cat_filter)
    ]
    if not pool:
        st.warning("По выбранным фильтрам слов пока нет.")
        return

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

    filter_sig = f"{pos_filter}|{cat_filter}"
    if (
        "fc_card_id" not in st.session_state
        or st.session_state.get("fc_last_sig") != filter_sig
        or not any(w["id"] == st.session_state.fc_card_id for w in pool)
    ):
        st.session_state.fc_last_sig = filter_sig
        st.session_state.fc_card_id = _pick_next_card()["id"]
        st.session_state.fc_flipped = False

    card = next(w for w in pool if w["id"] == st.session_state.fc_card_id)
    w_state = get_word_state(progress, card["id"])
    card_pos = card.get("pos") or "Без части речи"
    card_cat = card.get("category") or "Без темы"
    is_en_front = side_mode.startswith("🇬🇧")

    st.divider()

    with st.container(border=True):
        st.caption(
            f"Часть речи: **{card_pos}** | Тема: {card_cat} | Уровень: {card.get('level', 'A1')} | Статус: **{w_state['status']}**"
        )

        if not st.session_state.fc_flipped:
            st.markdown("#### Лицевая сторона")
            if is_en_front:
                st.markdown(f"# {card.get('word', '')}")
                st.markdown(f"### `{card.get('ipa', '')}`")
                a1, a2, _ = st.columns([1, 1, 2])
                with a1:
                    if st.button("🔊 Произнести", key="fc_front_audio", use_container_width=True):
                        audio = get_audio_bytes(card.get("word", ""), accent=accent, slow=False)
                        if audio:
                            st.audio(audio, format="audio/mp3", autoplay=True)
                with a2:
                    if st.button("🐢 Медленно", key="fc_front_slow", use_container_width=True):
                        audio = get_audio_bytes(card.get("word", ""), accent=accent, slow=True)
                        if audio:
                            st.audio(audio, format="audio/mp3", autoplay=True)
            else:
                st.markdown(f"# 🇷🇺 {card.get('translation', '')}")

            st.write("")
            if st.button("🔄 Перевернуть карточку", type="primary", use_container_width=True):
                st.session_state.fc_flipped = True
                record_activity(progress, st.session_state, actions=1)
                st.rerun()

        else:
            st.markdown("#### Обратная сторона")
            st.markdown(f"# {card.get('word', '')}  `{card.get('ipa', '')}`")
            st.markdown(f"## 🇷🇺 {card.get('translation', '')}")

            a1, a2, _ = st.columns([1, 1, 2])
            with a1:
                if st.button("🔊 Произнести слово", key="fc_back_audio", use_container_width=True):
                    audio = get_audio_bytes(card.get("word", ""), accent=accent, slow=False)
                    if audio:
                        st.audio(audio, format="audio/mp3", autoplay=True)
            with a2:
                if st.button("🎧 Озвучить пример", key="fc_back_ex_audio", use_container_width=True):
                    audio_ex = get_audio_bytes(card.get("example", ""), accent=accent, slow=False)
                    if audio_ex:
                        st.audio(audio_ex, format="audio/mp3", autoplay=True)

            st.info(f"📖 *Пример:* **{card.get('example', '')}**\n\n🇷🇺 *Перевод:* {card.get('example_ru', '')}")

            if st.button("🔄 Повернуть обратно (лицевая сторона)", use_container_width=True):
                st.session_state.fc_flipped = False
                st.rerun()

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
    if not words:
        st.warning("Словарь пока пуст или не удалось загрузить JSON-файлы из папки curriculum.")
        return

    pos_list = ["Все части речи"] + sorted(list({w.get("pos") or "Без части речи" for w in words}))
    categories = ["Все изученные и сложные", "Все слова из базы"] + sorted(
        list({w.get("category") or "Без темы" for w in words})
    )

    col1, col2, col3 = st.columns([1.2, 1.4, 1])
    with col1:
        pos_scope = st.selectbox("Часть речи:", pos_list, key="vtest_pos")
    with col2:
        scope = st.selectbox("Какие слова проверять:", categories, key="vtest_scope")
    with col3:
        accent = st.selectbox("Озвучка:", ["US (Американский)", "UK (Британский)"], key="vtest_accent")

    base_words = [
        w for w in words
        if pos_scope == "Все части речи" or (w.get("pos") or "Без части речи") == pos_scope
    ]

    if scope == "Все изученные и сложные":
        pool = [w for w in base_words if get_word_state(progress, w["id"])["status"] != STATUS_NEW]
        if not pool:
            st.info("Вы ещё не отметили изученные слова, поэтому тест запущен по всем словам выбранной части речи.")
            pool = base_words
    elif scope == "Все слова из базы":
        pool = base_words
    else:
        pool = [w for w in base_words if (w.get("category") or "Без темы") == scope]

    if not pool:
        st.warning("По выбранным фильтрам слов пока нет.")
        return

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

    def _select_test_word(exclude_id: str | None = None) -> dict:
        valid_queue = [
            wid for wid in st.session_state.get("vtest_retry_queue", [])
            if wid != exclude_id and any(w["id"] == wid for w in pool)
        ]
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

    test_sig = f"{pos_scope}|{scope}"
    if (
        "vtest_word_id" not in st.session_state
        or st.session_state.get("vtest_last_sig") != test_sig
        or not any(w["id"] == st.session_state.vtest_word_id for w in pool)
    ):
        st.session_state.vtest_last_sig = test_sig
        st.session_state.vtest_word_id = _select_test_word()["id"]
        st.session_state.vtest_answered = False
        st.session_state.vtest_user_input = ""

    current_w = next(w for w in pool if w["id"] == st.session_state.vtest_word_id)
    w_state = get_word_state(progress, current_w["id"])
    w_pos = current_w.get("pos") or "Без части речи"
    w_cat = current_w.get("category") or "Без темы"
    is_retry = current_w["id"] in st.session_state.get("vtest_retry_queue", [])

    st.divider()

    with st.container(border=True):
        if is_retry:
            st.caption("🔁 Повторное слово из очереди ошибок для закрепления")
        st.caption(
            f"Часть речи: **{w_pos}** | Тема: {w_cat} | Уровень: {current_w.get('level', 'A1')} | Статус: **{w_state['status']}**"
        )
        st.markdown(f"## 🇷🇺 {current_w.get('translation', '')}")

        user_ans = st.text_input(
            "Напишите слово по-английски:",
            value=st.session_state.get("vtest_user_input", ""),
            key=f"vtest_input_{current_w['id']}",
        )

        act_col1, act_col2 = st.columns([1, 1])
        with act_col1:
            check_clicked = st.button("✔️ Проверить ответ", type="primary", use_container_width=True)
        with act_col2:
            skip_clicked = st.button("⏭️ Пропустить / Следующее", use_container_width=True)

        if check_clicked:
            st.session_state.vtest_user_input = user_ans
            is_correct = _normalize(user_ans) == _normalize(current_w.get("word", ""))
            st.session_state.vtest_answered = True
            st.session_state.vtest_last_correct = is_correct

            update_word_review(progress, current_w["id"], is_correct, "vocab_test")
            save_progress(progress)
            record_activity(progress, st.session_state, actions=1)

            q = st.session_state.setdefault("vtest_retry_queue", [])
            if is_correct:
                while current_w["id"] in q:
                    q.remove(current_w["id"])
            else:
                if current_w["id"] not in q:
                    q.append(current_w["id"])
            st.rerun()

        if skip_clicked:
            st.session_state.vtest_word_id = _select_test_word(current_w["id"])["id"]
            st.session_state.vtest_answered = False
            st.session_state.vtest_user_input = ""
            st.rerun()

        if st.session_state.get("vtest_answered"):
            if st.session_state.get("vtest_last_correct"):
                st.success(f"Верно! **{current_w.get('word', '')}** `{current_w.get('ipa', '')}`")
            else:
                st.error(
                    f"Пока неверно. Ваш вариант: *{st.session_state.get('vtest_user_input', '')}* — "
                    f"правильно: **{current_w.get('word', '')}** `{current_w.get('ipa', '')}`"
                )

            if current_w.get("example"):
                st.markdown(f"📝 *Пример:* **{current_w['example']}**")
            if current_w.get("example_ru"):
                st.write(f"🇷🇺 *Перевод:* {current_w['example_ru']}")

            _render_audio_controls(current_w.get("word", ""), key_prefix=f"vtest_{current_w['id']}")

            if st.button("➡️ Следующее слово", use_container_width=True):
                st.session_state.vtest_word_id = _select_test_word(current_w["id"])["id"]
                st.session_state.vtest_answered = False
                st.session_state.vtest_user_input = ""
                st.rerun()
