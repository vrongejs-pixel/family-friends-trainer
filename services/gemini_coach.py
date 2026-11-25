import json
import os
import re
from datetime import datetime
import urllib.error
import urllib.request
import streamlit as st
from services.storage import save_progress
from services.progress_tracker import record_activity


DEFAULT_MODEL = "gemini-3.8-flash"


def _get_api_key() -> str:
    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return str(st.secrets["GEMINI_API_KEY"]).strip().strip('"').strip("'")
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "").strip().strip('"').strip("'")


def _get_model_name() -> str:
    try:
        if "GEMINI_MODEL" in st.secrets and st.secrets["GEMINI_MODEL"]:
            return str(st.secrets["GEMINI_MODEL"]).strip().strip('"').strip("'")
    except Exception:
        pass
    return os.environ.get("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _normalize(text: str) -> str:
    text = (text or "").lower().strip()
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[.,!?;:\"\(\)\-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_json(raw_text: str) -> dict | list | None:
    if not raw_text:
        return None
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    match = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            return None
    return None


def _send_gemini_request(url: str, headers: dict, payload: dict) -> tuple[bool, str]:
    req = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=35) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        candidates = body.get("candidates") or []
        if not candidates:
            return False, "Модель вернула пустой ответ. Попробуйте ещё раз."
        parts = ((candidates[0].get("content") or {}).get("parts")) or []
        text_out = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
        if not text_out:
            return False, "Не удалось прочитать текст ответа от Gemini."
        return True, text_out
    except urllib.error.HTTPError as e:
        err_detail = e.read().decode("utf-8", errors="ignore")
        return False, f"Ошибка Gemini API ({e.code}): {err_detail[:250]}"
    except Exception as e:
        return False, f"Ошибка подключения к Gemini API: {e}"


def ask_gemini(prompt: str, system_instruction: str = "", expect_json: bool = False) -> tuple[bool, str]:
    api_key = _get_api_key()
    if not api_key:
        return False, "Не найден GEMINI_API_KEY. Добавьте его в Secrets приложения на Streamlit Cloud."

    model = _get_model_name()
    base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    payload: dict = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.6 if expect_json else 0.7,
        },
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
    if expect_json:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    if api_key.startswith("AQ."):
        ok, res = _send_gemini_request(
            url=base_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            payload=payload,
        )
        if ok:
            return True, res
        return _send_gemini_request(
            url=f"{base_url}?key={api_key}",
            headers={"Content-Type": "application/json"},
            payload=payload,
        )

    return _send_gemini_request(
        url=f"{base_url}?key={api_key}",
        headers={"Content-Type": "application/json"},
        payload=payload,
    )


def _log_mistake(progress: dict, topic: str, task: str, user_ans: str, correct_ans: str, explanation: str):
    mistakes = progress.setdefault("mistakes_log", [])
    mistakes.append(
        {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "topic": topic,
            "task": task,
            "user_answer": str(user_ans),
            "correct_answer": str(correct_ans),
            "explanation": explanation,
        }
    )


