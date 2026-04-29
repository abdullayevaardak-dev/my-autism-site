import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="Спектр-Помощь: Консилиум", page_icon="🧩", layout="wide")

def init_db():
    conn = sqlite3.connect('school_final_consilium.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (date TEXT, role TEXT, teacher_name TEXT, child_id TEXT, score INTEGER, summary TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- АВТОРИЗАЦИЯ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.header("🔑 Вход")
    if not st.session_state.logged_in:
        role = st.selectbox("Ваша роль:", ["Учитель", "Психолог", "Логопед", "Дефектолог"])
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
    tabs = st.tabs(["📝 Провести тест", "📋 Консилиум (Сводка)", "📁 Архив"])

    with tabs[0]:
        child_id = st.text_input("Идентификатор ученика (ФИО/Код)", "Ученик-01")
        st.write("---")
        
        current_score = 0
        report_parts = []

        # 1. АНКЕТА УЧИТЕЛЯ (твои 12 вопросов)
        if st.session_state.role == "Учитель":
            st.subheader("Скрининг-анкета для классного руководителя")
            with st.expander("1. Социальное взаимодействие", expanded=True):
                q1 = st.checkbox("Необычный визуальный контакт (взгляд «сквозь»)")
                q2 = st.checkbox("Предпочитает одиночество; нет интереса к сверстникам")
                q3 = st.checkbox("Не понимает личных границ (касания/близость)")
                q4 = st.checkbox("Редко делится радостями/достижениями с классом")
            with st.expander("2. Коммуникация и речь", expanded=True):
                q5 = st.checkbox("Использует цитаты/повторы (эхолалия)")
                q6 = st.checkbox("Речь «роботизированная» или необычная интонация")
                q7 = st.checkbox("Буквальное понимание (не понимает шутки/сарказм)")
                q8 = st.checkbox("Трудности с инициацией разговора/просьбой")
            with st.expander("3. Сенсорика и поведение", expanded=True):
                q9 = st.checkbox("Острая реакция на шумы (звонок, столовая)")
                q10 = st.checkbox("Избирательность в еде")
                q11 = st.checkbox("Повторяющиеся движения (взмахи, раскачивания)")
                q12 = st.checkbox("Стресс при изменении расписания")
            current_score = sum([q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12])
            report_parts.append(f"Выявлено {current_score} из 12 маркеров поведения.")

        # 2. АНКЕТА ПСИХОЛОГА (твои 14 вопросов)
        elif st.session_state.role == "Психолог":
            st.subheader("Общий скрининг-тест психолога")
            with st.expander("Блок 1-2: Эмоции и Коммуникация"):
                p1 = st.checkbox("Нарушение зрительного контакта")
                p2 = st.checkbox("Отсутствие разделенного внимания")
                p3 = st.checkbox("Несоответствующий эмоциональный отклик")
                p4 = st.checkbox("Трудности понимания эмоций по лицам")
                p5 = st.checkbox("Речь только для просьб (нет спонтанной речи)")
                p6 = st.checkbox("Трудности выполнения инструкций")
                p7 = st.checkbox("Необычная интонация (монотонность)")
                p8 = st.checkbox("Буквальное понимание метафор")
            with st.expander("Блок 3-4: Мышление и Поведение"):
                p9 = st.checkbox("Трудности обобщения (категории)")
                p10 = st.checkbox("Ошибки в 'Четвертый лишний'")
                p11 = st.checkbox("Нарушение причинно-следственных связей")
                p12 = st.checkbox("Наличие стереотипий (стимминг)")
                p13 = st.checkbox("Сенсорный поиск/избегание")
                p14 = st.checkbox("Высокая тревожность при переменах")
            current_score = sum([p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,p13,p14])
            report_parts.append(f"Психологический риск: {current_score} из 14.")

        # 3. АНКЕТА ЛОГОПЕДА
        elif st.session_state.role == "Логопед":
            st.subheader("Логопедический скрининг")
            l1 = st.checkbox("Эхолалии (повторы)")
            l2 = st.checkbox("Смешение местоимений (Я/Он)")
            l3 = st.checkbox("Монотонный/роботизированный темп")
            l4 = st.checkbox("Нет инициативы в диалоге")
            l5 = st.checkbox("Трудности сложной инструкции")
            l6 = st.checkbox("Не понимает прагматику (скрытый смысл)")
            current_score = sum([l1,l2,l3,l4,l5,l6])
            report_parts.append(f"Речевые дефициты: {current_score} из 6.")

        # 4. АНКЕТА ДЕФЕКТОЛОГА
        elif st.session_state.role == "Дефектолог":
            st.subheader("Дефектологический скрининг")
            d1 = st.checkbox("Трудности имитации движений")
            d2 = st.checkbox("Слабая зрительно-моторная координация")
            d3 = st.checkbox("Трудности с предлогами (пространство)")
            d4 = st.checkbox("Низкая переключаемость внимания")
            d5 = st.checkbox("Трудности классификации объектов")
            d6 = st.checkbox("Нарушение логических связей")
            current_score = sum([d1,d2,d3,d4,d5,d6])
            report_parts.append(f"Когнитивные дефициты: {current_score} из 6.")

        if st.button("💾 Сохранить в общую базу"):
            summary = " ".join(report_parts)
            conn = sqlite3.connect('school_final_consilium.db')
            c = conn.cursor()
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            c.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)", 
                      (now, st.session_state.role, st.session_state.user, child_id, current_score, summary))
            conn.commit()
            conn.close()
            st.success(f"Данные по ученику {child_id} сохранены!")

    with tabs[1]:
        st.subheader("🔍 Сводная ведомость консилиума")
        conn = sqlite3.connect('school_final_consilium.db')
        all_data = pd.read_sql_query("SELECT * FROM reports", conn)
        conn.close()
        
        if not all_data.empty:
            target_child = st.selectbox("Выберите ребенка", all_data['child_id'].unique())
            if st.button("🤖 Сформировать общий отчет ИИ"):
                child_results = all_data[all_data['child_id'] == target_child]
                st.table(child_results[['date', 'role', 'teacher_name', 'summary']])
                
                total_sum = child_results['score'].sum()
                
                st.divider()
                st.subheader("📢 Комплексное заключение ИИ")
                if total_sum >= 15:
                    ai_rec = "ВЫСОКИЙ УРОВЕНЬ РИСКА. Требуется направление на ПМПК. Рекомендовано тьюторское сопровождение и АОП."
                elif total_sum >= 7:
                    ai_rec = "СРЕДНИЙ УРОВЕНЬ РИСКА. Рекомендованы занятия в ресурсном классе, работа с логопедом и психологом."
                else:
                    ai_rec = "НИЗКИЙ УРОВЕНЬ РИСКА. Рекомендовано наблюдение и социальные тренинги."
                
                final_text = f"Общий балл по всем специалистам: {total_sum}\n\nЗАКЛЮЧЕНИЕ: {ai_rec}"
                st.info(final_text)
                st.download_button("📥 Скачать ведомость", final_text.encode('utf-8-sig'), f"Consilium_{target_child}.txt")
        else:
            st.write("База данных пуста.")

    with tabs[2]:
        st.subheader("Полный архив")
        st.dataframe(all_data)

else:
    st.warning("Пожалуйста, войдите в систему в боковой панели.")
