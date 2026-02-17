import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from schema_v2 import SessionLocal, Flat


def get_optimized_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(30)
    return driver


def parse_and_save(url, driver=None):
    local_driver = False
    if driver is None:
        driver = get_optimized_driver()
        local_driver = True

    session = SessionLocal()

    try:
        if session.query(Flat).filter(Flat.url == url).first():
            print(f"--- Пропуск: {url}")
            return

        print(f"Парсим: {url}")
        driver.get(url)

        # Ожидание появления данных в JS
        raw_json = None
        for _ in range(5):
            raw_json = driver.execute_script("""
                return (window._cianConfig && window._cianConfig['frontend-offer-card']) 
                ? window._cianConfig['frontend-offer-card'] 
                : null;
            """)
            if raw_json: break
            time.sleep(2)

        if not raw_json:
            print("!!! ОШИБКА: Данные не прогрузились (возможно капча)")
            return

        offer_data = None
        for item in raw_json:
            if item.get('key') == 'defaultState':
                offer_data = item['value']['offerData']['offer']
                break

        if not offer_data: return

        # --- ПОЛНЫЙ СБОР ВСЕХ ПОЛЕЙ ---
        building = offer_data.get('building', {})
        geo_data = offer_data.get('geo', {})
        bargain = offer_data.get('bargainTerms', {})

        new_flat = Flat()
        new_flat.cian_id = str(offer_data.get('id'))
        new_flat.url = url

        # Деньги
        new_flat.price = bargain.get('price', 0)
        new_flat.sale_type = bargain.get('saleType', 'unknown')

        # Площади
        new_flat.total_area = float(offer_data.get('totalArea', 0))
        new_flat.kitchen_area = float(offer_data.get('kitchenArea', 0) or 0)
        new_flat.living_area = float(offer_data.get('livingArea', 0) or 0)
        new_flat.price_per_m2 = round(new_flat.price / new_flat.total_area, 2) if new_flat.total_area else 0

        # Этажность и дом
        new_flat.floor = offer_data.get('floorNumber')
        new_flat.floors_count = building.get('floorsCount')
        new_flat.build_year = building.get('buildYear')
        new_flat.material_type = building.get('materialType')

        # Координаты и адрес
        coords = geo_data.get('coordinates', {})
        new_flat.lat = coords.get('lat')
        new_flat.lon = coords.get('lng')
        new_flat.address = ", ".join([a['fullName'] for a in geo_data.get('address', [])])

        # Детали для флиппинга
        new_flat.repair_type = offer_data.get('repairType', 'no')
        new_flat.balconies = offer_data.get('balconiesCount', 0) or 0
        new_flat.loggias = offer_data.get('loggiasCount', 0) or 0
        comb = offer_data.get('combinedWcsCount', 0) or 0
        sep = offer_data.get('separateWcsCount', 0) or 0
        if comb > 0 and sep > 0:
            new_flat.wc_type = f"Смеж: {comb}, Разд: {sep}"
        elif comb > 0:
            new_flat.wc_type = f"Совмещенный ({comb})"
        elif sep > 0:
            new_flat.wc_type = f"Раздельный ({sep})"
        else:
            new_flat.wc_type = "Нет данных"

        # Лифт (суммируем все типы)
        lifts = (building.get('passengerLiftsCount', 0) or 0) + (building.get('cargoLiftsCount', 0) or 0)
        new_flat.has_lift = 1 if lifts > 0 else 0

        new_flat.description = offer_data.get('description', '')

        session.add(new_flat)
        session.commit()
        print(
            f"+++ СОХРАНЕНО: {new_flat.address} | Этаж: {new_flat.floor}/{new_flat.floors_count} | Год: {new_flat.build_year}")

    except Exception as e:
        print(f"!!! Ошибка: {e}")
    finally:
        session.close()
        if local_driver:
            driver.quit()