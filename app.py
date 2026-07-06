import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Спектр-Помощь: Консилиум ПМПК", page_icon="🧩", layout="wide")

# --- ПОДКЛЮЧЕНИЕ К SUPABASE (ОБЛАКО) ---
@st.cache_resource
def init_connection():
    return create_engine(st.secrets["DATABASE_URL"])

engine = init_connection()

def init_db():
    with engine.begin() as conn:
        conn.execute(text('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)'''))
        conn.execute(text('''CREATE TABLE IF NOT EXISTS teacher_reports 
                     (id SERIAL PRIMARY KEY, date TEXT, teacher_name TEXT, child_id TEXT, 
                      asd_score INTEGER, adhd_score INTEGER, details TEXT, adhd_details TEXT, notes TEXT, lang TEXT)'''))
        conn.execute(text('''CREATE TABLE IF NOT EXISTS psychologist_reports 
                     (id SERIAL PRIMARY KEY, date TEXT, psych_name TEXT, child_id TEXT, 
                      total_score INTEGER, details TEXT, notes TEXT, lang TEXT)'''))
        conn.execute(text('''CREATE TABLE IF NOT EXISTS speech_reports 
                     (id SERIAL PRIMARY KEY, date TEXT, speech_name TEXT, child_id TEXT, 
                      total_score INTEGER, details TEXT, notes TEXT, lang TEXT)'''))
        conn.execute(text('''CREATE TABLE IF NOT EXISTS defect_reports 
                     (id SERIAL PRIMARY KEY, date TEXT, defect_name TEXT, child_id TEXT, 
                      total_score INTEGER, details TEXT, notes TEXT, lang TEXT)'''))

init_db()

