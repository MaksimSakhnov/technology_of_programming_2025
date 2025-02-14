from elasticsearch import Elasticsearch
import time
import os


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# Подключение к Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Константы
PAGE_SIZE = 10


def search_apartments(city, query, page=1):
    start_time = time.time()
    response = es.search(index="apartament_index", body={
        "query": {
            "bool": {
                "must": [
                    {"match": {"town": city}},
                    {"multi_match": {"query": query, "fields": ["title", "description"]}}
                ]
            }
        },
        "from": (page - 1) * PAGE_SIZE,
        "size": PAGE_SIZE
    })
    end_time = time.time()
    execution_time = end_time - start_time
    return response['hits']['hits'], response['hits']['total']['value'], execution_time


def print_apartments(apartments, total, current_page):
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"\nНайдено всего: {total} (Страница {current_page} из {total_pages})")
    for apt in apartments:
        print(f"\nTitle: {apt['_source']['title']}")
        print(f"City: {apt['_source']['town']}")
        print(f"Price: {apt['_source']['price']}")
        print(f"Description: {apt['_source']['description']}")
        print(f"Score: {apt['_score']}")
        print("-" * 40)


def search_menu(city, query):
    current_page = 1
    while True:
        clear_screen()
        apartments, total, execution_time = search_apartments(city, query, current_page)
        print_apartments(apartments, total, current_page)
        print(f"\nВремя выполнения запроса: {execution_time:.4f} секунд")

        print("\nВыберите действие:")
        print("1 - Назад")
        print("2 - Далее")
        print("3 - Ввести страницу")
        print("4 - Выйти в меню")

        choice = input("Ваш выбор: ")

        if choice == "1":  # Назад
            if current_page > 1:
                current_page -= 1
            else:
                print("Вы уже на первой странице.")
                time.sleep(1)
        elif choice == "2":
            total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
            if current_page < total_pages:
                current_page += 1
            else:
                print("Вы уже на последней странице.")
                time.sleep(1)
        elif choice == "3":
            total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
            try:
                page = int(input(f"Введите номер страницы (от 1 до {total_pages}): "))
                if 1 <= page <= total_pages:
                    current_page = page
                else:
                    print("Некорректный номер страницы.")
                    time.sleep(1)
            except ValueError:
                print("Введите число.")
                time.sleep(1)
        elif choice == "4":
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
            time.sleep(1)


def main():
    city = input("Введите город: ")

    while True:
        clear_screen()
        print("\nВыберите действие:")
        print("1 - Поиск")
        print("2 - Сменить город")
        print("3 - Выйти")

        choice = input("Ваш выбор: ")

        if choice == "1":
            query = input("Введите запрос для поиска: ")
            search_menu(city, query)
        elif choice == "2":
            city = input("Введите новый город: ")
        elif choice == "3":
            print("Выход из приложения.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
            time.sleep(1)


if __name__ == "__main__":
    main()