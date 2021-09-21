from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QStackedWidget,
    QHBoxLayout,
)
from PySide6.QtGui import QPalette, QColor

APP_WIDTH = 600
APP_HEIGHT = 600


class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window design
        # self.resize(APP_WIDTH, APP_HEIGHT)
        self.setWindowTitle("Tempo")

        # Pages
        self.main_menu = MainMenu(self.openCompetionWindow)
        self.competitions = CompetitionsList(self.openMainMenu)

        # Actice page controller
        self.cur_page = QStackedWidget()
        self.cur_page.addWidget(self.main_menu)  # opened by default
        self.cur_page.addWidget(self.competitions)

        self.setCentralWidget(self.cur_page)
        self.show()

    def openCompetionWindow(self):
        self.cur_page.setCurrentWidget(self.competitions)

    def openMainMenu(self):
        self.cur_page.setCurrentWidget(self.main_menu)


class MainMenu(QWidget):
    def __init__(self, openCompetionWindow):
        super().__init__()

        # Header
        title = QLabel("Tempo")
        subtitle = QLabel("Lap time tracker")

        header = QVBoxLayout()
        header.addWidget(title)
        header.addWidget(subtitle)

        # Menu options
        competition_btn = QPushButton("Competitions")
        competition_btn.clicked.connect(openCompetionWindow)

        menu_options = QVBoxLayout()
        menu_options.addWidget(competition_btn)

        # Main layout
        main_layout = QGridLayout()
        main_layout.addLayout(header, 0, 0)
        main_layout.addLayout(menu_options, 1, 0)

        self.setLayout(main_layout)


class CompetitionsList(QWidget):
    def __init__(self, openMainMenu):
        super().__init__()

        # Header
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(openMainMenu)

        page_title = QLabel("Competitions")

        header = QHBoxLayout()
        header.addWidget(back_btn)
        header.addWidget(page_title)

        # Page
        main_layout = QGridLayout()
        main_layout.addLayout(header, 0, 0)

        self.setLayout(main_layout)


app = QApplication()
window = MainWindow()
app.exec()
