import json
import csv
import os

def to_csv():
    towns = ["samara", "rostov", "vologda", "volgograd", "krasnodar", "kazan", "velikiy_novgorod", "nizhniy_novgorod",
             "moskva"]
    # Список путей к JSON файлам
    json_files = [f"combined_{i}.json" for i in towns]  # file_1.json, file_2.json, ..., file_25.json

    # Объединение всех JSON объектов
    all_data = []
    for file_name in json_files:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Добавляем обработанные данные в общий список
            all_data.extend(data)


    # Конвертация в CSV
    csv_file = 'result.csv'
    keys = all_data[0].keys()  # Используем ключи первого элемента как заголовки столбцов
    with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_data)

if __name__ == '__main__':
    to_csv()