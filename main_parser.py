import time
import random
from schema_v2 import Session, LinkQueue
from parser_engine import parse_and_save


def start_night_shift():
    print("Запуск ночной смены парсинга...")

    while True:
        session = Session()
        # Берем одну самую старую необработанную ссылку
        task = session.query(LinkQueue).filter_by(status="new").first()

        if not task:
            print("Все ссылки обработаны! Засыпаю.")
            session.close()
            break

        print(f"\nРаботаю над: {task.url}")
        task.status = "processing"
        session.commit()

        try:
            parse_and_save(task.url)
            task.status = "done"
        except Exception as e:
            print(f"Ошибка при парсинге: {e}")
            task.status = "error"

        session.commit()
        session.close()

        # Анти-бан пауза
        wait = random.uniform(2, 3)
        print(f"Готово. Жду {wait:.1f} сек...")
        time.sleep(wait)


if __name__ == "__main__":
    start_night_shift()