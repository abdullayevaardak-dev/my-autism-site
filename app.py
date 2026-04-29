import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Спектр-Помощь PRO", page_icon="🧩", layout="wide")

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('school_final.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                 (date TEXT, teacher TEXT, child_id TEXT, score INTEGER, recommendations TEXT)''')
    conn.commit()
    conn.close()

def save_to_db(teacher, child_id, score, recs):
    conn = sqlite3.connect('school_final.db')
    c = conn.cursor()
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?)", (now, teacher, child_id, score, recs))
    conn.commit()
    conn.close()

init_db()

# --- АВТОРИЗАЦИЯ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.title("🔐 Вход")
    if not st.session_state.logged_in:
        user = st.text_input("Фамилия педагога")
        pwd = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if pwd == "12345":
                st.session_state.logged_in = True
                st.session_state.teacher = user
                st.rerun()
            else:
                st.error("Неверный пароль")
    else:
        st.success(f"Личный кабинет: {st.session_state.teacher}")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

# --- ОСНОВНОЙ КОНТЕНТ ---
if st.session_state.logged_in:
    st.title("🧩 Скрининг-система «Спектр-Помощь»")
    
    tab1, tab2 = st.tabs(["📝 Новая анкета", "📁 Архив и Печать"])

    with tab1:
        child_id = st.text_input("Ученик (Код или ФИО)", "Ученик-01")
        st.markdown("### Скрининг-анкета для классного руководителя")
        st.info("Инструкция: Отметьте утверждения, проявляющиеся регулярно в течение последних 6 месяцев.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 1. Социальное взаимодействие")
            s1 = st.checkbox("Необычный визуальный контакт (взгляд «сквозь»)")
            s2 = st.checkbox("Предпочитает одиночество; нет интереса к сверстникам")
            s3 = st.checkbox("Не понимает личных границ (касания/близость)")
            s4 = st.checkbox("Редко делится радостями/достижениями с классом")
            
        with col2:
            st.markdown("#### 2. Коммуникация и речь")
            c1 = st.checkbox("Использует цитаты/повторы (эхолалия)")
            c2 = st.checkbox("Речь «роботизированная» или необычная интонация")
            c3 = st.checkbox("Буквальное понимание (не понимает шутки/сарказм)")
            c4 = st.checkbox("Трудности с инициацией разговора/просьбой")
            
        with col3:
            st.markdown("#### 3. Сенсорика и поведение")
            p1 = st.checkbox("Острая реакция на шумы (звонок, столовая)")
            p2 = st.checkbox("Избирательность в еде (отказ от школьной еды)")
            p3 = st.checkbox("Повторяющиеся движения (взмахи, раскачивания)")
            p4 = st.checkbox("Стресс при изменении расписания или маршрута")

        if st.button("💾 Провести анализ ИИ и сохранить"):
            total_score = sum([s1, s2, s3, s4, c1, c2, c3, c4, p1, p2, p3, p4])
            
            # --- ИНТЕРПРЕТАЦИЯ ИИ ---
            if total_score >= 8:
                risk = "ВЫСОКИЙ"
                recs = ("**Рекомендации для психолога:** Срочная углубленная диагностика. "
                        "**Для родителей:** Консультация врача-психиатра. "
                        "**Для учителя:** Использование визуального расписания, организация 'тихого уголка'.")
            elif total_score >= 4:
                risk = "СРЕДНИЙ"
                recs = ("**Рекомендации для психолога:** Наблюдение в динамике, развитие соц. навыков. "
                        "**Для учителя:** Предупреждать об изменениях в расписании заранее, снизить шум.")
            else:
                risk = "НИЗКИЙ"
                recs = "Явных маркеров РАС не выявлено. Рекомендуется общее педагогическое наблюдение."

            full_report = f"Уровень риска: {risk}\n\n{recs}"
            
            save_to_db(st.session_state.teacher, child_id, total_score, full_report)
            st.success("Результат успешно сохранен в ваш личный журнал!")
            st.markdown(f"### Анализ ИИ:\n {full_report}")

    with tab2:
        st.subheader("Мой личный архив")
        conn = sqlite3.connect('school_final.db')
        # Фильтруем, чтобы учитель видел только своих детей
        df = pd.read_sql_query("SELECT * FROM results WHERE teacher = ?", conn, params=(st.session_state.teacher,))
        conn.close()

        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("🖨 Формирование отчета для печати")
            selected_id = st.selectbox("Выберите ученика", df['child_id'].unique())
            
            if st.button("Подготовить документ"):
                row = df[df['child_id'] == selected_id].iloc[-1]
                report_text = f"""
ОТЧЕТ ПО РЕЗУЛЬТАТАМ СКРИНИНГА РАС
--------------------------------------------------
Дата обследования: {row['date']}
Педагог: {row['teacher']}
Ученик: {row['child_id']}
Результат: {row['score']} баллов из 12
--------------------------------------------------
ИНТЕРПРЕТАЦИЯ И РЕКОМЕНДАЦИИ ИИ:
{row['recommendations']}
--------------------------------------------------
Подпись педагога: _________________
                """
                st.text_area("Готовый отчет (можно скопировать):", report_text, height=300)
                st.download_button("📥 Скачать файл отчета", report_text.encode('utf-8-sig'), f"Report_{selected_id}.txt")
        else:
            st.write("В вашем журнале пока нет записей.")
else:
    st.warning("Пожалуйста, войдите в систему слева.")
