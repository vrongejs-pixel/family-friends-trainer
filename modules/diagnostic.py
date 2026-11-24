import json
import os
import re
import streamlit as st
from datetime import datetime
from services.storage import save_progress
from services.progress_tracker import record_activity


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[.,!?;:'\"()\-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _load_diagnostic_data() -> dict:
    path = os.path.join("curriculum", "diagnostic.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _calculate_skill_level(correct: int, total: int) -> str:
    if total == 0:
        return "Не определён"
    ratio = correct / total
    if ratio < 0.4:
        return "Pre-A1 (Начальный с нуля)"
    elif ratio < 0.75:
        return "A1 (Базовый начальный)"
    else:
        return "A2 (Уверенный базовый — требуется проверка B1)"


def render_diagnostic(progress: dict):
    st.header("🧭 Диагностика знаний")
    st.write(
        "Перед началом обучения система проверит твои реальные знания по небольшим блокам. "
        "Не угадывай наугад — если не знаешь ответ, лучше выбрать «Не знаю» или пропустить, "
        "чтобы программа составила честный маршрут обучения."
    )

    data = _load_diagnostic_data()
    blocks = data["blocks"]

    if "diag_step" not in st.session_state:
        st.session_state.diag_step = 0
    if "diag_answers" not in st.session_state:
        st.session_state.diag_answers = {}
    if "diag_checked" not in st.session_state:
        st.session_state.diag_checked = {}

    total_blocks = len(blocks)
    step = st.session_state.diag_step

    st.progress(min(step / total_blocks, 1.0), text=f"Шаг {min(step + 1, total_blocks)} из {total_blocks}")

    if step < total_blocks:
        block = blocks[step]
        st.subheader(block["title"])
        st.caption(block["description"])

        if "passage" in block:
            st.info(f"📖 **Прочитайте текст:**\n\n{block['passage']}")

        for q in block["questions"]:
            qid = q["id"]
            st.markdown(f"**{q['prompt']}**")
            if q["type"] == "choice":
                options = ["— Не знаю / Пропустить —"] + q["options"]
                st.radio(
                    label="Выберите вариант:",
                    options=options,
                    key=f"input_{qid}",
                    label_visibility="collapsed",
                )
            elif q["type"] == "input":
                st.text_input(
                    label="Ваш ответ на английском:",
                    key=f"input_{qid}",
                    placeholder="Введите ответ здесь...",
                )
            st.write("")

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("Проверить блок", type="primary", use_container_width=True):
                record_activity(progress, st.session_state, actions=len(block["questions"]))
                st.session_state.diag_checked[block["id"]] = True
                for q in block["questions"]:
                    qid = q["id"]
                    val = st.session_state.get(f"input_{qid}", "")
                    st.session_state.diag_answers[qid] = val

        if st.session_state.diag_checked.get(block["id"]):
            st.divider()
            st.markdown("### Разбор ответов этого блока:")
            for q in block["questions"]:
                qid = q["id"]
                user_ans = st.session_state.diag_answers.get(qid, "")
                is_correct = False

                if q["type"] == "choice":
                    is_correct = user_ans == q["answer"]
                    right_display = q["answer"]
                else:
                    norm_user = _normalize(user_ans)
                    is_correct = norm_user in [_normalize(a) for a in q["accepted"]]
                    right_display = q["accepted"][0]

                if is_correct:
                    st.success(f"✅ **{q['prompt']}**\n\nВаш ответ: `{user_ans}` — Верно! {q['explanation']}")
                else:
                    shown_user = user_ans if user_ans and user_ans != "— Не знаю / Пропустить —" else "Нет ответа"
                    st.error(
                        f"❌ **{q['prompt']}**\n\n"
                        f"Ваш ответ: `{shown_user}` | Правильный ответ: **`{right_display}`**\n\n"
                        f"💡 *Объяснение:* {q['explanation']}"
                    )

            if st.button("Перейти к следующему блоку ➡️", type="primary"):
                st.session_state.diag_step += 1
                st.rerun()

    else:
        st.success("🎉 Диагностика завершена!")
        skill_scores = {
            "vocabulary": [0, 0],
            "grammar": [0, 0],
            "reading": [0, 0],
            "writing": [0, 0],
        }
        new_mistakes = []

        for block in blocks:
            sk = block["skill"]
            for q in block["questions"]:
                qid = q["id"]
                user_ans = st.session_state.diag_answers.get(qid, "")
                skill_scores[sk][1] += 1

                if q["type"] == "choice":
                    ok = user_ans == q["answer"]
                    right_str = q["answer"]
                else:
                    ok = _normalize(user_ans) in [_normalize(a) for a in q["accepted"]]
                    right_str = q["accepted"][0]

                if ok:
                    skill_scores[sk][0] += 1
                else:
                    new_mistakes.append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "topic": block["title"],
                        "task": q["prompt"],
                        "user_answer": user_ans if user_ans else "Пропущено",
                        "correct_answer": right_str,
                        "explanation": q["explanation"],
                        "status": "Не исправлено",
                    })

        focus_areas = []
        for sk, (corr, tot) in skill_scores.items():
            lvl = _calculate_skill_level(corr, tot)
            progress["skill_levels"][sk] = lvl
            if corr < tot:
                focus_areas.append(sk)

        progress["skill_levels"]["listening"] = "Ожидает проверки (Этап 7)"
        progress["skill_levels"]["speaking"] = "Ожидает проверки (Этап 7)"

        total_corr = sum(v[0] for v in skill_scores.values())
        total_q = sum(v[1] for v in skill_scores.values())
        progress["overall_level"] = _calculate_skill_level(total_corr, total_q)
        progress["diagnostic_completed"] = True
        progress["diagnostic_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        progress["diagnostic_raw_scores"] = skill_scores
        progress["focus_areas"] = focus_areas

        existing_tasks = {m["task"] for m in progress.get("mistakes_log", [])}
        for m in new_mistakes:
            if m["task"] not in existing_tasks:
                progress["mistakes_log"].append(m)

        save_progress(progress)

        st.subheader("📊 Результаты по навыкам")
        skill_names_ru = {
            "vocabulary": "Словарный запас",
            "grammar": "Грамматика",
            "reading": "Чтение",
            "writing": "Письмо (перевод)",
        }
        for sk, label in skill_names_ru.items():
            c, t = skill_scores[sk]
            st.write(f"- **{label}:** {c} из {t} → **{progress['skill_levels'][sk]}**")

        st.info(
            "Важно: по правилам метода Холмата система не завышает уровень искусственно. "
            "Даже при хороших ответах на базовые тесты мы начинаем с укрепления фундамента A1–A2."
        )

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Перейти на Главную панель 🏠", type="primary", use_container_width=True):
                st.session_state.diag_step = 0
                st.session_state.diag_answers = {}
                st.session_state.diag_checked = {}
                st.session_state.current_page = "Главная панель"
                st.rerun()
        with col_b:
            if st.button("Пройти диагностику заново 🔄", use_container_width=True):
                st.session_state.diag_step = 0
                st.session_state.diag_answers = {}
                st.session_state.diag_checked = {}
                st.rerun()
