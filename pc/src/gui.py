from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QStackedWidget,
    QHBoxLayout,
    QDialog,
    QDialogButtonBox,
)

from database import CompetitionDB
from competition import Competition

APP_WIDTH = 600
APP_HEIGHT = 600


def clearLayout(layout):
    if "Layout" in str(type(layout)):
        while layout.count():
            child = layout.takeAt(0)

            if child.layout():
                # Child is another layout
                clearLayout(child)  # recursion
            elif child.widget():
                # Child is actual widget
                child.widget().deleteLater()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(APP_WIDTH, APP_HEIGHT)
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

        self.openMainMenu = openMainMenu
        self.competition_data = Competition()
        self.prepareUI()

    def prepareUI(self):
        self.competitions_list = CompetitionsList(
            self.openMainMenu, self.openCompetitionUI, self.addCompetition
        )
        self.competition_ui = CompetitionUI(
            self.competition_data, self.showCompetitionsList, self.deleteCompetition
        )

        self.addWidget(self.competitions_list)
        self.addWidget(self.competition_ui)

    def openCompetitionUI(self, competition_name, competition_id):
        self.setCurrentWidget(self.competition_ui)
        self.competition_ui.openCompetition(competition_name, competition_id)

    def showCompetitionsList(self):
        self.setCurrentWidget(self.competitions_list)

    def addCompetition(self, competition_name):
        self.competition_data.create(competition_name)
        self.competitions_list.updateListOfCompetitions()

    def deleteCompetition(self):
        self.competitions_list.updateListOfCompetitions()
        self.showCompetitionsList()


class CompetitionsList(QWidget):
    def __init__(self, openMainMenu, openCompetitionUI, addCompetition):
        super().__init__()

        self.openCompetitionUI = openCompetitionUI
        self.openMainMenu = openMainMenu
        self.addCompetitionCallback = addCompetition

        self.generateUI()

    def generateUI(self):
        self.generateHeader()
        self.generateListOfCompetions()
        self.generateMainLayout()

    def generateHeader(self):
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.openMainMenu)
        page_title = QLabel("Competitions")

        self.header = QHBoxLayout()
        self.header.addWidget(back_btn)
        self.header.addWidget(page_title)

    def generateListOfCompetions(self):
        self.list_of_competitions = QVBoxLayout()

        create_competition_btn = QPushButton("Create competition")
        create_competition_btn.clicked.connect(self.createCompetition)
        self.list_of_competitions.addWidget(create_competition_btn)

        competition_data = CompetitionDB().getListOfCompetitions()
        for competition in competition_data:
            self.list_of_competitions.addWidget(
                CompetitionsListItem(
                    self.openCompetitionUI, competition["name"], competition["id"]
                )
            )

    def generateMainLayout(self):
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.main_layout.addLayout(self.header, 0, 0)
        self.main_layout.addLayout(self.list_of_competitions, 1, 0)

    def updateListOfCompetitions(self):
        clearLayout(self.list_of_competitions)
        self.generateListOfCompetions()
        self.main_layout.addLayout(self.list_of_competitions, 1, 0)

    def createCompetition(self):
        # self.addCompetitionCallback("Test")
        CreateCompetitionDialog()


class CreateCompetitionDialog(QDialog):
    def __init__(self):
        super().__init__()

        buttons = QDialogButtonBox.Save | QDialogButtonBox.Cancel
        btn_box = QDialogButtonBox(buttons)
        btn_box.accepted.connect(self.createCompetition)
        btn_box.rejected.connect(self.cancel)

        layout = QVBoxLayout()
        layout.addWidget(btn_box)
        layout.addWidget(btn_box)
        self.setLayout(layout)

        self.exec()

    def createCompetition(self):
        print("createCompetition")
        self.accept()

    def cancel(self):
        print("close")
        self.reject()


class CompetitionsListItem(QWidget):
    def __init__(self, openCompetitionUI, competition_name, competition_id):
        super().__init__()

        name_label = QLabel(competition_name)
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(
            lambda: openCompetitionUI(competition_name, competition_id)
        )

        layout = QHBoxLayout()
        layout.addWidget(name_label)
        layout.addWidget(open_btn)

        self.setLayout(layout)


class CompetitionUI(QWidget):
    def __init__(self, competition_data, showCompetitionsList, deleteCompetition):
        super().__init__()

        self.competition_data = competition_data
        self.showCompetitionsList = showCompetitionsList
        self.deleteCompetitionCallback = deleteCompetition

        self.prepareUI()

    def openCompetition(self, competition_name, competition_id):
        self.competition_data.resume(competition_name, competition_id)

        self.updateUI()

    def prepareUI(self):
        self.generateHeader()
        self.generateCompetitionControlUI()
        self.generateLayout()

    def generateHeader(self):
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.showCompetitionsList)
        self.page_title = QLabel(self.competition_data.name)

        self.header = QHBoxLayout()
        self.header.addWidget(back_btn)
        self.header.addWidget(self.page_title)

    def generateCompetitionControlUI(self):
        self.add_new_entry_btn = QPushButton("Add new entry")
        self.delete_competition_btn = QPushButton("Delete competition")
        self.delete_competition_btn.clicked.connect(self.deleteCompetition)

        self.control_layout = QGridLayout()
        self.control_layout.addWidget(self.add_new_entry_btn, 0, 0)
        self.control_layout.addWidget(self.delete_competition_btn, 0, 1)

    def generateLayout(self):
        self.main_layout = QGridLayout()
        self.main_layout.addLayout(self.header, 0, 0)
        self.main_layout.addLayout(self.control_layout, 1, 0)
        self.setLayout(self.main_layout)

    def updateUI(self):
        self.page_title.setText(self.competition_data.name)

    def deleteCompetition(self):
        self.competition_data.delete()
        self.deleteCompetitionCallback()
