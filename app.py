import streamlit as st
import pandas as pd
import random

# Настройка страницы (исправлено)
st.set_page_config(page_title="Family & Friends 2 Trainer | Методика Лайло Алимжановой", page_icon="🎒", layout="wide")

# Инициализация базы данных в памяти сессии
if "users" not in st.session_state:
    st.session_state.users = {
        "Алишер": {"score": 120, "homework": "Выполнено (95%)", "unit": 9},
        "Мадина": {"score": 150, "homework": "Выполнено (100%)", "unit": 10},
        "Тимур": {"score": 90, "homework": "Не выполнено", "unit": 8}
    }

# База слов и грамматики из Family and Friends 2 (2nd Edition)
if "dictionary" not in st.session_state:
    st.session_state.dictionary = {
        "Unit 9 (Jobs & Work)": [
            {"en": "fireman", "ru": "пожарный", "grammar": "Where does he work? He works in an airport."},
            {"en": "postman", "ru": "почтальон", "grammar": "Does she work in a shop? Yes, she does."},
            {"en": "pilot", "ru": "пилот", "grammar": "He works in an airport."}
        ],
        "Unit 10 (Weather & Clothes)": [
            {"en": "sunny", "ru": "солнечно", "grammar": "It's sunny. Put on your sun hat."},
            {"en": "coat", "ru": "пальто", "grammar": "Don't put on your coat."},
            {"en": "sun hat", "ru": "солнечная шляпа", "grammar": "Put on your sun hat."}
        ],
        "Unit 11 (What are you wearing?)": [
            {"en": "skirt", "ru": "юбка", "grammar": "I'm wearing a blue skirt."},
            {"en": "gloves", "ru": "перчатки", "grammar": "He's wearing red gloves."},
            {"en": "jeans", "ru": "джинсы", "grammar": "What are you wearing?"}
        ],
        "Unit 13 (Comparisons)": [
            {"en": "bigger", "ru": "больше", "grammar": "The sheep is bigger than the goat."},
            {"en": "shorter", "ru": "короче / ниже", "grammar": "The boy is shorter than the girl."}
        ]
    }

# --- АВТОРСКАЯ ШАПКА ПРИЛОЖЕНИЯ ---
st.markdown("<h1 style='text-align: center; color: #2e6c80;'>🎒 Family and Friends 2 — Интерактивный тренажер</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555;'>Методика и исследования учителя английского языка школы №20 <b>Лайло Алимжановой</b></h3>", unsafe_allow_html=True)
st.markdown("---")

# Боковое меню для выбора роли
st.sidebar.title("📌 Навигация")
role = st.sidebar.radio("Выберите режим:", ["👦 Режим ученика (Тренажер)", "👨‍🏫 Кабинет преподавателя", "🏆 Рейтинг и Призы"])

# ---------------------------------------------------------
# 1. КАБИНЕТ ПРЕПОДАВАТЕЛЯ (Для Лайло Алимжановой)
# ---------------------------------------------------------
if role == "👨‍🏫 Кабинет преподавателя":
    st.title("👨‍🏫 Кабинет преподавателя")
    st.info("Раздел предназначен для автора методики — Лайло Алимжановой.")
    
    password = st.text_input("Введите пароль преподавателя:", type="password")
    
    if password == "school20":
        st.success("Доступ разрешен!")
        
        st.subheader("➕ Добавить нового ученика")
        col1, col2 = st.columns(2)
        with col1:
            new_student_name = st.text_input("Имя ученика:")
            if st.button("Зарегистрировать ученика"):
                if new_student_name and new_student_name not in st.session_state.users:
                    st.session_state.users[new_student_name] = {"score": 0, "homework": "Не начато", "unit": 1}
                    st.success(f"Ученик {new_student_name} успешно добавлен в систему!")
                else:
                    st.warning("Введите имя или такое имя уже существует.")
        
        st.subheader("📊 Отчет по успеваемости и домашним заданиям")
        report_data = []
        for name, info in st.session_state.users.items():
            report_data.append({
                "Ученик": name,
                "Баллы (XP)": info["score"],
                "Статус ДЗ": info["homework"],
                "Текущий юнит": info["unit"]
            })
        
        df_report = pd.DataFrame(report_data)
        st.dataframe(df_report, use_container_width=True)
        
    elif password != "":
        st.error("Неверный пароль. Введите правильный пароль учителя.")

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
        
        tab1, tab2 = st.tabs(["🃏 Карточки слов (Flashcards)", "📝 Грамматический тренажер"])
        words_list = st.session_state.dictionary[selected_unit]
        
        with tab1:
            st.subheader("Изучение новых слов (Англо-Русский словарь)")
            for i, item in enumerate(words_list):
                with st.expander(f"Карточка {i+1}: {item['en']} 🇬🇧"):
                    st.write(f"🇷🇺 Перевод: **{item['ru']}**")
                    st.caption(f"💡 Пример из книги: *{item['grammar']}*")
                    if st.button(f"Я выучил это слово! (+10 XP)", key=f"card_{selected_unit}_{i}"):
                        st.session_state.users[student_name]["score"] += 10
                        st.success("Отлично! Баллы начислены на ваш баланс.")
                        
        with tab2:
            st.subheader("Закрепление грамматики из книги")
            current_item = random.choice(words_list)
            st.markdown(f"**Переведите слово на русский язык:** `{current_item['en']}`")
            
            user_ans = st.text_input("Ваш ответ (на русском):", key=f"ans_{selected_unit}")
            if st.button("Проверить"):
                if user_ans.strip().lower() == current_item['ru'].lower():
                    st.success("Правильно! 🎉 +15 баллов")
                    st.session_state.users[student_name]["score"] += 15
                    st.session_state.users[student_name]["homework"] = "Выполнено (100%)"
                else:
                    st.error(f"Неправильно. Правильный ответ: **{current_item['ru']}**")

# ---------------------------------------------------------
# 3. РЕЙТИНГ И ПРИЗЫ
# ---------------------------------------------------------
elif role == "🏆 Рейтинг и Призы":
    st.title("🏆 Доска почета и призы по итогам курса")
    st.write("Ученики, набравшие наибольшее количество баллов (XP), занимают призовые места в конце книги!")
    
    sorted_users = sorted(st.session_state.users.items(), key=lambda x: x[1]["score"], reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    
    for rank, (name, info) in enumerate(sorted_users):
        medal = medals[rank] if rank < 3 else "🏅"
        st.markdown(f"### {medal} **{rank+1} место:** {name} — **{info['score']} баллов (XP)**")
        
        if rank == 0:
            st.balloons()
            st.success("🎁 Приз за 1 место: Главный приз от Лайло Алимжановой — Книга комиксов на английском языке!")
        elif rank == 1:
            st.info("🎁 Приз за 2 место: Фирменный набор канцелярских принадлежностей.")
        elif rank == 2:
            st.info("🎁 Приз за 3 место: Набор коллекционных стикеров.")
