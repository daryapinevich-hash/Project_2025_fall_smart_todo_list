# Импорт общих библиотек
import os
import sys

import re
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.uic import loadUi
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QCheckBox,
    QInputDialog,
    QSizePolicy,
)

from database import Database


class WelcomeWindow(QWidget):

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        loadUi("ui/welcome_window.ui", self)
        self.connect_signals()

    def connect_signals(self):
        self.loginButton.clicked.connect(self.go_to_login)
        self.registerButton.clicked.connect(self.go_to_register)

    def go_to_login(self):
        self.stacked_widget.setCurrentIndex(1)

    def go_to_register(self):
        self.stacked_widget.setCurrentIndex(2)


class LoginWindow(QWidget):

    login_success = pyqtSignal(int)  # сигнал с user_id

    def __init__(self, stacked_widget, db):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.db = db
        loadUi("ui/login_window.ui", self)
        self.connect_signals()

    def connect_signals(self):
        self.loginButton.clicked.connect(self.login)
        self.backButton.clicked.connect(self.go_back)

    def login(self):
        login = self.loginInput.text().strip()
        password = self.passwordInput.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        if self.db.verify_user(login, password):
            user_id = self.db.get_user_id(login)
            if user_id is None:
                QMessageBox.warning(self, "Ошибка", "Пользователь не найден.")
                return
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {login}!")
            self.clear_fields()
            self.login_success.emit(
                user_id
            )  # отправляем сигнал о успешном входе с user_id
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")

    def go_back(self):
        self.clear_fields()
        self.stacked_widget.setCurrentIndex(0)

    def clear_fields(self):
        self.loginInput.clear()
        self.passwordInput.clear()