# --- МУЛЬТИЯЗЫЧНЫЙ СЛОВАРЬ (С РАСШИРЕННОЙ АНКЕТОЙ УЧИТЕЛЯ) ---
LANG_DATA = {
    'Русский': {
        'site_title': "ЦППМСП «Спектр-Помощь»",
        'site_subtitle': "Единая цифровая платформа психолого-медико-педагогического консилиума",
        'tab_survey': "📝 Новое обследование",
        'tab_report': "📋 Комплексный отчет ПМПК",
        'tab_history': "📁 Архив записей",
        'child_label': "Код ученика (для анонимности)",
        'child_placeholder': "Например: 1А01",
        'date_label': "Дата обследования",
        'save_btn': "💾 Сохранить данные специалиста",
        'report_gen': "🤖 Сформировать заключение ПМПК",
        'auth_title': "Авторизация специалиста",
        'auth_role': "Выберите вашу роль:",
        'auth_name': "Ваша Фамилия и Инициалы",
        'auth_pwd': "Ваш личный пароль",
        'auth_btn': "Войти в систему",
        'extra_notes_label': "✍️ Дополнительные экспертные наблюдения:",
        'placeholder_notes': "Введите информацию, которая не вошла в чек-лист...",
        
        # Учитель
        'teach_title': "🏫 Кабинет Учителя (Педагогический чек-лист)",
        'teach_secs': ["1️⃣ Маркеры особенностей поведения и общения (РАС)", "2️⃣ Маркеры внимания, гиперактивности и темпа (СДВГ)"],
        'teach_q': [
            "Трудности в установлении зрительного контакта и общения со сверстниками",
            "Наличие стереотипных, повторяющихся движений или действий",
            "Выраженная дезадаптация при изменении привычного расписания/обстановки",
            "Проявление вспышек гнева, агрессии или ухода в себя при трудностях",
            "Трудности концентрации и удержания внимания на учебной задаче",
            "Повышенная отвлекаемость на посторонние раздражители",
            "Суетливость, нетерпеливость, частые выкрики с места (импульсивность)",
            "Выраженно замедленный или неравномерный темп работы на уроке"
        ],
        
        # Логопед
        'logo_title': "🗣 Кабинет Логопеда (Речевая карта)",
        'logo_secs': ["1️⃣ Звукопроизношение и артикуляция", "2️⃣ Слоговая структура", "3️⃣ Фонематические процессы", "4️⃣ Лексико-грамматический строй", "5️⃣ Темпо-ритмическая организация"],
        'logo_q': ["Нарушения звукопроизношения", "Нарушения артикуляционной моторики", "Искажение слоговой структуры", "Нарушение фонематического слуха", "Трудности звукового анализа", "Бедный словарный запас", "Аграмматизмы", "Нарушение связной речи", "Темпо-ритмические нарушения"],
        
        # Дефектолог
        'def_title': "🎓 Кабинет Дефектолога (Специального педагога)",
        'def_secs': ["1️⃣ Зона ближайшего развития", "2️⃣ Высшие психические функции", "3️⃣ Сформированность представлений", "4️⃣ Академические навыки"],
        'def_q': ["Низкая обучаемость", "Несформированность учебной/игровой деятельности", "Нарушение зрительного/слухового гнозиса", "Дефициты конструирования и праксиса", "Особенности мышления (классификация, логика)", "Незнание сенсорных эталонов", "Нарушение временных/пространственных ориентировок", "Трудности формирования чтения", "Нарушения письма (дисграфия)", "Нарушения счета (дискалькулия)"]
    },
    'Қазақша': {
        'site_title': "«Спектр-Көмек» ПМПҚ Орталығы",
        'site_subtitle': "Психологиялық-медициналық-педагогикалық консилиумның бірыңғай цифрлық платформасы",
        'tab_survey': "📝 Жаңа тексеру",
        'tab_report': "📋 ПМПК кешенді есебі",
        'tab_history': "📁 Жазбалар архиві",
        'child_label': "Оқушы коды (анонимділік үшін)",
        'child_placeholder': "Мысалы: 1А01",
        'date_label': "Тексеру күні",
        'save_btn': "💾 Мәліметтерді сақтау",
        'report_gen': "🤖 ПМПК қорытындысын дайындау",
        'auth_title': "Маманның авторизациясы",
        'auth_role': "Рөліңізді таңдаңыз:",
        'auth_name': "Тегіңіз бен аты-жөніңіз",
        'auth_pwd': "Жеке құпия сөзіңіз",
        'auth_btn': "Жүйеге кіру",
        'extra_notes_label': "✍️ Маманның қосымша ескертулері:",
        'placeholder_notes': "Ақпаратты енгізіңіз...",
        
        # Учитель (Қаз)
        'teach_title': "🏫 Мұғалім кабинеті (Педагогикалық чек-лист)",
        'teach_secs': ["1️⃣ Мінез-құлық пен қарым-қатынас ерекшеліктерінің маркерлері (РАС)", "2️⃣ Назар аудару, белсенділік және жұмыс қарқынының маркерлері (СДВГ)"],
        'teach_q': [
            "Қатарластарымен көзбен байланыс орнату және қарым-қатынас жасау қиындықтары",
            "Стереотипті, қайталанатын қимылдардың немесе әрекеттердің болуы",
            "Әдеттегі кесте немесе орта өзгерген кезде айқын дезадаптация",
            "Қиындықтар туындағанда ашулану, агрессия немесе тұйықталу көріністері",
            "Оқу тапсырмасына назар аудару және оны ұстап тұру қиындықтары",
            "Сыртқы тітіркендіргіштерге алаңдаушылықтың жоғары болуы",
            "Мазасыздық, төзімсіздік, орыннан жиі айқайлау (импульсивтілік)",
            "Сабақтағы жұмыс қарқынының айқын баяулауы немесе біркелкі болмауы"
        ],
        
        # Логопед (Қаз)
        'logo_title': "🗣 Логопед кабинеті (Сөйлеу картасы)",
        'logo_secs': ["1️⃣ Дыбыстың айтылуы", "2️⃣ Сөздің буындық құрылымы", "3️⃣ Фонематикалық үрдістер", "4️⃣ Лексика-грамматикалық құрылым", "5️⃣ Сөйлеу қарқыны"],
        'logo_q': ["Дыбыстың айтылуындағы бұзылыстар", "Артикуляциялық моториканың бұзылуы", "Сөздің буындық құрылымын бұрмалау", "Фонематикалық есту қабілетінің бұзылуы", "Дыбыстық талдау қиындықтары", "Сөздік қордың жұтаңдығы", "Аграмматизмдер", "Байланыстырып сөйлеудің бұзылуы", "Сөйлеу қарқынының бұзылуы"],
        
        # Дефектолог (Қаз)
        'def_title': "🎓 Дефектолог кабинеті",
        'def_secs': ["1️⃣ Жақын арадағы даму аймағы", "2️⃣ Жоғары психикалық функциялар", "3️⃣ Қарапайым түсініктер", "4️⃣ Академиялық дағдылар"],
        'def_q': ["Төмен оқытылу деңгейі", "Оқу/ойын әрекетінің қалыктаспауы", "Көру және есту гнозисінің бұзылуы", "Конструкциялық праксис дефициті", "Ойлау ерекшеліктері (топтастыру, логика)", "Сенсорлық эталондарды білмеу", "Уақыт пен кеңістікті бағдарлай алмау", "Оқу дағдысының қиындықтары", "Жазудың бұзылыстары", "Есептеу дағдысының бұзылуы"]
    }
}

