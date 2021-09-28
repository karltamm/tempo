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
    QMessageBox,
    QListView,
    QTableView,
    QApplication,
    QHeaderView,
    QStyleOption,
    QStyle,
    QScrollArea,
    QStyleFactory,
    QAbstractButton,
)
from PySide6.QtCore import Qt, QAbstractListModel, QAbstractTableModel
from PySide6.QtGui import QPainter, QCursor
import random

from database import CompetitionDB
from tracking import Tracking

APP_WIDTH = 500
APP_HEIGHT = 700

ENTRY_ID_COL_I = 3


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

        with open("style.css", "r") as f:
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
        self.cur_page = QStackedWidget()
        self.cur_page.addWidget(self.main_menu)  # opened by default
        self.cur_page.addWidget(self.competitions_manager)
        self.setCentralWidget(self.cur_page)

    def openCompetionsManager(self):
        self.cur_page.setCurrentWidget(self.competitions_manager)
        self.competitions_manager.openCompetitionsList()

    def openMainMenu(self):
        self.cur_page.setCurrentWidget(self.main_menu)


class MyWidget(QWidget):
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
        opt = QStyleOption()
        opt.initFrom(self)

        painter = QPainter(self)

        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)


class SectionTitle(QLabel):
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


class Button(QPushButton):
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
        self.setCursor(QCursor(Qt.PointingHandCursor))


class PageTitle(QLabel):
    def __init__(self, text, id_tag="", class_tag="", parent=None):
        super().__init__(text, parent)

        # Set object name to easily identify widgets in stylesheet
        # self.__class__.__name__ gives Python class name
        class_name = self.__class__.__name__
        self.setObjectName(id_tag or class_name)

        self.setContentsMargins(0, 20, 0, 10)


class MainMenu(Page):
    def __init__(self, openCompetionsManager):
        super().__init__()

        # Header
        title = QLabel("Tempo")
        title.setObjectName("AppTitle")

        subtitle = QLabel("Lap time tracker")
        subtitle.setObjectName("AppSubtitle")

        header = QVBoxLayout()
        header.addWidget(title)
        header.addWidget(subtitle)

        # Menu options

        competition_btn = Button("Competitions", "OpenCompetitions")
        competition_btn.clicked.connect(openCompetionsManager)

        exit_btn = Button("Exit", "ExitApp", class_tag="red_btn")
        exit_btn.clicked.connect(QApplication.instance().quit)

        menu_options = QVBoxLayout()
        menu_options.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        menu_options.addWidget(competition_btn)
        menu_options.addWidget(exit_btn)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
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
        self.tracking_UI.openTracking(self.competition_UI.competitionInfo())


