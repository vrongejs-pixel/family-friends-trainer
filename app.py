import streamlit as st
import pandas as pd
import random

# Настройка страницы
st.set_page_config(page_title="Family & Friends 2 Trainer | Методика Алимжановой Л.Х.", page_icon="🎒", layout="wide")

# Список уроков по порядку (для системы замков)
UNITS = ["Starter Unit", "Unit 1", "Unit 2", "Unit 3", "Unit 4"]

# Инициализация базы данных учеников (добавлен прогресс от 0 до 40 для каждого урока)
if "users" not in st.session_state:
    st.session_state.users = {
        "Алишер": {"score": 120, "cards": 15, "homework": "Выполнено", "progress": {"Starter Unit": 40, "Unit 1": 15, "Unit 2": 0, "Unit 3": 0, "Unit 4": 0}},
        "Мадина": {"score": 350, "cards": 40, "homework": "Выполнено", "progress": {"Starter Unit": 40, "Unit 1": 40, "Unit 2": 40, "Unit 3": 0, "Unit 4": 0}},
        "Тимур": {"score": 10, "cards": 5, "homework": "Не выполнено", "progress": {"Starter Unit": 5, "Unit 1": 0, "Unit 2": 0, "Unit 3": 0, "Unit 4": 0}}
    }

# Словари лексики (Карточки) и Теории
if "dictionary" not in st.session_state:
    st.session_state.dictionary = {
        "Starter Unit": {
            "words": [{"en": "mum", "ru": "мама"}, {"en": "dad", "ru": "папа"}, {"en": "brother", "ru": "брат"}, {"en": "sister", "ru": "сестра"}],
            "rule": "Используйте **'ve got** (have got) для I/you/we/they и **'s got** (has got) для he/she/it."
        },
        "Unit 1": {
            "words": [{"en": "classroom", "ru": "класс"}, {"en": "table", "ru": "стол"}, {"en": "computer", "ru": "компьютер"}, {"en": "peg", "ru": "вешалка"}, {"en": "board", "ru": "доска"}],
            "rule": "**This** (это, ед.ч. близко), **That** (то, ед.ч. далеко), **These** (эти, мн.ч. близко), **Those** (те, мн.ч. далеко)."
        },
        "Unit 2": {
            "words": [{"en": "hot", "ru": "жарко"}, {"en": "cold", "ru": "холодно"}, {"en": "hungry", "ru": "голодный"}, {"en": "thirsty", "ru": "хочу пить"}, {"en": "happy", "ru": "счастливый"}, {"en": "sad", "ru": "грустный"}],
            "rule": "**We're** = We are (Мы), **They're** = They are (Они). Вопросы: **Are they** hot? Yes, they are / No, they aren't."
        },
        "Unit 3": {
            "words": [{"en": "ride a bike", "ru": "кататься на велосипеде"}, {"en": "skate", "ru": "кататься на коньках"}, {"en": "play tennis", "ru": "играть в теннис"}],
            "rule": "Выражение умений: **can** (умею), **can't** (не умею). Вопрос: **Can she** skate? Yes, she can / No, she can't."
        },
        "Unit 4": {
            "words": [{"en": "salad", "ru": "салат"}, {"en": "fries", "ru": "картофель фри"}, {"en": "pizza", "ru": "пицца"}, {"en": "milkshake", "ru": "молочный коктейль"}],
            "rule": "Вопросы о наличии еды: **Have you got...?** Yes, I have / No, I haven't. **Has he got...?** Yes, he has / No, he hasn't."
        }
    }

# Умный генератор бесконечных заданий
def generate_question(unit):
    if unit == "Starter Unit":
        sub = random.choice(["I", "He", "She", "They", "We"])
        trait = random.choice(["brown hair", "green eyes", "curly hair", "blue eyes"])
        ans = "'ve got" if sub in ["I", "They", "We"] else "'s got"
        return f"Вставьте правильную форму ({sub} [...] {trait}):", ans
    elif unit == "Unit 1":
        items_sg = ["computer", "board", "table", "peg"]
        items_pl = ["computers", "boards", "tables", "pegs"]
        dist = random.choice(["близко", "далеко"])
        is_pl = random.choice([True, False])
        if is_pl:
            item = random.choice(items_pl)
            ans = "these" if dist == "близко" else "those"
            return f"Вставьте (This/That/These/Those): [...] are new {item}. ({dist}, мн.ч.)", ans
        else:
            item = random.choice(items_sg)
            ans = "this" if dist == "близко" else "that"
            return f"Вставьте (This/That/These/Those): [...] is a new {item}. ({dist}, ед.ч.)", ans
    elif unit == "Unit 2":
        feel = random.choice(["hot", "cold", "hungry", "thirsty", "happy", "sad"])
        q_type = random.choice(["affirmative", "negative_ans", "positive_ans"])
        if q_type == "affirmative":
            return f"Напишите сокращение для 'Они {feel}': [...] {feel}.", "they're"
        elif q_type == "negative_ans":
            return f"Ответьте кратко (Нет): Are they {feel}? -> No, they [...].", "aren't"
        else:
            return f"Ответьте кратко (Да): Are they {feel}? -> Yes, they [...].", "are"
    elif unit == "Unit 3":
        act = random.choice(["ride a bike", "skate", "skateboard", "play tennis", "play football"])
        q_type = random.choice(["can", "cant", "question"])
        if q_type == "can":
            return f"Вставьте (can/can't): He [...] {act}. (Он умеет)", "can"
        elif q_type == "cant":
            return f"Вставьте (can/can't): She [...] {act}. (Она не умеет)", "can't"
        else:
            return f"Ответьте кратко (Да): Can he {act}? -> Yes, he [...].", "