if 'language' not in st.session_state: st.session_state.language = 'Русский'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = 'Учитель'

T = LANG_DATA[st.session_state.language]

# --- САЙДБАР ---
with st.sidebar:
    st.title("⚙️ Настройки / Баптаулар")
    st.radio("Язык / Тіл:", ['Русский', 'Қазақша'], key='lang_choice', on_change=lambda: setattr(st.session_state, 'language', st.session_state.lang_choice))
    st.write("---")
    if st.session_state.logged_in:
        st.write(f"👤 {st.session_state.user}")
        st.write(f"🎭 {st.session_state.role}")
        if st.button("Выйти / Шығу"):
            st.session_state.logged_in = False
            st.rerun()

# --- ЭКРАН АВТОРИЗАЦИИ ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align: center; color: #2e6c80;'>{T['site_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{T['site_subtitle']}</h4>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader(T['auth_title'])
        role = st.selectbox(T['auth_role'], ["Учитель", "Психолог", "Логопед", "Дефектолог"])
        u_name = st.text_input(T['auth_name'], placeholder="Иванова И.И.").strip()
        u_pwd = st.text_input(T['auth_pwd'], type="password")
        
        if st.button(T['auth_btn'], use_container_width=True, type="primary"):
            if (u_name.lower() == "ардак" or u_name.lower() == "директор") and u_pwd == "Admin2026":
                st.session_state.logged_in = True
                st.session_state.user = "Абдуллаева А.Ш. (Руководитель)"
                st.session_state.role = "Админ"
                st.rerun()
            elif u_name and u_pwd:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT password, role FROM users WHERE username = :u"), {"u": u_name}).fetchone()
                    if result:
                        saved_pwd, saved_role = result
                        if saved_pwd == u_pwd:
                            st.session_state.logged_in = True
                            st.session_state.user = u_name
                            st.session_state.role = saved_role
                            st.rerun()
                        else:
                            st.error("Неверный пароль!")
                    else:
                        with engine.begin() as insert_conn:
                            insert_conn.execute(text("INSERT INTO users (username, password, role) VALUES (:u, :p, :r)"), {"u": u_name, "p": u_pwd, "r": role})
                        st.session_state.logged_in = True
                        st.session_state.user = u_name
                        st.session_state.role = role
                        st.rerun()

    st.write("---")
    st.markdown("""
        <div style='text-align: center; color: gray; font-size: 14px;'>
            <b>Разработка и поддержка системы:</b><br>
            Абдуллаева Ардақ Шығайқызы<br>
            📞 Тел: +7 (778) 795-46-38 | ✉️ E-mail: <a href='mailto:ardak.abdullayeva@aktau7.edu.kz'>ardak.abdullayeva@aktau7.edu.kz</a>
        </div>
    """, unsafe_allow_html=True)

