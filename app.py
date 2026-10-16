import streamlit as st
import pandas as pd
import random

# Настройка страницы
st.set_page_config(page_title="Family & Friends 2 Trainer | Методика Алимжановой Л.Х.", page_icon="🎒", layout="wide")

# Инициализация базы данных учеников и статистики
if "users" not in st.session_state:
    st.session_state.users = {
        "Алишер": {"score": 120, "cards_learned": 15, "grammar_solved": 8, "homework": "Выполнено (95%)", "unit": "Unit 1"},
        "Мадина": {"score": 150, "cards_learned": 22, "grammar_solved": 14, "homework": "Выполнено (100%)", "unit": "Unit 2"},
        "Тимур": {"score": 90, "cards_learned": 8, "grammar_solved": 5, "homework": "Не выполнено", "unit": "Starter"}
    }

# СТРОГАЯ БАЗА СЛОВ И ГРАММАТИЧЕСКИХ ЗАДАНИЙ ИЗ КНИГИ (Let's learn! & Write)
if "dictionary" not in st.session_state:
    st.session_state.dictionary = {
        "Starter Unit (Welcome back!)": {
            "words": [
                {"en": "mum", "ru": "мама"}, {"en": "dad", "ru": "папа"}, {"en": "brother", "ru": "брат"},
                {"en": "sister", "ru": "сестра"}, {"en": "grandma", "ru": "бабушка"}, {"en": "grandpa", "ru": "дедушка"}
            ],
            "rule_title": "Грамматика: I've got / He's got / She's got",
            "rule_text": "Используйте **'ve got** (have got) для I/you/we/they и **'s got** (has got) для he/she/it.\n\n*Примеры:*\n- I've got brown hair.\n- He's got green eyes.",
            "grammar_tasks": [
                {"task": "Вставьте правильную форму: I [...] brown hair.", "answer": "'ve got"},
                {"task": "Вставьте правильную форму: He [...] green eyes.", "answer": "'s got"},
                {"task": "Вставьте правильную форму: She [...] curly hair.", "answer": "'s got"}
            ]
        },
        "Unit 1 (Our new things)": {
            "words": [
                {"en": "classroom", "ru": "класс (комната)"}, {"en": "table", "ru": "стол"}, {"en": "computer", "ru": "компьютер"},
                {"en": "peg", "ru": "вешалка"}, {"en": "pencil case", "ru": "пенал"}, {"en": "board", "ru": "доска"}
            ],
            "rule_title": "Грамматика: This / That / These / Those",
            "rule_text": "Указательные местоимения (стр. 9):\n- **This** is the new computer. (Это — ед.ч., близко)\n- **That** is a new board. (То — ед.ч., далеко)\n- **These** are new tables. (Эти — мн.ч., близко)\n- **Those** are new pegs. (Те — мн.ч., далеко)",
            "grammar_tasks": [
                {"task": "Вставьте (This / That / These / Those): [...] is the new computer. (близко, ед.ч.)", "answer": "this"},
                {"task": "Вставьте (This / That / These / Those): [...] is a new board. (далеко, ед.ч.)", "answer": "that"},
                {"task": "Вставьте (This / That / These / Those): [...] are new tables. (близко, мн.ч.)", "answer": "these"},
                {"task": "Вставьте (This / That / These / Those): [...] are new pegs. (далеко, мн.ч.)", "answer": "those"}
            ]
        },
        "Unit 2 (They're happy now!)": {
            "words": [
                {"en": "hot", "ru": "жарко"}, {"en": "cold", "ru": "холодно"}, {"en": "hungry", "ru": "голодный"},
                {"en": "thirsty", "ru": "хочу пить"}, {"en": "happy", "ru": "счастливый"}, {"en": "sad", "ru": "грустный"}
            ],
            "rule_title": "Грамматика: We're / They're & Are they...?",
            "rule_text": "Глагол to be во множественном числе (стр. 15):\n- We're = We are (Мы)\n- They're = They are (Они)\n*Вопросы и ответы:*\n- Are they hot? No, they aren't.\n- Are they happy? Yes, they are.",
            "grammar_tasks": [
                {"task": "Напишите сокращение для 'They are': [...]", "answer": "they're"},
                {"task": "Напишите сокращение для 'We are': [...]", "answer": "we're"},
                {"task": "Ответьте на вопрос (Are they hot?): Yes, they [...].", "answer": "are"},
                {"task": "Ответьте на вопрос (Are they cold?): No, they [...].", "answer": "aren't"}
            ]
        },
        "Unit 3 (I can ride a bike!)": {
            "words": [
                {"en": "ride a bike", "ru": "кататься на велосипеде"}, {"en": "skate", "ru": "кататься на коньках"},
                {"en": "skateboard", "ru": "кататься на скейтборде"}, {"en": "play tennis", "ru": "играть в теннис"}
            ],
            "rule_title": "Грамматика: Can / Can't",
            "rule_text": "Выражение умений (стр. 21):\n- I **can** skate. (Я умею)\n- I **can't** skateboard. (Я не умею)\n- **Can** he ride a bike? No, he can't.\n- **Can** she play tennis? Yes, she can.",
            "grammar_tasks": [
                {"task": "Вставьте (can / can't): He [...] ride a bike. (Умеет)", "answer": "can"},
                {"task": "Вставьте (can / can't): He [...] ride a horse. (Не умеет)", "answer": "can't"},
                {"task": "Вставьте (can / can't): They [...] play football. (Не умеют)", "answer": "can't"},
                {"task": "Ответьте на вопрос (Can she play tennis?): Yes, she [...].", "answer": "can"}
            ]
        },
        "Unit 4 (Have you got a milkshake?)": {
            "words": [
                {"en": "salad", "ru": "салат"}, {"en": "fries", "ru": "картофель фри"}, {"en": "pizza", "ru": "пицца"},
                {"en": "milkshake", "ru": "молочный коктейль"}, {"en": "cheese sandwich", "ru": "бутерброд с сыром"}
            ],
            "rule_title": "Грамматика: Have you got...? / Has he got...?",
            "rule_text": "Вопросы о наличии (стр. 31):\n- **Have you got** a milkshake? Yes, I have. / No, I haven't.\n- **Has he got** a cheese sandwich? Yes, he has.\n- **Has she got** a pizza? No, she hasn't.",
            "grammar_tasks": [
                {"task": "Ответьте на вопрос (Have you got a milkshake?): Yes, I [...].", "answer": "have"},
                {"task": "Ответьте на вопрос (Have you got fries?): No, I [...].", "answer": "haven't"},
                {"task": "Ответьте на вопрос (Has he got a cheese sandwich?): Yes, he [...].", "answer": "has"},
                {"task": "Ответьте на вопрос (Has she got a pizza?): No, she [...].", "answer": "hasn't"}
            ]
        }
    }

