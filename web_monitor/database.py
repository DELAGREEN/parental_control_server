### database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import Base  # Импорт Base из models для использования метаданных

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/mydatabase"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def create_or_update_database():
    """Создает таблицы и добавляет недостающие колонки в существующих таблицах."""
    print("Проверка базы данных и обновление структуры...")
    Base.metadata.create_all(bind=engine)

    with engine.connect() as connection:
        # Проверяем и добавляем недостающие колонки
        columns_to_add = [
            {
                "table": "computer",
                "column": "blocked_processes",
                "definition": "TEXT DEFAULT '[]'"
            },
            {
                "table": "computer",
                "column": "code",
                "definition": "VARCHAR(36) UNIQUE"
            }
        ]

        for item in columns_to_add:
            result = connection.execute(text(
                f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='{item['table']}' AND column_name='{item['column']}';
                """
            ))
            if not result.fetchone():
                print(f"Добавление колонки '{item['column']}' в таблицу '{item['table']}'...")
                connection.execute(text(
                    f"ALTER TABLE {item['table']} ADD COLUMN {item['column']} {item['definition']};"
                ))
                print(f"Колонка '{item['column']}' добавлена.")

    print("База данных проверена и обновлена.")

# Вызов функции для создания или обновления базы данных
create_or_update_database()