def render_gemini_practice_lab(progress: dict, scope_key: str = "main", default_topic: str = "Present Simple & Past Simple"):
    st.subheader("♾️ Бесконечная практика и жизненные ситуации (Gemini)")
    st.caption("Генерируй свежие задания, жизненные диалоги и слова под нужный момент без ограничения по числу попыток.")

    if not _get_api_key():
        st.info(
            "Чтобы включить бесконечную генерацию, добавьте `GEMINI_API_KEY` в **Settings → Secrets** "
            "на Streamlit Cloud и перезапустите приложение."
        )
        return

    recent_mistakes = progress.get("mistakes_log", [])[-5:]
    mistake_hint = "; ".join(
        f"{m.get('topic', '')}: {m.get('task', '')} (ошибка: {m.get('user_answer', '')})"
        for m in recent_mistakes
    )

    c1, c2, c3 = st.columns([1.4, 1, 1.2])
    with c1:
        topic_or_situation = st.text_input(
            "Тема грамматики или жизненный момент:",
            value=default_topic,
            placeholder="Например: собеседование, склад, аренда жилья, поход к врачу, Past Simple...",
            key=f"gem_topic_{scope_key}",
        )
    with c2:
        level = st.selectbox(
            "Уровень:",
            ["A1", "A2", "B1", "B2"],
            index=1,
            key=f"gem_level_{scope_key}",
        )
    with c3:
        mode = st.selectbox(
            "Что сгенерировать:",
            ["Упражнения на закрепление", "Жизненный сценарий и диалог", "Словарь и фразы под ситуацию"],
            key=f"gem_mode_{scope_key}",
        )

    focus_mistakes = st.checkbox(
        "Учитывать мои последние ошибки для закрепления",
        value=bool(recent_mistakes),
        key=f"gem_use_mistakes_{scope_key}",
    )

    gen_key = f"gem_data_{scope_key}"
    if st.button("⚡ Сгенерировать свежий пакет", type="primary", key=f"gem_gen_btn_{scope_key}"):
        clean_topic = topic_or_situation.strip() or "Повседневное общение и работа"
        m_context = f"\nНедавние ошибки ученика для усиления: {mistake_hint}" if (focus_mistakes and mistake_hint) else ""

        if mode == "Упражнения на закрепление":
            prompt = (
                f"Создай 5 практических упражнений на русском языке для изучения английского на уровне {level} "
                f"по теме/ситуации: '{clean_topic}'.{m_context}\n"
                "Верни ТОЛЬКО валидный JSON-объект вида:\n"
                '{"title": "Название", "exercises": ['
                '{"id": "ex1", "prompt": "Задание на русском с английской фразой или переводом", '
                '"options": ["вариант 1", "вариант 2", "вариант 3", "вариант 4"], '
                '"answer": "точный правильный вариант из options", '
                '"explanation": "Короткое понятное объяснение на русском"}'
                "]}"
            )
            with st.spinner("Gemini готовит новые упражнения..."):
                ok, res = ask_gemini(
                    prompt=prompt,
                    system_instruction="Ты методист английского языка. Отвечай строго в запрошенном JSON-формате на русском языке.",
                    expect_json=True,
                )
            parsed = _extract_json(res) if ok else None
            if ok and isinstance(parsed, dict) and isinstance(parsed.get("exercises"), list):
                st.session_state[gen_key] = {"kind": "exercises", "payload": parsed}
                record_activity(progress, st.session_state, actions=1)
                save_progress(progress)
            else:
                st.error(res if not ok else "Не удалось разобрать ответ модели. Нажмите сгенерировать ещё раз.")

        elif mode == "Жизненный сценарий и диалог":
            prompt = (
                f"Составь реалистичный жизненный сценарий на английском с переводом на русский для уровня {level} "
                f"по ситуации: '{clean_topic}'.{m_context}\n"
                "Верни ТОЛЬКО валидный JSON-объект вида:\n"
                '{"situation_title": "Название ситуации", "context_ru": "Когда и где это происходит", '
                '"dialogue": [{"speaker": "Роль", "en": "Фраза на английском", "ru": "Перевод на русский"}], '
                '"key_phrases": [{"en": "Полезная фраза", "ru": "Перевод", "tip": "Когда использовать"}], '
                '"mini_task_ru": "Переведи на английский или ответь на ситуацию", '
                '"sample_answer_en": "Пример хорошего ответа на английском"}'
            )
            with st.spinner("Gemini собирает жизненный сценарий..."):
                ok, res = ask_gemini(
                    prompt=prompt,
                    system_instruction="Ты практический преподаватель английского для жизни и работы. Отвечай строго в JSON.",
                    expect_json=True,
                )
            parsed = _extract_json(res) if ok else None
            if ok and isinstance(parsed, dict):
                st.session_state[gen_key] = {"kind": "scenario", "payload": parsed}
                record_activity(progress, st.session_state, actions=1)
                save_progress(progress)
            else:
                st.error(res if not ok else "Не удалось разобрать сценарий. Попробуйте ещё раз.")

        else:
            prompt = (
                f"Подбери 8 полезных слов и устойчивых выражений по теме/ситуации '{clean_topic}' для уровня {level}.{m_context}\n"
                "Верни ТОЛЬКО валидный JSON-объект вида:\n"
                '{"topic": "Тема", "items": ['
                '{"word": "слово или фраза", "ipa": "/транскрипция/", "translation_ru": "перевод", '
                '"example_en": "пример предложения", "example_ru": "перевод примера"}'
                "]}"
            )
            with st.spinner("Gemini подбирает слова и выражения..."):
                ok, res = ask_gemini(
                    prompt=prompt,
                    system_instruction="Ты составитель словарных подборок английского языка. Отвечай строго в JSON.",
                    expect_json=True,
                )
            parsed = _extract_json(res) if ok else None
            if ok and isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
                st.session_state[gen_key] = {"kind": "vocab", "payload": parsed}
                record_activity(progress, st.session_state, actions=1)
                save_progress(progress)
            else:
                st.error(res if not ok else "Не удалось разобрать подборку слов. Попробуйте ещё раз.")

    saved = st.session_state.get(gen_key)
    if not saved:
        return

    kind = saved.get("kind")
    data = saved.get("payload") or {}

    if kind == "exercises":
        st.markdown(f"### 📝 {data.get('title', 'Практика')}")
        for idx, ex in enumerate(data.get("exercises") or []):
            qid = f"{scope_key}_{ex.get('id', idx)}_{idx}"
            opts = ex.get("options") or []
            ans = ex.get("answer", "")
            expl = ex.get("explanation", "")
            with st.container(border=True):
                st.markdown(f"**{idx + 1}. {ex.get('prompt', '')}**")
                choice = st.radio("Выберите ответ:", options=opts, index=None, key=f"gem_opt_{qid}")
                if st.button("Проверить", key=f"gem_chk_{qid}", type="primary"):
                    if choice is None:
                        st.info("Выберите вариант ответа.")
                    else:
                        is_ok = _normalize(choice) == _normalize(ans)
                        st.session_state[f"gem_ans_{qid}"] = is_ok
                        if not is_ok:
                            _log_mistake(
                                progress=progress,
                                topic=f"AI-практика: {data.get('title', 'Практика')}",
                                task=ex.get("prompt", ""),
                                user_ans=choice,
                                correct_ans=ans,
                                explanation=expl,
                            )
                        save_progress(progress)
                        record_activity(progress, st.session_state, actions=1)

                if f"gem_ans_{qid}" in st.session_state:
                    if st.session_state[f"gem_ans_{qid}"]:
                        st.success(f"Верно! {expl}")
                    else:
                        st.error(f"Неверно. Правильный ответ: **{ans}**. {expl}")

    elif kind == "scenario":
        st.markdown(f"### 🎭 {data.get('situation_title', 'Жизненный сценарий')}")
        if data.get("context_ru"):
            st.info(data["context_ru"])

        for line in data.get("dialogue") or []:
            st.markdown(f"**{line.get('speaker', 'Собеседник')}:** {line.get('en', '')}")
            st.caption(f"🇷🇺 {line.get('ru', '')}")

        key_phrases = data.get("key_phrases") or []
        if key_phrases:
            st.markdown("#### Ключевые фразы")
            for kp in key_phrases:
                st.markdown(f"- **{kp.get('en', '')}** — {kp.get('ru', '')} *({kp.get('tip', '')})*")

        if data.get("mini_task_ru"):
            st.markdown("#### Проверка на практике")
            st.write(data["mini_task_ru"])
            user_try = st.text_input("Ваш вариант на английском:", key=f"gem_sc_inp_{scope_key}")
            if st.button("Проверить мой ответ с Gemini", key=f"gem_sc_btn_{scope_key}"):
                if not user_try.strip():
                    st.info("Напишите ваш вариант ответа.")
                else:
                    fb_prompt = (
                        f"Задача: {data.get('mini_task_ru')}\n"
                        f"Эталон: {data.get('sample_answer_en')}\n"
                        f"Ответ ученика: {user_try}\n"
                        "Оцени ответ на русском языке: что верно, есть ли ошибки и как сказать естественно."
                    )
                    with st.spinner("Gemini проверяет ваш ответ..."):
                        ok, fb = ask_gemini(fb_prompt)
                    if ok:
                        st.markdown(fb)
                    else:
                        st.error(fb)

    elif kind == "vocab":
        st.markdown(f"### 📚 Словарь к ситуации: {data.get('topic', '')}")
        for item in data.get("items") or []:
            with st.container(border=True):
                st.markdown(f"**{item.get('word', '')}** `{item.get('ipa', '')}` — **{item.get('translation_ru', '')}**")
                st.write(f"Пример: *{item.get('example_en', '')}*")
                st.caption(f"🇷🇺 {item.get('example_ru', '')}")