# --- АВТОРСКАЯ ШАПКА ПРИЛОЖЕНИЯ ---
st.markdown("<h1 style='text-align: center; color: #2e6c80;'>✨ Интерактивная обучающая платформа Family and Friends 2</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555;'>Инновационная методика учителя английского языка школы №20 <b>Алимжановой Лайло Хамадуллаевной</b></h3>", unsafe_allow_html=True)
st.markdown("---")

role = st.sidebar.radio("Выберите режим:", ["👦 Режим ученика (Тренажер)", "👨‍🏫 Кабинет преподавателя", "🏆 Рейтинг и Призы"])

# ---------------------------------------------------------
# 1. КАБИНЕТ ПРЕПОДАВАТЕЛЯ
# ---------------------------------------------------------
if role == "👨‍🏫 Кабинет преподавателя":
    st.title("👨‍🏫 Кабинет преподавателя")
    st.info("Раздел для автора методики — Алимжановой Лайло Хамадуллаевной.")
    password = st.text_input("Введите пароль преподавателя:", type="password")
    
    if password == "school20":
        st.success("Доступ разрешен!")
        
        st.subheader("➕ Добавить нового ученика")
        col1, col2 = st.columns(2)
        with col1:
            new_student_name = st.text_input("Имя нового ученика:")
            if st.button("Зарегистрировать ученика"):
                if new_student_name and new_student_name not in st.session_state.users:
                    st.session_state.users[new_student_name] = {"score": 0, "cards_learned": 0, "grammar_solved": 0, "homework": "Не начато", "unit": "Unit 1"}
                    st.success(f"Ученик {new_student_name} успешно добавлен!")
                else:
                    st.warning("Введите имя или такое имя уже существует.")
        
        st.subheader("📊 Отчет по успеваемости и практике")
        report_data = [{"Ученик": name, "Баллы (XP)": info["score"], "Выучено карточек": info["cards_learned"], "Решено грамматики": info["grammar_solved"], "Статус ДЗ": info["homework"]} for name, info in st.session_state.users.items()]
        st.dataframe(pd.DataFrame(report_data), use_container_width=True)
        
    elif password != "":
        st.error("Неверный пароль!")

