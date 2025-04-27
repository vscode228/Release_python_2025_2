import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QTimeEdit, QLabel, QTextEdit, QComboBox
)
from PyQt5.QtGui import QFont, QBrush, QColor
from PyQt5.QtCore import Qt, QTime

CONFIG_FILE = 'config.json'

# Кольорові стилі для світлої та темної тем:
light_stylesheet = """
QWidget {
    background-color: #f0f8ff;
    color: #333333;
}
QPushButton {
    background-color: #87cefa;
    color: #333333;
    border: 1px solid #1e90ff;
    border-radius: 5px;
    padding: 5px;
}
QLineEdit, QComboBox {
    background-color: white;
    color: #333333;
    border: 1px solid #1e90ff;
    border-radius: 3px;
    padding: 2px;
}
QListWidget {
    background-color: white;
    color: #333333;
    border: 1px solid #1e90ff;
    border-radius: 3px;
}
"""

dark_stylesheet = """
QWidget {
    background-color: #2c3e50;
    color: #ecf0f1;
}
QPushButton {
    background-color: #34495e;
    color: #ecf0f1;
    border: 1px solid #2980b9;
    border-radius: 5px;
    padding: 5px;
}
QLineEdit, QComboBox {
    background-color: #3c556e;
    color: #ecf0f1;
    border: 1px solid #2980b9;
    border-radius: 3px;
    padding: 2px;
}
QListWidget {
    background-color: #34495e;
    color: #ecf0f1;
    border: 1px solid #2980b9;
    border-radius: 3px;
}
"""

# Налаштування за замовчуванням
DEFAULT_CONFIG = {
    "theme": "Light",
    "window_geometry": {
        "x": 100,
        "y": 100,
        "width": 500,
        "height": 600
    },
    "last_tasks": [],
    "font": {
        "family": "Arial",
        "size": 12
    },
    "language": "uk"
}

# Віджет для одного завдання, який відображає текст, час, приорітет і теги
class TaskWidget(QWidget):
    def __init__(self, text, deadline, completed=False, priority="Середній", tags=None, parent=None):
        super().__init__(parent)
        self.text = text
        self.deadline = deadline
        self.completed = completed
        self.priority = priority
        self.tags = tags if tags is not None else []
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        # Формуємо текст для відображення інформації: текст, час, приорітет і теги (якщо є)
        info_text = f"{self.text} [{self.deadline}] (Приоритет: {self.priority})"
        if self.tags:
            info_text += " Теги: " + ", ".join(self.tags)
        self.label_main = QLabel(info_text)
        font_main = self.label_main.font()
        font_main.setPointSize(12)
        font_main.setStrikeOut(self.completed)
        self.label_main.setFont(font_main)
        # Більш маленький напис "виконано", який відображається, якщо завдання виконане
        self.label_done = QLabel("виконано")
        font_done = QFont(self.label_done.font())
        font_done.setPointSize(8)
        self.label_done.setFont(font_done)
        self.label_done.setStyleSheet("color: green;")
        self.label_done.setVisible(self.completed)
        layout.addWidget(self.label_main)
        layout.addWidget(self.label_done)
        layout.addStretch()
        self.setLayout(layout)
    
    def update_widget(self, text, deadline, completed, priority, tags):
        self.text = text
        self.deadline = deadline
        self.completed = completed
        self.priority = priority
        self.tags = tags
        info_text = f"{self.text} [{self.deadline}] (Приоритет: {self.priority})"
        if self.tags:
            info_text += " Теги: " + ", ".join(self.tags)
        self.label_main.setText(info_text)
        font_main = self.label_main.font()
        font_main.setStrikeOut(self.completed)
        self.label_main.setFont(font_main)
        self.label_done.setVisible(self.completed)

