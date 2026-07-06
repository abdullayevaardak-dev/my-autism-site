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

# --- МУЛЬТИЯЗЫЧНЫЙ СЛОВАРЬ ---
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
        'save_btn': "💾 Сохранить данные",
        'report_gen': "🤖 Сформировать заключение ПМПК",
        'auth_title': "Авторизация специалиста",
        'auth_role': "Выберите вашу роль:",
        'auth_name': "Ваша Фамилия и Инициалы",
        'auth_pwd': "Ваш личный пароль",
        'auth_btn': "Войти в систему",
        'extra_notes_label': "✍️ Дополнительные наблюдения:",
        'placeholder_notes': "Введите информацию...",

        # --- УЧИТЕЛЬ (РУС) ---
        'teach_title': "🏫 Анкета Учителя: Маркеры РАС и СДВГ",
        'teach_secs': [
            "РАС: Особенности коммуникации и речи", "РАС: Социальное взаимодействие", "РАС: Поведение и учебный процесс", "РАС: Сенсорные реакции",
            "СДВГ: Невнимательность (Дефицит внимания)", "СДВГ: Гиперактивность (Избыточная моторная активность)", "СДВГ: Импульсивность (Неумение тормозить реакции)"
        ],
        'teach_q': [
            ["Игнорирование обращений: ребенок не отзывается на свое имя, хотя со слухом все в порядке.", "Эхолалия: бесконтрольное повторение чужих слов, фраз или цитат из мультиков.", "Буквальное понимание: невосприимчивость к метафорам, сарказму, скрытому смыслу.", "Специфический тон: монотонная, излишне правильная («роботизированная») или слишком взрослая речь.", "Трудности с диалогом: ребенок может долго говорить на интересную ему тему, но не слушать собеседника."],
            ["Избегание зрительного контакта: ребенок смотрит «сквозь» учителя или быстро отводит глаза.", "Проблемы с границами: полное игнорирование личной дистанции либо, наоборот, резкое отстранение.", "Одиночество на переменах: ребенок не играет с одноклассниками, держится в стороне.", "Трудности с правилами игры: непонимание негласных социальных норм, неумение делиться.", "Нетипичная мимика: выражение лица часто не соответствует ситуации или остается маской."],
            ["Стереотипии (стимминг): повторяющиеся движения тела (взмахи руками, раскачивание).", "Протест против изменений: паника или агрессия при смене расписания, обстановки.", "Узкие интересы: фанатичная увлеченность одной темой в ущерб остальным урокам.", "Особый порядок: стремление раскладывать предметы в строгой последовательности."],
            ["Гиперчувствительность: закрывает уши руками при звонке, криках на перемене.", "Избирательность в еде: ест только строго определенные продукты.", "Дискомфорт от одежды: постоянные попытки снять форму, срезать ярлыки."],
            ["Быстрая отвлекаемость: реагирует на любой шорох, моментально теряя нить урока.", "Проблемы с инструкциями: не может выполнить задание из 3-4 шагов.", "Постоянная потеря вещей: регулярно теряет карандаши, ластики, тетради.", "Ошибки по «глупости»: из-за небрежности пропускает буквы или цифры.", "Избегание умственных усилий: оттягивает начало сложных, монотонных заданий."],
            ["Физическая неусидчивость: постоянно крутится, сползает под парту, раскачивается.", "Постоянные движения руками: вертит ручку, ломает карандаши, стучит пальцами.", "Бесцельное хождение: может встать посреди урока, потому что не в силах сидеть.", "«Шумное» поведение: часто производит много лишних звуков.", "Проблемы на переменах: бегает на пределе скорости, врезается в людей и углы."],
            ["Выкрикивание с места: отвечает до того, как учитель договорил вопрос.", "Перебивание: постоянно встревает в разговоры или прерывает одноклассников.", "Неумение ждать очереди: пытается всегда быть первым, бурно протестует в очереди.", "Слабый самоконтроль: сначала делает или говорит, а потом думает.", "Вспыльчивость: бурно реагирует на проигрыш или замечание, может расплакаться."]
        ],

        # --- ПСИХОЛОГ (РУС) ---
        'psych_title': "🧠 Анкета Психолога",
        'psych_secs': ["Блок 1: Эмоционально-волевая сфера и тревожность", "Блок 2: Когнитивная сфера", "Блок 3: Социализация и адаптация", "Блок 4: Мотивационный компонент"],
        'psych_q': [
            ["Психоэмоциональное напряжение: Высокий уровень базовой тревожности.", "Эмоциональная лабильность: Резкие перепады настроения без видимой причины.", "Агрессивные проявления: Вспышки гнева на сверстников или аутоагрессия.", "Страхи и фобии: Наличие выраженных страхов (доска, тесты, звуки).", "Низкая фрустрационная толерантность: Мгновенно сдается при неудаче."],
            ["Истощаемость психических процессов: Продуктивен только 10–15 минут.", "Особенности памяти: Трудности с кратковременным запоминанием.", "Ригидность мышления: С трудом переключается с алгоритма на алгоритм.", "Пространственная дезориентация: Путает «право/лево», зеркально пишет."],
            ["Проблемы с авторитетом: Трудности в принятии школьных правил.", "Отвержение коллективом: Объект насмешек, буллинга или игнорирования.", "Трудности эмпатии: Не понимает эмоций других людей."],
            ["Школьная дезадаптация: Полное отсутствие учебной мотивации.", "Низкий уровень самооценки: Установки «Я глупый», «У меня не получится»."]
        ],

        # --- ЛОГОПЕД (РУС) ---
        'logo_title': "🗣 Кабинет Логопеда (Речевая карта)",
        'logo_secs': ["Блок 1: Звукопроизношение и артикуляция", "Блок 2: Слоговая структура слова", "Блок 3: Фонематические процессы", "Блок 4: Лексико-грамматический строй", "Блок 5: Темпо-ритмическая организация"],
        'logo_q': [
            ["Нарушения звукопроизношения (сигматизм, ротацизм, ламбдацизм и др.).", "Нарушения артикуляционной моторики (вялость, девиация, тремор)."],
            ["Искажение слоговой структуры (пропуски слогов, перестановки, добавление)."],
            ["Нарушение фонематического слуха (не различает схожие звуки: Б-П, З-С).", "Трудности звукового анализа и синтеза."],
            ["Бедный словарный запас (не знает детенышей, профессий).", "Аграмматизмы (ошибки в согласовании, пропуски предлогов).", "Нарушение связной речи (не может пересказать или составить рассказ)."],
            ["Наличие запинок, заикания, тахилалия или брадилалия."]
        ],

        # --- ДЕФЕКТОЛОГ (РУС) ---
        'def_title': "🎓 Кабинет Дефектолога (Специального педагога)",
        'def_secs': ["Блок 1: Зона ближайшего развития", "Блок 2: Высшие психические функции", "Блок 3: Сформированность представлений", "Блок 4: Академические навыки"],
        'def_q': [
            ["Низкая обучаемость (не принимает помощь, не переносит способ действия).", "Несформированность игровой/учебной деятельности (хаотично перебирает предметы)."],
            ["Нарушение зрительного и слухового гнозиса.", "Дефициты конструирования и праксиса (не может собрать картинку или кубики).", "Особенности мышления (трудности классификации, обобщения)."],
            ["Незнание сенсорных эталонов (путает цвета, формы, размеры).", "Нарушение временных и пространственных ориентировок (путает дни, времена года)."],
            ["Трудности формирования навыка чтения (угадывающее чтение, непонимание).", "Нарушения письма (пропуски, слияние, зеркальное написание).", "Нарушения счета (дискалькулия, путает разряды, не понимает задач)."]
        ]
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
        'extra_notes_label': "✍️ Қосымша ескертулер:",
        'placeholder_notes': "Ақпаратты енгізіңіз...",

        # --- УЧИТЕЛЬ (ҚАЗ) ---
        'teach_title': "🏫 Мұғалім сауалнамасы: РАС және СДВГ маркерлері",
        'teach_secs': [
            "РАС: Коммуникация және сөйлеу ерекшеліктері", "РАС: Әлеуметтік өзара әрекеттесу", "РАС: Мінез-құлық және оқу процесі", "РАС: Сенсорлық реакциялар",
            "СДВГ: Зейінсіздік (Назар аудару тапшылығы)", "СДВГ: Гиперактивтілік (Артық моторлық белсенділік)", "СДВГ: Импульсивтілік (Реакцияларды тежей алмау)"
        ],
        'teach_q': [
            ["Өтініштерді елемеу: есту қабілеті қалыпты болса да, бала өз атына жауап бермейді.", "Эхолалия: басқалардың сөздерін немесе мультфильмдердегі сөздерді бақылаусыз қайталау.", "Тура мағынада түсіну: метафораларды, сарказмды немесе әзілді қабылдамау.", "Ерекше тон: монотонды, тым дұрыс («роботталған») немесе тым ересектерше сөйлеу.", "Диалог құру қиындықтары: бала өзіне қызықты тақырыпта ұзақ сөйлей алады, бірақ сұхбаттасушыны тыңдамайды."],
            ["Көзбен байланыстан қашу: бала мұғалімнің «ішіне» қарайды немесе көзін тез алып қашады.", "Шекаралармен мәселелер: жеке қашықтықты толық елемеу немесе кез келген жанасудан күрт бас тарту.", "Үзілістегі жалғыздық: бала сыныптастарымен ойнамайды, оқшау жүреді.", "Ойын ережелерімен қиындықтар: жазылмаған әлеуметтік нормаларды түсінбеу, бөлісе алмау.", "Типтік емес мимика: бет әлпеті көбінесе жағдайға сәйкес келмейді немесе бетперде сияқты қалады."],
            ["Стереотипиялар (стимминг): қайталанатын дене қимылдары (қолдарын қанат сияқты бұлғау, тербелу).", "Өзгерістерге қарсылық: кестенің немесе мұғалімнің ауысуына паника немесе агрессиямен жауап беру.", "Тар қызығушылықтар: басқа сабақтарға зиянын тигізетіндей бір тақырыпқа фанатикалық қызығушылық.", "Ерекше тәртіп: заттарды қатаң ретпен орналастыруға ұмтылу."],
            ["Аса сезімталдық: қоңырау соғылғанда немесе үзілістегі айқайлардан құлағын қолмен жабады.", "Тамақ талғау: мектеп асханасында тек белгілі бір өнімдерді жейді.", "Киімнен жайсыздық: мектеп формасын шешуге, затбелгілерді кесіп тастауға үнемі тырысу."],
            ["Тез алаңдаушылық: кез келген сыбдырға жауап беріп, сабақ желісін бірден жоғалтады.", "Нұсқаулармен мәселелер: 3-4 қадамдық тапсырманы орындай алмайды.", "Заттарды үнемі жоғалту: қарындаштарды, дәптерлерді үнемі жоғалтады.", "«Ақымақ» қателер: ұқыпсыздықтан әріптерді, тыныс белгілерін немесе сандарды тастап кетеді.", "Ақыл-ой күшінен қашу: күрделі тапсырмаларды бастауды барынша кешіктіреді."],
            ["Физикалық шыдамсыздық: үнемі бұрылады, партаның астына сырғып түседі, орындықта тербеледі.", "Қолдың үнемі қозғалыста болуы: қаламды айналдырады, саусақтарымен үстелді қағады.", "Мақсатсыз жүру: отыра алмайтындықтан сабақ ортасында орнынан тұруы мүмкін.", "«Шулы» мінез-құлық: жиі артық дыбыстар шығарады.", "Үзілістегі мәселелер: өте қатты жүгіреді, адамдарға соғылады."],
            ["Орыннан айқайлау: мұғалім сұрақты қойып бітпей жатып жауап береді.", "Сөзді бөлу: басқа балалармен сөйлесуіне араласады немесе сөзді бөледі.", "Кезекті күте алмау: үнемі бірінші болуға тырысады, кезекте тұруға қарсылық білдіреді.", "Өзін-өзі бақылаудың төмендігі: алдымен істейді немесе айтады, содан кейін ойлайды.", "Ашуланшақтық: тез көңілі түседі, ойында жеңілгеніне қатты реакция білдіреді."]
        ],

        # --- ПСИХОЛОГ (ҚАЗ) ---
        'psych_title': "🧠 Психолог сауалнамасы",
        'psych_secs': ["1-блок: Эмоционалды-ерік жігер аясы және мазасыздық", "2-блок: Когнитивті ая", "3-блок: Әлеуметтену және ұжымға бейімделу", "4-блок: Мотивациялық компонент"],
        'psych_q': [
            ["Жоғары базалық мазасыздық деңгейі (қате жіберуден қорқу, үнемі шиеленісте жүру).", "Эмоционалды лабильдік (көңіл-күйдің себепсіз күрт өзгеруі).", "Агрессия көріністері (құрдастарына бағытталған ашу-ыза немесе аутоагрессия).", "Үрей мен фобиялар (тақта алдында жауап беруден қорқу, тестілерден үрейлену).", "Фрустрацияға төзімділіктің төмендігі (кішігірім сәтсіздіктен кейін бірден бас тарту)."],
            ["Психикалық үрдістердің тез сарқылуы (алғашқы 10-15 минутта ғана өнімді).", "Естің ерекшеліктері (қысқа мерзімді ес тапшылығы).", "Ойлаудың ригидтілігі (бір логикалық алгоритмнен екіншісіне ауысудың қиындығы).", "Кеңістікті бағдарлай алмау («оң/сол», «жоғары/төмен» шатастыру)."],
            ["Ережелерді қабылдамау (мектеп тәртібін мойындау қиындығы).", "Ұжымнан шеттетілу (келемеждеу, буллинг немесе мүлдем елемеу нысаны болу).", "Эмпатияның төмендігі (басқалардың эмоциясын түсінбеу)."],
            ["Мектепке дезадаптация (оқуға деген ынтаның мүлдем болмауы).", "Өзін-өзі бағалаудың төмендігі («Мен ақымақпын», «Қолымнан келмейді»)."]
        ],

        # --- ЛОГОПЕД (ҚАЗ) ---
        'logo_title': "🗣 Логопед кабинеті (Сөйлеу картасы)",
        'logo_secs': ["1-блок: Дыбыстың айтылуы және артикуляция", "2-блок: Сөздің буындық құрылымы", "3-блок: Фонематикалық үрдістер", "4-блок: Лексика-грамматикалық құрылым", "5-блок: Сөйлеу қарқыны мен ырғағы"],
        'logo_q': [
            ["Дыбыстың айтылуындағы бұзылыстар (ысқырық, ызың, Р, Л дыбыстарын айта алмау).", "Артикуляциялық моториканың бұзылуы (тіл мен еріннің енжарлығы, тремор)."],
            ["Сөздің буындық құрылымын бұрмалау (буындарды өткізіп жіберу, орындарын ауыстыру)."],
            ["Фонематикалық есту қабілетінің бұзылуы (Б-П, Ж-Ш, З-С шатастыру).", "Дыбыстық талдау мен жинақтау қиындықтары."],
            ["Сөздік қордың жұтаңдығы (жануарлардың төлдерін, мамандықтарды білмеу).", "Аграмматизмдер (сөздерді септеудегі қателер, септеуліктерді қате қолдану).", "Байланыстырып сөйлеудің бұзылуы (мәтінді қайта айтып бере алмау)."],
            ["Тұтығу, сөйлеудегі кідірістер, тым тез (тахилалия) немесе баяу (брадилалия)."]
        ],

        # --- ДЕФЕКТОЛОГ (ҚАЗ) ---
        'def_title': "🎓 Дефектолог кабинеті",
        'def_secs': ["1-блок: Жақын арадағы даму аймағы", "2-блок: Жоғары психикалық функциялар", "3-блок: Қарапайым түсініктердің қалыптасуы", "4-блок: Академиялық дағдылар"],
        'def_q': [
            ["Төмен оқытылу деңгейі (ересектің көмегін қабылдамайды).", "Оқу/ойын әрекетінің қалыптаспауы (әрекеттері мақсатсыз)."],
            ["Көру және есту гнозисінің бұзылуы.", "Конструкциялық праксис дефициті (қиынды суреттерді жинай алмайды).", "Ойлау ерекшеліктері (топтастыру, жалпылау қиындығы)."],
            ["Сенсорлық эталондарды білмеу (түстерді, пішіндерді, көлемдерді шатастыру).", "Уақыт пен кеңістікті бағдарлай алмау (кеше/бүгін шатастыру)."],
            ["Оқу дағдысының қиындықтары (буындап оқи алмау, мазмұнын түсінбеу).", "Жазудың бұзылыстары (дисграфиялық қателер: әріптерді теріс жазу).", "Есептеу дағдысының бұзылуы (дискалькулия, есептің шартын түсінбеу)."]
        ]
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
                        if result[0] == u_pwd:
                            st.session_state.logged_in = True
                            st.session_state.user = u_name
                            st.session_state.role = result[1]
                            st.rerun()
                        else: st.error("Неверный пароль!")
                    else:
                        with engine.begin() as insert_conn:
                            insert_conn.execute(text("INSERT INTO users (username, password, role) VALUES (:u, :p, :r)"), {"u": u_name, "p": u_pwd, "r": role})
                        st.session_state.logged_in = True
                        st.session_state.user = u_name
                        st.session_state.role = role
                        st.rerun()

