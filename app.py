import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Family & Friends 2 Trainer | Методика Алимжановой Л.Х.", page_icon="🎒", layout="wide")

# Функция для безопасного создания прогресса нового ученика
def init_progress(user_name):
    if "progress" not in st.session_state.users[user_name]:
        st.session_state.users[user_name]["progress"] = {}

# Инициализация базы данных: добавлен словарь "progress" для 40 вопросов
if "users" not in st.session_state:
    st.session_state.users = {
        "Алишер": {"score": 120, "level": 2, "progress": {"Starter Unit": 40, "Unit 1": 15}},
        "Мадина": {"score": 150, "level": 3, "progress": {"Starter Unit": 40, "Unit 1": 40, "Unit 2": 5}},
        "Тимур": {"score": 90, "level": 1, "progress": {"Starter Unit": 0}}
    }

for u in st.session_state.users:
    init_progress(u)

# СТРОГАЯ БАЗА УРОКОВ ИЗ КНИГИ
if "dictionary" not in st.session_state:
    st.session_state.dictionary = {
        "Starter Unit": {
            "level_id": 1,
            "words": [
                {"en": "mum", "ru": "мама"}, {"en": "dad", "ru": "папа"}, {"en": "brother", "ru": "брат"},
                {"en": "sister", "ru": "сестра"}, {"en": "grandma", "ru": "бабушка"}, {"en": "grandpa", "ru": "дедушка"}
            ],
            "rule_title": "Грамматика: I've got / He's got",
            "rule_text": "Используйте **'ve got** для I/we/they и **'s got** для he/she/it.",
            "grammar_tasks": [
                {"task": "I [...] brown hair. (У меня каштановые волосы)", "answer": "'ve got"},
                {"task": "He [...] green eyes. (У него зеленые глаза)", "answer": "'s got"},
                {"task": "She [...] curly hair. (У нее кудрявые волосы)", "answer": "'s got"}
            ]
        },
        "Unit 1": {
            "level_id": 2,
            "words": [
                {"en": "classroom", "ru": "класс"}, {"en": "table", "ru": "стол"}, {"en": "computer", "ru": "компьютер"},
                {"en": "peg", "ru": "вешалка"}, {"en": "pencil case", "ru": "пенал"}, {"en": "board", "ru": "доска"}
            ],
            "rule_title": "Грамматика: This / That / These / Those",
            "rule_text": "This (это - ед.ч.), That (то - ед.ч.), These (эти - мн.ч.), Those (те - мн.ч.).",
            "grammar_tasks": [
                {"task": "[...] is the new computer. (близко, ед.ч.)", "answer": "this"},
                {"task": "[...] is a new board. (далеко, ед.ч.)", "answer": "that"},
                {"task": "[...] are new tables. (близко, мн.ч.)", "answer": "these"},
                {"task": "[...] are new pegs. (далеко, мн.ч.)", "answer": "those"}
            ]
        },
        "Unit 2": {
            "level_id": 3,
            "words": [
                {"en": "hot", "ru": "жарко"}, {"en": "cold", "ru": "холодно"}, {"en": "hungry", "ru": "голодный"},
                {"en": "thirsty", "ru": "хочу пить"}, {"en": "happy", "ru": "счастливый"}, {"en": "sad", "ru": "грустный"}
            ],
            "rule_title": "Грамматика: We're / They're & Are they...?",
            "rule_text": "We're (Мы), They're (Они). Вопросы: Are they...?",
            "grammar_tasks": [
                {"task": "Напишите сокращение для 'They are': [...]", "answer": "they're"},
                {"task": "Напишите сокращение для 'We are': [...]", "answer": "we're"},
                {"task": "Ответьте на вопрос (Are they hot?): Yes, they [...].", "answer": "are"},
                {"task": "Ответьте на вопрос (Are they cold?): No, they [...].", "answer": "aren't"}
            ]
        },
        "Unit 3": {
            "level_id": 4,
            "words": [
                {"en": "ride a bike", "ru": "кататься на велосипеде"}, {"en": "skate", "ru": "кататься на коньках"},
                {"en": "skateboard", "ru": "скейтборд"}, {"en": "play tennis", "ru": "играть в теннис"}
            ],
            "rule_title": "Грамматика: Can / Can't",
            "rule_text": "I can (я умею), I can't (я не умею).",
            "grammar_tasks": [
                {"task": "He [...] ride a bike. (Умеет)", "answer": "can"},
                {"task": "He [...] ride a horse. (Не умеет)", "answer": "can't"},
                {"task": "Ответьте: Can she play tennis? Yes, she [...].", "answer": "can"}
            ]
        },
        "Unit 4": {
            "level_id": 5,
            "words": [
                {"en": "salad", "ru": "салат"}, {"en": "fries", "ru": "картофель фри"}, {"en": "pizza", "ru": "пицца"},
                {"en": "milkshake", "ru": "молочный коктейль"}, {"en": "cheese sandwich", "ru": "бутерброд с сыром"}
            ],
            "rule_title": "Грамматика: Have you got...? / Has he got...?",
            "rule_text": "Вопросы о наличии еды: Have you got a milkshake? Yes, I have.",
            "grammar_tasks": [
                {"task": "Ответьте: Have you got a milkshake? Yes, I [...].", "answer": "have"},
                {"task": "Ответьте: Have you got fries? No, I [...].", "answer": "haven't"},
                {"task": "Ответьте: Has she got a pizza? No, she [...].", "answer": "hasn't"}
            ]
        },
        "Unit 5": {
            "level_id": 6,
            "words": [
                {"en": "art", "ru": "рисование"}, {"en": "maths", "ru": "математика"}, {"en": "English", "ru": "английский язык"},
                {"en": "science", "ru": "наука"}, {"en": "PE", "ru": "физкультура"}, {"en": "music", "ru": "музыка"}
            ],
            "rule_title": "Грамматика: What/When have we got...? our/their",
            "rule_text": "What have we got on Monday? We've got English.",
            "grammar_tasks": [
                {"task": "What have we got [...] Monday?", "answer": "on"},
                {"task": "These are [...] bags. (наши)", "answer": "our"},
                {"task": "You can wear [...] clothes. (их)", "answer": "their"}
            ]
        },
        "Unit 6": {
            "level_id": 7,
            "words": [
                {"en": "help", "ru": "помогать"}, {"en": "homework", "ru": "ДЗ"},
                {"en": "visit", "ru": "навещать"}, {"en": "swimming", "ru": "плавание"}
            ],
            "rule_title": "Грамматика: I visit... / I don't have...",
            "rule_text": "Повседневные действия после школы. I visit my grandma every Tuesday.",
            "grammar_tasks": [
                {"task": "I [...] my grandma every Tuesday. (навещаю)", "answer": "visit"},
                {"task": "I [...] watch TV. (не смотрю)", "answer": "don't"},
                {"task": "I [...] swimming every Thursday. (хожу)", "answer": "go"}
            ]
        },
        "Unit 7": {
            "level_id": 8,
            "words": [
                {"en": "chocolate", "ru": "шоколад"}, {"en": "sweets", "ru": "сладости"}, {"en": "balloon", "ru": "воздушный шар"}
            ],
            "rule_title": "Грамматика: I like / He likes / doesn't like",
            "rule_text": "I like balloons. He likes chocolate. He doesn't like balloons.",
            "grammar_tasks": [
                {"task": "I [...] sweets. (мне нравятся)", "answer": "like"},
                {"task": "He [...] chocolate. (ему нравится)", "answer": "likes"},
                {"task": "He [...] like balloons. (ему не нравятся)", "answer": "doesn't"}
            ]
        },
        "Unit 8": {
            "level_id": 9,
            "words": [
                {"en": "get up", "ru": "вставать"}, {"en": "have breakfast", "ru": "завтракать"}, {"en": "go to school", "ru": "идти в школу"}
            ],
            "rule_title": "Грамматика: Время и распорядок дня",
            "rule_text": "What's the time? It's seven o'clock.",
            "grammar_tasks": [
                {"task": "[...] the time? (Который час?)", "answer": "what's"},
                {"task": "It's seven [...]. (семь часов)", "answer": "o'clock"},
                {"task": "He gets up [...] six o'clock.", "answer": "at"}
            ]
        },
        "Unit 9": {
            "level_id": 10,
            "words": [
                {"en": "hospital", "ru": "больница"}, {"en": "school", "ru": "школа"}, {"en": "airport", "ru": "аэропорт"}
            ],
            "rule_title": "Грамматика: Where does he work?",
            "rule_text": "Where does he work? He works in a police station.",
            "grammar_tasks": [
                {"task": "Where [...] he work?", "answer": "does"},
                {"task": "He [...] in a police station. (работает)", "answer": "works"},
                {"task": "Does she work in a shop? Yes, she [...].", "answer": "does"}
            ]
        },
        "Unit 10": {
            "level_id": 11,
            "words": [
                {"en": "sunny", "ru": "солнечно"}, {"en": "windy", "ru": "ветрено"}, {"en": "raining", "ru": "идет дождь"}
            ],
            "rule_title": "Грамматика: What's the weather like?",
            "rule_text": "What's the weather like? It's sunny. Put on your sun hat.",
            "grammar_tasks": [
                {"task": "What's the weather [...]?", "answer": "like"},
                {"task": "[...] on your sun hat. (надень)", "answer": "put"},
                {"task": "[...] put on your coat. (не надевай)", "answer": "don't"}
            ]
        },
        "Unit 11": {
            "level_id": 12,
            "words": [
                {"en": "skirt", "ru": "юбка"}, {"en": "scarf", "ru": "шарф"}, {"en": "gloves", "ru": "перчатки"}
            ],
            "rule_title": "Грамматика: What are you wearing?",
            "rule_text": "What are you wearing? I'm wearing a blue skirt.",
            "grammar_tasks": [
                {"task": "What [...] you wearing?", "answer": "are"},
                {"task": "I'm [...] a blue skirt. (на мне надето)", "answer": "wearing"},
                {"task": "What's he wearing? He's wearing red [...]. (перчатки)", "answer": "gloves"}
            ]
        },
        "Unit 12": {
            "level_id": 13,
            "words": [
                {"en": "wedding", "ru": "свадьба"}, {"en": "guests", "ru": "гости"}, {"en": "cake", "ru": "торт"}
            ],
            "rule_title": "Грамматика: What are you doing?",
            "rule_text": "What are you doing? I'm dancing with friends.",
            "grammar_tasks": [
                {"task": "What [...] you doing?", "answer": "are"},
                {"task": "What's she doing? She's [...] the cake. (ест)", "answer": "eating"},
                {"task": "What are they doing? They're [...]. (разговаривают)", "answer": "talking"}
            ]
        },
        "Unit 13": {
            "level_id": 14,
            "words": [
                {"en": "cow", "ru": "корова"}, {"en": "goat", "ru": "коза"}, {"en": "horse", "ru": "лошадь"}
            ],
            "rule_title": "Грамматика: Сравнительная степень (-er than)",
            "rule_text": "This cow is bigger than that cow.",
            "grammar_tasks": [
                {"task": "The sheep is [...] than the goat. (больше)", "answer": "bigger"},
                {"task": "The boy is shorter [...] the girl. (чем)", "answer": "than"},
                {"task": "The horse is [...] than the goat. (больше)", "answer": "bigger"}
            ]
        },
        "Unit 14": {
            "level_id": 15,
            "words": [
                {"en": "was", "ru": "был(а)"}, {"en": "were", "ru": "были"}, {"en": "wasn't", "ru": "не был(а)"}
            ],
            "rule_title": "Грамматика: Past Simple (I was / You were)",
            "rule_text": "I was naughty. You were happy.",
            "grammar_tasks": [
                {"task": "I [...] happy. (был)", "answer": "was"},
                {"task": "You [...] happy. (были)", "answer": "were"},
                {"task": "They [...] cold. (не были)", "answer": "weren't"}
            ]
        },
        "Unit 15": {
            "level_id": 16,
            "words": [
                {"en": "children", "ru": "дети"}, {"en": "men", "ru": "мужчины"}, {"en": "women", "ru": "женщины"}
            ],
            "rule_title": "Грамматика: There were some / weren't any",
            "rule_text": "There were some children. There weren't any men.",
            "grammar_tasks": [
                {"task": "[...] were some children. (Там были...)", "answer": "there"},
                {"task": "There were [...] children. (несколько)", "answer": "some"},
                {"task": "There weren't [...] men. (никаких)", "answer": "any"}
            ]
        }
    }

