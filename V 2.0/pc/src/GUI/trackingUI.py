from PySide6 import QtWidgets
from PySide6 import QtCore, QtGui

import random  # for testing!

from .myWidgets import Page, PageTitle, Button, SectionTitle, InputDialog, formatTime
from assets import getCheckmarkIcon
from serialData import SerialDataHandler
from robotNames import *
from timer import Timer

ENTRY_ID_COL_INDEX = 4

class TrackingUI(Page):
    def __init__(self, competition_db, openCompetitionUI, serial_data_handler, practice=False):
        super().__init__()
        self.practice = practice
        
        # self.index = 0 # for testing

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
        self.serial_data_handler.addCallbacks(self.translateID)

    def generateHeader(self):
        if not self.practice:
            page_title = PageTitle("Tracking")
        else:
            page_title = PageTitle("Practice Mode")
            

        test_btn = QtWidgets.QPushButton("Add Laps")
        test_btn.clicked.connect(self.addDummyData)

        back_btn = Button("Back", class_tag="red_btn")
        if not self.practice:
            back_btn.clicked.connect(
                lambda: self.openCompetitionUI(self.competition_name, self.competition_id)
            )
        else:
            back_btn.clicked.connect(self.openCompetitionUI) # open MainMenu
            
        back_btn.clicked.connect(lambda: self.serial_data_handler.sendData("stop_tr"))
        back_btn.clicked.connect(lambda: self.tracking_model.clearTimer())

        back_btn_layout = QtWidgets.QVBoxLayout()
        back_btn_layout.setAlignment(QtCore.Qt.AlignLeft)
        back_btn_layout.addWidget(back_btn)

        self.header = QtWidgets.QVBoxLayout()
        self.header.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.header.addLayout(back_btn_layout)
        self.header.addWidget(page_title)
        # self.header.addWidget(test_btn) # enable for testing

    def translateID(self, id, time):
        self.tracking_model.inputData(getName(id), time)  # e.g. 'B83C5E' to 'R1'
                                                    # and outputs name, time into TrackingModel

    def addDummyData(self):
        robots = [['B83C5E', 0], ['B82A56', 0], ['965FC2', 0], ['B8A72A', 0], ['B85958', 0], ['B81B6D', 0],
                  ['B83C5E', 10000], ['B82A56', 20000], ['965FC2', 30000], ['B8A72A', 40000], ['B85958', 25000], ['B81B6D', 32567]]
        self.translateID(robots[self.index][0], robots[self.index][1])
        self.index += 1
        if self.index == len(robots):
            self.index = 0

    def deleteSelectedTimes(self):
        selected_cells = self.tracking_view.selectedIndexes()

        for i, cell in enumerate(selected_cells):
            if i % ENTRY_ID_COL_INDEX == 0:  # "- 1" because counting starts from 0
                # selectedIndexes gives all selected cells. If user clicks on a row then all row cells are automatically selected. 
                # Program only needs to use 1 cell, so "discard" every other cell

                tracking_row_index = cell.row()
                self.tracking_model.removeTime(tracking_row_index)
                self.tracking_view.clearSelection() # Clear selection after deleting a table entry

        self.tracking_model.updateTable()

    def saveData(self):
        results = self.tracking_model.results_to_save

        if len(results):
            for entry in results:
                for robot_name, lap_time in entry.items():
                    if not self.competition_db.addRobotLapTimes(self.competition_id, robot_name, lap_time):
                        QtWidgets.QMessageBox.critical(self, "Database Error", "Lap times couldn't be saved!")
            self.serial_data_handler.sendData("stop_tr")
            self.tracking_model.clearTimer()
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
        # self.tracking.addLayout(restart_lap_layout)
        self.tracking.addWidget(self.tracking_view)
        self.tracking.addWidget(delete_time_btn)
        if not self.practice:
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
        self.tracking_model.results_to_table = []  # Clear
        self.tracking_model.results_to_save = []
        self.tracking_model.racing_robots = {}
        self.tracking_model.table = []

        # Send reset signal to PC module
        # Check if PC radio module is connected
        if not self.serial_data_handler.sendData("start_tr"):
            QtWidgets.QMessageBox.critical(
                self, "Error", "Connect PC radio module into USB port!"
            )

            # Go back because tracking is useless without radio module
            if not self.practice:
                self.openCompetitionUI(self.competition_name, self.competition_id)
            else:
                self.openCompetitionUI() # open main menu

