#начни тут создавать приложение с умными заметками
import json
import datetime
import os

from PyQt5 import Qt, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                            QLabel, QHBoxLayout, QVBoxLayout,
                            QTextEdit, QLineEdit, QListWidget, QMessageBox)

class NotesApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.data = {}

        self.setWindowTitle("Заметки")

        # скелет приложения
        self.main_vbox = QVBoxLayout()
        self.hbox_labels = QHBoxLayout()
        self.hbox1 = QHBoxLayout()
        self.control_panel_vbox = QVBoxLayout()

        self.note_label = QLabel("Текст заметки")
        self.hbox_labels.addWidget(self.note_label)

        # поле для ввода заметок
        self.note_text_edit = QTextEdit()
        self.hbox1.addWidget(self.note_text_edit)

        # список заметок
        self.note_list_label = QLabel("Список заметок")
        self.control_panel_vbox.addWidget(self.note_list_label)

        self.list_of_notes = QListWidget()
        self.list_of_notes.setFixedWidth(150)
        self.fill_list_of_notes()
        self.list_of_notes.itemClicked.connect(self.select_note)
        self.control_panel_vbox.addWidget(self.list_of_notes)

        self.tags_list_label = QLabel("Теги")
        self.control_panel_vbox.addWidget(self.tags_list_label)

        self.tags_text_edit = QTextEdit()
        self.tags_text_edit.setFixedWidth(150)
        self.control_panel_vbox.addWidget(self.tags_text_edit)

        # кнопка для поиска заметок по тегу
        self.find_notes_button = QPushButton("Поиск по тегу")
        self.find_notes_button.clicked.connect(self.find_notes)
        self.control_panel_vbox.addWidget(self.find_notes_button)

        # кнопка для сохранения заметки
        self.create_note_button = QPushButton("Создать заметку")
        self.create_note_button.clicked.connect(self.create_note)
        self.control_panel_vbox.addWidget(self.create_note_button)

        # кнопка для сохранения заметки
        self.save_note_button = QPushButton("Сохранить заметку")
        self.save_note_button.clicked.connect(self.save_note)
        self.control_panel_vbox.addWidget(self.save_note_button)

        # кнопка удаления заметки
        self.delete_note_button = QPushButton("Удалить заметку")
        self.delete_note_button.clicked.connect(self.delete_note)
        self.control_panel_vbox.addWidget(self.delete_note_button)

        # навешиваем шампуры друг на друга
        self.main_vbox.addLayout(self.hbox_labels)
        self.main_vbox.addLayout(self.hbox1)
        self.hbox1.addLayout(self.control_panel_vbox)
        self.setLayout(self.main_vbox)

    def find_notes(self):
        self.finder_widget = FindNotesWidget(self)

    def save_note(self):
        tags_text = self.tags_text_edit.toPlainText()
        tags_list = tags_text.replace("\n", " ").split(" ")
        print(tags_list)

        tags_list_result = []

        for i, tag in enumerate(tags_list):
            if tag[0] == "#":
                tags_list_result.append(tag)

        self.data["tags"] = tags_list_result

        if len(self.data) == 0:
            self.data["name"] = None
        self.data["text"] = self.note_text_edit.toPlainText()
        self.save_widget = SaveNoteWidget(self.data, self)

    def create_note(self):
        self.data["name"] = None
        self.data["text"] = self.note_text_edit.toPlainText()
        self.save_widget = SaveNoteWidget(self.data, self)

    def delete_note(self):
        try:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Question)
            msgBox.setText(f'Вы действительно хотите удалить заметку {self.data["name"]}')
            msgBox.setWindowTitle(f'Удаление заметки {self.data["name"]}')
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            returnValue = msgBox.exec()
            if returnValue == QMessageBox.Ok:
                os.remove(f'notes/{self.data["name"]}')
                self.fill_list_of_notes()
        except:
            pass

    def fill_list_of_notes(self):
        self.list_of_notes.clear()
        for name in os.listdir("notes"):
            if name[-5:] == ".json":
                self.list_of_notes.addItem(name.replace(".json", ""))

    def select_note(self, note):
        filename = f'notes/{note.text()}.json'

        try:
            with open(filename, "r") as file:
                self.data = json.load(file)
                self.note_text_edit.setText(self.data["text"])
                file.close()
        except:
            self.fill_list_of_notes()

class SaveNoteWidget(QWidget):
    def __init__(self, data, parent_win: NotesApp) -> None:
        super().__init__()
        self.parent_win = parent_win
        self.data = data

        self.main_vbox = QVBoxLayout()

        self.name_edit = QLineEdit()
        if "name" in data.keys():
            if data["name"]:
                self.name_edit.setText(data["name"][:-5])
        else:
            self.name_edit.setText("")
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.close_window)

        self.main_vbox.addWidget(self.name_edit)
        self.main_vbox.addWidget(self.save_button)
        self.main_vbox.addWidget(self.cancel_button)
        self.setLayout(self.main_vbox)

        self.show()

    def save(self):
        if self.name_edit.text() not in ("", None):
            self.note_name = f'{self.name_edit.text()}.json'

            data = {
                "text":str(self.data["text"]),
                "name":str(self.note_name),
                "tags":self.data["tags"],
                "date": str(datetime.datetime.now())
            }
            
            with open(f'notes/{self.note_name}', "w+", encoding="utf-8") as file:
                json.dump(data, file)
                file.close()

            self.close_window()
            self.parent_win.fill_list_of_notes()


    def close_window(self):
        self.close()

class FindNotesWidget(QWidget):
    def __init__(self, parent_win: NotesApp) -> None:
        super().__init__()
        self.parent_win = parent_win

        self.main_vbox = QVBoxLayout()

        self.tag_name_edit = QLineEdit()

        self.find_button = QPushButton("Найти...")
        self.find_button.clicked.connect(self.find_note)
 
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.close_window)

        self.main_vbox.addWidget(self.tag_name_edit)
        self.main_vbox.addWidget(self.find_button)
        self.main_vbox.addWidget(self.cancel_button)
        self.setLayout(self.main_vbox)

        self.show()

    def find_note(self):
        tag = self.tag_name_edit.text().split(" ")[0]
        if len(tag):
            if tag[0] != "#":
                tag = f'#{tag}'

        for name in os.listdir("notes"):
            if name[-5:] == ".json":
                with open(f'notes/{name}', "r") as file:
                    try:
                        self.data = json.load(file)
                        if tag in self.data["tags"]:
                            for item in self.parent_win.list_of_notes.findItems(name[:-5], Qt.MatchExactly):
                                item.setBackground(QtGui.QColor(0, 255, 0, 64))
                        file.close()
                    except:
                        file.close()


    def close_window(self):
        self.close()

app = QApplication([])
win = NotesApp()
win.show()
app.exec_()

