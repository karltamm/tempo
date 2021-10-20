from PySide6 import QtWidgets
from PySide6 import QtCore

from .myWidgets import Page, Button, PageTitle, SectionTitle, formatTime

ENTRY_ID_COL_INDEX = 4


class CompetitionUI(Page):
    def __init__(
        self, competition_db, showCompetitionsList, openTrackingUI, openRobotDataUI
    ):
        super().__init__()

        self.competition_db = competition_db
        self.showCompetitionsList = showCompetitionsList
        self.openTrackingUI = openTrackingUI
        self.openRobotDataUI = openRobotDataUI

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

        back_btn_layout = QtWidgets.QVBoxLayout()
        back_btn_layout.addWidget(back_btn)
        back_btn_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.page_title = PageTitle(self.competition_name)

        self.header = QtWidgets.QVBoxLayout()
        self.header.addLayout(back_btn_layout)
        self.header.addWidget(self.page_title)
        self.header.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

    def generateTrackingButton(self):
        track_robot_btn = Button(
            "Track Robot", id_tag="TrackRobotBtn", class_tag="green_btn"
        )
        track_robot_btn.clicked.connect(self.openTrackingUI)

        self.control_layout = QtWidgets.QHBoxLayout()
        self.control_layout.addWidget(track_robot_btn)
        self.control_layout.setAlignment(QtCore.Qt.AlignLeft)

    def generateLayout(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(main_layout)

        main_layout.addLayout(self.header)
        main_layout.addLayout(self.control_layout)
        main_layout.addLayout(self.leaderboard_layout)

    def competitionInfo(self):
        # If competition page is opened, this info is necessary to work with database
        return self.competition_name, self.competition_id

    def setTableViewConfiguration(self):
        self.leaderboard_view.setCornerButtonEnabled(False)
        self.leaderboard_view.setShowGrid(False)
        self.leaderboard_view.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignLeft
        )
        self.leaderboard_view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Fixed
        )  # Cant resize columns

        self.leaderboard_view.clearSelection()
        self.leaderboard_view.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.leaderboard_view.setSelectionMode(QtWidgets.QTableView.SingleSelection)

        self.leaderboard_view.setColumnHidden(ENTRY_ID_COL_INDEX, True)  # Hide entry ID
        self.leaderboard_view.resizeColumnsToContents()

    def generateLeaderboard(self):
        open_robot_data_btn = Button("Open Robot Data", id_tag="OpenRobotDataBtn")
        open_robot_data_btn.clicked.connect(self.openRobotData)

        self.leaderboard_model = LeaderboardTableModel(self.competition_db, self)
        self.leaderboard_view = QtWidgets.QTableView()
        self.leaderboard_view.setModel(self.leaderboard_model)

        self.leaderboard_layout = QtWidgets.QVBoxLayout()
        self.leaderboard_layout.addWidget(SectionTitle("Leaderboard"))
        self.leaderboard_layout.addWidget(self.leaderboard_view)
        self.leaderboard_layout.addWidget(open_robot_data_btn)

    def openRobotData(self):
        selected_cell = self.leaderboard_view.selectedIndexes()

        if selected_cell:
            row_index = selected_cell[0].row()
            robot_name = self.leaderboard_model.getRobotNameFromRow(row_index)
            self.openRobotDataUI(robot_name, self.competition_id)


class LeaderboardTableModel(QtCore.QAbstractTableModel):
    def __init__(self, competition_db, parent):
        super().__init__()
        self.table = [[]]  # 2D array
        self.competition_db = competition_db
        self.competition_id = None
        self.parent_widget = parent

    def initData(self, id):
        self.competition_id = id
        self.updateTable()

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.table[index.row()][index.column()]

        # if index.column() == 0 and role == QtCore.Qt.TextAlignmentRole:
        #     return QtCore.Qt.AlignLeft

    def getRobotNameFromRow(self, entry_index):
        return self.table[entry_index][1]

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
                        entry["date"],
                        entry["entry_id"],
                    ]
                )  # Add new row thats has column about entry data
        else:
            self.table.append([])  # Add at least one row with column, otherwise error

        self.layoutChanged.emit()  # Notify table view about data change

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == 0:
                    return "#"
                if section == 1:
                    return "Name"
                if section == 2:
                    return "Best Lap"
                if section == 3:
                    return "Date"

            if orientation == QtCore.Qt.Vertical:
                return ""  # None