class TrackingModel(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.checkmark = getCheckmarkIcon()
        
        self.table = [[]]  # 2D array
        
        self.timer_running = False # if timer tracking robots is on
        
        # all results to show in table (counting+finished)
        self.results_to_table = []  # [{name1: time, ..}]
        # only finished results
        self.results_to_save = []  # [{'name1': finish_time, ..}]
        # currently racing robots
        self.racing_robots = {}  # {'name1': [index, start_time(from arduino)] ..}
        
        self.threadpool = QtCore.QThreadPool()

    # draw to 2D array (self.table)
    def data(self, index, role):
        # decorationrole to draw checkmark
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 3:
                return self.table[index.row()][index.column()]
        # displayrole to draw text
        if role == QtCore.Qt.DisplayRole:
            return self.table[index.row()][index.column()]
    
    # Num of rows in 2D array
    def rowCount(self, index):
        return len(self.table)

    # Num of columns in first row (all rows have same length)
    def columnCount(self, index):
        return len(self.table[0])
                
    # work with robot_name detected from tag-id
    def inputData(self, robot_name, time_ms):        
        if robot_name not in self.racing_robots:    # check if robot is already racing
            
            self.results_to_table.append({robot_name: 0})  # if robot not racing, add new entry
            self.updateTable()
            
            index = len(self.results_to_table) - 1         # get index # of newly racing robot
            self.racing_robots[robot_name] = [index, time_ms]  # add to racing_robots dict
            
            # starts thread if not running
            if(len(self.racing_robots) == 1):
                self.timer = Timer(self.updateTimer)
                self.threadpool.start(self.timer)
                self.timer_running = True
                
            self.timer.inputData(robot_name, index) # input data to thread

        else:                                       # if robot was already racing
            # add finished robot to results_to_save
            index = self.racing_robots.get(robot_name)[0]
            start_time = self.racing_robots.get(robot_name)[1]

            # Replace finished time with time from pc-module
            self.results_to_table[index][robot_name] = time_ms - start_time # calculate finish time with finish_time-start_time from arduino
            finish_time = self.results_to_table[index].get(robot_name)
            self.results_to_save.append({robot_name: finish_time})
            
            # stop timer for robot_name
            self.stopTimer(robot_name)
    
    # stop timer for robot_name
    def stopTimer(self, robot_name):
        self.racing_robots.pop(robot_name)      # remove from currently racing robots
        self.timer.stopCount(robot_name)        # stop counting time
            
        # stop thread from working if no racing robots
        if(len(self.racing_robots) == 0):
            self.timer.stop()
            self.timer_running = False

    # delete highlighted row
    def removeTime(self, selected_index):
        # if selected_index is currently racing, stop its timer
        for values in self.racing_robots.values():
            if values[0] == selected_index:
                robot_name = list(self.results_to_table[selected_index].keys())[0]
                self.stopTimer(robot_name)
                break
        # if time was already ready to be saved
        else:
            if self.results_to_table[selected_index] in self.results_to_save:
                for i, val in enumerate(self.results_to_save):
                    if val == self.results_to_table[selected_index]:
                        del self.results_to_save[i]
        # delete row and fix other indexes
        del self.results_to_table[selected_index]
        self.fixIndexes(selected_index) 
        self.updateTable()
        
    # fix all indexes if a row gets deleted
    def fixIndexes(self, start_index):
        for key, value in self.racing_robots.items():
            if value[0] > start_index:
                self.racing_robots[key][0] = value[0] - 1
        self.timer.fixIndexes(start_index)
    
    # update information showed in table
    def updateTable(self):
        self.table = []
        finished_rows = []
        
        for i, lap_time in enumerate(self.results_to_table):
            if lap_time in self.results_to_save:
                finished_rows.append(i)
        
        if self.results_to_table:
            for index, entry in enumerate(self.results_to_table):
                for robot_name, lap_time in entry.items():
                    self.table.append(
                            [
                                index + 1,
                                robot_name,
                                formatTime(lap_time),
                                " "
                            ]
                        )
                    if index in finished_rows:
                        self.table[index][3] = self.checkmark

        else:
            self.table.append([])  # Add at least one row with column, otherwise error

        self.layoutChanged.emit()  # Notify table view about data change
    
    # update counting time to show in table
    def updateTimer(self, robots_dict, index_list):
        for index, key in zip(index_list, robots_dict):
            self.results_to_table[index][key] = robots_dict[key][0]
        self.updateTable()
        
    def clearTimer(self):
        if self.timer_running:
            self.timer.stop()
            self.timer_running = False

    # table header titles
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
                if section == 3:
                    return "Done"

            if orientation == QtCore.Qt.Vertical:
                return ""  # None
