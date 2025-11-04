import os
import sqlite3


def get_db_path():
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    data_dir = os.path.join(base_dir, "data")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Папка базы данных не найдена: {data_dir}")

    db_path = os.path.join(data_dir, "smart_todo_db.sqlite")
    if not os.path.isfile(db_path):
        raise FileNotFoundError(f"Файл базы данных не найден: {db_path}")

    return db_path


def test_db_connection():
    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("База данных подключена успешно")

        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"Версия SQLite: {version[0]}")

        # Выбираем все таблицы в базе
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if tables:
            print("Таблицы в базе:")
            for table_name_tuple in tables:
                table_name = table_name_tuple[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"  {table_name} (строк: {count})")
        else:
            print("В базе данных нет таблиц")

        cursor.close()
        conn.close()
    except sqlite3.Error as e:
        print(f"Ошибка работы с базой данных SQLite: {e}")


if __name__ == "__main__":
    test_db_connection()
