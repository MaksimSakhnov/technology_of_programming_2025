from elasticsearch import Elasticsearch, helpers
import json

# Подключение к Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Чтение JSON-файла
with open('result_id.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Подготовка данных для bulk-запроса
actions = [
    {
        "_index": "apartament_index",
        "_id": item["id"],
        "_source": item
    }
    for item in data
]

# Загрузка данных в Elasticsearch
helpers.bulk(es, actions)

print("Данные успешно загружены в Elasticsearch.")