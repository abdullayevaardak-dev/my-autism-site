import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Спектр-Помощь PRO", page_icon="🧩", layout="wide")

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('school_v3.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                 (date TEXT, teacher TEXT, child_id TEXT, score INTEGER, report TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(teacher, child_id, score, report):
    conn = sqlite3.connect('school_v3.db')
    c = conn.cursor()
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?)", (now, teacher, child_id, score, report))
    conn.commit()
    conn.close()

init_db()

# --- СИСТЕМА АВТОРИЗАЦИИ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.title("🔑 Авторизация")
    if not st.session_state.logged_in:
        user = st.text_input("Логин (Фамилия)")
        password = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if password == "12345": # Можно поменять на свой
                st.session_state.logged_in = True
                st.session_state.teacher = user
                st.rerun()
            else:
                st.error("Неверный пароль")
    else:
        st.success(f"Педагог: {st.session_state.teacher}")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

# --- ОСНОВНОЙ МОДУЛЬ ---
if st.session_state.logged_in:
    st.title("🧩 Скрининг-система «Спектр-Помощь»")
    
    tab1, tab2 = st.tabs(["📋 Провести скрининг", "📜 Журнал и Отчеты"])

    with tab1:
        child_id = st.text_input("Ученик (Код или ФИО)", "Ученик-01")
        st.info("Инструкция: Отметьте утверждения, проявляющиеся регулярно в течение последних 6 месяцев.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("1. Социализация")
            s1 = st.checkbox("Необычный визуальный контакт")
            s2 = st.checkbox("Предпочитает одиночество")
            s3 = st.checkbox("Не понимает личных границ")
            s4 = st.checkbox("Не делится радостями")
            
        with col2:
            st.subheader("2. Коммуникация")
            c1 = st.checkbox("Эхолалия (цитаты/повторы)")
            c2 = st.checkbox("Роботизированная речь")
            c3 = st.checkbox("Буквальное понимание слов")
            c4 = st.checkbox("Трудности с инициацией разговора")
            
        with col3:
            st.subheader("3. Поведение")
            p1 = st.checkbox("Острая реакция на шумы")
            p2 = st.checkbox("Избирательность в еде")
            p3 = st.checkbox("Повторяющиеся движения")
            p4 = st.checkbox("Стресс при переменах")

        if st.button("🚀 Анализ ИИ и сохранение"):
            score = sum([s1, s2, s3, s4, c1, c2, c3, c4, p1, p2, p3, p4])
            
            # Генерация рекомендаций ИИ
            if score >= 7:
                res = "ВЫСОКИЙ РИСК. Рекомендуется ПМПК. Психологу: углубленная диагностика. Родителям: консультация психиатра."
            elif score >= 4:
                res = "СРЕДНИЙ РИСК. Рекомендуется адаптация среды (тихая зона, визуальное расписание). Наблюдение психолога."
            else:
                res = "НИЗКИЙ РИСК. Выраженных маркеров нет. Рекомендовано развитие социальных навыков в общей группе."
            
            full_report = f"Результат: {res}\n\nРекомендации: Снизить сенсорную нагрузку, использовать карточки-подсказки."
            
            save_to_db(st.session_state.teacher, child_id, score, full_report)
            st.success("Данные успешно сохранены в базе!")
            st.subheader("Заключение ИИ:")
            st.write(full_report)

    with tab2:
        st.subheader("Архив обследований")
        conn = sqlite3.connect('school_v3.db')
        df = pd.read_sql_query("SELECT * FROM results", conn)
        conn.close()

        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("🖨 Подготовка к печати")
            record_id = st.selectbox("Выберите ребенка для выгрузки отчета", df['child_id'].unique())
            
            if st.button("Сформировать документ"):
                row = df[df['child_id'] == record_id].iloc[-1]
                report_text = f"""
                ОТЧЕТ ПО РЕЗУЛЬТАТАМ СКРИНИНГА
                Дата: {row['date']}
                Учитель: {row['teacher']}
                Ученик: {row['child_id']}
                Баллы: {row['score']} из 12
                -----------------------------------
                ЗАКЛЮЧЕНИЕ И РЕКОМЕНДАЦИИ:
                {row['report']}
                -----------------------------------
                Подпись: _________________
                """
                st.text_area("Готовый текст для копирования в Word/Печати:", report_text, height=250)
                st.download_button("📥 Скачать текстовый файл", report_text.encode('utf-8-sig'), f"{record_id}.txt")
        else:
            st.write("История пуста.")

else:
    st.warning("Войдите в систему в боковой панели, чтобы начать работу.")