# ---------------------------------------------------------
# 2. РЕЖИМ УЧЕНИКА
# ---------------------------------------------------------
elif role == "👦 Режим ученика (Тренажер)":
    st.title("🎮 Ученический тренажер слов и грамматики")
    
    if not st.session_state.users:
        st.warning("Список учеников пуст. Попросите преподавателя добавить ваше имя.")
    else:
        student_name = st.selectbox("Выберите ваше имя:", list(st.session_state.users.keys()))
        selected_unit = st.selectbox("Выберите юнит из книги:", list(st.session_state.dictionary.keys()))
        
        user_info = st.session_state.users[student_name]
        st.info(f"👤 **{student_name}** | ⭐️ Баллы: **{user_info['score']} XP** | 🃏 Выучено карточек: **{user_info['cards_learned']}** | 📝 Решено грамматики: **{user_info['grammar_solved']}**")

        tab1, tab2 = st.tabs(["🃏 Компактные карточки слов", "📝 Тренажер грамматики из книги"])
        unit_data = st.session_state.dictionary[selected_unit]
        
        # --- ВКЛАДКА 1: КАРТОЧКИ СЛОВ (ИЗ УРОКА 1) ---
        with tab1:
            st.subheader("🃏 Карточки для запоминания слов (Lesson One: Words)")
            words_list = unit_data["words"]
            
            if f"card_idx_{selected_unit}" not in st.session_state:
                st.session_state[f"card_idx_{selected_unit}"] = 0
            
            idx = st.session_state[f"card_idx_{selected_unit}"]
            if idx >= len(words_list):
                idx = 0
                st.session_state[f"card_idx_{selected_unit}"] = 0
                
            current_card = words_list[idx]
            
            if f"is_flipped_{selected_unit}_{idx}" not in st.session_state:
                st.session_state[f"is_flipped_{selected_unit}_{idx}"] = False
            
            is_flipped = st.session_state[f"is_flipped_{selected_unit}_{idx}"]
            
            st.markdown("""
            <style>
            .card-container { display: flex; justify-content: center; align-items: center; margin: 20px 0; }
            .flashcard {
                width: 350px; height: 180px; background: linear-gradient(135deg, #2e6c80 0%, #4682b4 100%);
                color: white; border-radius: 15px; display: flex; flex-direction: column; justify-content: center;
                align-items: center; box-shadow: 0 8px 16px rgba(0,0,0,0.2); font-family: sans-serif; text-align: center; padding: 20px;
            }
            .card-title { font-size: 14px; opacity: 0.8; margin-bottom: 8px; }
            .card-word { font-size: 32px; font-weight: bold; }
            </style>
            """, unsafe_allow_html=True)
            
            word_display = current_card['ru'] if is_flipped else current_card['en']
            title_display = "🇷🇺 Перевод на русском:" if is_flipped else "🇬🇧 Английское слово из книги:"
            
            st.markdown(f'<div class="card-container"><div class="flashcard"><div class="card-title">{title_display}</div><div class="card-word">{word_display}</div></div></div>', unsafe_allow_html=True)
            
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

        # --- ВКЛАДКА 2: ГРАММАТИЧЕСКИЙ ТРЕНАЖЕР (Lesson Two: Grammar) ---
        with tab2:
            st.subheader("📝 Упражнения по грамматике из учебника")
            
            with st.expander("💡 Открыть Подсказку и Правило по уроку (Grammar)"):
                st.markdown(f"### {unit_data['rule_title']}")
                st.markdown(unit_data['rule_text'])
            
            if "grammar_tasks" in unit_data:
                # Берем случайное грамматическое задание для этого юнита
                if f"gram_idx_{selected_unit}" not in st.session_state:
                    st.session_state[f"gram_idx_{selected_unit}"] = random.randint(0, len(unit_data["grammar_tasks"]) - 1)
                
                g_idx = st.session_state[f"gram_idx_{selected_unit}"]
                task_item = unit_data["grammar_tasks"][g_idx]
                
                st.markdown(f"**Задание из книги:** `{task_item['task']}`")
                
                user_ans = st.text_input("Ваш ответ (на английском):", key=f"ans_gram_{selected_unit}_{g_idx}")
                
                if st.button("Проверить упражнение"):
                    if user_ans.strip().lower() == task_item['answer'].lower():
                        st.success("🎉 Верно! Вы отлично
