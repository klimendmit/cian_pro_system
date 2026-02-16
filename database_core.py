from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Базовый класс
Base = declarative_base()


class Flat(Base):
    __tablename__ = 'realty_objects'

    id = Column(Integer, primary_key=True)
    cian_id = Column(String(50), unique=True, index=True)
    url = Column(String(500))
    title = Column(String(500))  # <-- ДОБАВЬ ЭТУ СТРОКУ
    price = Column(Integer)
    area = Column(Float)
    floor = Column(Integer)

    # Геоданные
    lat = Column(Float)
    lon = Column(Float)
    address = Column(String(500))

    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)


class LinkQueue(Base):
    __tablename__ = 'links_queue'

    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True)
    status = Column(String(20), default="new")  # new, processing, done, error
    added_at = Column(DateTime, default=datetime.now)

# Создание движка и базы
engine = create_engine('sqlite:///cian_database.db')
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
    print("--- БАЗА ДАННЫХ ГОТОВА! Файл cian_database.db создан ---")


if __name__ == "__main__":
    init_db()