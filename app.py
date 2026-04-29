import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
from fpdf import FPDF # Библиотека для создания PDF
import base64

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Спектр-Помощь PRO", page_icon="🧩", layout="wide")

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('school_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                 (date TEXT, teacher TEXT, child_id TEXT, score INTEGER, interpretation TEXT)''')
    conn.commit()
    conn.close()

def save_result(teacher, child_id, score, text):
    conn = sqlite3.connect('school_v2.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?)", (now, teacher, child_id, score, text))
    conn.commit()
    conn.close()

# --- ФУНКЦИЯ ПЕЧАТИ В PDF ---
def create_pdf(child_id, teacher, score, text):
    pdf = FPDF()
    pdf.add_page()
    # Добавляем шрифт, поддерживающий кириллицу (убедитесь, что он есть в папке или используйте стандартный)
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Результаты скрининга «Спектр-Помощь»", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Дата: {datetime.now().strftime('%d.%m.%Y')}", ln=True)
    pdf.cell(200, 10, txt=f"Учитель: {teacher}", ln=True)
    pdf.cell(200, 10, txt=f"Ученик (ID): {child_id}", ln=True)
    pdf.cell(200, 10, txt=f"Общий балл: {score}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Заключение ИИ-помощника: \n{text}")
    pdf.ln(20)
    pdf.cell(200, 10, txt="Подпись педагога: ________________", ln=True)
    
    return pdf.output(dest='S').encode('latin-1', 'replace') # Упрощенная кодировка для примера

# --- ИНИЦИАЛИЗАЦИЯ ---
init_db()

# --- ЛОГИН (АККАУНТ УЧИТЕЛЯ) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

with st.sidebar:
    st.header("🔑 Вход в систему")
    if not st.session_state.auth:
        user = st.text_input("Логин (Фамилия)")
        pwd = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            if pwd == "12345": # Простой пароль для теста
                st.session_state.auth = True
                st.session_state.user = user
                st.success(f"Добро пожаловать, {user}!")
                st.rerun()
            else:
                st.error("Неверный пароль")
    else:
        st.write(f"Вы вошли как: **{st.session_state.user}**")
        if st.button("Выйти"):
            st.session_state.auth = False
            st.rerun()

# --- ОСНОВНОЙ КОНТЕНТ (только если залогинены) ---
if st.session_state.auth:
    st.title("🧩 Рабочее место педагога")
    
    tab1, tab2 = st.tabs(["📝 Новое обследование", "📅 Журнал и Печать"])

    with tab1:
        child_id = st.text_input("ID Ученика", "Ученик-01")
        
        # Блок вопросов (те самые 12 вопросов из анкеты)
        st.subheader("Скрининг-анкета")
        col1, col2 = st.columns(2)
        with col1:
            s_checks = [st.checkbox(f"Вопрос соц. блок {i+1}") for i in range(4)]
            c_checks = [st.checkbox(f"Вопрос речь блок {i+1}") for i in range(4)]
        with col2:
            p_checks = [st.checkbox(f"Вопрос сенсорика блок {i+1}") for i in range(4)]

        if st.button("📈 Рассчитать и Сохранить"):
            total_score = sum(s_checks + c_checks + p_checks)
            
            # Логика ИИ
            if total_score >= 7: interpretation = "ВЫСОКИЙ РИСК. Требуется консультация ПМПК."
            elif total_score >= 4: interpretation = "СРЕДНИЙ РИСК. Рекомендуется школьный психолог."
            else: interpretation = "НИЗКИЙ РИСК. Особенности поведения не критичны."
            
            save_result(st.session_state.user, child_id, total_score, interpretation)
            st.success("Результат занесен в базу данных!")
            st.info(interpretation)

    with tab2:
        st.subheader("Архив обследований")
        conn = sqlite3.connect('school_v2.db')
        df = pd.read_sql_query("SELECT * FROM results", conn)
        conn.close()
        
        if not df.empty:
            st.dataframe(df)
            
            # Выбор записи для печати
            st.write("---")
            st.write("### 🖨 Подготовка отчета для печати")
            row_to_print = st.selectbox("Выберите ID ребенка из базы", df['child_id'].unique())
            
            if st.button("Сгенерировать PDF для печати"):
                # Берем последнюю запись для этого ребенка
                child_data = df[df['child_id'] == row_to_print].iloc[-1]
                pdf_bytes = create_pdf(child_data['child_id'], child_data['teacher'], child_data['score'], child_data['interpretation'])
                
                st.download_button(
                    label="📥 Скачать PDF отчет",
                    data=pdf_bytes,
                    file_name=f"Otchet_{row_to_print}.pdf",
                    mime="application/pdf"
                )
        else:
            st.write("Записей пока нет.")
else:
    st.warning("Пожалуйста, авторизуйтесь через боковую панель.")
