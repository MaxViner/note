from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QListWidget, QPushButton, QWidget, \
    QDialog, QLineEdit, QTextEdit, QFormLayout, QDialogButtonBox, QLabel, QMessageBox
from PyQt5.QtCore import Qt
import sys
import sqlite3
from datetime import datetime


class Note:
    def __init__(self, id, title, content, date_added):
        self.id = id
        self.title = title
        self.content = content
        self.date_added = date_added


class NotesApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.notes = []

        self.init_db()
        self.init_ui()
        self.load_notes()

    def init_db(self):
        self.conn = sqlite3.connect("not.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                date_added TEXT
            )
        """)
        self.conn.commit()

    def init_ui(self):
        # Установка размеров окна
        self.setFixedSize(1000, 600)

        # Создание главного виджета и применение фонового изображения и стиля к нему
        central_widget = QWidget()
        central_widget.setStyleSheet("background-image: url(bg.png);"
                                     "font-size: 26px;"
                                     "background-color: #c6c6c6;")

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.show_note)

        add_button = QPushButton("Добавить заметку")
        add_button.clicked.connect(self.add_note)
        # Добавление тени для кнопки
        add_button.setStyleSheet("""
            font: 18px;
            QPushButton {
                background-color: #3daee9;
                color: white;
                border-radius: 5px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #51adf6;
            }
            QPushButton:pressed {
                background-color: #3daee9;
            }
        """)
        add_button.setGraphicsEffect(self.create_shadow())

        layout.addWidget(self.list_widget)
        layout.addWidget(add_button)

        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
    def create_shadow(self):
        from PyQt5.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(Qt.black)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        return shadow

    def load_notes(self):
        self.notes = []
        self.list_widget.clear()
        notes_data = self.cursor.execute("SELECT * FROM notes").fetchall()

        for note_data in notes_data:
            note = Note(*note_data)
            self.notes.append(note)
            self.list_widget.addItem(note.title)

    def add_note_to_db(self, note):
        self.cursor.execute("""
            INSERT INTO notes (title, content, date_added)
            VALUES (?, ?, ?)
        """, (note.title, note.content, note.date_added))
        self.conn.commit()

    def remove_note_from_db(self, note):
        self.cursor.execute("DELETE FROM notes WHERE id = ?", (note.id,))
        self.conn.commit()

    def update_note_in_db(self, note):
        self.cursor.execute("""
            UPDATE notes
            SET title = ?, content = ?
            WHERE id = ?
        """, (note.title, note.content, note.id))
        self.conn.commit()

    def add_note(self):

        note_dialog = QDialog(self)
        note_dialog.setWindowTitle("Добавить заметку")
        note_dialog.setStyleSheet(
        "QLineEdit { font: 20px; background: white;} QLineEdit:focus { border: 1px solid green; } QTextEdit { font: 18px; background: white;} QTextEdit:focus { border: 1px solid green; }")

        note_dialog = QDialog(self)
        note_dialog.setWindowTitle("Добавить заметку")
        note_dialog.setStyleSheet("QLineEdit { font: 20px; } QTextEdit { font: 18px; }")

        form_layout = QFormLayout()

        title_edit = QLineEdit()
        content_edit = QTextEdit()

        form_layout.addRow("Заголовок:", title_edit)
        form_layout.addRow("Содержание:", content_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(note_dialog.accept)
        button_box.rejected.connect(note_dialog.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        note_dialog.setLayout(layout)

        result = note_dialog.exec_()

        if result == QDialog.Accepted:
            title = title_edit.text()
            content = content_edit.toPlainText()
            date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note = Note(None, title, content, date_added)
            self.add_note_to_db(note)
            self.load_notes()

    def show_note(self):
        note = self.notes[self.list_widget.currentRow()]

        note_dialog = QDialog(self)
        note_dialog.setWindowTitle("Просмотр заметки")
        note_dialog.setStyleSheet(
        "QLineEdit { font: 20px; background: white;} QLineEdit:focus { border: 1px solid green; } QTextEdit { font: 18px; background: white;} QTextEdit:focus { border: 1px solid green; }")



        note_dialog = QDialog(self)
        note_dialog.setWindowTitle("Просмотр заметки")
        note_dialog.setStyleSheet("QLineEdit { font: 20px; } QTextEdit { font: 18px; }")

        form_layout = QFormLayout()

        title_edit = QLineEdit(note.title)
        title_edit.setReadOnly(True)
        content_edit = QTextEdit(note.content)
        content_edit.setReadOnly(True)

        form_layout.addRow("Заголовок:", title_edit)
        form_layout.addRow("Содержание:", content_edit)
        form_layout.addRow("Дата создания:", QLabel(note.date_added))

        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(note_dialog.reject)

        edit_button = QPushButton("Редактировать")
        edit_button.clicked.connect(lambda: self.edit_note(
            note, title_edit, content_edit, note_dialog))

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(note_dialog.accept)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(delete_button)
        layout.addWidget(edit_button)
        layout.addWidget(close_button)

        note_dialog.setLayout(layout)

        result = note_dialog.exec_()

        if result == QDialog.Rejected:
            confirm = QMessageBox.question(self, "Удалить заметку?",
                                           "Вы уверены, что хотите удалить эту заметку?",
                                           QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:
                self.remove_note_from_db(note)
                self.load_notes()

    def edit_note(self, note, title_edit, content_edit, dialog):
        if title_edit.isReadOnly():
            title_edit.setReadOnly(False)
            content_edit.setReadOnly(False)
        else:
            note.title = title_edit.text()
            note.content = content_edit.toPlainText()
            self.update_note_in_db(note)

            self.list_widget.currentItem().setText(note.title)

            title_edit.setReadOnly(True)
            content_edit.setReadOnly(True)

            QMessageBox.information(self, "Сохранено", "Заметка успешно сохранена.")


app = QApplication(sys.argv)
window = NotesApp()
window.show()
sys.exit(app.exec_())