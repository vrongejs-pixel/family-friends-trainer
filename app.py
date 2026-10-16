import streamlit as st
import pandas as pd
import random

# Настройка страницы
st.set_page_config(page_title="Family & Friends 2 Trainer | Методика Лайло Алимжановой", page_icon="🎒", layout="wide")

# Инициализация базы данных учеников и статистики
if "users" not in st.session_state:
    st.session_state.users = {
        "Алишер": {"score": 120, "cards_learned": 15, "grammar_solved": 8, "homework": "Выполнено (95%)", "unit": 9},
        "Мадина": {"score": 150, "cards_learned": 22, "grammar_solved": 14, "homework": "Выполнено (100%)", "unit": 10},
        "Тимур": {"score": 90, "cards_learned": 8, "grammar_solved": 5, "homework": "Не выполнено", "unit": 8}
    }

# База слов, грамматики и подробных подсказок (правил) из книги
if "dictionary" not in st.session_state:
    st.session_state.dictionary = {
        "Unit 9 (Jobs & Work)": {
            "words": [
                {"en": "fireman", "ru": "пожарный"},
                {"en": "postman", "ru": "почтальон"},
                {"en": "pilot", "ru": "пилот"}
            ],
            "rule_title": "Грамматика: Описание профессий и мест работы",
            "rule_text": "Для вопроса о работе используется вспомогательный глагол **does** (для he/she/it):\n- *Where does he work?* — Он работает в аэропорту (*He works in an airport*).\n- *Does she work in a shop?* — Да/Нет (*Yes, she does / No, she doesn't*)."
        },
        "Unit 10 (Weather & Clothes)": {
            "words": [
                {"en": "sunny", "ru": "солнечно"},
                {"en": "coat", "ru": "пальто"},
                {"en": "sun hat", "ru": "солнечная шляпа"}
            ],
            "rule_title": "Грамматика: Погода и побудительные предложения",
            "rule_text": "Для указания погоды используем *It's...* (например, *It's sunny* — солнечно).\nДля советов по одежде используем повелительное наклонение:\n- **Put on** your sun hat. (Надень...)\n- **Don't put on** your coat. (Не надевай...)"
        },
        "Unit 11 (What are you wearing?)": {
            "words": [
                {"en": "skirt", "ru": "юбка"},
                {"en": "gloves", "ru": "перчатки"},
                {"en": "jeans", "ru": "джинсы"}
            ],
            "rule_title": "Грамматика: Что ты ноишь (Present Continuous)",
            "rule_text": "Для описания одежды в данный момент используем глагол *to be + verb-ing*:\n- *What are you wearing?* — *I'm wearing a blue skirt.*\n- *What's he wearing?* — *He's wearing red gloves.*"
        },
        "Unit 13 (Comparisons)": {
            "words": [
                {"en": "bigger", "ru": "больше"},
                {"en": "shorter", "ru": "короче / ниже"}
            ],
            "rule_title": "Грамматика: Сравнительная степень прилагательных",
            "rule_text": "Чтобы сравнить два предмета или человека, к короткому прилагательному добавляется суффикс **-er** и слово **than** (чем):\n- *The sheep is **bigger than** the goat.*\n- *The boy is **shorter than** the girl.*"
        }
    }

# --- АВТОРСКАЯ ШАПКА ПРИЛОЖЕНИЯ ---
st.markdown("<h1 style='text-align: center; color: #2e6c80;'>🎒 Family and Friends 2 — Интерактивный тренажер</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555;'>Методика и исследования учителя английского языка школы №20 <b>Лайло Алимжановой</b></h3>", unsafe_allow_html=True)
st.markdown("---")

role = st.sidebar.radio("Выберите режим:", ["👦 Режим ученика (Тренажер)", "👨‍🏫 Кабинет преподавателя", "🏆 Рейтинг и Призы"])

# ---------------------------------------------------------
# 1. КАБИНЕТ ПРЕПОДАВАТЕЛЯ
# ---------------------------------------------------------
if role == "👨‍🏫 Кабинет преподавателя":
    st.title("👨‍🏫 Кабинет преподавателя")
    password = st.text_input("Введите пароль преподавателя:", type="password")
    
    if password == "school20":
        st.success("Доступ разрешен!")
        new_student_name = st.text_input("Имя нового ученика:")
        if st.button("Зарегистрировать ученика"):
            if new_student_name and new_student_name not in st.session_state.users:
                st.session_state.users[new_student_name] = {"score": 0, "cards_learned": 0, "grammar_solved": 0, "homework": "Не начато", "unit": 1}
                st.success(f"Ученик {new_student_name} добавлен!")
        
        report_data = [{"Ученик": name, "Баллы (XP)": info["score"], "Карточки": info["cards_learned"], "Грамматика": info["grammar_solved"], "ДЗ": info["homework"]} for name, info in st.session_state.users.items()]
        st.dataframe(pd.DataFrame(report_data), use_container_width=True)
    elif password != "":
        st.error("Неверный пароль!")

