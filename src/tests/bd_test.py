import os
import sqlite3


def test_db_connection():
    # Корень проекта - на два уровня выше этого файла (database.py лежит в src/smart_todo_list/)
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    # Путь к папке для базы данных (data в корне проекта)
    data_dir = os.path.join(base_dir, "data")
    # Путь к файлу базы данных SQLite
    db_path = os.path.join(data_dir, "smart_todo_db.sqlite")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("База данных подключена успешно")

        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"Версия SQLite: {version[0]}")

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
        )
        table = cursor.fetchone()
        if table:
            print("Таблица 'users' существует")
        else:
            print("Таблица 'users' отсутствует")

        cursor.close()
        conn.close()
    except sqlite3.Error as e:
        print(f"Ошибка работы с базой данных SQLite: {e}")


test_db_connection()
