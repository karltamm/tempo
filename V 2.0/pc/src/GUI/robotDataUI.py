from PySide6 import QtWidgets
from PySide6 import QtCore

from .myWidgets import Page, Button, PageTitle, SectionTitle, formatTime

NUM_OF_ENTRY_COLS = 4
ENTRY_ID_COL_INDEX = NUM_OF_ENTRY_COLS - 1


class RobotDataUI(Page):
    def __init__(self, competition_db, openCompetitionUI) -> None:
        super().__init__()

        self.competition_db = competition_db
        self.openCompetitionUI = openCompetitionUI

        self.prepareUI()

    def openRobotData(self, robot_name, competion_id):
        self.page_title.setText(robot_name)
        self.entries_model.initData(robot_name, competion_id)
        self.setTableViewConfiguration()

    def prepareUI(self):
        self.generateHeader()
        self.generateEntriesList()
        self.generateLayout()

    def generateHeader(self):
        back_btn = Button("Back", id_tag="BackBtn", class_tag="red_btn")
        back_btn.clicked.connect(self.openCompetitionUI)

        back_btn_layout = QtWidgets.QVBoxLayout()
        back_btn_layout.addWidget(back_btn)
        back_btn_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.page_title = PageTitle("")

        self.header = QtWidgets.QVBoxLayout()
        self.header.addLayout(back_btn_layout)
        self.header.addWidget(self.page_title)
        self.header.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

    def generateLayout(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(main_layout)

        main_layout.addLayout(self.header)
        main_layout.addLayout(self.entries_layout)

    def setTableViewConfiguration(self):
        self.entries_view.setCornerButtonEnabled(False)
        self.entries_view.setShowGrid(False)
        self.entries_view.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.entries_view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Fixed
        )  # Cant resize columns
        self.entries_view.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.entries_view.setColumnHidden(ENTRY_ID_COL_INDEX, True)  # Hide entry ID
        self.entries_view.resizeColumnsToContents()

    def generateEntriesList(self):
        delete_entry_btn = Button(
            "Delete Time", id_tag="DeleteEntryBtn", class_tag="red_btn"
        )
        delete_entry_btn.clicked.connect(self.deleteEntry)

        self.entries_model = EntriesModel(self.competition_db, self)
        self.entries_view = QtWidgets.QTableView()
        self.entries_view.setModel(self.entries_model)

        self.entries_layout = QtWidgets.QVBoxLayout()
        self.entries_layout.addWidget(SectionTitle("Lap Times"))
        self.entries_layout.addWidget(self.entries_view)
        self.entries_layout.addWidget(delete_entry_btn)

    def deleteEntry(self):
        selected_cells = self.entries_view.selectedIndexes()

        for i, cell in enumerate(selected_cells):
            if i % (NUM_OF_ENTRY_COLS - 1) == 0:  # "- 1" because counting starts from 0
                # selectedIndexes gives all selected cells. If user clicks on a row then all row cells are automatically selected. Program only needs to use 1 cell, so "discard" every other cell

                entry_row_index = cell.row()
                self.entries_model.removeEntry(entry_row_index)

        self.entries_model.updateTable()
        self.setTableViewConfiguration()


class EntriesModel(QtCore.QAbstractTableModel):
    def __init__(self, competition_db, parent):
        super().__init__()
        self.competition_db = competition_db
        self.parent_widget = parent

        self.table = [[]]  # 2D array

        self.competition_id = None
        self.robot_name = None

    def initData(self, robot_name, competition_id):
        self.robot_name = robot_name
        self.competition_id = competition_id
        self.updateTable()

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.table[index.row()][index.column()]

    def removeEntry(self, entry_index):
        entry_id = self.table[entry_index][ENTRY_ID_COL_INDEX]
        if not self.competition_db.deleteRobotLapTime(entry_id):
            QtWidgets.QMessageBox.critical(
                self.parent_widget, "Database Error", "Entry couldn't be deleted!"
            )

    def rowCount(self, index):
        # Num of rows in this 2D array
        return len(self.table)

    def columnCount(self, index):
        # Num of columns in first row (all rows have same length)
        return len(self.table[0])

    def updateTable(self):
        self.table = []  # Clear old data
        data = self.competition_db.getRobotEntries(self.robot_name, self.competition_id)

        if data:
            for placement, entry in enumerate(data):
                # Add new row
                self.table.append(
                    [
                        placement + 1,  # + 1 because counting starts from 0
                        formatTime(entry["lap_time"]),
                        entry["date"],
                        entry["entry_id"],
                    ]
                )
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
                    return "Time"
                if section == 2:
                    return "Date"

            if orientation == QtCore.Qt.Vertical:
                return ""  # None