def text_to_speech_button(text):
    html = f"""
    <button onclick="let u = new SpeechSynthesisUtterance('{text}'); u.lang = 'en-US'; window.speechSynthesis.speak(u);" 
    style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; font-size:16px;">
        🔊 Послушать: {text}
    </button>
    """
    return html

# --- ШАПКА ---
st.markdown("<h1 style='text-align: center; color: #2e6c80;'>✨ Интерактивная обучающая платформа Family and Friends 2</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555;'>Инновационная методика учителя школы №20 <b>Алимжановой Лайло Хамадуллаевной</b></h3>", unsafe_allow_html=True)
st.markdown("---")

role = st.sidebar.radio("Выберите режим:", ["👦 Режим ученика", "👨‍🏫 Кабинет преподавателя", "🏆 Рейтинг"])

# --- КАБИНЕТ ПРЕПОДАВАТЕЛЯ ---
if role == "👨‍🏫 Кабинет преподавателя":
    st.title("👨‍🏫 Кабинет преподавателя")
    password = st.text_input("Введите пароль:", type="password")
    
    # Ваш новый пароль
    if password == "lx890723":
        new_student = st.text_input("Имя нового ученика:")
        if st.button("Зарегистрировать"):
            if new_student and new_student not in st.session_state.users:
                st.session_state.users[new_student] = {"score": 0, "level": 1, "progress": {}}
                init_progress(new_student)
                st.success(f"Ученик {new_student} добавлен!")
        
        report = [{"Ученик": k, "XP (Общий балл)": v["score"], "Открытый уровень": v["level"]} for k, v in st.session_state.users.items()]
        st.dataframe(pd.DataFrame(report))
    elif password != "":
        st.error("Неверный пароль!")

