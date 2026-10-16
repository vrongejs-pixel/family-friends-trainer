import streamlit as st
import pandas as pd
import random

# Настройка страницы
st.set_page_config(page_title="Family & Friends 2 Trainer | Методика Лайло Алимжановой", page_icon="🎒", layout="wide")

# Инициализация базы данных учеников и статистики
if "users" not in st.session_state:
    st.session_state.users = {
        "Алишер": {"score": 120, "cards_learned": 15, "grammar_solved": 8, "homework": "Выполнено (95%)", "unit": 1},
        "Мадина": {"score": 150, "cards_learned": 22, "grammar_solved": 14, "homework": "Выполнено (100%)", "unit": 2},
        "Тимур": {"score": 90, "cards_learned": 8, "grammar_solved": 5, "homework": "Не выполнено", "unit": 1}
    }

# СТРОГАЯ БАЗА СЛОВ И ГРАММАТИКИ ИЗ КНИГИ FAMILY AND FRIENDS 2 (2nd Edition)
if "dictionary" not in st.session_state:
    st.session_state.dictionary = {
        "Starter Unit (Welcome back!)": {
            "words": [
                {"en": "mum", "ru": "мама"},
                {"en": "dad", "ru": "папа"},
                {"en": "brother", "ru": "брат"},
                {"en": "sister", "ru": "сестра"},
                {"en": "grandma", "ru": "бабушка"},
                {"en": "grandpa", "ru": "дедушка"},
                {"en": "aunt", "ru": "тётя"},
                {"en": "uncle", "ru": "дядя"},
                {"en": "cousin", "ru": "двоюродный брат / сестра"}
            ],
            "rule_title": "Грамматика: I've got / He's got / Where's...?",
            "rule_text": "Описание внешности и членов семьи:\n- *I've got brown hair.* (У меня каштановые волосы)\n- *He's got green eyes.* (У него зеленые глаза)\n- *Where's Billy? Is he under the bed?* (Где Билли? Он под кроватью?)"
        },
        "Unit 1 (Our new things)": {
            "words": [
                {"en": "classroom", "ru": "класс (комната)"},
                {"en": "table", "ru": "стол"},
                {"en": "computer", "ru": "компьютер"},
                {"en": "peg", "ru": "вешалка / крючок"},
                {"en": "pencil case", "ru": "пенал"},
                {"en": "board", "ru": "доска"},
                {"en": "poster", "ru": "плакат"},
                {"en": "picture", "ru": "картинка"},
                {"en": "cupboard", "ru": "шкаф"}
            ],
            "rule_title": "Грамматика: This / That / These / Those",
            "rule_text": "Указательные местоимения в школе:\n- *This is the new computer.* (Это... ед. число, близко)\n- *That is a new board.* (То... ед. число, далеко)\n- *These are new tables.* (Эти... мн. число, близко)\n- *Those are new pegs.* (Те... мн. число, далеко)"
        },
        "Unit 2 (They're happy now!)": {
            "words": [
                {"en": "hot", "ru": "жаркий / жарко"},
                {"en": "cold", "ru": "холодный / холодно"},
                {"en": "hungry", "ru": "голодный"},
                {"en": "thirsty", "ru": "хочу пить"},
                {"en": "happy", "ru": "счастливый"},
                {"en": "sad", "ru": "грустный"},
                {"en": "tired", "ru": "уставший"},
                {"en": "angry", "ru": "злой"},
                {"en": "scared", "ru": "испуганный"},
                {"en": "brave", "ru": "храбрый"}
            ],
            "rule_title": "Грамматика: We're / They're и вопросы Are they...?",
            "rule_text": "Выражение чувств и состояний:\n- *We're happy.* / *They're hungry.*\n- *Are they hot?* — *No, they aren't. / Yes, they are.*"
        },
        "Unit 3 (I can ride a bike!)": {
            "words": [
                {"en": "ride a bike", "ru": "кататься на велосипеде"},
                {"en": "ride a horse", "ru": "скакать на лошади"},
                {"en": "skate", "ru": "кататься на коньках"},
                {"en": "skateboard", "ru": "кататься на скейтборде"},
                {"en": "play tennis", "ru": "играть в теннис"},
                {"en": "play football", "ru": "играть в футбол"}
            ],
            "rule_title": "Грамматика: Can / Can't и предлоги места",
            "rule_text": "Умения и расположение предметов:\n- *I can skate.* / *I can't skateboard.*\n- *Can she play tennis?* — *Yes, she can.* / *No, he can't.*\n- Предлоги: *behind* (за), *in front of* (перед), *next to* (рядом), *between* (между)."
        },
        "Unit 4 (Have you got a milkshake?)": {
            "words": [
                {"en": "salad", "ru": "салат"},
                {"en": "fries", "ru": "картофель фри"},
                {"en": "pizza", "ru": "пицца"},
                {"en": "milkshake", "ru": "молочный коктейль"},
                {"en": "cheese", "ru": "сыр"},
                {"en": "sandwich", "ru": "бутерброд"},
                {"en": "chicken", "ru": "курица"}
            ],
            "rule_title": "Грамматика: Have you got...? / Has he got...?",
            "rule_text": "Вопросы о наличии еды:\n- *Have you got a milkshake?* — *Yes, I have. / No, I haven't.*\n- *Has he got a cheese sandwich?* — *Yes, he has. / No, he hasn't.*"
        },
        "Unit 5 (We've got English!)": {
            "words": [
                {"en": "art", "ru": "рисование (изо)"},
                {"en": "maths", "ru": "математика"},
                {"en": "English", "ru": "английский язык"},
                {"en": "science", "ru": "окружающий мир / наука"},
                {"en": "PE", "ru": "физкультура"},
                {"en": "music", "ru": "музыка"}
            ],
            "rule_title": "Грамматика: What/When have we got...? our/their",
            "rule_text": "Школьные предметы и расписание:\n- *What have we got on Monday? We've got English.*\n- *When have we got PE? We've got PE on Thursday.*\n- Местоимения: *our* (наш), *their* (их)."
        },
        "Unit 6 (Let's play after school!)": {
            "words": [
                {"en": "help my mum", "ru": "помогать маме"},
                {"en": "do my homework", "ru": "делать домашнее задание"},
                {"en": "visit my grandma", "ru": "навещать бабушку"},
                {"en": "go swimming", "ru": "ходить плавать"},
                {"en": "have a music lesson", "ru": "быть на уроке музыки"},
                {"en": "watch TV", "ru": "смотреть телевизор"}
            ],
            "rule_title": "Грамматика: I visit... / I don't have...",
            "rule_text": "Повседневные действия после школы:\n- *I visit my grandma every Tuesday.*\n- *I don't have a music lesson.*\n- *I go swimming every Thursday.*"
        },
        "Unit 7 (Let's buy presents!)": {
            "words": [
                {"en": "chocolate", "ru": "шоколад"},
                {"en": "sweets", "ru": "конфеты / сладости"},
                {"en": "balloon", "ru": "воздушный шар"},
                {"en": "present", "ru": "подарок"},
                {"en": "cake", "ru": "торт / пирог"},
                {"en": "card", "ru": "открытка"}
            ],
            "rule_title": "Грамматика: I like / He likes / doesn't like",
            "rule_text": "Выражение предпочтений:\n- *I like balloons. / I don't like sweets.*\n- *He likes chocolate. / He doesn't like balloons.*"
        },
        "Unit 8 (What's the time?)": {
            "words": [
                {"en": "get up", "ru": "вставать"},
                {"en": "have breakfast", "ru": "завтракать"},
                {"en": "go to school", "ru": "идти в школу"},
                {"en": "go home", "ru": "идти домой"},
                {"en": "have dinner", "ru": "ужинать"},
                {"en": "go to bed", "ru": "ложиться спать"}
            ],
            "rule_title": "Грамматика: Время и распорядок дня",
            "rule_text": "Определение времени и действий по часам:\n- *What's the time? It's seven o'clock.*\n- *He gets up at six o'clock.*\n- *She goes to bed at nine o'clock.*"
        },
        "Unit 9 (Where does she work?)": {
            "words": [
                {"en": "hospital", "ru": "больница"},
                {"en": "school", "ru": "школа"},
                {"en": "airport", "ru": "аэропорт"},
                {"en": "police station", "ru": "полицейский участок"},
                {"en": "fire station", "ru": "пожарная станция"},
                {"en": "shop", "ru": "магазин"}
            ],
            "rule_title": "Грамматика: Where does he work? / Does she work...?",
            "rule_text": "Вопросы о местах работы:\n- *Where does he work? He works in a police station.*\n- *Does she work in a shop? Yes, she does / No, she doesn't.*"
        },
        "Unit 10 (It's hot today!)": {
            "words": [
                {"en": "sunny", "ru": "солнечно"},
                {"en": "windy", "ru": "ветрено"},
                {"en": "raining", "ru": "идет дождь"},
                {"en": "snowing", "ru": "идет снег"},
                {"en": "hot", "ru": "жарко"},
                {"en": "cold", "ru": "холодно"}
            ],
            "rule_title": "Грамматика: What's the weather like? Put on / Don't put on",
            "rule_text": "Описание погоды и советы по одежде:\n- *What's the weather like? It's sunny.*\n- *Put on your sun hat.*\n- *Don't put on your coat.*"
        },
        "Unit 11 (What are you wearing?)": {
            "words": [
                {"en": "skirt", "ru": "юбка"},
                {"en": "scarf", "ru": "шарф"},
                {"en": "gloves", "ru": "перчатки"},
                {"en": "jeans", "ru": "джинсы"},
                {"en": "boots", "ru": "ботинки / сапоги"},
                {"en": "shirt", "ru": "рубашка"}
            ],
            "rule_title": "Грамматика: Present Continuous (What are you wearing?)",
            "rule_text": "Описание одежды на человеке в данный момент:\n- *What are you wearing? I'm wearing a blue skirt.*\n- *What's he wearing? He's wearing a yellow shirt.*\n- *She's wearing red trousers.*"
        },
        "Unit 12 (You're sleeping!)": {
            "words": [
                {"en": "wedding", "ru": "свадьба"},
                {"en": "guests", "ru": "гости"},
                {"en": "cake", "ru": "торт"},
                {"en": "bride", "ru": "невеста"},
                {"en": "band", "ru": "музыкальная группа / оркестр"},
                {"en": "invitation", "ru": "приглашение"}
            ],
            "rule_title": "Грамматика: Present Continuous (What are you doing?)",
            "rule_text": "Описание действий в момент речи:\n- *What are you doing? I'm dancing with friends.*\n- *What's she doing? She's eating the cake.*\n- *What are they doing? They're talking.*"
        },
        "Unit 13 (Look at all the animals!)": {
            "words": [
                {"en": "cow", "ru": "корова"},
                {"en": "goat", "ru": "коза"},
                {"en": "horse", "ru": "лошадь"},
                {"en": "sheep", "ru": "овца / баран"},
                {"en": "donkey", "ru": "осел"},
                {"en": "goose", "ru": "гусь"}
            ],
            "rule_title": "Грамматика: Сравнительная степень прилагательных (-er than)",
            "rule_text": "Сравнение животных и предметов:\n- *This cow is bigger than that cow.*\n- *This sheep is smaller than that sheep.*\n- *The horse is bigger than the goat.*"
        },
        "Unit 14 (Look at the photos!)": {
            "words": [
                {"en": "was", "ru": "был / была (ед.ч.)"},
                {"en": "were", "ru": "были (мн.ч.)"},
                {"en": "wasn't", "ru": "не был / не была"},
                {"en": "weren't", "ru": "не были"}
            ],
            "rule_title": "Грамматика: Past Simple (I was / You were)",
            "rule_text": "Прошедшее время глагола to be:\n- *I was naughty. You were happy.*\n- *He wasn't sad. They weren't cold.*"
        },
        "Unit 15 (Well done!)": {
            "words": [
                {"en": "children", "ru": "дети"},
                {"en": "men", "ru": "мужчины"},
                {"en": "women", "ru": "женщины"},
                {"en": "people", "ru": "люди"}
            ],
            "rule_title": "Грамматика: There were some / weren't any",
            "rule_text": "Утверждения и отрицания в прошедшем времени с множественным числом:\n- *There were some children.*\n- *There weren't any men.*"
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
        selected_unit = st.selectbox("Выберите юнит из книги:", list(st.session_state.dictionary.keys()))
        
        user_info = st.session_state.users[student_name]
        st.info(f"👤 **{student_name}** | ⭐️ Баллы: **{user_info['score']} XP** | 🃏 Выучено карточек: **{user_info['cards_learned']}** | 📝 Решено грамматики: **{user_info['grammar_solved']}**")

        tab1, tab2 = st.tabs(["🃏 Компактные карточки", "📝 Упражнения и Подсказки"])
        unit_data = st.session_state.dictionary[selected_unit]
        words_list = unit_data["words"]
        
        # --- ВКЛАДКА 1: КОМПАКТНЫЕ КАРТОЧКИ ПО ЦЕНТРУ С ПЕРЕВОРОТОМ ---
        with tab1:
            st.subheader("🃏 Карточки слов по юнитам из книги")
            
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
            .card-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 20px 0;
            }
            .flashcard {
                width: 350px;
                height: 180px;
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
            }
            .card-title {
                font-size: 14px;
                opacity: 0.8;
                margin-bottom: 8px;
            }
            .card-word {
                font-size: 32px;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            word_display = current_card['ru'] if is_flipped else current_card['en']
            title_display = "🇷🇺 Перевод на русском:" if is_flipped else "🇬🇧 Английское слово из книги:"
            
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
            st.subheader("📝 Упражнения по грамматике из книги")
            
            with st.expander("💡 Нажмите здесь, чтобы открыть Подсказку и Правило по уроку"):
                st.markdown(f"### {unit_data['rule_title']}")
                st.markdown(unit_data['rule_text'])
            
            current_item = random.choice(words_list)
            st.markdown(f"**Переведите слово из этого юнита на русский язык:** `{current_item['en']}`")
            
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
        st.markdown(f"### {medal} {rank+1} место: {name} — **{info['score']} XP** (Карточки: {info['cards_learned']}, Грамматика: {info['grammar_solved']})")
        if rank == 0:
            st.balloons()
            st.success("🎁 Главный приз от Лайло Алимжановой — Книга комиксов на английском языке!")
