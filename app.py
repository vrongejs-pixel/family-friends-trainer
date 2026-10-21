import streamlit as st
import pandas as pd
import random
import json
import os

st.set_page_config(page_title="Family & Friends 2 Trainer | Методика Алимжановой Л.Х.", page_icon="🎒", layout="wide")

# --- СИСТЕМА СОХРАНЕНИЯ ДАННЫХ ---
DATA_FILE = "users_data.json"

def load_users():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users_dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users_dict, f, ensure_ascii=False, indent=4)

if "users" not in st.session_state:
    st.session_state.users = load_users()

def init_progress(user_name):
    if "progress" not in st.session_state.users[user_name]:
        st.session_state.users[user_name]["progress"] = {}

for u in st.session_state.users:
    init_progress(u)

# --- ПОЛНАЯ БАЗА СЛОВ И ГРАММАТИКИ (БЕЗ ОШИБОК) ---
if "dictionary" not in st.session_state:
    st.session_state.dictionary = {
        "Starter Unit": {
            "level_id": 1,
            "words": [
                {"en": "welcome", "ru": "добро пожаловать"}, {"en": "hello", "ru": "привет"},
                {"en": "family", "ru": "семья"}, {"en": "mum", "ru": "мама"}, {"en": "dad", "ru": "папа"},
                {"en": "brother", "ru": "брат"}, {"en": "sister", "ru": "сестра"}, {"en": "cousin", "ru": "кузен"},
                {"en": "toys", "ru": "игрушки"}, {"en": "car", "ru": "машина"}, {"en": "doll", "ru": "кукла"}
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
                {"en": "classroom", "ru": "класс"}, {"en": "school", "ru": "школа"}, {"en": "computer", "ru": "компьютер"},
                {"en": "board", "ru": "доска"}, {"en": "table", "ru": "стол"}, {"en": "peg", "ru": "вешалка"},
                {"en": "poster", "ru": "плакат"}, {"en": "picture", "ru": "картина"}, {"en": "cupboard", "ru": "шкаф"}
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
                {"en": "happy", "ru": "счастливый"}, {"en": "sad", "ru": "грустный"}, {"en": "angry", "ru": "злой"},
                {"en": "tired", "ru": "уставший"}, {"en": "hungry", "ru": "голодный"}, {"en": "thirsty", "ru": "хочу пить"},
                {"en": "scared", "ru": "испуганный"}, {"en": "hot", "ru": "жарко"}, {"en": "cold", "ru": "холодно"}
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
                {"en": "skateboard", "ru": "скейтборд"}, {"en": "scooter", "ru": "самокат"}, {"en": "kite", "ru": "воздушный змей"},
                {"en": "ride", "ru": "кататься"}, {"en": "play", "ru": "играть"}, {"en": "behind", "ru": "позади"},
                {"en": "next to", "ru": "рядом с"}, {"en": "between", "ru": "между"}, {"en": "under", "ru": "под"}
            ],
            "rule_title": "Грамматика: Can / Can't и Предлоги",
            "rule_text": "I can (я умею), I can't (я не умею). Предлоги: in front of, behind, next to.",
            "grammar_tasks": [
                {"task": "He [...] ride a bike. (Умеет)", "answer": "can"},
                {"task": "He [...] ride a horse. (Не умеет)", "answer": "can't"},
                {"task": "Ответьте: Can she play tennis? Yes, she [...].", "answer": "can"},
                {"task": "Где мяч? It is [...] the table. (под)", "answer": "under"}
            ]
        },
        "Unit 4": {
            "level_id": 5,
            "words": [
                {"en": "food", "ru": "еда"}, {"en": "apple", "ru": "яблоко"}, {"en": "banana", "ru": "банан"},
                {"en": "orange", "ru": "апельсин"}, {"en": "bread", "ru": "хлеб"}, {"en": "cheese", "ru": "сыр"},
                {"en": "milk", "ru": "молоко"}, {"en": "water", "ru": "вода"}, {"en": "juice", "ru": "сок"}
            ],
            "rule_title": "Грамматика: Have you got...? / Has he got...?",
            "rule_text": "Вопросы о наличии еды: Have you got a milkshake? Yes, I have.",
            "grammar_tasks": [
                {"task": "Ответьте: Have you got a milkshake? Yes, I [...].", "answer": "have"},
                {"task": "Ответьте: Have you got fries? No, I [...].", "answer": "haven't"},
                {"task": "Ответьте: Has she got an apple? No, she [...].", "answer": "hasn't"}
            ]
        },
        "Unit 5": {
            "level_id": 6,
            "words": [
                {"en": "subject", "ru": "предмет"}, {"en": "art", "ru": "рисование"}, {"en": "maths", "ru": "математика"},
                {"en": "English", "ru": "английский язык"}, {"en": "science", "ru": "естествознание"}, {"en": "PE", "ru": "физкультура"},
                {"en": "music", "ru": "музыка"}, {"en": "our", "ru": "наш"}, {"en": "their", "ru": "их"}
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
                {"en": "after school", "ru": "после школы"}, {"en": "read", "ru": "читать"}, {"en": "draw", "ru": "рисовать"},
                {"en": "sing", "ru": "петь"}, {"en": "dance", "ru": "танцевать"}, {"en": "swim", "ru": "плавать"},
                {"en": "visit", "ru": "навещать"}, {"en": "don't", "ru": "не (отрицание)"}
            ],
            "rule_title": "Грамматика: I visit... / I don't...",
            "rule_text": "Повседневные действия после школы. I visit my grandma.",
            "grammar_tasks": [
                {"task": "I [...] my grandma every Tuesday. (навещаю)", "answer": "visit"},
                {"task": "I [...] watch TV. (не смотрю)", "answer": "don't"},
                {"task": "I [...] swimming every Thursday. (хожу)", "answer": "go"}
            ]
        },
        "Unit 7": {
            "level_id": 8,
            "words": [
                {"en": "present", "ru": "подарок"}, {"en": "buy", "ru": "покупать"}, {"en": "like", "ru": "любить"},
                {"en": "tennis", "ru": "теннис"}, {"en": "football", "ru": "футбол"}, {"en": "gloves", "ru": "перчатки"},
                {"en": "slippers", "ru": "тапочки"}, {"en": "slide", "ru": "горка"}
            ],
            "rule_title": "Грамматика: I like / He likes / doesn't like",
            "rule_text": "I like balloons. He likes chocolate. He doesn't like balloons.",
            "grammar_tasks": [
                {"task": "I [...] presents. (мне нравятся)", "answer": "like"},
                {"task": "He [...] tennis. (ему нравится)", "answer": "likes"},
                {"task": "He [...] like football. (ему не нравится)", "answer": "doesn't"}
            ]
        },
        "Unit 8": {
            "level_id": 9,
            "words": [
                {"en": "time", "ru": "время"}, {"en": "morning", "ru": "утро"}, {"en": "afternoon", "ru": "день"},
                {"en": "evening", "ru": "вечер"}, {"en": "night", "ru": "ночь"}, {"en": "breakfast", "ru": "завтрак"},
                {"en": "get up", "ru": "вставать"}, {"en": "go to bed", "ru": "ложиться спать"}
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
                {"en": "hospital", "ru": "больница"}, {"en": "school", "ru": "школа"}, {"en": "airport", "ru": "аэропорт"},
                {"en": "police station", "ru": "полицейский участок"}, {"en": "fire station", "ru": "пожарная часть"},
                {"en": "shop", "ru": "магазин"}
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
                {"en": "weather", "ru": "погода"}, {"en": "sunny", "ru": "солнечно"}, {"en": "rainy", "ru": "дождливо"},
                {"en": "windy", "ru": "ветрено"}, {"en": "snowy", "ru": "снежно"}, {"en": "hot", "ru": "жарко"},
                {"en": "cold", "ru": "холодно"}
            ],
            "rule_title": "Грамматика: What's the weather like?",
            "rule_text": "What's the weather like? It's sunny. Put on your coat.",
            "grammar_tasks": [
                {"task": "What's the weather [...]?", "answer": "like"},
                {"task": "[...] on your hat. (надень)", "answer": "put"},
                {"task": "[...] put on your coat. (не надевай)", "answer": "don't"}
            ]
        },
        "Unit 11": {
            "level_id": 12,
            "words": [
                {"en": "clothes", "ru": "одежда"}, {"en": "shirt", "ru": "рубашка"}, {"en": "T-shirt", "ru": "футболка"},
                {"en": "trousers", "ru": "брюки"}, {"en": "dress", "ru": "платье"}, {"en": "shoes", "ru": "обувь"},
                {"en": "jacket", "ru": "куртка"}, {"en": "hat", "ru": "шапка"}
            ],
            "rule_title": "Грамматика: What are you wearing?",
            "rule_text": "What are you wearing? I'm wearing a blue skirt.",
            "grammar_tasks": [
                {"task": "What [...] you wearing?", "answer": "are"},
                {"task": "I'm [...] a blue skirt. (на мне надето)", "answer": "wearing"},
                {"task": "What's he wearing? He's wearing red [...]. (носки)", "answer": "socks"}
            ]
        },
        "Unit 12": {
            "level_id": 13,
            "words": [
                {"en": "celebration", "ru": "праздник"}, {"en": "party", "ru": "вечеринка"}, {"en": "cake", "ru": "торт"},
                {"en": "candles", "ru": "свечи"}, {"en": "birthday", "ru": "день рождения"}, {"en": "wedding", "ru": "свадьба"}
            ],
            "rule_title": "Грамматика: What are you doing?",
            "rule_text": "What are you doing? I'm dancing.",
            "grammar_tasks": [
                {"task": "What [...] you doing?", "answer": "are"},
                {"task": "What's she doing? She's [...] the cake. (ест)", "answer": "eating"},
                {"task": "What are they doing? They're [...]. (разговаривают)", "answer": "talking"}
            ]
        },
        "Unit 13": {
            "level_id": 14,
            "words": [
                {"en": "animal", "ru": "животное"}, {"en": "farm", "ru": "ферма"}, {"en": "cow", "ru": "корова"},
                {"en": "horse", "ru": "лошадь"}, {"en": "sheep", "ru": "овца"}, {"en": "goat", "ru": "коза"},
                {"en": "big", "ru": "большой"}, {"en": "bigger", "ru": "больше"}
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
                {"en": "was", "ru": "был(а)"}, {"en": "wasn't", "ru": "не был(а)"}, {"en": "were", "ru": "были"},
                {"en": "yesterday", "ru": "вчера"}, {"en": "fireman", "ru": "пожарный"}, {"en": "well done", "ru": "молодец"}
            ],
            "rule_title": "Грамматика: Past Simple (I was / You were)",
            "rule_text": "I was happy. You were brave.",
            "grammar_tasks": [
                {"task": "I [...] happy. (был)", "answer": "was"},
                {"task": "You [...] happy. (были)", "answer": "were"},
                {"task": "They [...] cold. (не были)", "answer": "weren't"}
            ]
        },
        "Unit 15": {
            "level_id": 16,
            "words": [
                {"en": "people", "ru": "люди"}, {"en": "children", "ru": "дети"}, {"en": "men", "ru": "мужчины"},
                {"en": "women", "ru": "женщины"}, {"en": "some", "ru": "несколько"}, {"en": "any", "ru": "какой-нибудь"}
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

st.markdown("<h1 style='text-align: center; color: #2e6c80;'>✨ Интерактивная обучающая платформа Family and Friends 2</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555;'>Инновационная методика учителя школы №20 <b>Алимжановой Лайло Хамадуллаевной</b></h3>", unsafe_allow_html=True)
st.markdown("---")

role = st.sidebar.radio("Выберите режим:", ["👦 Режим ученика", "👨‍🏫 Кабинет преподавателя", "🏆 Рейтинг"])

if role == "👨‍🏫 Кабинет преподавателя":
    st.title("👨‍🏫 Кабинет преподавателя")
    password = st.text_input("Введите пароль:", type="password")
    
    if password == "lx890723":
        st.success("Доступ разрешен!")
        st.subheader("➕ Добавить нового ученика")
        
        with st.form("add_student_form", clear_on_submit=True):
            new_student = st.text_input("Имя нового ученика:")
            submitted = st.form_submit_button("Зарегистрировать")
            if submitted:
                if new_student.strip() == "":
                    st.warning("Имя не может быть пустым!")
                elif new_student in st.session_state.users:
                    st.warning(f"Ученик '{new_student}' уже есть в журнале!")
                else:
                    st.session_state.users[new_student] = {"score": 0, "level": 1, "progress": {}}
                    init_progress(new_student)
                    save_users(st.session_state.users)
                    st.success(f"Ученик {new_student} успешно добавлен!")
        
        st.markdown("---")
        st.subheader("📊 Журнал успеваемости")
        if st.session_state.users:
            report = [{"Ученик": k, "XP": v["score"], "Уровень": v["level"]} for k, v in st.session_state.users.items()]
            st.dataframe(pd.DataFrame(report), use_container_width=True)
            
            st.markdown("---")
            st.subheader("❌ Удалить ученика")
            col_del1, col_del2 = st.columns([2, 1])
            with col_del1:
                student_to_delete = st.selectbox("Кого удалить?", list(st.session_state.users.keys()))
            with col_del2:
                st.write(""); st.write("")
                if st.button("Удалить навсегда"):
                    del st.session_state.users[student_to_delete]
                    save_users(st.session_state.users)
                    st.success("Ученик удален.")
                    st.rerun()
        else:
            st.info("Нет учеников.")
    elif password != "":
        st.error("Неверный пароль!")

elif role == "👦 Режим ученика":
    if not st.session_state.users:
        st.warning("В системе нет учеников.")
    else:
        student_name = st.selectbox("Ваше имя:", list(st.session_state.users.keys()))
        selected_unit = st.selectbox("Выберите урок:", list(st.session_state.dictionary.keys()))
        
        user_info = st.session_state.users[student_name]
        unit_data = st.session_state.dictionary[selected_unit]
        
        st.info(f"👤 **{student_name}** | ⭐️ Счет: **{user_info['score']} XP** | 🔓 Уровень: **{user_info['level']}**")

        tab1, tab2 = st.tabs(["🃏 Словарь", "🔥 Марафон грамматики (40 вопросов)"])
        
        with tab1:
            st.subheader("🃏 Карточки слов")
            words_list = unit_data["words"]
            if f"c_idx_{selected_unit}" not in st.session_state:
                st.session_state[f"c_idx_{selected_unit}"] = 0
            idx = st.session_state[f"c_idx_{selected_unit}"]
            if idx >= len(words_list): idx = 0
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
                        save_users(st.session_state.users)
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
                            save_users(st.session_state.users)
                        else:
                            st.error(f"❌ Ошибка! Правильно: **{task['answer']}**. Штраф -1 балл!")
                            st.session_state.users[student_name]["progress"][selected_unit] = max(0, current_prog - 1)
                            save_users(st.session_state.users)
                        
                        st.session_state[f"g_idx_{selected_unit}"] = random.randint(0, len(unit_data["grammar_tasks"])-1)
                        st.rerun()

elif role == "🏆 Рейтинг":
    st.title("🏆 Доска почета")
    if not st.session_state.users:
        st.info("В системе пока нет учеников.")
    else:
        sorted_users = sorted(st.session_state.users.items(), key=lambda x: x[1]["score"], reverse=True)
        medals = ["🥇", "🥈", "🥉"]
        for rank, (name, info) in enumerate(sorted_users):
            medal = medals[rank] if rank < 3 else "🏅"
            st.markdown(f"### {medal} {rank+1} место: {name} — **{info['score']} XP** (Уровень: {info['level']})")
