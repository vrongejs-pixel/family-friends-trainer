import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Family & Friends 2 Trainer | Методика Алимжановой Л.Х.", page_icon="🎒", layout="wide")

# Функция для безопасного создания прогресса нового ученика
def init_progress(user_name):
    if "progress" not in st.session_state.users[user_name]:
        st.session_state.users[user_name]["progress"] = {}

# Инициализация базы данных
if "users" not in st.session_state:
    st.session_state.users = {
        "Алишер": {"score": 120, "level": 2, "progress": {"Starter Unit": 40, "Unit 1": 15}},
        "Мадина": {"score": 150, "level": 3, "progress": {"Starter Unit": 40, "Unit 1": 40, "Unit 2": 5}},
        "Тимур": {"score": 90, "level": 1, "progress": {"Starter Unit": 0}}
    }

for u in st.session_state.users:
    init_progress(u)

# СТРОГАЯ БАЗА ИЗ ВСЕХ 15 ЮНИТОВ КНИГИ FAMILY AND FRIENDS 2
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
