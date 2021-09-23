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
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QListView,
    QAbstractItemView,
    QMessageBox,
)
from PySide6 import QtCore
from PySide6.QtCore import QAbstractListModel, Qt

from database import CompetitionDB

APP_WIDTH = 300
APP_HEIGHT = 300


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(APP_WIDTH, APP_HEIGHT)
        self.setWindowTitle("Tempo")

        self.createMainPages()
        self.createPageController()

        self.show()

    def createMainPages(self):
        self.main_menu = MainMenu(self.openCompetionsManager)
        self.competitions_manager = CompetitionsManager(self.openMainMenu)

    def createPageController(self):
        self.cur_page = QStackedWidget()
        self.cur_page.addWidget(self.main_menu)  # opened by default
        self.cur_page.addWidget(self.competitions_manager)
        self.setCentralWidget(self.cur_page)

    def openCompetionsManager(self):
        self.cur_page.setCurrentWidget(self.competitions_manager)
        self.competitions_manager.openCompetitionsList()

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
        menu_options.setAlignment(QtCore.Qt.AlignLeft)
        menu_options.addWidget(competition_btn)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.addLayout(header)
        main_layout.addLayout(menu_options)

        self.setLayout(main_layout)


class CompetitionsManager(QStackedWidget):
    def __init__(self, openMainMenu):
        super().__init__()

        self.openMainMenu = openMainMenu
        self.competition_db = CompetitionDB()
        self.prepareUI()

    def prepareUI(self):
        self.competitions_list = CompetitionsList(
            self.competition_db,
            self.openMainMenu,
            self.openCompetitionUI,
        )
        self.competition_UI = CompetitionUI(
            self.competition_db,
            self.openCompetitionsList,
            self.openTrackingUI,
        )
        self.tracking_UI = TrackingUI(self.competition_db, self.openCompetitionUI)

        self.addWidget(self.competitions_list)
        self.addWidget(self.competition_UI)
        self.addWidget(self.tracking_UI)

    def openCompetitionsList(self):
        self.setCurrentWidget(self.competitions_list)
        self.competitions_list.getList()

    def openCompetitionUI(self, competition_name, competition_id):
        self.setCurrentWidget(self.competition_UI)
        self.competition_UI.openCompetition(competition_name, competition_id)

    def openTrackingUI(self):
        self.setCurrentWidget(self.tracking_UI)
        self.tracking_UI.setCompetitionInfo(self.competition_UI.competitionInfo())


class CompetitionsList(QWidget):
    def __init__(self, competition_db, openMainMenu, openCompetitionUI):
        super().__init__()

        self.competition_db = competition_db
        self.openCompetitionUI = openCompetitionUI
        self.openMainMenu = openMainMenu

        self.competitions_list = None

        self.generateUI()

    def generateUI(self):
        self.generateHeader()
        self.generateListSection()
        self.generateMainLayout()

    def generateHeader(self):
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.openMainMenu)

        self.header = QHBoxLayout()
        self.header.addWidget(back_btn)

    def generateListSection(self):
        title = QLabel("Competitions")
        add_competition_btn = QPushButton("Add Competition")
        add_competition_btn.clicked.connect(self.openCompetitionCreator)

        self.list_section = QVBoxLayout()
        self.list_section.addWidget(title)
        self.list_section.addWidget(add_competition_btn)

    def generateMainLayout(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(main_layout)

        main_layout.addLayout(self.header)
        main_layout.addLayout(self.list_section)

    def getList(self):
        data = self.competition_db.getListOfCompetitions()

        if data != None:
            # Reset list
            clearLayout(self.competitions_list)
            self.competitions_list = QVBoxLayout()

            # Populate list
            for competition in data:
                self.competitions_list.addWidget(
                    CompetitionListItem(
                        competition["name"],
                        competition["id"],
                        self.openCompetitionUI,
                        self.deleteCompetition,
                    )
                )

            # Add list to view
            self.list_section.addLayout(self.competitions_list)
        else:
            QMessageBox.critical(
                self, "Database Error", "List of competitions could not be retrived!"
            )

    def openCompetitionCreator(self):
        CompetitionCreator(self, self.addCompetition)

    def addCompetition(self, name):
        if self.competition_db.addCompetition(name):
            self.getList()  # Update list
        else:
            QMessageBox.critical(
                self, "Database Error", "Competition could not be created!"
            )

    def deleteCompetition(self, competition_ID):
        if self.competition_db.deleteCompetition(competition_ID):
            self.getList()  # Update list
        else:
            QMessageBox.critical(
                self, "Database Error", "Competition could not be deleted!"
            )


class CompetitionListItem(QWidget):
    def __init__(
        self,
        competition_name,
        competition_ID,
        openCompetitionUI,
        deleteCompetition,
    ):
        super().__init__()

        name = QLabel(competition_name)
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(
            lambda: openCompetitionUI(competition_name, competition_ID)
        )
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: deleteCompetition(competition_ID))

        layout = QHBoxLayout()
        layout.addWidget(name)
        layout.addWidget(open_btn)
        layout.addWidget(delete_btn)
        self.setLayout(layout)