class CompetitionsList(Page):
    def __init__(self, competition_db, openMainMenu, openCompetitionUI):
        super().__init__()

        self.competition_db = competition_db
        self.openCompetitionUI = openCompetitionUI
        self.openMainMenu = openMainMenu

        self.generateUI()

    def generateUI(self):
        self.generateHeader()
        self.generateListSection()
        self.generateMainLayout()

    def generateHeader(self):
        back_btn = Button("Back", id_tag="BackBtn", class_tag="red_btn")
        back_btn.clicked.connect(self.openMainMenu)

        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignLeft)
        button_layout.addWidget(back_btn)

        page_title = PageTitle("Competitions")

        self.header = QVBoxLayout()
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.header.addLayout(button_layout)
        self.header.addWidget(page_title)

    def generateListSection(self):

        add_competition_btn = Button("Add Competition", id_tag="AddCompetitionBtn")
        add_competition_btn.setProperty("class2", "green_btn")
        add_competition_btn.clicked.connect(self.openCompetitionCreator)

        button_box = QHBoxLayout()
        button_box.addWidget(add_competition_btn)
        button_box.setAlignment(Qt.AlignLeft)

        # Actual list part
        self.competitions_list = (
            QVBoxLayout()
        )  # You put competition list items into this
        self.competitions_list.setAlignment(Qt.AlignTop)

        self.competition_list_widget = MyWidget(
            id_tag="CompetitionList"
        )  # This is needed to use scroll area. "competitions_list" layout is put into this widget

        self.competitions_list_scroll = QScrollArea()
        self.competitions_list_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.competitions_list_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        self.competitions_list_scroll.setWidgetResizable(True)
        self.competitions_list_scroll.setWidget(self.competition_list_widget)

        self.list_section = QVBoxLayout()
        self.list_section.setAlignment(Qt.AlignTop)
        self.list_section.addLayout(button_box)
        self.list_section.addWidget(self.competitions_list_scroll)

    def generateMainLayout(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(main_layout)

        main_layout.addLayout(self.header)
        main_layout.addLayout(self.list_section)

    def getList(self):
        data = self.competition_db.getListOfCompetitions()

        if data != None:
            # Reset list
            clearLayout(self.competitions_list)

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
            # for i in range(300):
            #     self.competitions_list.addWidget(
            #         CompetitionListItem(
            #             "Test " + str(i),
            #             1,
            #             self.openCompetitionUI,
            #             self.deleteCompetition,
            #         )
            #     )

            # Add list to view
            self.competition_list_widget.setLayout(self.competitions_list)
        else:
            QMessageBox.critical(
                self, "Database Error", "List of competitions could not be retrived!"
            )

    def openCompetitionCreator(self):
        InputDialog("Competition Name", self, self.addCompetition)

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
        name_layout = QHBoxLayout()
        name_layout.addWidget(name)
        name_layout.setAlignment(Qt.AlignLeft)

        open_btn = Button("Open")
        open_btn.clicked.connect(
            lambda: openCompetitionUI(competition_name, competition_ID)
        )
        delete_btn = Button("Delete", class_tag="red_btn")
        delete_btn.clicked.connect(lambda: deleteCompetition(competition_ID))

        button_layout = QHBoxLayout()
        button_layout.addWidget(open_btn)
        button_layout.addWidget(delete_btn)
        button_layout.setAlignment(Qt.AlignRight)

        layout = QHBoxLayout()
        layout.addLayout(name_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)


class InputDialog(QDialog):
    def __init__(self, input_label, parent=None, callback=None):
        super().__init__(parent)

        self.callback = callback or (lambda x: None)

        self.setWindowTitle(input_label)

        input_label = QLabel(input_label)
        input_label.setProperty("class", "input_label")

        self.input = QLineEdit()
        self.input.textChanged.connect(self.validateInput)

        self.input_feedback = QLabel()
        self.input_feedback.setProperty("class", "input_feedback")

        save_btn = Button("Save", class_tag="green_btn")
        save_btn.clicked.connect(self.save)

        cancel_btn = Button("Cancel", class_tag="red_btn")
        cancel_btn.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        buttons.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        layout = QVBoxLayout()
        layout.addWidget(input_label)
        layout.addWidget(self.input)
        layout.addWidget(self.input_feedback)
        layout.addLayout(buttons)
        self.setLayout(layout)

        self.exec()

    def save(self):
        input_val = self.input.text()
        if self.validateInput(input_val):
            self.callback(input_val)
            self.accept()

    def validateInput(self, value):
        if not value:
            self.input_feedback.setText("Too short")
            return False

        if len(value) > 20:
            self.input_feedback.setText("Max 20 chars")
            return False

        # Everything okay
        self.input_feedback.setText("")  # Remove previously set error
        return True


class CompetitionUI(Page):
    def __init__(self, competition_db, showCompetitionsList, openTrackingUI):
        super().__init__()

        self.competition_db = competition_db
        self.showCompetitionsList = showCompetitionsList
        self.openTrackingUI = openTrackingUI

        self.competition_name = ""
        self.competition_id = None

        self.prepareUI()

    def openCompetition(self, competition_name, competition_id):
        self.competition_name = competition_name
        self.competition_id = competition_id

        self.page_title.setText(self.competition_name)

        self.leaderboard_model.initData(competition_id)
        self.setTableViewConfiguration()

    def prepareUI(self):
        self.generateHeader()
        self.generateTrackingButton()
        self.generateLeaderboard()
        self.generateLayout()

    def generateHeader(self):
        back_btn = Button("Back", id_tag="BackBtn", class_tag="red_btn")
        back_btn.clicked.connect(self.showCompetitionsList)

        back_btn_layout = QVBoxLayout()
        back_btn_layout.addWidget(back_btn)
        back_btn_layout.setAlignment(Qt.AlignLeft)

        self.page_title = PageTitle(self.competition_name)

        self.header = QVBoxLayout()
        self.header.addLayout(back_btn_layout)
        self.header.addWidget(self.page_title)
        self.header.setAlignment(Qt.AlignTop | Qt.AlignLeft)

    def generateTrackingButton(self):
        track_robot_btn = Button(
            "Track Robot", id_tag="TrackRobotBtn", class_tag="green_btn"
        )
        track_robot_btn.clicked.connect(self.openTrackingUI)

        self.control_layout = QHBoxLayout()
        self.control_layout.addWidget(track_robot_btn)
        self.control_layout.setAlignment(Qt.AlignLeft)

    def generateLayout(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(main_layout)

        main_layout.addLayout(self.header)
        main_layout.addLayout(self.control_layout)
        main_layout.addLayout(self.leaderboard_layout)

    def competitionInfo(self):
        # If competition page is opened, this info is necessary to work with database
        return self.competition_name, self.competition_id

    def setTableViewConfiguration(self):
        # After competition page is (re)opened, make sure that table is displayed nicely

        self.leaderboard_view.horizontalHeader().setSectionResizeMode(
            QHeaderView.Fixed
        )  # Cant resize columns

        self.leaderboard_view.clearSelection()
        self.leaderboard_view.setSelectionBehavior(QTableView.SelectRows)
        # self.leaderboard_view.setSelectionMode(QTableView.SingleSelection)

        self.leaderboard_view.setColumnHidden(ENTRY_ID_COL_I, True)  # Hide entry ID

        self.leaderboard_view.resizeColumnsToContents()

    def generateLeaderboard(self):
        delete_lap_time_btn = Button(
            "Delete Time", id_tag="DeleteEntryBtn", class_tag="red_btn"
        )
        delete_lap_time_btn.clicked.connect(self.deleteEntry)

        leaderboard_title = SectionTitle("Leaderboard")

        self.leaderboard_model = LeaderboardTableModel(self.competition_db)
        self.leaderboard_model.updateTable()

        self.leaderboard_view = QTableView()
        self.leaderboard_view.setCornerButtonEnabled(False)
        self.leaderboard_view.setShowGrid(False)
        self.leaderboard_view.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        self.leaderboard_view.setObjectName("LeaderboardView")
        self.leaderboard_view.setModel(self.leaderboard_model)
        self.setTableViewConfiguration()

        self.leaderboard_layout = QVBoxLayout()
        self.leaderboard_layout.addWidget(leaderboard_title)
        self.leaderboard_layout.addWidget(self.leaderboard_view)
        self.leaderboard_layout.addWidget(delete_lap_time_btn)

    def deleteEntry(self):
        selected_cells = self.leaderboard_view.selectedIndexes()

        for i, cell in enumerate(selected_cells):
            if i % 2 == 0:
                # selectedIndexes gives all selected cells. Every row has 2 cells. If user clicks on a row then both cells are automatically selected. Program only needs to use 1 cell, so "discard" every other cell

                entry_row_index = cell.row()
                self.leaderboard_model.removeEntry(entry_row_index)

        self.leaderboard_model.updateTable()
        self.setTableViewConfiguration()


class LeaderboardTableModel(QAbstractTableModel):
    def __init__(self, competition_db):
        super().__init__()
        self.table = []  # 2D array
        self.competition_db = competition_db
        self.competition_id = None

    def initData(self, id):
        self.competition_id = id
        self.updateTable()

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.table[index.row()][index.column()]

    def removeEntry(self, entry_index):
        entry_id = self.table[entry_index][ENTRY_ID_COL_I]
        self.competition_db.deleteRobotLapTime(entry_id)

    def rowCount(self, index):
        # Num of rows in this 2D array
        return len(self.table)

    def columnCount(self, index):
        # Num of columns in first row (all rows have same length)
        return len(self.table[0])

    def updateTable(self):
        self.table = []  # Clear old data
        data = self.competition_db.getCompetitionLeaderboard(self.competition_id)

        if data:
            for placement, entry in enumerate(data):
                self.table.append(
                    [
                        placement + 1,  # + 1 because counting starts from 0
                        entry["robot_name"],
                        formatTime(entry["lap_time"]),
                        entry["entry_id"],
                    ]
                )  # Add new row thats has column about entry data
        else:
            self.table.append([])  # Add at least one row with column, otherwise error

        self.layoutChanged.emit()  # Notify table view about data change

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "#"
                if section == 1:
                    return "Name"
                if section == 2:
                    return "Lap Time"

            if orientation == Qt.Vertical:
                return ""  # None


class TrackingUI(Page):
    def __init__(self, competition_db, openCompetitionUI):
        super().__init__()

        self.competition_db = competition_db
        self.openCompetitionUI = openCompetitionUI

        self.competition_name = None
        self.competition_id = None
        self.lap_times_list_model = LapTimesListModel()

        self.robot_default_name = "None"

        self.generateLayout()

        self.number = 0

    def generateHeader(self):
        page_title = PageTitle("Tracking")

        test_btn = QPushButton("Add Laps")
        test_btn.clicked.connect(self.addDummyData)

        back_btn = Button("Back", class_tag="red_btn")
        back_btn.clicked.connect(
            lambda: self.openCompetitionUI(self.competition_name, self.competition_id)
        )

        back_btn_layout = QVBoxLayout()
        back_btn_layout.setAlignment(Qt.AlignLeft)
        back_btn_layout.addWidget(back_btn)

        self.header = QVBoxLayout()
        self.header.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.header.addLayout(back_btn_layout)
        self.header.addWidget(page_title)
        self.header.addWidget(test_btn)

    def generateRobotNameSection(self):
        robot_name_label = SectionTitle("Robot Name")

        self.robot_name = QLabel(self.robot_default_name)
        self.robot_name.setObjectName("RobotName")
        rename_btn = Button("Rename", id_tag="RobotRenameBtn")
        rename_btn.clicked.connect(self.openRenameDialog)

        rename_layout = QHBoxLayout()
        rename_layout.addWidget(self.robot_name)
        rename_layout.addWidget(rename_btn)
        rename_layout.setAlignment(Qt.AlignLeft)

        self.robot_name_layout = QVBoxLayout()
        self.robot_name_layout.addWidget(robot_name_label)
        self.robot_name_layout.addLayout(rename_layout)

    def openRenameDialog(self):
        InputDialog("Rename Robot", self, self.renameRobot)

    def renameRobot(self, name):
        self.robot_name.setText(name)

    def addDummyData(self):

        self.lap_times_list_model.addTime(random.randrange(30000, 300000))
        self.number += 1

    def deleteSelectedTimes(self):
        all_selected = self.lap_times_list_view.selectedIndexes()
        for time in all_selected:
            self.lap_times_list_model.removeTime(time.row())
            self.lap_times_list_view.clearSelection()

    def saveData(self):
        robot_name = self.robot_name.text()
        lap_times = self.lap_times_list_model.lap_times

        if len(lap_times):
            self.competition_db.addRobotLapTimes(
                self.competition_id, robot_name, lap_times
            )
            self.openCompetitionUI(self.competition_name, self.competition_id)
        else:
            QMessageBox.critical(self, "Error", "No lap times to save!")

    def generateLapTimesList(self):
        list_title = SectionTitle("Lap Times")

        self.lap_times_list_view = QListView()
        self.lap_times_list_view.setObjectName("TrackingLapTimesView")
        self.lap_times_list_view.setModel(self.lap_times_list_model)

        delete_time_btn = Button(
            "Delete Time", id_tag="DeleteLapTimeBtn", class_tag="red_btn"
        )
        delete_time_btn.clicked.connect(self.deleteSelectedTimes)

        save_btn = Button("Save", class_tag="green_btn", id_tag="SaveLapTimesBtn")
        save_btn.clicked.connect(self.saveData)

        save_btn_layout = QHBoxLayout()
        save_btn_layout.setAlignment(Qt.AlignRight)
        save_btn_layout.addWidget(save_btn)

        self.lap_times_list = QVBoxLayout()
        self.lap_times_list.addWidget(list_title)
        self.lap_times_list.addWidget(self.lap_times_list_view)
        self.lap_times_list.addWidget(delete_time_btn)
        self.lap_times_list.addLayout(save_btn_layout)

    def generateLayout(self):
        self.generateHeader()
        self.generateRobotNameSection()
        self.generateLapTimesList()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addLayout(self.header)
        main_layout.addLayout(self.robot_name_layout)
        main_layout.addLayout(self.lap_times_list)

    def openTracking(self, data):
        self.competition_name, self.competition_id = data

        # Removes previously held data
        self.lap_times_list_model.lap_times = []  # Clear
        self.robot_name.setText(self.robot_default_name)


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


class LapTimesListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()

        self.lap_times = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return formatTime(self.lap_times[index.row()])

    def rowCount(self, index):
        return len(self.lap_times)

    def addTime(self, time):
        self.lap_times.append(time)
        self.layoutChanged.emit()

    def removeTime(self, time_index):
        del self.lap_times[time_index]
        self.layoutChanged.emit()


# Test
import os
import sys

# Make sure that this file runs in its folder!
file_dir_path = os.path.dirname(sys.argv[0])  # sys.argv[0] == current file path
os.chdir(file_dir_path)

# Test
app = QApplication()
app.setStyle(QStyleFactory.create("fusion"))
window = MainWindow()
app.exec()
