from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # Импорт Base из models для использования метаданных

# URL подключения к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/mydatabase"

# Создание двигателя и сессии
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Флаг отладки
DEBUG = True

if DEBUG:
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Database structure recreated successfully.")

# Вы можете добавить дополнительные действия, например, предварительное заполнение данных:
# with SessionLocal() as session:
#     new_user = User(username="admin", password="admin")
#     session.add(new_user)
#     session.commit()
