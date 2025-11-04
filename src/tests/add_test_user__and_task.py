import os
import sqlite3
import bcrypt


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


def add_test_user_and_tasks():
    db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Добавляем пользователя с логином "1" и паролем "1"
        password = "1"
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        cursor.execute(
            "INSERT OR IGNORE INTO users (login, email, password_hash) VALUES (?, ?, ?)",
            ("1", "test1@example.com", hashed.decode("utf-8")),
        )
        conn.commit()

        # Получаем id пользователя
        cursor.execute("SELECT id FROM users WHERE login = ?", ("1",))
        user_id = cursor.fetchone()[0]

        # Добавляем 2 тестовые задачи
        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, is_done) VALUES (?, ?, ?, ?)",
            (user_id, "Тестовая задача 1", "Описание задачи 1", 1),
        )
        cursor.execute(
            "INSERT INTO tasks (user_id, title, description, is_done) VALUES (?, ?, ?, ?)",
            (user_id, "Тестовая задача 2", "Описание задачи 2", 0),
        )
        conn.commit()

        print("Тестовый пользователь и задачи добавлены успешно!")

    except Exception as e:
        print(f"Ошибка при добавлении тестовых данных: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    add_test_user_and_tasks()
