import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="Спектр-Помощь: Итоговый протокол", page_icon="📜", layout="wide")

def init_db():
    conn = sqlite3.connect('school_consilium_v4.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (date TEXT, role TEXT, name TEXT, child_id TEXT, score INTEGER, summary TEXT)''')
    conn.commit()
    conn.close()

init_db()

REQUIRED_ROLES = ["Учитель", "Психолог", "Логопед", "Дефектолог"]

# --- АВТОРИЗАЦИЯ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.header("🔑 Авторизация")
    if not st.session_state.logged_in:
        role = st.selectbox("Ваша специализация:", REQUIRED_ROLES)
        name = st.text_input("Ваша Фамилия")
        pwd = st.text_input("Пароль доступа", type="password")
        if st.button("Войти в систему"):
            if pwd == "12345": # Пароль для демонстрации
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user = name
                st.rerun()
    else:
        st.success(f"{st.session_state.role}: {st.session_state.user}")
        if st.button("Завершить сеанс"):
            st.session_state.logged_in = False
            st.rerun()

# --- ОСНОВНОЙ КОНТЕНТ ---
if st.session_state.logged_in:
    st.title(f"🧩 Рабочее место: {st.session_state.role}")
    tabs = st.tabs(["📝 Анкетирование", "📄 Итоговый протокол ИИ", "🗄 Архив записей"])

    with tabs[0]:
        child_id = st.text_input("Введите ФИО или ID ученика", "Иванов Иван")
        st.divider()
        
        score = 0
        details = []

        # ДИНАМИЧЕСКИЕ ВОПРОСЫ В ЗАВИСИМОСТИ ОТ РОЛИ
        if st.session_state.role == "Учитель":
            st.subheader("Скрининг классного руководителя (12 маркеров)")
            q = [st.checkbox(f"Маркер {i+1}") for i in range(12)] # Здесь будут твои 12 вопросов
            score = sum(q)
            details = [f"Поведенческие особенности: {score}/12"]

        elif st.session_state.role == "Психолог":
            st.subheader("Диагностика психолога (14 маркеров)")
            p = [st.checkbox(f"Психологический индикатор {i+1}") for i in range(14)] # Здесь твои 14 вопросов
            score = sum(p)
            details = [f"Психоэмоциональный профиль: {score}/14"]

        elif st.session_state.role == "Логопед":
            st.subheader("Логопедическое заключение (6 маркеров)")
            l = [st.checkbox(f"Речевой показатель {i+1}") for i in range(6)]
            score = sum(l)
            details = [f"Речевой статус: {score}/6"]

        elif st.session_state.role == "Дефектолог":
            st.subheader("Дефектологическое обследование (6 маркеров)")
            d = [st.checkbox(f"Когнитивный показатель {i+1}") for i in range(6)]
            score = sum(d)
            details = [f"Когнитивный статус: {score}/6"]

        if st.button("💾 Сохранить в архив"):
            conn = sqlite3.connect('school_consilium_v4.db')
            c = conn.cursor()
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            c.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)", 
                      (now, st.session_state.role, st.session_state.user, child_id, score, ". ".join(details)))
            conn.commit()
            conn.close()
            st.success(f"Данные по ученику {child_id} внесены в базу.")

    with tabs[1]:
        st.subheader("📊 Генерация комплексного заключения")
        conn = sqlite3.connect('school_consilium_v4.db')
        all_data = pd.read_sql_query("SELECT * FROM reports", conn)
        conn.close()

        if not all_data.empty:
            target = st.selectbox("Выберите ученика для формирования протокола", all_data['child_id'].unique())
            subset = all_data[all_data['child_id'] == target]
            
            roles_present = subset['role'].unique()
            missing = [r for r in REQUIRED_ROLES if r not in roles_present]

            # Визуализация готовности
            cols = st.columns(len(REQUIRED_ROLES))
            for i, r in enumerate(REQUIRED_ROLES):
                cols[i].metric(label=r, value="✅ Да" if r in roles_present else "❌ Нет")
