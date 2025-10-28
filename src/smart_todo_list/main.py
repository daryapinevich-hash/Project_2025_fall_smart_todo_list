import sys
import re
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QMessageBox,
    QStackedWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi


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

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
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

        # Здесь должна быть реальная проверка логина/пароля
        QMessageBox.information(self, "Успех", f"Добро пожаловать, {login}!")
        self.clear_fields()
        self.go_back()

    def go_back(self):
        self.clear_fields()
        self.stacked_widget.setCurrentIndex(0)

    def clear_fields(self):
        self.loginInput.clear()
        self.passwordInput.clear()


class RegisterWindow(QWidget):

    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
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
        QMessageBox.information(
            self, "Успех", f"Пользователь {login} успешно зарегистрирован!"
        )
        self.clear_fields()
        self.go_back()

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


class MainWindow(QMainWindow):
    """Главное окно приложения со StackedWidget"""

    def __init__(self):
        super().__init__()
        loadUi("ui/main_window.ui", self)
        self.init_windows()

    def init_windows(self):
        """Инициализация и добавление окон в stacked widget"""
        # Создаем окна
        self.welcome_window = WelcomeWindow(self.stackedWidget)
        self.login_window = LoginWindow(self.stackedWidget)
        self.register_window = RegisterWindow(self.stackedWidget)

        # Добавляем окна в stacked widget
        self.stackedWidget.addWidget(self.welcome_window)
        self.stackedWidget.addWidget(self.login_window)
        self.stackedWidget.addWidget(self.register_window)

        # Устанавливаем начальное окно
        self.stackedWidget.setCurrentIndex(0)


def load_stylesheet(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def main():
    app = QApplication(sys.argv)

    # Загружаем QSS-файл со стилем
    style = load_stylesheet("styles/ConsoleStyle.qss")
    app.setStyleSheet(style)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
