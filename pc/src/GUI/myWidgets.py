from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore
import math

SECOND_IN_MS = 1000
MINUTE_IN_MS = 60 * SECOND_IN_MS


def formatTime(time_ms):
    time_ms = int(time_ms)  # Make sure that its actually number

    minutes = math.floor(time_ms / MINUTE_IN_MS)  # How many full minutes?
    seconds = math.floor(
        (time_ms % MINUTE_IN_MS) / SECOND_IN_MS
    )  # Remainder of full minute
    # milliseconds = math.floor(((time_ms % MINUTE_IN_MS) % SECOND_IN_MS))

    minutes_str = ""
    if minutes < 10:
        minutes_str = "0" + str(minutes) + ":"
    else:
        minutes_str = str(minutes) + ":"

    seconds_str = ""
    if seconds < 10:
        seconds_str = "0" + str(seconds)
    else:
        seconds_str = str(seconds)

    return minutes_str + seconds_str


def clearLayout(layout):
    if "Layout" in str(type(layout)):
        while layout.count():
            child = layout.takeAt(0)

            if child.layout():
                # Child is another layout
                clearLayout(child)
            elif child.widget():
                # Child is actual widget
                child.widget().deleteLater()


class MyWidget(QtWidgets.QWidget):
    def __init__(self, id_tag=None, parent=None):
        super().__init__(parent)

        # Set object name to easily identify widgets in stylesheet
        # self.__class__.__name__ gives Python class name
        class_name = self.__class__.__name__
        self.setObjectName(id_tag or class_name)

        self.setProperty("class", "page")

    def paintEvent(self, event):
        # This is a method override to make sure that stylesheet identifies object by its name.
        # For some reason if widget is a custom (subclassed from QWidget) then stylesheet doesn't work correctly.
        opt = QtWidgets.QStyleOption()
        opt.initFrom(self)

        painter = QtGui.QPainter(self)

        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, painter, self)


class SectionTitle(QtWidgets.QLabel):
    def __init__(self, text, id_tag="", class_tag="", parent=None):
        super().__init__(text, parent)

        self.setObjectName(id_tag)
        self.setProperty("class", "section_title")
        self.setProperty("class2", class_tag)

        self.setContentsMargins(0, 20, 0, 5)


class Page(MyWidget):
    def __init__(self, id_tag=None, parent=None):
        super().__init__(id_tag, parent)

        self.setProperty("class", "page")


class Button(QtWidgets.QPushButton):
    def __init__(self, text, id_tag="", class_tag="", parent=None):
        super().__init__(text, parent)

        # Set object name to easily identify widgets in stylesheet
        # self.__class__.__name__ gives Python class name
        class_name = self.__class__.__name__
        self.setObjectName(id_tag or class_name)

        # To access multiple instances of this object in stylesheet
        self.setProperty("class", "button")
        self.setProperty("class2", class_tag)

        # If user hovers over a button, then show correct cursor type
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))


class PageTitle(QtWidgets.QLabel):
    def __init__(self, text, id_tag="", class_tag="", parent=None):
        super().__init__(text, parent)

        # Set object name to easily identify widgets in stylesheet
        # self.__class__.__name__ gives Python class name
        class_name = self.__class__.__name__
        self.setObjectName(id_tag or class_name)

        self.setContentsMargins(0, 20, 0, 0)


class InputDialog(QtWidgets.QDialog):
    def __init__(self, input_label_name, max_length=None, parent=None, callback=None):
        super().__init__(parent)

        self.callback = callback or (lambda x: None)
        self.input_label_name = input_label_name

        self.max_length = max_length or 20  # Default

        self.setupUI()

        self.exec()

    def setupUI(self):
        self.setFixedSize(300, 200)
        self.setWindowTitle(self.input_label_name)

        input_label = QtWidgets.QLabel(self.input_label_name)
        input_label.setProperty("class", "input_label")

        self.input = QtWidgets.QLineEdit()
        self.input.textChanged.connect(self.validateInput)

        self.input_feedback = QtWidgets.QLabel()
        self.input_feedback.setProperty("class", "input_feedback")

        save_btn = Button("Save", class_tag="green_btn")
        save_btn.clicked.connect(self.save)

        cancel_btn = Button("Cancel", class_tag="red_btn")
        cancel_btn.clicked.connect(self.reject)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        buttons.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(input_label)
        layout.addWidget(self.input)
        layout.addWidget(self.input_feedback)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def setInputMaxLength(self, length):
        self.max_length = length

    def save(self):
        input_val = self.input.text()
        if self.validateInput(input_val):
            self.callback(input_val)
            self.accept()

    def validateInput(self, value):
        if not value:
            self.input_feedback.setText("Too short")
            return False

        if len(value) > self.max_length:
            self.input_feedback.setText(f"Max {self.max_length} characters")
            return False

        # Everything okay
        self.input_feedback.setText("")  # Remove previously set error
        return True
