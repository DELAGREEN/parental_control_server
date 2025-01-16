### models.py
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from uuid import uuid4
import json

# URL подключения к базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/mydatabase"

# Создание базового класса для моделей
Base = declarative_base()

# Определение моделей
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True)
    password = Column(String(255))

    computers = relationship("Computer", back_populates="owner")

class Computer(Base):
    __tablename__ = 'computer'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(150), index=True)
    status = Column(String(50))
    code = Column(String(36), unique=True, default=lambda: str(uuid4()))  # Уникальный код
    blocked_processes = Column(String, default=json.dumps([]))  # Список запрещённых процессов в формате JSON

    owner = relationship("User", back_populates="computers")

# Создание двигателя и сессии
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
