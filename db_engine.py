import sqlalchemy
import pandas as pd
import sqlite3
import os


class DBManager:
    def __init__(self, db_type, file_path):
        self.db_type = db_type
        self.file_path = file_path
        self.engine = None
        self.connection = None

        # Автоматическая подготовка базы при создании объекта
        self._prepare_engine()

    def _prepare_engine(self):
        """Создает подключение в зависимости от того, что подкинул пользователь"""
        if self.file_path.endswith('.db'):
            # Сценарий SQLite: работаем напрямую с файлом
            self.engine = sqlalchemy.create_engine(
                f"sqlite:///{self.file_path}")

        elif self.file_path.endswith('.sql'):
            # Сценарий SQL-скрипта: создаем временную базу в памяти
            # и выполняем в ней этот скрипт, чтобы создать таблицы
            self.engine = sqlalchemy.create_engine("sqlite:///:memory:")
            with open(self.file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # Используем стандартный sqlite3, чтобы выполнить скрипт с данными
            raw_conn = self.engine.raw_connection()
            raw_conn.executescript(sql_script)
            raw_conn.commit()
            raw_conn.close()

    def get_schema_text(self):
        """Извлекает структуру таблиц для Настиного ИИ"""
        inspector = sqlalchemy.inspect(self.engine)
        schema_info = "Схема базы данных:\n"

        for table_name in inspector.get_table_names():
            schema_info += f"\nТаблица: {table_name}\nКолонки:\n"
            for col in inspector.get_columns(table_name):
                schema_info += f" - {col['name']} ({col['type']})\n"
        return schema_info

    def execute_query(self, sql):
        """Выполняет запрос и возвращает таблицу"""
        with self.engine.connect() as conn:
            return pd.read_sql(sql, conn)
