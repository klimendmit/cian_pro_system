import time
import random
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy.orm import Session
from database_core import Flat, SessionLocal, engine


def get_coordinates_from_page(driver):
    """
    Улучшенная версия: ищет координаты в JSON и в мета-тегах.
    """
    # Попытка №1: Ищем в window._cianConfig_
    try:
        scripts = driver.find_elements(By.TAG_NAME, "script")
        for script in scripts:
            inner_html = script.get_attribute("innerHTML")
            if "window._cianConfig_['frontend-offer-card']" in inner_html:
                match = re.search(r"window\._cianConfig_\['frontend-offer-card'\]\s*=\s*(\[.*?\]);", inner_html)
                if match:
                    data = json.loads(match.group(1))
                    for item in data:
                        if item.get('key') == 'defaultState':
                            offer = item['value']['offerData']['offer']
                            return offer['geo']['coordinates']['lat'], offer['geo']['coordinates']['lng']
    except:
        pass

    # Попытка №2: Ищем в мета-тегах (иногда они там лежат для поисковиков)
    try:
        # Циан часто кладет координаты в ссылки для карт
        map_link = driver.find_element(By.CSS_SELECTOR, "a[href*='static-maps']").get_attribute("href")
        # Извлекаем из ссылки типа ...center=47.23,39.71...
        coords = re.search(r"center=([\d\.]+),([\d\.]+)", map_link)
        if coords:
            return float(coords.group(1)), float(coords.group(2))
    except:
        pass

    return None, None

def parse_single_offer(driver, url):
    """Парсит одну страницу объявления и сохраняет в БД"""
    session = SessionLocal()

    # 1. Умная проверка: уже есть в базе?
    existing = session.query(Flat).filter(Flat.url == url).first()
    if existing:
        print(f"--- Пропуск: {url} уже в базе")
        session.close()
        return

    driver.get(url)
    time.sleep(random.uniform(4, 7))

    try:
        # Извлекаем ID из URL (цифры в конце ссылки)
        cian_id = re.findall(r'\d+', url)[-1]

        # Собираем данные
        title = driver.find_element(By.CSS_SELECTOR, "[data-name='OfferTitleNew']").text
        price_text = driver.find_element(By.CSS_SELECTOR, "[data-name='PriceInfo']").text
        # Очищаем цену от символов валюты и пробелов
        price = int(''.join(filter(str.isdigit, price_text)))

        # Гео-магия
        lat, lon = get_coordinates_from_page(driver)
        address = driver.find_element(By.CSS_SELECTOR, "[data-name='AddressContainer']").text

        # Создаем объект для БД
        new_flat = Flat(
            cian_id=cian_id,
            url=url,
            price=price,
            lat=lat,
            lon=lon,
            address=address,
            title=title
        )

        session.add(new_flat)
        session.commit()
        print(f"+++ Сохранено: {title} ({lat}, {lon})")

    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
    finally:
        session.close()


# ТЕСТОВЫЙ ЗАПУСК
if __name__ == "__main__":
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    test_url = "https://rostov.cian.ru/sale/flat/326957220/?mlSearchSessionGuid=c4f1103f418ff3488ce6afbcb3d06b5b"  # Возьми любую ссылку на квартиру из Циана
    try:
        parse_single_offer(driver, test_url)
    finally:
        driver.quit()