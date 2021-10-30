from PySide6 import QtWidgets
from PySide6 import QtCore

import random  # for testing!

from .myWidgets import Page, PageTitle, Button, SectionTitle, InputDialog, formatTime
from serialData import SerialDataHandler
from robotNames import *

ENTRY_ID_COL_INDEX = 3

class TrackingUI(Page):
    def __init__(self, competition_db, openCompetitionUI, serial_data_handler):
        super().__init__()

        self.competition_db = competition_db
        self.openCompetitionUI = openCompetitionUI

        self.competition_name = None
        self.competition_id = None
        self.tracking_model = TrackingModel()

        self.robot_name = "None"

        self.generateLayout()

        self.setupSerialDataHandler(serial_data_handler)

    def setupSerialDataHandler(self, serial_data_handler):
        self.serial_data_handler = serial_data_handler
        self.serial_data_handler.addCallbacks(
            self.tracking_model.addTime, self.renameRobot
        )

    def generateHeader(self):
        page_title = PageTitle("Tracking")

        test_btn = QtWidgets.QPushButton("Add Laps")
        test_btn.clicked.connect(self.addDummyData)

        back_btn = Button("Back", class_tag="red_btn")
        back_btn.clicked.connect(
            lambda: self.openCompetitionUI(self.competition_name, self.competition_id)
        )
        back_btn.clicked.connect(lambda: self.serial_data_handler.sendData("stop_tr"))

        back_btn_layout = QtWidgets.QVBoxLayout()
        back_btn_layout.setAlignment(QtCore.Qt.AlignLeft)
        back_btn_layout.addWidget(back_btn)

        self.header = QtWidgets.QVBoxLayout()
        self.header.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.header.addLayout(back_btn_layout)
        self.header.addWidget(page_title)
        # self.header.addWidget(test_btn) # enable for testing

    def renameRobot(self, id):  # gets tag id as input e.g. 'B83C5E'
        self.robot_name = getName(id)  # gets name from tag id

    def addDummyData(self):
        self.robot_name = (random.choice(list(id_to_name.values())))  # random robot name
        self.tracking_model.addTime(random.randrange(30000, 300000), self.robot_name) # rand lap time & name to function

    def deleteSelectedTimes(self):
        selected_cells = self.tracking_view.selectedIndexes()

        for i, cell in enumerate(selected_cells):
            if i % ENTRY_ID_COL_INDEX == 0:  # "- 1" because counting starts from 0
                # selectedIndexes gives all selected cells. If user clicks on a row then all row cells are automatically selected. Program only needs to use 1 cell, so "discard" every other cell

                tracking_row_index = cell.row()
                self.tracking_model.removeTime(tracking_row_index)

        self.tracking_model.updateTable()

    def saveData(self):
        lap_times = self.tracking_model.lap_times

        if len(lap_times):
            for entry in lap_times:
                for robot_name, lap_time in entry.items():
                    if not self.competition_db.addRobotLapTimes(self.competition_id, robot_name, lap_time):
                        QtWidgets.QMessageBox.critical(self, "Database Error", "Lap times couldn't be saved!")
            self.serial_data_handler.sendData("stop_tr")
            self.openCompetitionUI(self.competition_name, self.competition_id)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "No lap times to save!")

    def setTableViewConfiguration(self):
        self.tracking_view.setCornerButtonEnabled(False)
        self.tracking_view.setShowGrid(False)
        self.tracking_view.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignLeft
        )
        self.tracking_view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Fixed
        )  # Cant resize columns

        self.tracking_view.clearSelection()
        self.tracking_view.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.tracking_view.setSelectionMode(QtWidgets.QTableView.SingleSelection)

        self.tracking_view.setColumnHidden(ENTRY_ID_COL_INDEX, True)  # Hide entry ID
        self.tracking_view.resizeColumnsToContents()
    
    def generateLapTimesList(self):
        list_title = SectionTitle("Lap Times")

        restart_lap_btn = Button("Restart Lap", id_tag="RestartLapBtn")
        restart_lap_btn.clicked.connect(
            lambda: self.serial_data_handler.sendData("reset_lap")
        )
        restart_lap_layout = QtWidgets.QHBoxLayout()
        restart_lap_layout.addWidget(restart_lap_btn)
        restart_lap_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.tracking_view = QtWidgets.QTableView()
        self.tracking_view.setObjectName("TrackingLapTimesView")
        self.tracking_view.setModel(self.tracking_model)

        delete_time_btn = Button(
            "Delete Time", id_tag="DeleteLapTimeBtn", class_tag="red_btn"
        )
        delete_time_btn.clicked.connect(self.deleteSelectedTimes)

        save_btn = Button("Save", class_tag="green_btn", id_tag="SaveLapTimesBtn")
        save_btn.clicked.connect(self.saveData)

        save_btn_layout = QtWidgets.QHBoxLayout()
        save_btn_layout.setAlignment(QtCore.Qt.AlignRight)
        save_btn_layout.addWidget(save_btn)

        self.tracking = QtWidgets.QVBoxLayout()
        self.tracking.addWidget(list_title)
        self.tracking.addLayout(restart_lap_layout)
        self.tracking.addWidget(self.tracking_view)
        self.tracking.addWidget(delete_time_btn)
        self.tracking.addLayout(save_btn_layout)

    def generateLayout(self):
        self.generateHeader()
        self.generateLapTimesList()

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addLayout(self.header)
        main_layout.addLayout(self.tracking)
        self.setTableViewConfiguration()

    def openTracking(self, data):
        self.competition_name, self.competition_id = data

        # Removes previously held data
        self.tracking_model.lap_times = []  # Clear
        self.tracking_model.table = []

        # Send reset signal to PC module
        # Check if PC radio module is connected
        if not self.serial_data_handler.sendData("start_tr"):
            QtWidgets.QMessageBox.critical(
                self, "Error", "Connect PC radio module into USB port!"
            )

            # Go back because tracking is useless without radio module
            self.openCompetitionUI(self.competition_name, self.competition_id)

class TrackingModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.table = [[]]  # 2D array
        self.lap_times = []
        
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            return self.table[index.row()][index.column()]
                
    def addTime(self, time, robot_name):
        new_time = {robot_name: time}
        self.lap_times.append(new_time)
        self.updateTable()
        self.layoutChanged.emit()

    def removeTime(self, time_index):
        del self.lap_times[time_index]
        self.updateTable()
        self.layoutChanged.emit()
        
    def rowCount(self, index):
        # Num of rows in this 2D array
        return len(self.table)

    def columnCount(self, index):
        # Num of columns in first row (all rows have same length)
        return len(self.table[0])
            
    def updateTable(self):
        self.table = []
        
        if self.lap_times:
            for index, entry in enumerate(self.lap_times):
                for robot_name, lap_time in entry.items():
                    self.table.append(
                        [
                            index + 1,
                            robot_name,
                            formatTime(lap_time),
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
                    return "Name"
                if section == 2:
                    return "Time"

            if orientation == QtCore.Qt.Vertical:
                return ""  # None
