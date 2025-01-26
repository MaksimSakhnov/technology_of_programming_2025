import json
import csv
import os


def parse_title(title):
    # Разделение строки по " · "
    parts = title.split(" · ")

    # Инициализация переменных
    rooms = None
    floor = None
    total_floors = None
    area = None  # Новая переменная для площади

    # Обработка частей строки
    for part in parts:
        # Извлечение площади
        if "м²" in part:
            try:
                area = float(part.split(" ")[0].replace(",", "."))
            except ValueError:
                area = None

        # Количество комнат
        elif "комнатная" in part:
            rooms = int(part.split("-")[0])

        # Обработка студии
        elif "студия" in part:
            rooms = 1

        # Этажи
        elif "этаж из" in part:
            floor_info = part.split(" этаж из ")
            floor = int(floor_info[0])
            total_floors = int(floor_info[1])

    return {
        "area": area,
        "rooms": rooms,
        "floor": floor,
        "total_floors": total_floors
    }


def parse_price_for_square(price_str):
    # Проверяем, является ли строка "-1"
    if price_str.strip() == "-1":
        return -1
    try:
        # Удаляем лишние символы и преобразуем в число
        price = int(price_str.split(" ")[0].replace("₽", "").replace(" ", "").strip())
        return price
    except ValueError:
        # Возвращаем None, если не удалось извлечь число
        return None


def parse_price(price_str):
    # Преобразуем строку цены в число
    try:
        # Убираем символы, не относящиеся к числу (например, ₽, пробелы)
        price = int(price_str.replace("₽", "").replace(" ", "").strip())
        return price
    except ValueError:
        return None  # Если не удаётся преобразовать строку в число, возвращаем None


def combine(town='saratov'):


    # Список путей к JSON файлам
    json_files = [f"parsed_data{i}.json" for i in range(1, 26)]  # file_1.json, file_2.json, ..., file_25.json

    # Объединение всех JSON объектов
    all_data = []
    for file_name in json_files:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)

            # Обработка каждого элемента
            for item in data:
                # Обрабатываем title
                title_data = parse_title(item.get("title", ""))
                item.update(title_data)

                # Обрабатываем price_for_square
                item["price_for_square"] = parse_price_for_square(item.get("price_for_square", ""))

                # Обрабатываем price
                item["price"] = parse_price(item.get("price", ""))
                item["town"] = town

            # Добавляем обработанные данные в общий список
            all_data.extend(data)

    # Сохранение объединенного JSON в отдельный файл
    with open(f'combined_{town}.json', 'w', encoding='utf-8') as combined_file:
        json.dump(all_data, combined_file, ensure_ascii=False, indent=4)


    # Конвертация в CSV
    csv_file = 'result.csv'
    keys = all_data[0].keys()  # Используем ключи первого элемента как заголовки столбцов
    with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_data)

    for file_name in json_files:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Файл {file_name} удален.")

    print(f"JSON объединён и сохранён как 'combined.json'. CSV создан как '{csv_file}'.")


if __name__ == '__main__':
    combine()
