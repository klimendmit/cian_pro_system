import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from schema_v2 import SessionLocal, LinkQueue


def collect_roster(base_url, pages=5):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    session = SessionLocal()

    for p in range(1, pages + 1):
        print(f"Сканирую страницу {p}...")
        url = f"{base_url}&p={p}" if p > 1 else base_url
        driver.get(url)
        time.sleep(random.uniform(3, 5))

        links = driver.find_elements(By.CSS_SELECTOR, "article[data-name='CardComponent'] a[href*='/sale/flat/']")

        new_links = 0
        for link in links:
            href = link.get_attribute('href').split('?')[0]
            # Проверяем на дубликат в очереди
            exists = session.query(LinkQueue).filter_by(url=href).first()
            if not exists:
                session.add(LinkQueue(url=href, status="new"))
                new_links += 1

        session.commit()
        print(f"Добавлено {new_links} новых ссылок со страницы {p}")

    driver.quit()
    session.close()


if __name__ == "__main__":
    # Твоя ссылка на Ростов
    URL = "https://rostov.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=4959"
    collect_roster(URL, pages=3)  # Соберем первые 3 страницы