class RegisterWindow(QWidget):

    def __init__(self, stacked_widget, db):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.db = db
        loadUi("ui/register_window.ui", self)
        self.connect_signals()

    def connect_signals(self):
        self.registerButton.clicked.connect(self.register)
        self.backButton.clicked.connect(self.go_back)
        self.passwordInput.textChanged.connect(self.check_password_strength)

    def check_password_strength(self, password):
        if not password:
            self.passwordStrengthLabel.setText("")
            self.passwordStrengthLabel.setStyleSheet("")
            return

        strength = self.calculate_password_strength(password)

        if strength == "weak":
            self.passwordStrengthLabel.setText("Слабый пароль")
            self.passwordStrengthLabel.setStyleSheet("color: red;")
        elif strength == "medium":
            self.passwordStrengthLabel.setText("Средний пароль")
            self.passwordStrengthLabel.setStyleSheet("color: orange;")
        else:
            self.passwordStrengthLabel.setText("Сильный пароль")
            self.passwordStrengthLabel.setStyleSheet("color: green;")

    def calculate_password_strength(self, password):
        if len(password) < 8:
            return "weak"

        has_letter = bool(re.search(r"[a-zA-Zа-яА-Я]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        if has_letter and has_digit and has_special:
            return "strong"
        elif has_letter and has_digit:
            return "medium"
        else:
            return "weak"

    def is_safe_password(self, password):
        """Проверка безопасности пароля"""
        if len(password) < 8:
            return False, "Пароль должен содержать минимум 8 символов"

        if not re.search(r"[a-zA-Zа-яА-Я]", password):
            return False, "Пароль должен содержать буквы"

        if not re.search(r"\d", password):
            return False, "Пароль должен содержать цифры"

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Пароль должен содержать специальные символы"

        return True, "Пароль безопасен"

    def register(self):
        """Обработка регистрации"""
        login = self.loginInput.text().strip()
        email = self.emailInput.text().strip()
        password = self.passwordInput.text()
        confirm_password = self.confirmPasswordInput.text()

        # Проверка заполнения полей
        if not all([login, email, password, confirm_password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        # Проверка email
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            QMessageBox.warning(self, "Ошибка", "Введите корректный email!")
            return

        # Проверка совпадения паролей
        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        # Проверка безопасности пароля
        is_safe, message = self.is_safe_password(password)
        if not is_safe:
            QMessageBox.warning(self, "Ненадежный пароль", message)
            return

        # Здесь должна быть реальная логика регистрации
        # Попытка зарегистрировать пользователя через метод БД
        try:
            self.db.register_user(login, email, password)
            QMessageBox.information(
                self, "Успех", f"Пользователь {login} успешно зарегистрирован!"
            )
            self.clear_fields()
            self.go_back()
        except RuntimeError as e:
            QMessageBox.warning(self, "Ошибка регистрации", str(e))

    def go_back(self):
        """Возврат к приветственному окну"""
        self.clear_fields()
        self.stacked_widget.setCurrentIndex(0)

    def clear_fields(self):
        """Очистка полей ввода"""
        self.loginInput.clear()
        self.emailInput.clear()
        self.passwordInput.clear()
        self.confirmPasswordInput.clear()
        self.passwordStrengthLabel.setText("")


class TasksWindow(QWidget):
    def __init__(self, stacked_widget, db, user_id):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.db = db
        self.user_id = user_id
        loadUi("ui/tasks_window.ui", self)

        self.tasks = []

        # Используем чекбокс из ui
        self.hideCompletedCheckBox.stateChanged.connect(self.load_tasks)
        self.taskTable.cellClicked.connect(self.on_cell_clicked)
        self.taskTable.cellChanged.connect(self.on_cell_changed)

        # Кнопка из ui
        self.pushButtonAddTask.clicked.connect(self.add_task_dialog)

        self.load_tasks()

    def load_tasks(self):
        self.taskTable.blockSignals(
            True
        )  # чтобы не триггерить cellChanged при обновлении
        self.taskTable.setRowCount(0)
        if not self.db:
            self.taskTable.blockSignals(False)
            return

        self.tasks = self.db.get_tasks(self.user_id)
        hide_completed = self.hideCompletedCheckBox.isChecked()

        for task in self.tasks:
            task_id, title, description, is_done = task
            if hide_completed and is_done:
                continue

            row = self.taskTable.rowCount()
            self.taskTable.insertRow(row)

            title_item = QTableWidgetItem(title)
            description_item = QTableWidgetItem(description)
            if is_done:
                font = title_item.font()
                font.setStrikeOut(True)
                title_item.setFont(font)
                font_desc = description_item.font()
                font_desc.setStrikeOut(True)
                description_item.setFont(font_desc)
            self.taskTable.setItem(row, 0, title_item)
            self.taskTable.setItem(row, 1, description_item)

            status_item = QTableWidgetItem()
            status_item.setFlags(
                status_item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsEnabled
            )
            status_item.setCheckState(
                Qt.CheckState.Checked if is_done else Qt.CheckState.Unchecked
            )
            self.taskTable.setItem(row, 2, status_item)

        self.taskTable.blockSignals(False)

    def on_cell_clicked(self, row, column):
        if column == 2:  # Клик по колонке со статусом
            item = self.taskTable.item(row, column)
            if item is None:
                return
            current_state = item.checkState()
            new_state = (
                Qt.CheckState.Unchecked
                if current_state == Qt.CheckState.Checked
                else Qt.CheckState.Checked
            )
            item.setCheckState(new_state)
            # Обновление статуса в базе и UI вызовется через on_cell_changed

    def on_cell_changed(self, row, column):
        if column == 2:
            # Обработка изменения статуса по чекбоксу
            item = self.taskTable.item(row, column)
            if item is None:
                return
            is_done = item.checkState() == Qt.CheckState.Checked
            task_id = self.tasks[row][0]
            self.db.update_task_status(task_id, is_done)
            self.load_tasks()
        elif column in (0, 1):
            # Обработка изменения названия или описания
            item = self.taskTable.item(row, column)
            if item is None:
                return
            new_text = item.text()
            task_id = self.tasks[row][0]
            if column == 0:
                self.db.update_task_title(task_id, new_text)
            else:
                self.db.update_task_description(task_id, new_text)

    def add_task_dialog(self):
        title, ok = QInputDialog.getText(self, "Добавить задачу", "Название задачи:")
        if not ok or not title.strip():
            return

        description, ok = QInputDialog.getText(
            self, "Добавить задачу", "Описание задачи (необязательно):"
        )
        if not ok:
            description = ""

        try:
            self.db.add_task(self.user_id, title.strip(), description.strip())
            QMessageBox.information(self, "Успех", "Задача успешно добавлена")
            self.load_tasks()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить задачу:\n{e}")


class MainWindow(QMainWindow):
    """Главное окно приложения со StackedWidget"""

    def __init__(self, db):
        super().__init__()
        loadUi("ui/main_window.ui", self)
        self.db = db
        self.current_user_id = None  # здесь будем хранить вошедшего пользователя
        self.tasks_window = (
            None  # окно списка задач создаётся позже, когда появится user_id
        )

        # явно задать размер главного окна и дать возможность stackedWidget и страницам занимать динамически подходящий размер
        self.setMinimumSize(300, 400)
        self.stackedWidget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.stackedWidget.currentChanged.connect(self.on_page_changed)

        self.init_windows()

    def init_windows(self):
        """Инициализация и добавление окон в stacked widget"""

        # Создаем окна, кроме tasks_window, т.к. user_id ещё неизвестен
        self.welcome_window = WelcomeWindow(self.stackedWidget)
        self.login_window = LoginWindow(self.stackedWidget, self.db)
        self.register_window = RegisterWindow(self.stackedWidget, self.db)

        # Подписываемся на сигнал успешного входа из окна логина
        self.login_window.login_success.connect(self.on_login_success)

        # Добавляем окна, которые создали
        self.stackedWidget.addWidget(self.welcome_window)
        self.stackedWidget.addWidget(self.login_window)
        self.stackedWidget.addWidget(self.register_window)

        # Показываем стартовое окно
        self.stackedWidget.setCurrentIndex(0)

    def on_login_success(self, user_id):
        """Вызывается при успешном входе пользователя"""
        self.current_user_id = user_id
        if self.tasks_window is None:
            # Создаём окно задач с user_id, теперь можно загрузить задачи конкретного пользователя
            self.tasks_window = TasksWindow(self.stackedWidget, self.db, user_id)
            self.stackedWidget.addWidget(self.tasks_window)
        else:
            # Если окно задач уже есть, просто обновляем user_id и загружаем задачи
            self.tasks_window.user_id = user_id
            self.tasks_window.load_tasks()
        # Показываем окно задач
        self.stackedWidget.setCurrentWidget(self.tasks_window)

    def on_page_changed(self, index):
        widget = self.stackedWidget.widget(index)
        if widget:
            size = widget.sizeHint()
            self.resize(size)


def load_stylesheet(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


# Адаптация масштабирования
# Этот код включает поддержку масштабирования интерфейса на экранах с высокой плотностью пикселей (HiDPI)
if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


def main():
    app = QApplication(sys.argv)

    # Загружаем иконку окна на все приложение сразу
    app.setWindowIcon(QIcon("images/icons8-clipboard-list-64"))

    # Загружаем QSS-файл со стилем
    style = load_stylesheet("styles/ConsoleStyle.qss")
    app.setStyleSheet(style)

    # Создаем объект базы данных
    db = Database()

    # Создаем главное окно и передаем объект базы
    window = MainWindow(db)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