class CompetitionCreator(QDialog):
    def __init__(self, parent, addCompetitionCallback):
        super().__init__(parent)

        self.addCompetitionCallback = addCompetitionCallback

        # Input to get name
        input_label = QLabel("Competition name")
        self.name_input = QLineEdit()
        self.input_feedback = QLabel()

        input_layout = QVBoxLayout()
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.input_feedback)

        # Buttons to take action
        buttons = QDialogButtonBox.Save | QDialogButtonBox.Cancel
        btn_box = QDialogButtonBox(buttons)
        btn_box.accepted.connect(self.createCompetition)
        btn_box.rejected.connect(self.reject)

        # Set layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(btn_box)
        self.setLayout(main_layout)

        self.exec()

    def createCompetition(self):
        name = self.name_input.text()
        if self.nameIsOkay(name):
            self.addCompetitionCallback(name)
            self.accept()

    def nameIsOkay(self, name):
        name = str(name)

        if not len(name):
            self.input_feedback.setText("Too short")
            return False

        if len(name) > 20:
            self.input_feedback.setText("Max 20 characters")
            return False

        return True


class CompetitionUI(QWidget):
    def __init__(self, competition_db, showCompetitionsList, openTrackingUI):
        super().__init__()

        self.competition_db = competition_db
        self.showCompetitionsList = showCompetitionsList
        self.openTrackingUI = openTrackingUI

        self.competition_name = None
        self.competition_id = None

        self.prepareUI()

    def openCompetition(self, competition_name, competition_id):
        self.competition_name = competition_name
        self.competition_id = competition_id

        self.page_title.setText(self.competition_name)

    def prepareUI(self):
        self.generateHeader()
        self.generateCompetitionControlUI()
        self.generateLayout()

    def generateHeader(self):
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.showCompetitionsList)
        self.page_title = QLabel(self.competition_name)

        self.header = QHBoxLayout()
        self.header.addWidget(back_btn)
        self.header.addWidget(self.page_title)

    def generateCompetitionControlUI(self):
        track_robot_btn = QPushButton("Track Robot")
        track_robot_btn.clicked.connect(self.openTrackingUI)

        self.control_layout = QHBoxLayout()
        self.control_layout.addWidget(track_robot_btn)

    def generateLayout(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(main_layout)

        main_layout.addLayout(self.header)
        main_layout.addLayout(self.control_layout)

    def competitionInfo(self):
        return self.competition_name, self.competition_id


class TrackingUI(QWidget):
    def __init__(self, competition_db, openCompetitionUI):
        super().__init__()

        self.competition_db = competition_db
        self.openCompetitionUI = openCompetitionUI

        self.competition_name = None
        self.competition_id = None

        page_title = QLabel("Tracking")
        start_btn = QPushButton("Start")

        header = QHBoxLayout()
        header.addWidget(page_title)
        header.addWidget(start_btn)

        robot_name_layout = QHBoxLayout()
        robot_name_label = QLabel("Robot name")
        rename_robot_btn = QPushButton("Rename robot")
        robot_name_layout.addWidget(robot_name_label)
        robot_name_layout.addWidget(rename_robot_btn)

        lap_times_table = QTableWidget()
        lap_times_table.setColumnCount(3)
        lap_times_table.setHorizontalHeaderLabels(["#", "Time", ""])

        lap_times_table.setItem(0, 0, QTableWidgetItem("1"))
        lap_times_table.setItem(0, 1, QTableWidgetItem("01:01"))
        lap_times_table.setItem(0, 2, QTableWidgetItem("Delete"))

        save_btn = QPushButton("Save results")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(
            lambda: self.openCompetitionUI(self.competition_name, self.competition_id)
        )
        footer = QHBoxLayout()
        footer.addWidget(save_btn)
        footer.addWidget(cancel_btn)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addLayout(robot_name_layout)
        layout.addWidget(lap_times_table)
        layout.addLayout(footer)
        self.setLayout(layout)

    def setCompetitionInfo(self, data):
        self.competition_name, self.competition_id = data
