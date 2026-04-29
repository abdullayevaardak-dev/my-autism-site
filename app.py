import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Спектр-Помощь: Скрининг", page_icon="🧩", layout="wide")

# --- ФУНКЦИИ БАЗЫ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('school_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                 (date TEXT, child_id TEXT, total_score INTEGER, interpretation TEXT)''')
    conn.commit()
    conn.close()

def save_result(child_id, score, text):
    conn = sqlite3.connect('school_data.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?)", (now, child_id, score, text))
    conn.commit()
    conn.close()

# Инициализация БД
init_db()

# --- ИНТЕРФЕЙС ---
st.title("🧩 Система «Спектр-Помощь»")
st.caption("Профессиональный скрининг для классных руководителей")

with st.sidebar:
    st.header("Данные")
    child_id = st.text_input("Код/ФИО ученика", "Ученик-01")
    st.divider()
    st.write("**Инструкция:** Отметьте утверждения, которые проявляются регулярно (минимум 6 месяцев).")

tab1, tab2 = st.tabs(["📝 Анкета", "📊 Журнал записей"])

with tab1:
    st.subheader("Скрининг-анкета")
    
    # 1. Социальное взаимодействие
    with st.expander("1. Социальное взаимодействие", expanded=True):
        s1 = st.checkbox("Необычный визуальный контакт (избегает или смотрит «сквозь»)")
        s2 = st.checkbox("Предпочитает одиночество; нет интереса к сверстникам")
        s3 = st.checkbox("Не понимает личных границ (близость/касания)")
        s4 = st.checkbox("Редко делится радостями/достижениями с классом")

    # 2. Коммуникация и речь
    with st.expander("2. Коммуникация и речь", expanded=True):
        c1 = st.checkbox("Использует цитаты/повторы вместо своих слов (эхолалия)")
        c2 = st.checkbox("Речь звучит «роботизированно» или официально")
        c3 = st.checkbox("Понимает всё буквально (не понимает сарказм/шутки)")
        c4 = st.checkbox("Трудности с инициацией разговора (не может попросить о помощи)")

    # 3. Сенсорное восприятие и поведение
    with st.expander("3. Сенсорное восприятие и поведение", expanded=True):
        p1 = st.checkbox("Остро реагирует на шум (звонок, столовая), закрывает уши")
        p2 = st.checkbox("Необычные пищевые привычки (ест только 2-3 вида продуктов)")
        p3 = st.checkbox("Повторяющиеся движения (взмахи руками, раскачивания)")
        p4 = st.checkbox("Сильный стресс при замене урока или изменении маршрута")

    if st.button("📈 Получить интерпретацию ИИ"):
        total_score = sum([s1, s2, s3, s4, c1, c2, c3, c4, p1, p2, p3, p4])
        
        # ЛОГИКА ИИ-ПОМОЩНИКА (ИНТЕРПРЕТАЦИЯ)
        if total_score == 0:
            interpretation = "Маркеров РАС не обнаружено. Поведение в пределах возрастной нормы."
            st.success(interpretation)
        elif 1 <= total_score <= 3:
            interpretation = "Низкий риск. Есть отдельные особенности. Рекомендуется наблюдение в течение четверти."
            st.info(interpretation)
        elif 4 <= total_score <= 6:
            interpretation = "Средний риск. Выявлено несколько ключевых маркеров. Рекомендуется консультация школьного психолога и мягкая адаптация среды."
            st.warning(interpretation)
        else:
            interpretation = "Высокий риск. Наблюдается комплекс дефицитов. Необходима консультация ПМПК для разработки ИУП и создания специальных условий."
            st.error(interpretation)
        
        # Сохранение в базу
        save_result(child_id, total_score, interpretation)
        st.toast("Результат сохранен в журнал!")

with tab2:
    st.subheader("История скринингов")
    conn = sqlite3.connect('school_data.db')
    df = pd.read_sql_query("SELECT * FROM results", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Журнал пока пуст.")
