import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="Спектр-Помощь: Консилиум PRO", page_icon="🧩", layout="wide")

def init_db():
    conn = sqlite3.connect('school_consilium_final.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (date TEXT, role TEXT, teacher_name TEXT, child_id TEXT, score INTEGER, summary TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- СПИСОК ВСЕХ РОЛЕЙ ---
REQUIRED_ROLES = ["Учитель", "Психолог", "Логопед", "Дефектолог"]

# --- АВТОРИЗАЦИЯ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.header("🔑 Вход")
    if not st.session_state.logged_in:
        role = st.selectbox("Ваша роль:", REQUIRED_ROLES)
        name = st.text_input("Фамилия специалиста")
        pwd = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if pwd == "12345":
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user = name
                st.rerun()
    else:
        st.success(f"{st.session_state.role}: {st.session_state.user}")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

# --- ОСНОВНОЙ МОДУЛЬ ---
if st.session_state.logged_in:
    st.title(f"🧩 Рабочее пространство: {st.session_state.role}")
    tabs = st.tabs(["📝 Провести тест", "📋 Общий отчет (Консилиум)", "📁 Архив"])

    with tabs[0]:
        child_id = st.text_input("Идентификатор ученика (ФИО/Код)", "Иванов Иван")
        st.write("---")
        
        current_score = 0
        report_parts = []

        if st.session_state.role == "Учитель":
            st.subheader("Скрининг классного руководителя")
            q1 = st.checkbox("Необычный визуальный контакт")
            q2 = st.checkbox("Предпочитает одиночество")
            q3 = st.checkbox("Не понимает личных границ")
            q4 = st.checkbox("Редко делится радостями")
            q5 = st.checkbox("Использует эхолалии")
            q6 = st.checkbox("Роботизированная речь")
            q7 = st.checkbox("Буквальное понимание")
            q8 = st.checkbox("Трудности инициации разговора")
            q9 = st.checkbox("Реакция на шумы")
            q10 = st.checkbox("Избирательность в еде")
            q11 = st.checkbox("Повторяющиеся движения")
            q12 = st.checkbox("Стресс при переменах")
            current_score = sum([q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12])
            report_parts.append(f"Поведенческие маркеры: {current_score}/12")

        elif st.session_state.role == "Психолог":
            st.subheader("Скрининг психолога")
            p1 = st.checkbox("Зрительный контакт нарушен")
            p2 = st.checkbox("Нет разделенного внимания")
            p3 = st.checkbox("Неадекватный эмоц. отклик")
            p4 = st.checkbox("Трудности понимания эмоций")
            p5 = st.checkbox("Речь только для просьб")
            p6 = st.checkbox("Трудности выполнения инструкций")
            p7 = st.checkbox("Монотонная интонация")
            p8 = st.checkbox("Буквальное понимание метафор")
            p9 = st.checkbox("Трудности обобщения")
            p10 = st.checkbox("Ошибки в '4-й лишний'")
            p11 = st.checkbox("Нарушение причинно-следственных связей")
            p12 = st.checkbox("Наличие стереотипий")
            p13 = st.checkbox("Сенсорный поиск/избегание")
            p14 = st.checkbox("Высокая тревожность")
            current_score = sum([p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14])
            report_parts.append(f"Психоэмоциональная сфера: {current_score}/14")

        elif st.session_state.role == "Логопед":
            st.subheader("Логопедический скрининг")
            l1 = st.checkbox("Эхолалии")
            l2 = st.checkbox("Путаница местоимений")
            l3 = st.checkbox("Нарушение просодики (темп/ритм)")
            l4 = st.checkbox("Отсутствие инициативы")
            l5 = st.checkbox("Трудности сложной инструкции")
            l6 = st.checkbox("Нарушение прагматики")
            current_score = sum([l1,l2,l3,l4,l5,l6])
            report_parts.append(f"Речевые дефициты: {current_score}/6")

        elif st.session_state.role == "Дефектолог":
            st.subheader("Дефектологический скрининг")
            d1 = st.checkbox("Нарушение имитации")
            d2 = st.checkbox("Слабая координация")
            d3 = st.checkbox("Трудности с пространством (предлоги)")
            d4 = st.checkbox("Слабая переключаемость")
            d5 = st.checkbox("Трудности классификации")
            d6 = st.checkbox("Нарушение логики")
            current_score = sum([d1,d2,d3,d4,d5,d6])
            report_parts.append(f"Когнитивные дефициты: {current_score}/6")

        if st.button("💾 Сохранить мои данные"):
            conn = sqlite3.connect('school_consilium_final.db')
            c = conn.cursor()
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            summary_text = " ".join(report_parts)
            c.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)", 
                      (now, st.session_state.role, st.session_state.user, child_id, current_score, summary_text))
            conn.commit()
            conn.close()
            st.success("Ваша часть обследования сохранена!")

    with tabs[1]:
        st.subheader("🔍 Формирование комплексного отчета")
        conn = sqlite3.connect('school_consilium_final.db')
        all_data = pd.read_sql_query("SELECT * FROM reports", conn)
        conn.close()
        
        if not all_data.empty:
            target_child = st.selectbox("Выберите ученика для проверки готовности", all_data['child_id'].unique())
            child_results = all_data[all_data['child_id'] == target_child]
            
            # ПРОВЕРКА: КТО УЖЕ ПРОШЕЛ ТЕСТ
            roles_done = child_results['role'].unique()
            missing_roles = [r for r in REQUIRED_ROLES if r not in roles_done]
            
            st.write(f"**Статус обследования:**")
            for r in REQUIRED_ROLES:
                if r in roles_done:
                    st.write(f"✅ {r}: Данные внесены")
                else:
                    st.write(f"❌ {r}: Ожидание данных")

            if not missing_roles:
                st.success("🚀 Все специалисты прошли анкетирование! Можно формировать общий отчет.")
                if st.button("📄 Сгенерировать Сводный отчет ИИ"):
                    total_sum = child_results['score'].sum()
                    
                    st.divider()
                    st.subheader(f"ИТОГОВЫЙ ПРОТОКОЛ: {target_child}")
                    st.table(child_results[['role', 'teacher_name', 'summary']])