# --- ПАНЕЛЬ АДМИНА ---
elif st.session_state.role == "Админ":
    st.title("🛡️ Закрытая панель Администратора")
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

        total_score = 0
        asd_score, adhd_score = 0, 0

        # Генерация интерфейса на основе словаря
        if st.session_state.role == "Учитель":
            st.subheader(T['teach_title'])
            for i, sec in enumerate(T['teach_secs']):
                st.markdown(f"### {sec}")
                for q in T['teach_q'][i]:
                    if st.checkbox(q):
                        if i < 4: asd_score += 1
                        else: adhd_score += 1
        
        elif st.session_state.role == "Психолог":
            st.subheader(T['psych_title'])
            for i, sec in enumerate(T['psych_secs']):
                st.markdown(f"### {sec}")
                for q in T['psych_q'][i]:
                    if st.checkbox(q): total_score += 1
                    
        elif st.session_state.role == "Логопед":
            st.subheader(T['logo_title'])
            for i, sec in enumerate(T['logo_secs']):
                st.markdown(f"### {sec}")
                for q in T['logo_q'][i]:
                    if st.checkbox(q): total_score += 1
                    
        elif st.session_state.role == "Дефектолог":
            st.subheader(T['def_title'])
            for i, sec in enumerate(T['def_secs']):
                st.markdown(f"### {sec}")
                for q in T['def_q'][i]:
                    if st.checkbox(q): total_score += 1

        extra_notes = st.text_area(T['extra_notes_label'], placeholder=T['placeholder_notes'])
        
        # Сохранение в БД
        if st.button(T['save_btn'], use_container_width=True, type="primary"):
            if child_name:
                with engine.begin() as conn:
                    if st.session_state.role == "Учитель":
                        conn.execute(text("INSERT INTO teacher_reports (date, teacher_name, child_id, asd_score, adhd_score, details, adhd_details, notes, lang) VALUES (:d, :n, :c, :a, :ad, 'РАС', 'СДВГ', :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state.user, "c": child_name, "a": asd_score, "ad": adhd_score, "not": extra_notes, "l": st.session_state.language})
                    elif st.session_state.role == "Психолог":
                        conn.execute(text("INSERT INTO psychologist_reports (date, psych_name, child_id, total_score, details, notes, lang) VALUES (:d, :n, :c, :s, 'Анкета', :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state.user, "c": child_name, "s": total_score, "not": extra_notes, "l": st.session_state.language})
                    elif st.session_state.role == "Логопед":
                        conn.execute(text("INSERT INTO speech_reports (date, speech_name, child_id, total_score, details, notes, lang) VALUES (:d, :n, :c, :s, 'Анкета', :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state.user, "c": child_name, "s": total_score, "not": extra_notes, "l": st.session_state.language})
                    elif st.session_state.role == "Дефектолог":
                        conn.execute(text("INSERT INTO defect_reports (date, defect_name, child_id, total_score, details, notes, lang) VALUES (:d, :n, :c, :s, 'Анкета', :not, :l)"),
                                     {"d": survey_date.strftime("%d.%m.%Y"), "n": st.session_state.user, "c": child_name, "s": total_score, "not": extra_notes, "l": st.session_state.language})
                st.success("✅ Данные успешно сохранены!")
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
                if not t_data.empty: st.write(f"Маркеры РАС: {t_data.iloc[-1]['asd_score']} шт., СДВГ: {t_data.iloc[-1]['adhd_score']} шт. Заметки: {t_data.iloc[-1]['notes']}")
                else: st.warning("Нет данных")
                
                st.markdown("#### 🧠 2. Психолог:")
                if not p_data.empty: st.write(f"Выявлено проблемных зон: {p_data.iloc[-1]['total_score']}. Заметки: {p_data.iloc[-1]['notes']}")
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
