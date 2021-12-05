from PySide6 import QtWidgets, QtCore

from .mainMenu import MainMenu
from .competitionsManager import CompetitionsManager
from .trackingUI import TrackingUI
from assets import getStylesheetPath, getWindowIcon
from serialData import SerialDataHandler

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
        self.setWindowIcon(getWindowIcon())

        self.setupSerialDataHandler()

        self.createMainPages()
        self.createPageController()

        self.show()

    def setupSerialDataHandler(self):
        self.serial_data_handler = SerialDataHandler()
        self.threadpool = QtCore.QThreadPool()
        # NB! if threadpool is not this class variable (no ".self") then GUI wont be displayed
        self.threadpool.start(self.serial_data_handler)

    def createMainPages(self):
        self.main_menu = MainMenu(self.openCompetionsManager, self.openPractice)
        self.competitions_manager = CompetitionsManager(
            self.openMainMenu, self.serial_data_handler
        )
        self.tracking_UI = TrackingUI(
            "practice", self.openMainMenu, self.serial_data_handler, practice=True
        )

    def createPageController(self):
        self.cur_page = QtWidgets.QStackedWidget()
        self.cur_page.addWidget(self.main_menu)  # opened by default
        self.cur_page.addWidget(self.competitions_manager)
        self.cur_page.addWidget(self.tracking_UI)
        self.setCentralWidget(self.cur_page)

    def openCompetionsManager(self):
        self.cur_page.setCurrentWidget(self.competitions_manager)
        self.competitions_manager.openCompetitionsList()
        
    def openPractice(self):
        self.cur_page.setCurrentWidget(self.tracking_UI)
        self.tracking_UI.openTracking(("Practice", 0))

    def openMainMenu(self):
        self.cur_page.setCurrentWidget(self.main_menu)

    def closeEvent(self, event) -> None:
        self.serial_data_handler.stop()

        return super().closeEvent(event)