class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config = DEFAULT_CONFIG.copy()
        self.load_settings()
        self.current_theme = self.config.get("theme", "Light")
        geom = self.config.get("window_geometry", DEFAULT_CONFIG["window_geometry"])
        self.setGeometry(geom.get("x", 100), geom.get("y", 100),
                         geom.get("width", 500), geom.get("height", 600))
        font_config = self.config.get("font", DEFAULT_CONFIG["font"])
        font = QFont(font_config.get("family", "Arial"), font_config.get("size", 12))
        self.setFont(font)
        self.setWindowTitle("Топовий To‑Do List")
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout()

        # Рядок у верхньому правому куті для вибору теми (емодзі)
        theme_layout = QHBoxLayout()
        theme_layout.setContentsMargins(0, 0, 0, 0)
        theme_layout.setAlignment(Qt.AlignRight)
        self.light_button = QPushButton("☀️")
        self.light_button.setFixedSize(30, 30)
        self.light_button.clicked.connect(lambda: self.change_theme("Light"))
        self.dark_button = QPushButton("🌙")
        self.dark_button.setFixedSize(30, 30)
        self.dark_button.clicked.connect(lambda: self.change_theme("Dark"))
        theme_layout.addWidget(self.light_button)
        theme_layout.addWidget(self.dark_button)
        layout.addLayout(theme_layout)

        # Розклад для введення завдання, вибору часу, приорітету та тегів
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Введіть завдання")
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setTime(QTime.currentTime())
        self.priority_box = QComboBox()
        self.priority_box.addItems(["Високий", "Середній", "Низький"])
        self.priority_box.setCurrentText("Середній")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Теги (через кому)")
        self.add_button = QPushButton("Додати")
        self.add_button.clicked.connect(self.add_task)
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.time_input)
        input_layout.addWidget(self.priority_box)
        input_layout.addWidget(self.tags_input)
        input_layout.addWidget(self.add_button)

        # Список завдань
        self.task_list = QListWidget()
        self.task_list.itemDoubleClicked.connect(self.toggle_task_done)
        self.task_list.currentItemChanged.connect(self.on_task_selection_changed)
        # Завантаження збережених завдань із параметрами
        for task in self.config.get("last_tasks", []):
            if isinstance(task, dict):
                text = task.get("text", "")
                completed = task.get("completed", False)
                deadline = task.get("time", "")
                description = task.get("description", "")
                priority = task.get("priority", "Середній")
                tags = task.get("tags", [])
            else:  # для сумісності
                text = task
                completed = False
                deadline = ""
                description = ""
                priority = "Середній"
                tags = []
            self.add_task_item(text, deadline, completed, description, priority, tags)

        # Розклад для кнопок управління завданнями
        controls_layout = QHBoxLayout()
        self.delete_button = QPushButton("Видалити вибране")
        self.delete_button.clicked.connect(self.delete_selected)
        self.clear_completed_button = QPushButton("Очистити виконані")
        self.clear_completed_button.clicked.connect(self.clear_completed)
        controls_layout.addWidget(self.delete_button)
        controls_layout.addWidget(self.clear_completed_button)

        # Блок для редагування детального опису завдання
        description_label = QLabel("Опис:")
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Введіть докладний опис завдання...")
        self.description_edit.setFixedHeight(100)
        self.description_edit.textChanged.connect(self.update_current_task_description)

        layout.addLayout(input_layout)
        layout.addWidget(self.task_list)
        layout.addLayout(controls_layout)
        layout.addWidget(description_label)
        layout.addWidget(self.description_edit)

        self.setLayout(layout)

    def add_task(self):
        text = self.task_input.text().strip()
        deadline = self.time_input.time().toString("HH:mm")
        priority = self.priority_box.currentText()
        tags_str = self.tags_input.text().strip()
        tags = [t.strip() for t in tags_str.split(",")] if tags_str else []
        if text:
            self.add_task_item(text, deadline, completed=False, description="", priority=priority, tags=tags)
            self.task_input.clear()
            self.tags_input.clear()

    def add_task_item(self, text, deadline, completed=False, description="", priority="Середній", tags=None):
        if tags is None:
            tags = []
        item = QListWidgetItem()
        task = {
            "text": text,
            "time": deadline,
            "completed": completed,
            "description": description,
            "priority": priority,
            "tags": tags
        }
        item.setData(Qt.UserRole, task)
        self.task_list.addItem(item)
        widget = TaskWidget(text, deadline, completed, priority, tags)
        self.task_list.setItemWidget(item, widget)

    def toggle_task_done(self, item):
        task = item.data(Qt.UserRole)
        task["completed"] = not task.get("completed", False)
        item.setData(Qt.UserRole, task)
        widget = self.task_list.itemWidget(item)
        if widget is not None and isinstance(widget, TaskWidget):
            widget.update_widget(task["text"], task["time"], task["completed"], task.get("priority", "Середній"), task.get("tags", []))
        self.save_settings()

    def on_task_selection_changed(self, current, previous):
        if current is not None:
            task = current.data(Qt.UserRole)
            self.description_edit.blockSignals(True)
            self.description_edit.setPlainText(task.get("description", ""))
            self.description_edit.blockSignals(False)
        else:
            self.description_edit.blockSignals(True)
            self.description_edit.clear()
            self.description_edit.blockSignals(False)

    def update_current_task_description(self):
        current = self.task_list.currentItem()
        if current is not None:
            task = current.data(Qt.UserRole)
            task["description"] = self.description_edit.toPlainText()
            current.setData(Qt.UserRole, task)
            self.save_settings()

    def delete_selected(self):
        for item in self.task_list.selectedItems():
            row = self.task_list.row(item)
            self.task_list.takeItem(row)
        self.save_settings()

    def clear_completed(self):
        for i in range(self.task_list.count() - 1, -1, -1):
            item = self.task_list.item(i)
            task = item.data(Qt.UserRole)
            if task.get("completed", False):
                self.task_list.takeItem(i)
        self.save_settings()

    def change_theme(self, theme):
        self.current_theme = theme
        self.config["theme"] = theme
        self.apply_theme()
        self.save_settings()

    def apply_theme(self):
        if self.current_theme == "Light":
            QApplication.instance().setStyleSheet(light_stylesheet)
        elif self.current_theme == "Dark":
            QApplication.instance().setStyleSheet(dark_stylesheet)

    def save_settings(self):
        geom = self.geometry()
        self.config["window_geometry"] = {
            "x": geom.x(),
            "y": geom.y(),
            "width": geom.width(),
            "height": geom.height()
        }
        tasks = []
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            task = item.data(Qt.UserRole)
            tasks.append(task)
        self.config["last_tasks"] = tasks
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        loaded_config = json.loads(content)
                        self.config.update(loaded_config)
            except (json.JSONDecodeError, IOError):
                self.config = DEFAULT_CONFIG.copy()
                self.save_settings()
        else:
            self.config = DEFAULT_CONFIG.copy()
            self.save_settings()

    def closeEvent(self, event):
        self.save_settings()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec_())
