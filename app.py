import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- НАСТРОЙКИ ---
st.set_page_config(page_title="Спектр-Помощь: Консилиум", page_icon="🧩", layout="wide")

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('school_consilium.db')
    c = conn.cursor()
    # Таблица результатов: хранит специализацию, кто заполнил, ID ребенка и сами ответы
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (date TEXT, specialist_type TEXT, name TEXT, child_id TEXT, score INTEGER, details TEXT)''')
    conn.commit()
    conn.close()

def save_data(spec, name, child, score, details):
    conn = sqlite3.connect('school_consilium.db')
    c = conn.cursor()
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    c.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)", (now, spec, name, child, score, details))
    conn.commit()
    conn.close()

init_db()

# --- АВТОРИЗАЦИЯ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.header("🔑 Вход в систему")
    if not st.session_state.logged_in:
        role = st.selectbox("Ваша роль:", ["Учитель", "Психолог", "Логопед", "Дефектолог"])
        user_name = st.text_input("Ваша Фамилия")
        pwd = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if pwd == "12345":
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.user = user_name
                st.rerun()
    else:
        st.success(f"{st.session_state.role}: {st.session_state.user}")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

# --- ОСНОВНОЙ КОНТЕНТ ---
if st.session_state.logged_in:
    st.title(f"🧩 Рабочее место: {st.session_state.role}")
    
    tabs = st.tabs(["📝 Заполнить тест", "📋 Сводная ведомость", "📁 Архив"])

    with tabs[0]:
        child_id = st.text_input("ID или ФИО ребенка", "Иванов Иван")
        st.divider()

        # ДИНАМИЧЕСКАЯ АНКЕТА В ЗАВИСИМОСТИ ОТ РОЛИ
        score = 0
        details = ""

        if st.session_state.role == "Учитель":
            st.subheader("Скрининг классного руководителя")
            q1 = st.checkbox("Избегает визуального контакта")
            q2 = st.checkbox("Предпочитает одиночество")
            q3 = st.checkbox("Нарушает границы / Реакция на касания")
            q4 = st.checkbox("Трудности с переменами в расписании")
            score = sum([q1, q2, q3, q4])
            details = f"Соц. взаимодействие: {score}/4"

        elif st.session_state.role == "Психолог":
            st.subheader("Диагностика психолога")
            p1 = st.checkbox("Сенсорная гиперчувствительность (шум/свет)")
            p2 = st.checkbox("Наличие стереотипных движений (стимминг)")
            p3 = st.checkbox("Трудности с пониманием эмоций других")
            p4 = st.checkbox("Высокий уровень тревожности")
            score = sum([p1, p2, p3, p4])
            details = f"Психоэмоц. сфера: {score}/4"

        elif st.session_state.role == "Логопед":
            st.subheader("Логопедическое обследование")
            l1 = st.checkbox("Наличие эхолалий (повторов)")
            l2 = st.checkbox("Речь монотонная/роботизированная")
            l3 = st.checkbox("Буквальное понимание (не понимает шуток)")
            l4 = st.checkbox("Отсутствие коммуникативной инициативы")
            score = sum([l1, l2, l3, l4])
            details = f"Речевая сфера: {score}/4"

        elif st.session_state.role == "Дефектолог":
            st.subheader("Дефектологическое обследование")
            d1 = st.checkbox("Трудности имитации движений")
            d2 = st.checkbox("Слабая переключаемость внимания")
            d3 = st.checkbox("Трудности обобщения (логика)")
            d4 = st.checkbox("Нарушение пространственного восприятия")
            score = sum([d1, d2, d3, d4])
            details = f"Когнитивная сфера: {score}/4"

        if st.button("💾 Сохранить результат"):
            save_data(st.session_state.role, st.session_state.user, child_id, score, details)
            st.success("Данные успешно добавлены в общую базу!")

    with tabs[1]:
        st.subheader("🔍 Формирование общего заключения (Консилиум)")
        all_children = pd.read_sql_query("SELECT DISTINCT child_id FROM reports", sqlite3.connect('school_consilium.db'))
        target_child = st.selectbox("Выберите ребенка для сводки", all_children)

        if st.button("🤖 Собрать данные и запустить ИИ-анализ"):
            conn = sqlite3.connect('school_consilium.db')
            child_data = pd.read_sql_query("SELECT * FROM reports WHERE child_id = ?", conn, params=(target_child,))
            conn.close()

            if not child_data.empty:
                st.markdown(f"### Сводная таблица по ребенку: {target_child}")
                st.table(child_data[['date', 'specialist_type', 'name', 'details']])
                
                total_points = child_data['score'].sum()
                specs_involved = child_data['specialist_type'].unique()

                st.divider()
                st.subheader("📢 Комплексная рекомендация ИИ")
                
                # ЛОГИКА ИИ КОНСИЛИУМА
                analysis = f"В обследовании участвовали: {', '.join(specs_involved)}. "
                if total_points >= 10:
                    rec = "ВЫСОКИЙ РИСК РАС. Требуется направление на ПМПК. Рекомендована разработка ИОП (Индивидуальной образовательной программы) с участием всех специалистов."
                elif total_points >= 5:
                    rec = "СРЕДНИЙ РИСК. Требуется внутренняя поддержка школы: коррекционные занятия с логопедом и психологом 2 раза в неделю."
                else:
                    rec = "НИЗКИЙ РИСК. Рекомендовано наблюдение в динамике и работа над социальными навыками в группе."
                
                full_text = f"**Анализ:** {analysis}\n\n**Заключение:** {rec}"
                st.info(full_text)
                
                # Кнопка для скачивания
                report_file = f"СВОДНАЯ ВЕДОМОСТЬ: {target_child}\n\n{full_text}\n\nДата: {datetime.now()}"
                st.download_button("📥 Скачать общую ведомость (TXT)", report_file.encode('utf-8-sig'), f"Consilium_{target_child}.txt")
            else:
                st.error("По этому ребенку еще нет данных.")

    with tabs[2]:
        st.subheader("Полный архив базы данных")
        conn = sqlite3.connect('school_consilium.db')
        df_all = pd.read_sql_query("SELECT * FROM reports", conn)
        conn.close()
        st.dataframe(df_all, use_container_width=True)

else:
    st.warning("Пожалуйста, войдите в систему.")
