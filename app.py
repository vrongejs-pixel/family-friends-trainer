import streamlit as st
import pandas as pd
import random
import json
import os

st.set_page_config(page_title="Family & Friends 2 Trainer | Методика Алимжановой Л.Х.", page_icon="🎒", layout="wide")

# --- НАДЕЖНАЯ СИСТЕМА СОХРАНЕНИЯ ДАННЫХ ---
DATA_FILE = "users_data.json"

def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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

# --- ПОЛНАЯ БАЗА СЛОВ И ГРАММАТИКИ (Все 197 слов) ---
if "dictionary" not in st.session_state:
    st.session_state.dictionary = {
        "Starter Unit": {
            "level_id": 1,
            "words": [
                {"en": "welcome", "ru": "добро пожаловать"}, {"en": "back", "ru": "назад / обратно"}, {"en": "hello", "ru": "привет"},
                {"en": "name", "ru": "имя"}, {"en": "friend", "ru": "друг"}, {"en": "boy", "ru": "мальчик"}, {"en": "girl", "ru": "девочка"},
                {"en": "old", "ru": "старый"}, {"en": "fine", "ru": "в порядке"}, {"en": "thank you", "ru": "спасибо"},
                {"en": "family", "ru": "семья"}, {"en": "mum", "ru": "мама"}, {"en": "dad", "ru": "папа"}, {"en": "brother", "ru": "брат"},
                {"en": "sister", "ru": "сестра"}, {"en": "grandma", "ru": "бабушка"}, {"en": "grandpa", "ru": "дедушка"}, {"en": "cousin", "ru": "двоюродный брат/сестра"},
                {"en": "hair", "ru": "волосы"}, {"en": "brown", "ru": "коричневый"}, {"en": "green", "ru": "зеленый"}, {"en": "eyes", "ru": "глаза"},
                {"en": "numbers", "ru": "цифры"}, {"en": "colours", "ru": "цвета"}, {"en": "toys", "ru": "игрушки"}, {"en": "ball", "ru": "мяч"},
                {"en": "car", "ru": "машина"}, {"en": "train", "ru": "поезд"}, {"en": "doll", "ru": "кукла"}, {"en": "teddy", "ru": "мишка"},
                {"en": "puzzle", "ru": "пазл"}, {"en": "bike", "ru": "велосипед"}, {"en": "his", "ru": "его"}, {"en": "her", "ru": "её"}
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
                {"en": "poster", "ru": "плакат"}, {"en": "picture", "ru": "картина"}, {"en": "drawer", "ru": "выдвижной ящик"},
                {"en": "cupboard", "ru": "шкаф"}, {"en": "this", "ru": "этот"}, {"en": "these", "ru": "эти"},
                {"en": "those", "ru": "те"}, {"en": "there is", "ru": "есть (ед.ч.)"}, {"en": "there are", "ru": "есть (мн.ч.)"},
                {"en": "alphabet", "ru": "алфавит"}
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
                {"en": "scared", "ru": "испуганный"}, {"en": "hot", "ru": "жарко"}, {"en": "cold", "ru": "холодно"},
                {"en": "feelings", "ru": "чувства"}, {"en": "he", "ru": "он"}, {"en": "she", "ru": "она"}, {"en": "they", "ru": "они"},
                {"en": "isn't", "ru": "не (ед.ч.)"}, {"en": "aren't", "ru": "не (мн.ч.)"}
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
                {"en": "balloon", "ru": "шарик"}, {"en": "ride", "ru": "кататься"}, {"en": "fly", "ru": "летать / запускать"},
                {"en": "play", "ru": "играть"}, {"en": "run", "ru": "бегать"}, {"en": "jump", "ru": "прыгать"},
                {"en": "behind", "ru": "позади"}, {"en": "in front of", "ru": "спереди"}, {"en": "next to", "ru": "рядом с"},
                {"en": "between", "ru": "между"}, {"en": "where", "ru": "где"}, {"en": "under", "ru": "под"},
                {"en": "can", "ru": "мочь / уметь"}, {"en": "can't", "ru": "не уметь"}
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
                {"en": "orange", "ru": "апельсин"}, {"en": "grapes", "ru": "виноград"}, {"en": "bread", "ru": "хлеб"},
                {"en": "cheese", "ru": "сыр"}, {"en": "eggs", "ru": "яйца"}, {"en": "milk", "ru": "молоко"},
                {"en": "water", "ru": "вода"}, {"en": "juice", "ru": "сок"}, {"en": "milkshake", "ru": "молочный коктейль"},
                {"en": "lunch", "ru": "обед"}, {"en": "have got", "ru": "иметь (у меня есть)"}, {"en": "haven't got", "ru": "не иметь (у меня нет)"}
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
                {"en": "subject", "ru": "школьный предмет"}, {"en": "art", "ru": "рисование"}, {"en": "English", "ru": "английский язык"},
                {"en": "maths", "ru": "математика"}, {"en": "music", "ru": "музыка"}, {"en": "science", "ru": "естествознание"},
                {"en": "PE", "ru": "физкультура"}, {"en": "library", "ru": "библиотека"}, {"en": "playground", "ru": "игровая площадка"},
                {"en": "our", "ru": "наш"}, {"en": "their", "ru": "их"}
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
                {"en": "after school", "ru": "после школы"}, {"en": "read", "ru": "читать"}, {"en": "book", "ru": "книга"},
                {"en": "draw", "ru": "рисовать"}, {"en": "sing", "ru": "петь"}, {"en": "dance", "ru": "танцевать"},
                {"en": "swim", "ru": "плавать"}, {"en": "visit", "ru": "навещать"}, {"en": "don't", "ru": "не (отрицание)"}
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
                {"en": "present", "ru": "подарок"}, {"en": "buy", "ru": "покупать"}, {"en": "like", "ru": "нравиться / любить"},
                {"en": "doesn't like", "ru": "не нравится"}, {"en": "tennis", "ru": "теннис"}, {"en": "football", "ru": "футбол"},
                {"en": "gloves", "ru": "перчатки"}, {"en": "glue", "ru": "клей"}, {"en": "slippers", "ru": "тапочки"},
                {"en": "slide", "ru": "горка"}, {"en": "special day", "ru": "особенный день"}
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
                {"en": "time", "ru": "время"}, {"en": "o'clock", "ru": "час(ов)"}, {"en": "morning", "ru": "утро"},
                {"en": "afternoon", "ru": "день"}, {"en": "evening", "ru": "вечер"}, {"en": "night", "ru": "ночь"},
                {"en": "breakfast", "ru": "завтрак"}, {"en": "get up", "ru": "вставать"}, {"en": "go to bed", "ru": "ложиться спать"},
                {"en": "homework", "ru": "домашнее задание"}
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
                {"en": "places", "ru": "места"}, {"en": "hospital", "ru": "больница"}, {"en": "school", "ru": "школа"},
                {"en": "airport", "ru": "аэропорт"}, {"en": "police station", "ru": "полицейский участок"}, {"en": "fire station", "ru": "пожарная часть"},
                {"en": "shop", "ru": "магазин"}
            ],
            "rule_title": "Грамматика: Where does he work?",
            "
