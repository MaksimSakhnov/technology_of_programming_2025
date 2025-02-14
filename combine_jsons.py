import json

# Загрузка данных из JSON-файла
with open('result.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Добавление индекса каждому элементу
for index, item in enumerate(data):
    item['id'] = index + 1  # Индекс начинается с 1

# Сохранение обновлённых данных в новый файл
with open('result_id.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Индексы добавлены. Результат сохранён в data_with_index.json")