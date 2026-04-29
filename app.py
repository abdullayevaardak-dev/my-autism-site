import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Спектр-Помощь: Личный кабинет", page_icon="🔐", layout="wide")

# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('school_secure.db')
    c = conn.cursor()
    # Добавляем поле teacher для фильтрации
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                 (date TEXT, teacher TEXT, child_id TEXT, score INTEGER, report TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(teacher, child_id, score, report):
    conn = sqlite3.connect('school_secure.db')
    c = conn.cursor()
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?)", (now, teacher, child_id, score, report))
    conn.commit()
    conn.close()

# Функция загрузки данных ТОЛЬКО для конкретного учителя
def load_my_results(teacher_name):
    conn = sqlite3.connect('school_secure.db')
    query = "SELECT * FROM results WHERE teacher = ?"
    df = pd.read_sql_query(query, conn, params=(teacher_name,))
    conn.close()
    return df

init_db()

# --- СИСТЕМА АВТОРИЗАЦИИ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.teacher = None

with st.sidebar:
    st.title("🔐 Личный кабинет")
    if not st.session_state.logged_in:
        st.info("Войдите, чтобы увидеть своих учеников")
        user = st.text_input("Фамилия учителя")
        password = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if password == "12345": # Единый пароль для школы (можно усложнить)
                st.session_state.logged_in = True
                st.session_state.teacher = user
                st.rerun()
            else:
                st.error("Неверный пароль")
    else:
        st.success(f"Вы вошли как: {st.session_state.teacher}")
        if st.button("Выйти из системы"):
            st.session_state.logged_in = False
            st.session_state.teacher = None
            st.rerun()

# --- ОСНОВНОЙ ЭКРАН ---
if st.session_state.logged_in:
    st.title(f"🧩 Рабочее пространство: {st.session_state.teacher}")
    
    tab1, tab2 = st.tabs(["📋 Новый скрининг", "📁 Мой личный журнал"])

    with tab1:
        st.subheader("Заполнение анкеты")
        child_id = st.text_input("Имя/Код ученика", help="Данные сохранятся только в вашем кабинете")
        
        # Ваши 12 вопросов (упрощенная визуализация для кода)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Социализация**")
            s1 = st.checkbox("Необычный визуальный контакт")
            s2 = st.checkbox("Одиночество")
            s3 = st.checkbox("Личные границы")
            s4 = st.checkbox("Не делится радостью")
        with col2:
            st.write("**Коммуникация**")
            c1 = st.checkbox("Эхолалия")
            c2 = st.checkbox("Робо-речь")
            c3 = st.checkbox("Буквальность")
            c4 = st.checkbox("Трудности контакта")
        with col3:
            st.write("**Поведение**")
            p1 = st.checkbox("Шум")
            p2 = st.checkbox("Еда")
            p3 = st.checkbox("Стимминг")
            p4 = st.checkbox("Стресс от перемен")

        if st.button("💾 Сохранить и получить анализ ИИ"):
            score = sum([s1, s2, s3, s4, c1, c2, c3, c4, p1, p2, p3, p4])
            
            # Интерпретация ИИ
            if score >= 7: risk, advice = "ВЫСОКИЙ", "Срочно: консультация ПМПК и психиатра."
            elif score >= 4: risk, advice = "СРЕДНИЙ", "Рекомендовано: работа с психологом, визуальные опоры."
            else: risk, advice = "НИЗКИЙ", "Рекомендовано: наблюдение, развитие соц. навыков."
            
            report_text = f"Уровень риска: {risk}. {advice}"
            
            save_to_db(st.session_state.teacher, child_id, score, report_text)
            st.success(f"Запись для {child_id} добавлена в ваш журнал.")
            st.info(f"ИИ-анализ: {report_text}")

    with tab2:
        st.subheader(f"Журнал учителя {st.session_state.teacher}")
        # ЗАГРУЖАЕМ ТОЛЬКО СВОИ ДАННЫЕ
        my_df = load_my_results(st.session_state.teacher)
        
        if not my_df.empty:
            st.write("Ниже представлены только те дети, которых оценивали вы:")
            st.dataframe(my_df, use_container_width=True)
            
            st.divider()
            st.subheader("🖨 Печать отчета")
            selected_child = st.selectbox("Выберите ученика", my_df['child_id'].unique())
            
            if st.button("Подготовить отчет"):
                row = my_df[my_df['child_id'] == selected_child].iloc[-1]
                print_text = f"""
                ПРОТОКОЛ СКРИНИНГА РАС
                ------------------------------
                УЧИТЕЛЬ: {row['teacher']}
                УЧЕНИК: {row['child_id']}
                ДАТА: {row['date']}
                РЕЗУЛЬТАТ: {row['score']} баллов из 12
                
                ЗАКЛЮЧЕНИЕ И РЕКОМЕНДАЦИИ ИИ:
                {row['report']}
                ------------------------------
                Подпись: _________________
                """
                st.text_area("Текст для копирования в Word:", print_text, height=200)
                st.download_button("📥 Скачать файл .txt", print_text.encode('utf-8-sig'), f"Otchet_{selected_child}.txt")
        else:
            st.write("В вашем личном журнале пока нет записей.")

else:
    # Заставка для неавторизованных
    st.image("https://img.freepik.com/free-vector/puzzle-background-design_1235-236.jpg", width=300)
    st.info("Добро пожаловать в систему «Спектр-Помощь». Пожалуйста, авторизуйтесь слева, чтобы получить доступ к своим данным.")
