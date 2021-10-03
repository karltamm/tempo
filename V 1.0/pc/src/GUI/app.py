from PySide6 import QtWidgets

from .mainMenu import MainMenu
from .competitionsManager import CompetitionsManager
from assets import getStylesheetPath, getWindowIcon

APP_WIDTH = 500
APP_HEIGHT = 700


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        with open(getStylesheetPath()) as f:
            self.setStyleSheet(f.read())

        self.setFixedSize(APP_WIDTH, APP_HEIGHT)
        self.setWindowTitle("Tempo")
        self.setContentsMargins(20, 30, 20, 30)
        # self.setWindowIcon(getWindowIcon())

        self.createMainPages()
        self.createPageController()

        self.show()

    def createMainPages(self):
        self.main_menu = MainMenu(self.openCompetionsManager)
        self.competitions_manager = CompetitionsManager(self.openMainMenu)

    def createPageController(self):
        self.cur_page = QtWidgets.QStackedWidget()
        self.cur_page.addWidget(self.main_menu)  # opened by default
        self.cur_page.addWidget(self.competitions_manager)
        self.setCentralWidget(self.cur_page)

    def openCompetionsManager(self):
        self.cur_page.setCurrentWidget(self.competitions_manager)
        self.competitions_manager.openCompetitionsList()

    def openMainMenu(self):
        self.cur_page.setCurrentWidget(self.main_menu)
