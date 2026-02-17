import time
import random
from selenium.webdriver.common.by import By
from parser_engine import get_optimized_driver
from schema_v2 import SessionLocal, LinkQueue


def collect_roster(base_url, pages=5):
    # Запуск драйвера в фоновом режиме (через настройки из parser_engine)
    driver = get_optimized_driver()
    session = SessionLocal()
    # Фиксируем время старта
    start_time = time.time()

    try:
        for p in range(1, pages + 1):
            url = f"{base_url}&p={p}" if p > 1 else base_url

            try:
                driver.get(url)
                # Ожидание прогрузки динамического контента
                time.sleep(random.uniform(4, 6))

                # Ищем контейнеры (карточки), а не все ссылки подряд
                cards = driver.find_elements(By.CSS_SELECTOR, "article[data-name='CardComponent']")

                total_found = len(cards)
                new_count = 0

                for card in cards:
                    try:
                        # Извлекаем только одну (первую) ссылку из каждой карточки
                        link_el = card.find_element(By.CSS_SELECTOR, "a[href*='/sale/flat/']")
                        href = link_el.get_attribute('href').split('?')[0]

                        # Проверка на дубликат в базе
                        exists = session.query(LinkQueue).filter_by(url=href).first()
                        if not exists:
                            session.add(LinkQueue(url=href, status="new"))
                            new_count += 1
                    except:
                        continue

                session.commit()

                # Сжатый информативный вывод в одну строку
                print(f"Стр {p:2}: Карточек {total_found:2} | Новых {new_count:2} | Старых {total_found - new_count:2}")

                # Если карточек вообще нет — возможно, это конец выдачи или блок
                if total_found == 0:
                    print(f"!!! Стр {p}: Карточки не найдены. Остановка.")
                    break

            except Exception as e:
                print(f"!!! Стр {p}: Ошибка: {str(e)[:50]}")
                continue

    finally:
        driver.quit()
        session.close()
        print("\nСбор ссылок завершен успешно.")
        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        print(f"\nСбор ссылок завершен успешно за {minutes} мин {seconds} сек.")


if __name__ == "__main__":
    # Ссылка на выдачу (пример для Ростова)
    TARGET_URL = "https://rostov.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=4959"

    print("Запуск ночного коллектора...")
    collect_roster(TARGET_URL, pages=10)