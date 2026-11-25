import glob
import json
import os
import re
from datetime import datetime
import streamlit as st
from services.storage import save_progress
from services.progress_tracker import record_activity
from services.speech import get_audio_bytes


def _normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[.,!?;:\"\(\)\-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _record_grammar_mistake(progress: dict, topic: str, task: str, user_answer: str, correct_answer: str, explanation: str):
    mistakes = progress.setdefault("mistakes_log", [])
    mistakes.append(
        {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "topic": f"Грамматика: {topic}",
            "task": task,
            "user_answer": str(user_answer),
            "correct_answer": str(correct_answer),
            "explanation": explanation or "Проверьте правило построения формы и повторите тему.",
        }
    )


def _mark_lesson_practiced(progress: dict, lesson_id: str, passed: bool):
    grammar_prog = progress.setdefault("grammar_progress", {})
    item = grammar_prog.setdefault(
        lesson_id,
        {"attempts": 0, "correct": 0, "mistakes": 0, "completed": False, "last_practiced": None},
    )
    item["attempts"] += 1
    if passed:
        item["correct"] += 1
    else:
        item["mistakes"] += 1
    if item["correct"] >= 2:
        item["completed"] = True
    item["last_practiced"] = datetime.now().strftime("%Y-%m-%d %H:%M")


@st.cache_data(ttl=60)
def _load_grammar_lessons() -> list[dict]:
    lessons = []
    for path in sorted(glob.glob(os.path.join("curriculum", "grammar*.json"))):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            default_level = data.get("level", "A1") if isinstance(data, dict) else "A1"
            raw_lessons = data.get("lessons", []) if isinstance(data, dict) else []
            for idx, lsn in enumerate(raw_lessons):
                if not isinstance(lsn, dict):
                    continue
                item = dict(lsn)
                item.setdefault("id", f"{default_level}_{idx}")
                item.setdefault("level", default_level)
                item.setdefault("order", idx + 1)
                item.setdefault("title", "Урок грамматики")
                item.setdefault("explanation_ru", "")
                item.setdefault("when_to_use", "")
                item.setdefault("formula", item.get("formula_aff", ""))
                item.setdefault("affirmative", "")
                item.setdefault("negative", "")
                item.setdefault("question", "")
                item.setdefault("examples", [])
                item.setdefault("common_mistakes", [])
                item.setdefault("comparisons", [])
                item.setdefault("exercises", [])
                item.setdefault("sentence_practice", {})
                lessons.append(item)
        except Exception:
            continue

    lessons.sort(key=lambda x: (str(x.get("level", "A1")), int(x.get("order", 999))))
    return lessons


def _render_lesson_theory(lesson: dict, accent: str):
    st.markdown(f"### 📖 {lesson['title']}")
    st.caption(f"Уровень: **{lesson['level']}**")

    if lesson.get("explanation_ru"):
        st.markdown("#### 1. Суть правила")
        st.write(lesson["explanation_ru"])

    if lesson.get("when_to_use"):
        st.info(f"🕒 **Когда используется:** {lesson['when_to_use']}")

    st.markdown("#### 2. Формулы и формы (+ / − / ?)")
    if lesson.get("formula"):
        st.code(lesson["formula"], language="text")

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        if lesson.get("formula_aff"):
            st.caption("Формула (+)")
            st.code(lesson["formula_aff"], language="text")
        if lesson.get("affirmative"):
            st.markdown(f"**Утверждение (+):** {lesson['affirmative']}")
    with f_col2:
        if lesson.get("formula_neg"):
            st.caption("Формула (−)")
            st.code(lesson["formula_neg"], language="text")
        if lesson.get("negative"):
            st.markdown(f"**Отрицание (−):** {lesson['negative']}")
    with f_col3:
        if lesson.get("formula_q"):
            st.caption("Формула (?)")
            st.code(lesson["formula_q"], language="text")
        if lesson.get("question"):
            st.markdown(f"**Вопрос (?):** {lesson['question']}")

    examples = lesson.get("examples") or []
    if examples:
        st.markdown("#### 3. Примеры с переводом и озвучкой")
        for idx, ex in enumerate(examples):
            en_txt = ex.get("en", "")
            ru_txt = ex.get("ru", "")
            with st.container(border=True):
                c_left, c_right = st.columns([3, 1])
                with c_left:
                    st.markdown(f"**{en_txt}**")
                    st.write(f"🇷🇺 {ru_txt}")
                with c_right:
                    if en_txt and st.button("🔊 Озвучить", key=f"g_ex_{lesson['id']}_{idx}", use_container_width=True):
                        audio = get_audio_bytes(en_txt, accent=accent, slow=False)
                        if audio:
                            st.audio(audio, format="audio/mp3", autoplay=True)

    mistakes = lesson.get("common_mistakes") or []
    if mistakes:
        st.markdown("#### 4. Типичные ошибки")
        for m in mistakes:
            st.warning(m)

    comparisons = lesson.get("comparisons") or []
    if comparisons:
        st.markdown("#### 5. Сравнение с похожими конструкциями")
        for cmp_item in comparisons:
            st.markdown(f"- **{cmp_item.get('form', '')}** — {cmp_item.get('meaning', '')}")


def _render_lesson_practice(lesson: dict, progress: dict):
    st.markdown("#### 6. Практические упражнения")
    exercises = lesson.get("exercises") or []
    if not exercises:
        st.info("Упражнения для этого урока скоро появятся.")
        return

    for q_idx, q in enumerate(exercises):
        qid = q.get("id", f"{lesson['id']}_q{q_idx}")
        qtype = q.get("type", "choice")
        prompt = q.get("prompt", "")
        explanation = q.get("explanation", "")
        res_key = f"g_res_{qid}"

        with st.container(border=True):
            st.markdown(f"**Задание {q_idx + 1}.** {prompt}")

            if qtype == "choice":
                options = q.get("options") or []
                choice_val = st.radio(
                    "Выберите вариант:",
                    options=options,
                    key=f"g_opt_{qid}",
                    index=None,
                )
                if st.button("Проверить ответ", key=f"g_chk_{qid}", type="primary"):
                    if choice_val is None:
                        st.info("Сначала выберите один из вариантов.")
                    else:
                        is_ok = choice_val == q.get("answer")
                        st.session_state[res_key] = is_ok
                        _mark_lesson_practiced(progress, lesson["id"], is_ok)
                        if not is_ok:
                            _record_grammar_mistake(
                                progress=progress,
                                topic=lesson["title"],
                                task=prompt,
                                user_answer=choice_val,
                                correct_answer=q.get("answer", ""),
                                explanation=explanation,
                            )
                        save_progress(progress)
                        record_activity(progress, st.session_state, actions=1)

            else:
                user_inp = st.text_input("Введите ответ:", key=f"g_inp_{qid}")
                if st.button("Проверить ответ", key=f"g_chk_inp_{qid}", type="primary"):
                    accepted = q.get("accepted") or []
                    norm_user = _normalize_text(user_inp)
                    norm_acc = [_normalize_text(a) for a in accepted]
                    is_ok = bool(norm_user) and norm_user in norm_acc
                    st.session_state[res_key] = is_ok
                    _mark_lesson_practiced(progress, lesson["id"], is_ok)
                    if not is_ok:
                        correct_display = accepted[0] if accepted else ""
                        _record_grammar_mistake(
                            progress=progress,
                            topic=lesson["title"],
                            task=prompt,
                            user_answer=user_inp,
                            correct_answer=correct_display,
                            explanation=explanation,
                        )
                    save_progress(progress)
                    record_activity(progress, st.session_state, actions=1)

            if res_key in st.session_state:
                if st.session_state[res_key]:
                    st.success(f"Верно! {explanation}")
                else:
                    correct_ans = q.get("answer") if qtype == "choice" else (q.get("accepted") or [""])[0]
                    st.error(f"Есть ошибка. Правильный ответ: **{correct_ans}**. {explanation}")

    sp = lesson.get("sentence_practice") or {}
    if sp.get("prompt_ru"):
        st.markdown("#### 7. Самостоятельное составление предложения")
        sp_key = f"g_sp_res_{lesson['id']}"
        with st.container(border=True):
            st.markdown(f"**{sp['prompt_ru']}**")
            hints = sp.get("hint_words") or []
            if hints:
                st.caption("Опорные слова: " + " · ".join(hints))

            sp_inp = st.text_input("Напишите предложение целиком:", key=f"g_sp_inp_{lesson['id']}")
            if st.button("Проверить предложение", key=f"g_sp_btn_{lesson['id']}"):
                accepted = sp.get("accepted") or []
                norm_u = _normalize_text(sp_inp)
                norm_a = [_normalize_text(a) for a in accepted]
                is_ok = bool(norm_u) and norm_u in norm_a
                st.session_state[sp_key] = is_ok
                _mark_lesson_practiced(progress, lesson["id"], is_ok)
                if not is_ok:
                    _record_grammar_mistake(
                        progress=progress,
                        topic=lesson["title"],
                        task=sp["prompt_ru"],
                        user_answer=sp_inp,
                        correct_answer=sp.get("model_answer", (accepted or [""])[0]),
                        explanation=sp.get("explanation", ""),
                    )
                save_progress(progress)
                record_activity(progress, st.session_state, actions=1)

            if sp_key in st.session_state:
                if st.session_state[sp_key]:
                    st.success(f"Отлично! Эталон: **{sp.get('model_answer', '')}**. {sp.get('explanation', '')}")
                else:
                    st.error(
                        f"Попробуем ещё раз. Пример правильного варианта: **{sp.get('model_answer', '')}**. "
                        f"{sp.get('explanation', '')}"
                    )


def render_grammar(progress: dict):
    """Раздел Грамматика (A1–B2): теория, формулы, примеры и тренажёр с проверкой."""
    st.header("📐 Грамматика (A1–B2)")
    st.caption("Изучай правила по шагам, сравнивай похожие конструкции и закрепляй на практике.")

    lessons = _load_grammar_lessons()
    if not lessons:
        st.warning(
            "Уроки грамматики пока не найдены в папке `curriculum/`. "
            "Добавьте файл `curriculum/grammar_a1.json`, чтобы открыть уроки."
        )
        return

    levels = ["Все уровни"] + sorted(list({str(l.get("level", "A1")) for l in lessons}))
    col_l, col_a = st.columns([1.3, 1])
    with col_l:
        selected_level = st.selectbox("Уровень:", levels, key="gram_level_filter")
    with col_a:
        accent = st.selectbox("Озвучка примеров:", ["US (Американский)", "UK (Британский)"], key="gram_tts_accent")

    filtered_lessons = [
        l for l in lessons if selected_level == "Все уровни" or str(l.get("level", "A1")) == selected_level
    ]
    if not filtered_lessons:
        filtered_lessons = lessons

    lesson_titles = [f"[{l['level']}] {l['title']}" for l in filtered_lessons]
    selected_idx = st.selectbox(
        "Выберите тему урока:",
        options=list(range(len(filtered_lessons))),
        format_func=lambda i: lesson_titles[i],
        key="gram_lesson_select",
    )
    current_lesson = filtered_lessons[selected_idx]

    g_prog = progress.get("grammar_progress", {}).get(current_lesson["id"], {})
    st.caption(
        f"Пройдено попыток: **{g_prog.get('attempts', 0)}** | "
        f"Верных ответов: **{g_prog.get('correct', 0)}** | "
        f"Ошибок: **{g_prog.get('mistakes', 0)}**"
    )

    tab_theory, tab_practice, tab_both = st.tabs(["📚 Теория и примеры", "✍️ Тренажёр", "🔄 Теория + Практика"])
    with tab_theory:
        _render_lesson_theory(current_lesson, accent=accent)
    with tab_practice:
        _render_lesson_practice(current_lesson, progress=progress)
    with tab_both:
        _render_lesson_theory(current_lesson, accent=accent)
        st.divider()
        _render_lesson_practice(current_lesson, progress=progress)
