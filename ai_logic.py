from langchain_ollama import ChatOllama


class SQLAgent:
    def __init__(self, schema, dialect, lang):
        # Используем современный класс для Ollama
        self.llm = ChatOllama(model="llama3", temperature=0)
        self.schema = schema
        self.dialect = dialect
        self.lang = lang

    def generate_sql(self, user_query, error_msg=None):
        correction_prompt = f"\nПредыдущая ошибка БД: {error_msg}. Исправь SQL." if error_msg else ""

        # Обычная f-строка вместо сложных шаблонов LangChain
        prompt = f"""
        Ты эксперт по SQL. Напиши запрос для {self.dialect}.
        Язык пользователя: {self.lang}
        
        Схема базы данных:
        {self.schema}
        {correction_prompt}
        
        Запрос: {user_query}
        
        Ответь ТОЛЬКО готовым SQL кодом. Без пояснений. Без кавычек.
        """

        try:
            response = self.llm.invoke(prompt)
            # Очищаем ответ от лишних символов (Markdown и т.д.)
            sql = response.content.replace(
                "```sql", "").replace("```", "").strip()
            return sql
        except Exception as e:
            return f"Error: {str(e)}"

    def smart_execute(self, user_query, db_manager):
        sql = self.generate_sql(user_query)
        if sql.startswith("Error:"):
            return None, sql

        try:
            result_df = db_manager.execute_query(sql)
            return result_df, sql
        except Exception as e:
            # Одна попытка самоисправления
            corrected_sql = self.generate_sql(user_query, error_msg=str(e))
            return db_manager.execute_query(corrected_sql), corrected_sql
