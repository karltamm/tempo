from PySide6 import QtWidgets
from PySide6 import QtGui
from pathlib import Path
import os

from .mainMenu import MainMenu
from .competitionsManager import CompetitionsManager


APP_WIDTH = 500
APP_HEIGHT = 700
DIR_PATH = Path(__file__).parent


def loadFont(font_folder, font_name):
    return QtGui.QFontDatabase.addApplicationFont(
        os.path.join(DIR_PATH, "fonts", font_folder, font_name + ".ttf")
    )


def setFontSmooth():
    # For some reason you don't have to specify a font name.
    # Somehow setHintingPreference applies to every font
    font_obj = QtGui.QFont()
    font_obj.setHintingPreference(QtGui.QFont.HintingPreference.PreferNoHinting)
    QtWidgets.QApplication.instance().setFont(font_obj)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        stylesheet_path = os.path.join(DIR_PATH, "style.css")
        with open(stylesheet_path) as f:
            self.setStyleSheet(f.read())

        self.setFixedSize(APP_WIDTH, APP_HEIGHT)
        self.setWindowTitle("Tempo")
        self.setContentsMargins(20, 30, 20, 30)

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