# ---------------------------------------------------------
# 2. РЕЖИМ УЧЕНИКА
# ---------------------------------------------------------
elif role == "👦 Режим ученика (Тренажер)":
    st.title("🎮 Ученический тренажер слов и грамматики")
    
    if not st.session_state.users:
        st.warning("Список учеников пуст.")
    else:
        student_name = st.selectbox("Выберите ваше имя:", list(st.session_state.users.keys()))
        selected_unit = st.selectbox("Выберите тему / юнит:", list(st.session_state.dictionary.keys()))
        
        user_info = st.session_state.users[student_name]
        st.info(f"👤 **{student_name}** | ⭐️ Баллы: **{user_info['score']} XP** | 🃏 Выучено карточек: **{user_info['cards_learned']}** | 📝 Решено грамматики: **{user_info['grammar_solved']}**")

        tab1, tab2 = st.tabs(["🃏 Компактные карточки", "📝 Упражнения и Подсказки"])
        unit_data = st.session_state.dictionary[selected_unit]
        words_list = unit_data["words"]
        
        # --- ВКЛАДКА 1: КОМПАКТНЫЕ КАРТОЧКИ ПО ЦЕНТРУ С ПЕРЕВОРОТОМ ---
        with tab1:
            st.subheader("🃏 Карточки для запоминания слов")
            
            if f"card_idx_{selected_unit}" not in st.session_state:
                st.session_state[f"card_idx_{selected_unit}"] = 0
            
            idx = st.session_state[f"card_idx_{selected_unit}"]
            current_card = words_list[idx]
            
            if f"is_flipped_{selected_unit}_{idx}" not in st.session_state:
                st.session_state[f"is_flipped_{selected_unit}_{idx}"] = False
            
            is_flipped = st.session_state[f"is_flipped_{selected_unit}_{idx}"]
            
            # CSS для красивой компактной карточки по центру с анимацией переворота
            st.markdown("""
            <style>
            .card-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 20px 0;
            }
            .flashcard {
                width: 350px;
                height: 200px;
                background: linear-gradient(135deg, #2e6c80 0%, #4682b4 100%);
                color: white;
                border-radius: 15px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                font-family: sans-serif;
                text-align: center;
                padding: 20px;
                transition: transform 0.6s;
            }
            .card-title {
                font-size: 16px;
                opacity: 0.8;
                margin-bottom: 10px;
            }
            .card-word {
                font-size: 36px;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Отображение лицевой или оборотной стороны карточки
            word_display = current_card['ru'] if is_flipped else current_card['en']
            title_display = "🇷🇺 Перевод на русском:" if is_flipped else "🇬🇧 Английское слово:"
            
            st.markdown(f"""
            <div class="card-container">
                <div class="flashcard">
                    <div class="card-title">{title_display}</div>
                    <div class="card-word">{word_display}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("🔄 Перевернуть карточку"):
                    st.session_state[f"is_flipped_{selected_unit}_{idx}"] = not is_flipped
                    st.rerun()
            with col_c2:
                if is_flipped and st.button("✅ Я вспомнил (+10 XP)"):
                    st.session_state.users[student_name]["score"] += 10
                    st.session_state.users[student_name]["cards_learned"] += 1
                    st.session_state[f"is_flipped_{selected_unit}_{idx}"] = False
                    st.session_state[f"card_idx_{selected_unit}"] = (idx + 1) % len(words_list)
                    st.rerun()

        # --- ВКЛАДКА 2: УПРАЖНЕНИЯ С КНОПКОЙ ПОДСКАЗКИ / ПРАВИЛА ---
        with tab2:
            st.subheader("📝 Упражнения по грамматике и лексике")
            
            # Кнопка подсказки (теория и примеры по аналогии с приложением)
            with st.expander("💡 Нажмите здесь, чтобы открыть Подсказку и Правило по уроку"):
                st.markdown(f"### {unit_data['rule_title']}")
                st.markdown(unit_data['rule_text'])
            
            current_item = random.choice(words_list)
            st.markdown(f"**Переведите слово на русский язык:** `{current_item['en']}`")
            
            user_ans = st.text_input("Ваш ответ:", key=f"ans_{selected_unit}")
            if st.button("Проверить упражнение"):
                if user_ans.strip().lower() == current_item['ru'].lower():
                    st.success("🎉 Верно! Отличная работа.")
                    st.session_state.users[student_name]["score"] += 15
                    st.session_state.users[student_name]["grammar_solved"] += 1
                    st.session_state.users[student_name]["homework"] = "Выполнено (100%)"
                else:
                    st.error(f"❌ Неверно. Правильный ответ: **{current_item['ru']}**")

# ---------------------------------------------------------
# 3. РЕЙТИНГ И ПРИЗЫ
# ---------------------------------------------------------
elif role == "🏆 Рейтинг и Призы":
    st.title("🏆 Доска почета и призы по итогам курса")
    sorted_users = sorted(st.session_state.users.items(), key=lambda x: x[1]["score"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    
    for rank, (name, info) in enumerate(sorted_users):
        medal = medals[rank] if rank < 3 else "🏅"
        st.markdown(### `{medal} {rank+1} место: {name}` — **{info['score']} XP** (Карточки: {info['cards_learned']}, Грамматика: {info['grammar_solved']})")
        if rank == 0:
            st.balloons()
            st.success("🎁 Главный приз от Лайло Алимжановой — Книга комиксов на английском языке!")
