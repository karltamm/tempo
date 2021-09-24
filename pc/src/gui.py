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
)
from PySide6.QtCore import Qt, QAbstractListModel, QAbstractTableModel

from database import CompetitionDB
from tracking import Tracking

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
        menu_options.setAlignment(Qt.AlignLeft)
        menu_options.addWidget(competition_btn)

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
        main_layout.setAlignment(Qt.AlignTop)
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


class InputDialog(QDialog):
    def __init__(self, input_label, parent=None, callback=None):
        super().__init__(parent)

        self.callback = callback or (lambda x: None)

        input_label = QLabel(input_label)
        self.input = QLineEdit()
        self.input.textChanged.connect(self.validateInput)
        self.input_feedback = QLabel()

        buttons = QDialogButtonBox.Save | QDialogButtonBox.Cancel
        btn_box = QDialogButtonBox(buttons)
        btn_box.accepted.connect(self.save)
        btn_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(input_label)
        layout.addWidget(self.input)
        layout.addWidget(self.input_feedback)
        layout.addWidget(btn_box)
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

        return True


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

        self.leaderboard_model.initData(competition_id)
        self.setTableViewDefault()

    def prepareUI(self):
        self.generateHeader()
        self.generateCompetitionControlUI()
        self.showLeaderboard()
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
        main_layout.addLayout(self.leaderboard_layout)

    def competitionInfo(self):
        return self.competition_name, self.competition_id

    def setTableViewDefault(self):
        self.leaderboard_view.clearSelection()
        self.leaderboard_view.setColumnHidden(2, True)  # Hide entry ID
        self.leaderboard_view.setSelectionBehavior(QTableView.SelectRows)

    def showLeaderboard(self):
        delete_lap_time_btn = QPushButton("Delete Time")
        delete_lap_time_btn.clicked.connect(self.deleteEntry)

        self.leaderboard_model = LeaderboardTableModel(self.competition_db)
        self.leaderboard_model.updateTable()

        self.leaderboard_view = QTableView()
        self.leaderboard_view.setModel(self.leaderboard_model)
        self.setTableViewDefault()

        self.leaderboard_layout = QVBoxLayout()
        self.leaderboard_layout.addWidget(self.leaderboard_view)
        self.leaderboard_layout.addWidget(delete_lap_time_btn)

    def deleteEntry(self):
        selected = self.leaderboard_view.selectedIndexes()
        if selected:
            entry_index = selected[0].row()
            self.leaderboard_model.removeEntry(entry_index)
            self.setTableViewDefault()


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
        entry_id = self.table[entry_index][2]  # ID is in the 3rd col
        self.competition_db.deleteRobotLapTime(entry_id)
        self.updateTable()

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
            for entry in data:
                self.table.append(
                    [entry["robot_name"], entry["lap_time"], entry["entry_id"]]
                )  # Add new row thats has column about entry data
        else:
            self.table.append([])  # Add at least one row with column, otherwise error

        self.layoutChanged.emit()  # Notify table view about data change

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    return "Robot"
                elif section == 1:
                    return "Lap Time"

            if orientation == Qt.Vertical:
                return ""  # None


class TrackingUI(QWidget):
    def __init__(self, competition_db, openCompetitionUI):
        super().__init__()

        self.competition_db = competition_db
        self.openCompetitionUI = openCompetitionUI

        self.competition_name = None
        self.competition_id = None
        self.lap_times_list_model = LapTimesListModel()

        self.setupLayout()

        self.number = 0

    def generateHeader(self):
        page_title = QLabel("Tracking")

        test_btn = QPushButton("Test")
        test_btn.clicked.connect(self.addDummyData)

        self.header = QHBoxLayout()
        self.header.addWidget(page_title)
        self.header.addWidget(test_btn)

    def generateRobotNameSection(self):
        robot_name_label = QLabel("Robot name")

        self.robot_name = QLabel("Robot")
        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.openRenameDialog)

        rename_layout = QHBoxLayout()
        rename_layout.addWidget(self.robot_name)
        rename_layout.addWidget(rename_btn)

        self.robot_name_layout = QVBoxLayout()
        self.robot_name_layout.addWidget(robot_name_label)
        self.robot_name_layout.addLayout(rename_layout)

    def openRenameDialog(self):
        InputDialog("Rename Robot", self, self.renameRobot)

    def renameRobot(self, name):
        self.robot_name.setText(name)

    def addDummyData(self):

        self.lap_times_list_model.addTime(self.number)
        self.number += 1

    def deleteSelectedTimes(self):
        all_selected = self.lap_times_list_view.selectedIndexes()
        for time in all_selected:
            self.lap_times_list_model.removeTime(time.row())
            self.lap_times_list_view.clearSelection()

    def saveData(self):
        robot_name = self.robot_name.text() or "Robot"
        lap_times = self.lap_times_list_model.lap_times

        self.competition_db.addRobotLapTimes(self.competition_id, robot_name, lap_times)

        self.openCompetitionUI(self.competition_name, self.competition_id)

    def generateLapTimesList(self):
        list_title = QLabel("Lap times")

        self.lap_times_list_view = QListView()
        self.lap_times_list_view.setModel(self.lap_times_list_model)

        delete_time_btn = QPushButton("Delete Time")
        delete_time_btn.clicked.connect(self.deleteSelectedTimes)

        self.lap_times_list = QVBoxLayout()
        self.lap_times_list.addWidget(list_title)
        self.lap_times_list.addWidget(self.lap_times_list_view)
        self.lap_times_list.addWidget(delete_time_btn)

    def generateEndTrackingUI(self):
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.saveData)

        cancel_btn = QPushButton("Discard")
        cancel_btn.clicked.connect(
            lambda: self.openCompetitionUI(self.competition_name, self.competition_id)
        )

        self.end_tracking_layout = QHBoxLayout()
        self.end_tracking_layout.addWidget(save_btn)
        self.end_tracking_layout.addWidget(cancel_btn)

    def setupLayout(self):
        self.generateHeader()
        self.generateRobotNameSection()
        self.generateLapTimesList()
        self.generateEndTrackingUI()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addLayout(self.header)
        main_layout.addLayout(self.robot_name_layout)
        main_layout.addLayout(self.lap_times_list)
        main_layout.addLayout(self.end_tracking_layout)

    def openTracking(self, data):
        self.competition_name, self.competition_id = data

        # Removes previously held data
        self.lap_times_list_model.lap_times = []  # Clear
        self.robot_name.setText("Robot")


class LapTimesListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()

        self.lap_times = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.lap_times[index.row()]

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
window = MainWindow()
app.exec()