# --- ПАНЕЛЬ АДМИНА ---
elif st.session_state.role == "Админ":
    st.title("🛡️ Закрытая панель Администратора (Облако Supabase)")
    st.success("Все данные теперь безопасно хранятся в облачной базе PostgreSQL!")
    
    st.subheader("👥 Пользователи платформы")
    try:
        users_df = pd.read_sql_query("SELECT username as Имя, role as Должность, password as Пароль FROM users", engine)
        st.dataframe(users_df, use_container_width=True)
    except Exception as e: st.write("ОШИБКА:", e)
        
    st.write("---")
    st.subheader("🗄️ База данных ПМПК")
    adm_tabs = st.tabs(["Учителя", "Психологи", "Логопеды", "Дефектологи"])
    with adm_tabs[0]: st.dataframe(pd.read_sql_query("SELECT * FROM teacher_reports", engine))
    with adm_tabs[1]: st.dataframe(pd.read_sql_query("SELECT * FROM psychologist_reports", engine))
    with adm_tabs[2]: st.dataframe(pd.read_sql_query("SELECT * FROM speech_reports", engine))
    with adm_tabs[3]: st.dataframe(pd.read_sql_query("SELECT * FROM defect_reports", engine))

# --- РАБОЧАЯ ЗОНА СПЕЦИАЛИСТОВ ---
else:
    st.title(f"🧩 Кабинет: {st.session_state.role}")
    tabs = st.tabs([T['tab_survey'], T['tab_report'], T['tab_history']])

    # ================= 1. АНКЕТЫ =================
    with tabs[0]:
        c_col1, c_col2 = st.columns(2)
        child_name = c_col1.text_input(T['child_label'], placeholder=T['child_placeholder'])
        survey_date = c_col2.date_input(T['date_label'], datetime.now())
        st.write("---")

        extra_notes = ""
        
        # --- ЛОГОПЕД ---
        if st.session_state.role == "Логопед":
            st.subheader(T['logo_title'])
            st.markdown(f"### {T['logo_secs'][0]}")
            l1, l2 = st.checkbox(T['logo_q'][0]), st.checkbox(T['logo_q'][1])
            st.markdown(f"### {T['logo_secs'][1]}")
            l3 = st.checkbox(T['logo_q'][2])
            st.markdown(f"### {T['logo_secs'][2]}")
            l4, l5 = st.checkbox(T['logo_q'][3]), st.checkbox(T['logo_q'][4])
            st.markdown(f"### {T['logo_secs'][3]}")
            l6, l7, l8 = st.checkbox(T['logo_q'][5]), st.checkbox(T['logo_q'][6]), st.checkbox(T['logo_q'][7])
            st.markdown(f"### {T['logo_secs'][4]}")
            l9 = st.checkbox(T['logo_q'][8])
            
            extra_notes = st.text_area(T['extra_notes_label'], placeholder=T['placeholder_notes'])
            if st.button(T['save_btn'], use_container_width=True, type="primary"):
                if child_name:
                    l_score = sum([l1,l2,l3,l4,l5,l6,l7,l8,l9])
                    l_det = f"Артик:{sum([l1,l2])};Слог:{l3};Фон:{sum([l4,l5])};Лекс:{sum([l6,l7,l8])};Темп:{l9}"
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO speech_reports (date, speech_name, child_id, total_score, details, notes, lang) VALUES (:d, :n, :c, :s, :det, :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state.user, "c": child_name, "s": l_score, "det": l_det, "not": extra_notes, "l": st.session_state.language})
                    st.success("✅ Данные логопеда успешно загружены в облако!")
                else: st.error("Укажите код ученика!")

        # --- ДЕФЕКТОЛОГ ---
        elif st.session_state.role == "Дефектолог":
            st.subheader(T['def_title'])
            st.markdown(f"### {T['def_secs'][0]}")
            d1, d2 = st.checkbox(T['def_q'][0]), st.checkbox(T['def_q'][1])
            st.markdown(f"### {T['def_secs'][1]}")
            d3, d4, d5 = st.checkbox(T['def_q'][2]), st.checkbox(T['def_q'][3]), st.checkbox(T['def_q'][4])
            st.markdown(f"### {T['def_secs'][2]}")
            d6, d7 = st.checkbox(T['def_q'][5]), st.checkbox(T['def_q'][6])
            st.markdown(f"### {T['def_secs'][3]}")
            d8, d9, d10 = st.checkbox(T['def_q'][7]), st.checkbox(T['def_q'][8]), st.checkbox(T['def_q'][9])
            
            extra_notes = st.text_area(T['extra_notes_label'], placeholder=T['placeholder_notes'])
            if st.button(T['save_btn'], use_container_width=True, type="primary"):
                if child_name:
                    d_score = sum([d1,d2,d3,d4,d5,d6,d7,d8,d9,d10])
                    d_det = f"Обуч:{sum([d1,d2])};ВПФ:{sum([d3,d4,d5])};Сенс:{sum([d6,d7])};Акад:{sum([d8,d9,d10])}"
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO defect_reports (date, defect_name, child_id, total_score, details, notes, lang) VALUES (:d, :n, :c, :s, :det, :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state.user, "c": child_name, "s": d_score, "det": d_det, "not": extra_notes, "l": st.session_state.language})
                    st.success("✅ Данные дефектолога сохранены в облако!")
                else: st.error("Укажите код ученика!")

        # --- УЧИТЕЛЬ (ОБНОВЛЕННЫЙ, С ВОПРОСАМИ!) ---
        elif st.session_state.role == "Учитель":
            st.subheader(T['teach_title'])
            
            st.markdown(f"### {T['teach_secs'][0]}")
            t1 = st.checkbox(T['teach_q'][0])
            t2 = st.checkbox(T['teach_q'][1])
            t3 = st.checkbox(T['teach_q'][2])
            t4 = st.checkbox(T['teach_q'][3])
            
            st.markdown(f"### {T['teach_secs'][1]}")
            t5 = st.checkbox(T['teach_q'][4])
            t6 = st.checkbox(T['teach_q'][5])
            t7 = st.checkbox(T['teach_q'][6])
            t8 = st.checkbox(T['teach_q'][7])
            
            extra_notes = st.text_area(T['extra_notes_label'], placeholder=T['placeholder_notes'])
            if st.button(T['save_btn'], use_container_width=True, type="primary"):
                if child_name:
                    asd_total = sum([t1, t2, t3, t4])
                    adhd_total = sum([t5, t6, t7, t8])
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO teacher_reports (date, teacher_name, child_id, asd_score, adhd_score, details, adhd_details, notes, lang) VALUES (:d, :n, :c, :a, :ad, :det, :adet, :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state.user, "c": child_name, "a": asd_total, "ad": adhd_total, "det": "РАС", "adet": "СДВГ", "not": extra_notes, "l": st.session_state.language})
                    st.success("✅ Данные педагога отправлены в облако!")
                else: st.error("Укажите код ученика!")

        # --- ПСИХОЛОГ ---
        elif st.session_state.role == "Психолог":
            st.subheader("Анкета Психолога")
            p1, p2, p3 = st.checkbox("Высокая тревожность"), st.checkbox("Эмоциональная лабильность"), st.checkbox("Агрессия")
            p4, p5 = st.checkbox("Истощаемость процессов"), st.checkbox("Трудности памяти/внимания")
            extra_notes = st.text_area(T['extra_notes_label'], placeholder=T['placeholder_notes'])
            if st.button(T['save_btn'], use_container_width=True, type="primary"):
                if child_name:
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO psychologist_reports (date, psych_name, child_id, total_score, details, notes, lang) VALUES (:d, :n, :c, :s, :det, :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state.user, "c": child_name, "s": sum([p1,p2,p3,p4,p5]), "det": f"Эмоц:{sum([p1,p2,p3])};Когн:{sum([p4,p5])}", "not": extra_notes, "l": st.session_state.language})
                    st.success("✅ Данные психолога успешно сохранены!")
                else: st.error("Укажите код ученика!")

    # ================= 2. КОМПЛЕКСНЫЙ ОТЧЕТ =================
    with tabs[1]:
        st.subheader("📊 Аналитический модуль ПМПК")
        all_children = []
        for tbl in ['teacher_reports', 'psychologist_reports', 'speech_reports', 'defect_reports']:
            try:
                df_c = pd.read_sql_query(f"SELECT child_id FROM {tbl}", engine)
                all_children.extend(df_c['child_id'].tolist())
            except: pass
        
        unique_children = list(set(all_children))
        if unique_children:
            sel_child = st.selectbox("Выберите код ученика для отчета", unique_children)
            if st.button(T['report_gen'], use_container_width=True, type="primary"):
                st.divider()
                st.markdown(f"## 📄 КОМПЛЕКСНОЕ ЗАКЛЮЧЕНИЕ ПМПК")
                st.markdown(f"### Код учащегося: **{sel_child}**")
                
                t_data = pd.read_sql_query(f"SELECT * FROM teacher_reports WHERE child_id='{sel_child}'", engine)
                p_data = pd.read_sql_query(f"SELECT * FROM psychologist_reports WHERE child_id='{sel_child}'", engine)
                l_data = pd.read_sql_query(f"SELECT * FROM speech_reports WHERE child_id='{sel_child}'", engine)
                d_data = pd.read_sql_query(f"SELECT * FROM defect_reports WHERE child_id='{sel_child}'", engine)
                
                st.markdown("#### 🏫 1. Учитель:")
                if not t_data.empty: st.write(f"Маркеры РАС: {t_data.iloc[-1]['asd_score']}, СДВГ: {t_data.iloc[-1]['adhd_score']}. Заметки: {t_data.iloc[-1]['notes']}")
                else: st.warning("Нет данных")
                
                st.markdown("#### 🧠 2. Психолог:")
                if not p_data.empty: st.write(f"Сумма дефицитов: {p_data.iloc[-1]['total_score']} ({p_data.iloc[-1]['details']}). Заметки: {p_data.iloc[-1]['notes']}")
                else: st.warning("Нет данных")
                
                st.markdown("#### 🗣 3. Логопед:")
                if not l_data.empty: st.write(f"Индекс нарушений: {l_data.iloc[-1]['total_score']}/9. Заметки: {l_data.iloc[-1]['notes']}")
                else: st.warning("Нет данных")
                
                st.markdown("#### 🎓 4. Дефектолог:")
                if not d_data.empty: st.write(f"Индекс нарушений: {d_data.iloc[-1]['total_score']}/10. Заметки: {d_data.iloc[-1]['notes']}")
                else: st.warning("Нет данных")
        else:
            st.info("В облачной базе данных пока нет записей.")

    # ================= 3. АРХИВ =================
    with tabs[2]:
        st.subheader("📁 Сводная база данных (Ваш профиль)")
        if st.session_state.role == "Логопед": st.dataframe(pd.read_sql_query("SELECT date, child_id, total_score, notes FROM speech_reports", engine), use_container_width=True)
        elif st.session_state.role == "Дефектолог": st.dataframe(pd.read_sql_query("SELECT date, child_id, total_score, notes FROM defect_reports", engine), use_container_width=True)
        elif st.session_state.role == "Психолог": st.dataframe(pd.read_sql_query("SELECT date, child_id, total_score, notes FROM psychologist_reports", engine), use_container_width=True)
        elif st.session_state.role == "Учитель": st.dataframe(pd.read_sql_query("SELECT date, child_id, asd_score, adhd_score, notes FROM teacher_reports", engine), use_container_width=True)
