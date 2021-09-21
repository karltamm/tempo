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

        # self.resize(APP_WIDTH, APP_HEIGHT)
        self.setWindowTitle("Tempo")

        # All pages
        self.main_menu = MainMenu(self.openCompetionsManager)
        self.competitions_manager = CompetitionsManager(self.openMainMenu)

        # Active page
        self.cur_page = QStackedWidget()
        self.cur_page.addWidget(self.main_menu)  # opened by default
        self.cur_page.addWidget(self.competitions_manager)

        self.setCentralWidget(self.cur_page)
        self.show()

    def openCompetionsManager(self):
        self.cur_page.setCurrentWidget(self.competitions_manager)

    def openMainMenu(self):
        self.cur_page.setCurrentWidget(self.main_menu)


class MainMenu(QWidget):
    def __init__(self, openCompetionsManager):
        super().__init__()

        # Header
        title = QLabel("Tempo")
        subtitle = QLabel("Lap time tracker")

        header = QVBoxLayout()
        header.addWidget(title)
        header.addWidget(subtitle)

        # Menu options
        competition_btn = QPushButton("Competitions")
        competition_btn.clicked.connect(openCompetionsManager)

        menu_options = QVBoxLayout()
        menu_options.addWidget(competition_btn)

        # Main layout
        main_layout = QGridLayout()
        main_layout.addLayout(header, 0, 0)
        main_layout.addLayout(menu_options, 1, 0)

        self.setLayout(main_layout)


class CompetitionsManager(QStackedWidget):
    def __init__(self, openMainMenu):
        super().__init__()

        self.competitions_list = CompetitionsList(openMainMenu, self.openCompetition)
        self.competition = Competition(self.showCompetitionsList)

        self.addWidget(self.competitions_list)
        self.addWidget(self.competition)

    def openCompetition(self, name, competition_id):
        self.setCurrentWidget(self.competition)
        self.competition.openCompetition(name, competition_id)

    def showCompetitionsList(self):
        self.setCurrentWidget(self.competitions_list)


class CompetitionsList(QWidget):
    def __init__(self, openMainMenu, openCompetition):
        super().__init__()
        # Header
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(openMainMenu)

        page_title = QLabel("Competitions")

        header = QHBoxLayout()
        header.addWidget(back_btn)
        header.addWidget(page_title)

        # List of competitions
        competitions = QVBoxLayout()
        competitions.addWidget(CompetitionsListItem(openCompetition, "Race1", 1))
        competitions.addWidget(CompetitionsListItem(openCompetition, "Race2", 1))
        competitions.addWidget(CompetitionsListItem(openCompetition, "Race2", 1))

        # Page
        main_layout = QGridLayout()
        main_layout.addLayout(header, 0, 0)
        main_layout.addLayout(competitions, 1, 0)

        self.setLayout(main_layout)


class CompetitionsListItem(QWidget):
    def __init__(self, openCompetition, name, competition_id):
        super().__init__()

        name = QLabel(name)
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(lambda: openCompetition(name, competition_id))

        layout = QHBoxLayout()
        layout.addWidget(name)
        layout.addWidget(open_btn)

        self.setLayout(layout)


class Competition(QWidget):
    def __init__(self, showCompetitionsList):
        super().__init__()

        self.competition_name = None
        self.competition_id = None
        self.showCompetitionsList = showCompetitionsList

    def openCompetition(self, name, competition_id):
        self.competition_name = name
        self.competition_id = competition_id

        self.prepareUI()

    def prepareUI(self):
        # Header
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.showCompetitionsList)

        page_title = QLabel(self.competition_name)

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
