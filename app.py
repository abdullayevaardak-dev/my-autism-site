import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="Спектр-Помощь: Цифровой Консилиум", page_icon="🧩", layout="wide")

def init_db():
    conn = sqlite3.connect('school_consilium_final_v3.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports 
                 (date TEXT, role TEXT, specialist_name TEXT, child_id TEXT, score INTEGER, details TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Список специалистов, необходимых для закрытия консилиума
REQUIRED_ROLES = ["Учитель", "Психолог", "Логопед", "Дефектолог"]

# --- АВТОРИЗАЦИЯ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.sidebar:
    st.header("🔑 Вход в систему")
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
                st.error("Неверный пароль")
    else:
        st.success(f"{st.session_state.role}: {st.session_state.user}")
        if st.button("Выйти"):
            st.session_state.logged_in = False
            st.rerun()

# --- ОСНОВНОЙ МОДУЛЬ ---
if st.session_state.logged_in:
    st.title(f"🧩 Рабочее место: {st.session_state.role}")
    tabs = st.tabs(["📝 Провести обследование", "📄 Итоговый протокол ИИ", "📁 Архив"])

    with tabs[0]:
        child_id = st.text_input("Идентификатор ученика (ФИО)", "Иванов Иван")
        st.write("---")
        
        score = 0
        details_list = []

        # --- АНКЕТА УЧИТЕЛЯ (12 ВОПРОСОВ) ---
        if st.session_state.role == "Учитель":
            st.subheader("Скрининг-анкета для классного руководителя")
            q = [
                st.checkbox("Необычный визуальный контакт (взгляд «сквозь» человека)"),
                st.checkbox("Предпочитает играть или находиться в одиночестве"),
                st.checkbox("Не понимает личных границ (близость/касания)"),
                st.checkbox("Редко делится радостями или достижениями"),
                st.checkbox("Использует в речи цитаты или повторы (эхолалия)"),
                st.checkbox("Речь звучит «роботизированно» или официально"),
                st.checkbox("Не понимает сарказм, шутки (буквальное понимание)"),
                st.checkbox("Трудности с инициацией разговора / просьбой"),
                st.checkbox("Остро реагирует на шумы (звонок, столовая)"),
                st.checkbox("Необычные пищевые привычки"),
                st.checkbox("Повторяющиеся движения (взмахи, раскачивания)"),
                st.checkbox("Стресс при изменении распорядка или маршрута")
            ]
            score = sum(q)
            details_list.append(f"Педагогические маркеры: {score}/12")

        # --- АНКЕТА ПСИХОЛОГА (14 ВОПРОСОВ) ---
        elif st.session_state.role == "Психолог":
            st.subheader("Скрининг-тест психолога")
            p = [
                st.checkbox("Удерживание взгляда кратковременное/отсутствует"),
                st.checkbox("Отсутствие разделенного внимания (не показывает пальцем)"),
                st.checkbox("Несоответствующий эмоциональный отклик"),
                st.checkbox("Трудности определения эмоций по картинкам"),
                st.checkbox("Речь только для просьб (нет спонтанного общения)"),
                st.checkbox("Невыполнение простых инструкций с первого раза"),
                st.checkbox("Монотонная или слишком громкая интонация"),
                st.checkbox("Буквальное понимание переносного смысла"),
                st.checkbox("Трудности объединения предметов в группы (обобщение)"),
                st.checkbox("Ошибки в логике (Четвертый лишний)"),
                st.checkbox("Нарушение причинно-следственных связей"),
                st.checkbox("Наличие навязчивых движений (стереотипии)"),
                st.checkbox("Сенсорный поиск или избегание (трогает всё / боится грязи)"),
                st.checkbox("Высокий уровень тревожности при переменах")
            ]
            score = sum(p)
            details_list.append(f"Психологические маркеры: {score}/14")

        # --- АНКЕТА ЛОГОПЕДА ---
        elif st.session_state.role == "Логопед":
            st.subheader("Логопедический скрининг")
            l = [
                st.checkbox("Эхолалия (повторение фраз)"),
                st.checkbox("Путаница местоимений (Я/Он)"),
                st.checkbox("Нарушение просодики (ритм/темп)"),
                st.checkbox("Отсутствие коммуникативной инициативы"),
                st.checkbox("Трудности понимания многоступенчатых инструкций"),
                st.checkbox("Нарушение прагматики речи (поддержание диалога)")
            ]
            score = sum(l)
            details_list.append(f"Речевые дефициты: {score}/6")

        # --- АНКЕТА ДЕФЕКТОЛОГА ---
        elif st.session_state.role == "Дефектолог":
            st.subheader("Дефектологический скрининг")
            d = [
                st.checkbox("Трудности имитации простых действий"),
                st.checkbox("Слабая зрительно-моторная координация"),
                st.checkbox("Непонимание пространственных предлогов (над/под/за)"),
                st.checkbox("Трудности переключения между задачами"),
                st.checkbox("Нарушение узнавания сенсорных эталонов (форма/цвет)"),
                st.checkbox("Трудности логического обобщения")
            ]
            score = sum(d)
            details_list.append(f"Когнитивные дефициты: {score}/6")

        if st.button("💾 Сохранить в архив консилиума"):
            conn = sqlite3.connect('school_consilium_final_v3.db')
            c = conn.cursor()
            now = datetime.now().strftime("%d.%m.%Y %H:%M")
            summary = " ".join(details_list)
            c.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)", 
                      (now, st.session_state.role, st.session_state.user, child_id, score, summary))
            conn.commit()
            conn.close()
            st.success(f"Результат специалиста {st.session_state.user} успешно сохранен!")

    with tabs[1]:
        st.subheader("📋 Генерация Итогового Протокола")
        conn = sqlite3.connect('school_consilium_final_v3.db')
        all_data = pd.read_sql_query("SELECT * FROM reports", conn)
        conn.close()
        
        if not all_data.empty:
            target_child = st.selectbox("Выберите ученика", all_data['child_id'].unique())
            child_results = all_data[all_data['child_id'] == target_child]
            
            # Проверка полноты данных
            roles_submitted = child_results['role'].unique()
            missing = [r for r in REQUIRED_ROLES if r not in roles_submitted]
            
            st.write("**Статус готовности данных:**")
            cols = st.columns(len(REQUIRED_ROLES))
            for i, r in enumerate(REQUIRED_ROLES):
                cols[i].metric(r, "✅ Да" if r in roles_submitted else "❌ Нет")

            if not missing:
                st.success("✅ Все данные собраны. ИИ готов к формированию протокола.")
                if st.button("🤖 Сгенерировать Протокол и Рекомендации"):
                    total_score = child_results['score'].sum()
                    
                    # Логика ИИ-интерпретации
                    if total_score >= 20:
                        risk_level = "ВЫСОКИЙ"
                        advice = "Необходима консультация ПМПК. Рекомендовано обучение по АОП (вариант 8.2/8.3), тьюторское сопровождение и коррекционные занятия (логопед, дефектолог, психолог) не менее 5 раз в неделю."
                    elif total_score >= 10:
                        risk_level = "СРЕДНИЙ"
                        advice = "Рекомендована адаптация образовательной среды: визуальные опоры, сенсорная разгрузка. Занятия с психологом по развитию социальных навыков."
                    else:
                        risk_level = "НИЗКИЙ"
                        advice = "Выраженных признаков не обнаружено. Рекомендовано плановое педагогическое наблюдение и развитие коммуникации в группе."

                    # Формирование текста отчета
                    final_report = f"""ИТОГОВЫЙ ПРОТОКОЛ КОНСИЛИУМА: {target_child}
Дата завершения: {datetime.now().strftime('%d.%m.%Y')}
--------------------------------------------------
РЕЗУЛЬТАТЫ СПЕЦИАЛИСТОВ:
"""
                    for _, row in child_results.iterrows():
                        final_report += f"- {row['role']} ({row['specialist_name']}): {row['details']} (Балл: {row['score']})\n"
                    
                    final_report += f"""
--------------------------------------------------
ЗАКЛЮЧЕНИЕ ИИ-ПОМОЩНИКА:
Общий суммарный балл: {total_score}
Уровень риска: {risk_level}

РЕКОМЕНДАЦИИ:
{advice}
--------------------------------------------------
Члены консилиума: ________________ / {', '.join(child_results['specialist_name'].unique())} /
"""
                    st.text_area("Предпросмотр протокола:", final_report, height=400)
                    st.download_button(
                        label="📥 Скачать Итоговый Протокол (.txt)",
                        data=final_report.encode('utf-16'),
                        file_name=f"Protocol_{target_child}.txt",
                        mime="text/plain"
                    )
            else:
                st.warning(f"Для генерации отчета не хватает данных от: {', '.join(missing)}")
        else:
            st.info("В базе данных пока нет записей.")

    with tabs[2]:
        st.subheader("Архив всех обследований")
        st.dataframe(all_data, use_container_width=True)

else:
    st.info("Пожалуйста, авторизуйтесь в боковой панели, чтобы получить доступ к тестам.")