# --- РЕЖИМ УЧЕНИКА ---
elif role == "👦 Режим ученика":
    if not st.session_state.users:
        st.warning("Список учеников пуст.")
    else:
        student_name = st.selectbox("Ваше имя:", list(st.session_state.users.keys()))
        selected_unit = st.selectbox("Выберите урок:", list(st.session_state.dictionary.keys()))
        
        user_info = st.session_state.users[student_name]
        unit_data = st.session_state.dictionary[selected_unit]
        
        st.info(f"👤 **{student_name}** | ⭐️ Общий счет: **{user_info['score']} XP** | 🔓 Доступный уровень: **{user_info['level']}**")

        tab1, tab2 = st.tabs(["🃏 Словарь (Свободный доступ)", "🔥 Марафон грамматики (40 вопросов)"])
        
        # Вкладка 1: Карточки
        with tab1:
            st.subheader("🃏 Карточки слов")
            words_list = unit_data["words"]
            
            if f"c_idx_{selected_unit}" not in st.session_state:
                st.session_state[f"c_idx_{selected_unit}"] = 0
                
            idx = st.session_state[f"c_idx_{selected_unit}"]
            if idx >= len(words_list): 
                idx = 0
                
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
            .card-title { font-size: 16px; opacity: 0.8; margin-bottom: 8px; color: #f1c40f; font-weight: bold;}
            .card-word { font-size: 36px; font-weight: bold; }
            </style>
            """, unsafe_allow_html=True)
            
            word_display = current_card['ru'] if is_flipped else current_card['en']
            title_display = "RUS (Перевод):" if is_flipped else "ENG (Слово):"
            
            st.markdown(f'<div class="card-container"><div class="flashcard"><div class="card-title">{title_display}</div><div class="card-word">{word_display}</div></div></div>', unsafe_allow_html=True)
            
            if not is_flipped:
                st.components.v1.html(text_to_speech_button(current_card['en']), height=60)
            else:
                st.write("")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Перевернуть карточку"):
                    st.session_state[f"is_flipped_{selected_unit}_{idx}"] = not is_flipped
                    st.rerun()
            with col2:
                if st.button("Следующее слово ➡️"):
                    st.session_state[f"is_flipped_{selected_unit}_{idx}"] = False
                    st.session_state[f"c_idx_{selected_unit}"] = (idx + 1) % len(words_list)
                    st.rerun()

        # Вкладка 2: Марафон
        with tab2:
            st.subheader("🔥 Марафон: Докажи, что знаешь правило!")
            
            if user_info["level"] < unit_data["level_id"]:
                st.error("🔒 **УРОК ЗАКРЫТ!** Сначала пройди марафон в предыдущем юните.")
            else:
                if selected_unit not in user_info["progress"]:
                    user_info["progress"][selected_unit] = 0
                    
                current_prog = user_info["progress"][selected_unit]
                
                st.progress(min(current_prog / 40.0, 1.0))
                st.write(f"**Прогресс урока: {current_prog} / 40** (Осторожно: ошибка отнимает 1 балл!)")
                
                if current_prog >= 40:
                    st.success("🎉 ПОЗДРАВЛЯЕМ! ТЫ ИДЕАЛЬНО ОСВОИЛ ЭТОТ УРОК!")
                    if user_info["level"] == unit_data["level_id"]:
                        st.session_state.users[student_name]["level"] += 1
                        st.balloons()
                        st.info("🔓 Открыт следующий уровень!")
                else:
                    with st.expander("💡 Открыть правило из книги"):
                        st.write(unit_data["rule_text"])
                    
                    if f"g_idx_{selected_unit}" not in st.session_state:
                        st.session_state[f"g_idx_{selected_unit}"] = random.randint(0, len(unit_data["grammar_tasks"])-1)
                    
                    g_idx = st.session_state[f"g_idx_{selected_unit}"]
                    task = unit_data["grammar_tasks"][g_idx]
                    
                    st.markdown(f"**Задание:** `{task['task']}`")
                    ans = st.text_input("Ваш ответ:", key=f"ans_{selected_unit}_{g_idx}")
                    
                    if st.button("Проверить"):
                        if ans.strip().lower() == task['answer'].lower():
                            st.success("✅ Верно! +1 балл к прогрессу.")
                            st.session_state.users[student_name]["score"] += 5
                            st.session_state.users[student_name]["progress"][selected_unit] += 1
                        else:
                            st.error(f"❌ Ошибка! Правильно: **{task['answer']}**. Штраф -1 балл!")
                            st.session_state.users[student_name]["progress"][selected_unit] = max(0, current_prog - 1)
                        
                        st.session_state[f"g_idx_{selected_unit}"] = random.randint(0, len(unit_data["grammar_tasks"])-1)
                        st.rerun()

# --- РЕЙТИНГ ---
elif role == "🏆 Рейтинг":
    st.title("🏆 Доска почета")
    sorted_users = sorted(st.session_state.users.items(), key=lambda x: x[1]["score"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    for rank, (name, info) in enumerate(sorted_users):
        medal = medals[rank] if rank < 3 else "🏅"
        st.markdown(f"### {medal} {rank+1} место: {name} — **{info['score']} XP** (Уровень: {info['level']})")
