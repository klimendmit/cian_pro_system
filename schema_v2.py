from sqlalchemy import create_engine, Table, Column, Integer, String, Float, DateTime, Text, MetaData
from sqlalchemy.orm import registry, sessionmaker
from datetime import datetime

mapper_registry = registry()
metadata = MetaData()

# Таблица очереди (без изменений)
link_queue_table = Table(
    "links_queue",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("url", String(500), unique=True),
    Column("status", String(20), default="new"),
    Column("added_at", DateTime, default=datetime.now),
)

# РАСШИРЕННАЯ таблица объектов
realty_table = Table(
    "realty_objects",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("cian_id", String(50), unique=True),
    Column("url", String(500)),

    # Финансы
    Column("price", Integer),
    Column("price_per_m2", Float),
    Column("sale_type", String(50)),  # free / alternative

    # Площади и габариты
    Column("total_area", Float),
    Column("kitchen_area", Float),
    Column("living_area", Float),
    Column("ceiling_height", Float),  # Высота потолков

    # Этажность и дом
    Column("floor", Integer),
    Column("floors_count", Integer),
    Column("build_year", Integer),
    Column("material_type", String(100)),  # panel, brick...

    # Детали квартиры
    Column("balconies", Integer),  # Балконы
    Column("loggias", Integer),  # Лоджии
    Column("wc_type", String(50)),  # combined / separate
    Column("view_type", String(50)),  # yard / street
    Column("repair_type", String(50)),  # cosmetic, euro, none
    Column("has_lift", Integer),  # 1 если есть, 0 если нет

    # Гео и Инфо
    Column("address", String(500)),
    Column("lat", Float),
    Column("lon", Float),
    Column("description", Text),
    Column("date_added", DateTime, default=datetime.now),
)


class LinkQueue:
    pass


class Flat:
    pass


mapper_registry.map_imperatively(LinkQueue, link_queue_table)
mapper_registry.map_imperatively(Flat, realty_table)

engine = create_engine('sqlite:///cian_database.db')
SessionLocal = sessionmaker(bind=engine)
Session = SessionLocal

def init_db():
    metadata.create_all(engine)
    print("--- БАЗА ДАННЫХ ОБНОВЛЕНА (ВЕРСИЯ 2.0) ---")


if __name__ == "__main__":
    init_db()