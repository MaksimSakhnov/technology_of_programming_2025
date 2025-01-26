import multiprocessing
import time
import random

import requests
import os

from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selectolax.parser import HTMLParser
import json

from combine import combine

list = "OffersSerp__list"
list_item = "OffersSerpItem"
list_item_link = "OffersSerpItem__titleLink"
title = 'OffersSerpItemTitle__title'
address_container = 'OffersSerpItem__location'
description = 'OffersSerpItem__description'
price = 'Price'
price_for_square = 'OffersSerpItem__price-detail'
publish_date = 'OffersSerpItem__publish-date__hide'

def scroll_to_element(browser, element):
    browser.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)

def random_sleep(min_time=1, max_time=3):
    time.sleep(random.uniform(min_time, max_time))

def save_to_json(data, filename='parsed_data.json'):
    try:
        # Если файл существует, считываем старые данные
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        # Добавляем новые данные в существующие
        existing_data.extend(data)

        # Записываем обновленные данные обратно в файл
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

        print(f"Данные успешно сохранены в {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении данных в файл: {e}")

def parse_elements_on_page(browser, page, lastPage):
    list_items = browser.find_elements(By.CLASS_NAME, list_item)

    # Пустой список для хранения данных
    parsed_data = []
    print(f"Парсится страница ${page}")
    # Проходим по каждому элементу и извлекаем данные
    for item in list_items:
        try:
            scroll_to_element(browser, item)

            # Иногда добавляем случайную задержку
            if random.choice([True, False]):
                random_sleep(1, 2)

            # Ссылки
            link = item.find_element(By.CLASS_NAME, list_item_link)

            # Заголовок
            title_block = link.text

            # Адрес
            address = item.find_element(By.CLASS_NAME, address_container).text
            # street_name = address.find_element(By.TAG_NAME, "a").text
            # street_number = address.find_element(By.XPATH, ".//a/following-sibling::text()").strip()

            # Описание
            description_block = item.find_element(By.CLASS_NAME, description).text

            # Цена
            deal_info = item.find_element(By.CLASS_NAME, "OffersSerpItem__dealInfo")
            price_block = deal_info.find_element(By.CLASS_NAME, "Price").text.split("₽")[0].strip()

            # Извлекаем цену за квадратный метр
            try:
                price_per_square_block = deal_info.find_element(By.CLASS_NAME, "OffersSerpItem__price-detail").text
            except Exception as e:
                print(f"Ошибка при извлечении цены за квадратный метр на странице ${page} ${title_block}")
                price_per_square_block = '-1'

            # Дата публикации
            try:
                publish_date_block = item.find_element(By.CLASS_NAME, "OffersSerpItem__publish-date__hide").text
            except Exception as e:
                print(f"Ошибка при извлечении цены даты публикации ${page} ${title_block}")
                publish_date_block = ''
            # Добавление извлеченных данных в список
            parsed_data.append({
                "link": link.get_attribute("href"),
                "title": title_block,
                "address": address,
                "description": description_block,
                "price": price_block,
                "price_for_square": price_per_square_block,
                "publish_date": publish_date_block
            })
        except Exception as e:
            print(f"Ошибка при обработке элемента: {e}")


    save_to_json(parsed_data, filename=f'parsed_data{page}.json')

    if(page == lastPage):
        browser.quit()
    else:
        # Теперь переходим на следующую страницу
        try:

            next_button = browser.find_element(By.XPATH,"//a[@class='Pager__radio-link' and contains(text(), 'Следующая')]")

            # Если кнопка найдена, нажимаем на неё
            next_button.click()

            # Подождем, пока страница загрузится
            WebDriverWait(browser, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            print("Переход на следующую страницу завершён.")
            random_sleep(2, 4)  # Дополнительная задержка перед парсингом новой страницы
            parse_elements_on_page(browser, page + 1, lastPage)  # Рекурсивный вызов для новой страницы

        except Exception as e:
            print(f"Ошибка при переходе на следующую страницу или достигнут конец пагинации: ${page}")
            print("Последняя страница - ", page)


def init_browser(start_page, end_page, url):
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    option.add_argument("--disable-blink-features=AutomationControlled")
    browser = webdriver.Chrome(options=option)
    page = start_page
    if (start_page != 0):
        url = f"{url}?page={page}"
    browser.get(url)

    WebDriverWait(browser, 10).until(
        lambda driver: driver.execute_script("return document.readyState") == "complete"
    )
    print(f"Страница полностью загружена. - ${page}")
    parse_elements_on_page(browser, page, lastPage=end_page)


def start_processes(url, town):
    page_ranges = [(1, 5), (6, 10), (11, 15), (16, 20),(21, 25)]
    processes = []

    for start_page, end_page in page_ranges:
        process = multiprocessing.Process(target=init_browser, args=(start_page, end_page, url))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
    combine(town)


def main():
    urls = ["https://realty.yandex.ru/samara/kupit/kvartira/", "https://realty.yandex.ru/rostov-na-donu/kupit/kvartira/",
            "https://realty.yandex.ru/vologda/kupit/kvartira/",
            "https://realty.yandex.ru/volgograd/kupit/kvartira/", "https://realty.yandex.ru/krasnodar/kupit/kvartira/",
            "https://realty.yandex.ru/kazan/kupit/kvartira/", "https://realty.yandex.ru/velikiy_novgorod/kupit/kvartira/",
            "https://realty.yandex.ru/nizhniy_novgorod/kupit/kvartira/", "https://realty.yandex.ru/moskva/kupit/kvartira/"]
    towns = ["samara", "rostov", "vologda", "volgograd", "krasnodar", "kazan", "velikiy_novgorod", "nizhniy_novgorod", "moskva"]
    for i in range(0, len(urls)):
        url = urls[i]
        town = towns[i]
        start_processes(url, town)


if __name__ == "__main__":
    main()