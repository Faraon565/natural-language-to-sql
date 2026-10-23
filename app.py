import streamlit as st
from db_engine import DBManager
from ai_logic import SQLAgent
from visualizer import get_auto_chart

st.title("🤖 SQL Genius: NLQ to Visualization")

# 1. Боковая панель настроек
with st.sidebar:
    lang = st.selectbox("Язык запроса", ["Русский", "English", "Татарча"])
    db_type = st.selectbox("Тип СУБД", ["PostgreSQL", "Oracle", "SQLite"])
    uploaded_file = st.file_uploader("Загрузите БД (.db, .sql)")

if uploaded_file:
    # Инициализация
    db_path = f"temp_{uploaded_file.name}"
    with open(db_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    db_man = DBManager(db_type, db_path)
    schema = db_man.get_schema_text()
    agent = SQLAgent(schema, db_type, lang)

    # 2. Поле запроса
    user_input = st.text_input("Введите ваш запрос:")

    if user_input:
        with st.spinner("Агенты анализируют данные..."):
            df, final_sql = agent.smart_execute(user_input, db_man)

            # ПРОВЕРКА: Если ИИ выдал ошибку вместо данных
            if df is None:
                st.error(f"Ошибка: {final_sql}")
            else:
                st.code(final_sql, language="sql")  # Показываем SQL

                tab1, tab2 = st.tabs(["📊 График", "📋 Таблица"])

                with tab1:
                    chart = get_auto_chart(df)  # Теперь тут не упадет
                    if chart:
                        st.plotly_chart(chart)
                    else:
                        st.info(
                            "Для этих данных таблица подходит лучше, чем график.")

                with tab2:
                    st.dataframe(df)
