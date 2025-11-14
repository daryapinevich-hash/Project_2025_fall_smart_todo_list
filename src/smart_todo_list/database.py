import os
import sqlite3
import bcrypt


class Database:
    def __init__(self):
        # Корень проекта - на два уровня выше этого файла (database.py лежит в src/smart_todo_list/)
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

        # Путь к папке для базы данных (data в корне проекта)
        data_dir = os.path.join(base_dir, "data")

        # Создаем папку, если ее нет
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Путь к файлу базы данных SQLite
        self.db_path = os.path.join(data_dir, "smart_todo_db.sqlite")

        # Путь к файлу схемы SQL относительно этого файла
        schema_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "database", "schema.sql"
        )

        # Если база не существует, создаем ее
        if not os.path.exists(self.db_path):
            self._create_db(schema_path)

    def _create_db(self, schema_path):
        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path, "r", encoding="utf-8") as f:
                sql_script = f.read()
            conn.executescript(sql_script)

    def verify_user(self, login, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password_hash FROM users WHERE login = ?", (login,))
            result = cursor.fetchone()
            if not result:
                return False
            stored_hash = result[0].encode("utf-8")
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash)
        finally:
            cursor.close()
            conn.close()

    def register_user(self, login, email, password):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (login, email, password_hash) VALUES (?, ?, ?)",
                (login, email, hashed.decode("utf-8")),
            )
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise RuntimeError(f"Ошибка регистрации пользователя: {e}")
        finally:
            cursor.close()
            conn.close()

    def get_tasks(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, title, description, is_done FROM tasks WHERE user_id = ?",
                (user_id,),
            )
            tasks = cursor.fetchall()
            return tasks
        finally:
            cursor.close()
            conn.close()

    def add_task(self, user_id, title, description):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)",
                (user_id, title, description),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def update_task_status(self, task_id, is_done):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE tasks SET is_done = ? WHERE id = ?", (is_done, task_id)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def get_user_id(self, login):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()
            conn.close()
