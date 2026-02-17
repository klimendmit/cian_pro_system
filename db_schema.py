from sqlalchemy import create_engine, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from datetime import datetime
from typing import Optional


# 1. Базовый класс
class Base(DeclarativeBase):
    pass


# 2. Модель очереди ссылок
class LinkQueue(Base):
    tablename = 'links_queue'

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(500), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="new")  # new, processing, done, error
    added_at: Mapped[datetime] = mapped_column(default=datetime.now)


# 3. Модель Квартиры (для флиппинга)
class Flat(Base):
    tablename = 'realty_objects'

    id: Mapped[int] = mapped_column(primary_key=True)
    cian_id: Mapped[str] = mapped_column(String(50), unique=True)
    url: Mapped[str] = mapped_column(String(500))
    title: Mapped[Optional[str]] = mapped_column(String(500))

    # Деньги
    price: Mapped[Optional[int]] = mapped_column()
    price_per_m2: Mapped[Optional[float]] = mapped_column()

    # Гео
    lat: Mapped[Optional[float]] = mapped_column()
    lon: Mapped[Optional[float]] = mapped_column()
    address: Mapped[Optional[str]] = mapped_column(String(500))

    # Параметры из JSON (new 70.txt)
    total_area: Mapped[Optional[float]] = mapped_column()
    kitchen_area: Mapped[Optional[float]] = mapped_column()
    living_area: Mapped[Optional[float]] = mapped_column()
    floor: Mapped[Optional[int]] = mapped_column()
    floors_count: Mapped[Optional[int]] = mapped_column()
    build_year: Mapped[Optional[int]] = mapped_column()
    material_type: Mapped[Optional[str]] = mapped_column(String(100))

    description: Mapped[Optional[str]] = mapped_column(Text)
    date_added: Mapped[datetime] = mapped_column(default=datetime.now)


# 4. Инициализация
engine = create_engine('sqlite:///cian_database1.db', connect_args={'timeout': 30})
SessionLocal = sessionmaker(bind=engine)
Session = SessionLocal

def init_db():
    # Удаляем старую базу, если она была битая, и создаем новую
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("--- СИСТЕМА: База данных успешно создана в venv! ---")


if __name__ == "__main__":
    init_db()