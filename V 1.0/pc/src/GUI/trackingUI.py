from PySide6 import QtWidgets
from PySide6 import QtCore

import random  # for testing!


from .myWidgets import Page, PageTitle, Button, SectionTitle, InputDialog, formatTime
from serialData import SerialDataHandler


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

        self.setupSerialDataHandler()

    def setupSerialDataHandler(self):
        self.serial_data_handler = SerialDataHandler(
            self.lap_times_list_model.addTime, self.renameRobot
        )
        self.threadpool = QtCore.QThreadPool()
        # NB! if threadpool is not this class variable (no ".self") then GUI wont be displayed
        self.threadpool.start(self.serial_data_handler)

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
        # self.header.addWidget(test_btn)

    def generateRobotNameSection(self):
        robot_name_label = SectionTitle("Robot Name")

        self.robot_name = QtWidgets.QLabel(self.robot_default_name)
        self.robot_name.setObjectName("RobotName")
        rename_btn = Button("Rename", id_tag="RobotRenameBtn")
        rename_btn.clicked.connect(self.openRenameDialog)

        rename_layout = QtWidgets.QHBoxLayout()
        rename_layout.addWidget(self.robot_name)
        rename_layout.addWidget(rename_btn)
        rename_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.robot_name_layout = QtWidgets.QVBoxLayout()
        self.robot_name_layout.addWidget(robot_name_label)
        self.robot_name_layout.addLayout(rename_layout)

    def openRenameDialog(self):
        InputDialog("Rename Robot", parent=self, callback=self.renameRobot)

    def renameRobot(self, name):
        self.robot_name.setText(name)

    def addDummyData(self):
        self.lap_times_list_model.addTime(random.randrange(30000, 300000))

    def deleteSelectedTimes(self):
        all_selected = self.lap_times_list_view.selectedIndexes()
        for time in all_selected:
            self.lap_times_list_model.removeTime(time.row())
            self.lap_times_list_view.clearSelection()

    def saveData(self):
        robot_name = self.robot_name.text()
        lap_times = self.lap_times_list_model.lap_times

        if len(lap_times):
            if not self.competition_db.addRobotLapTimes(
                self.competition_id, robot_name, lap_times
            ):
                QtWidgets.QMessageBox.critical(
                    self, "Database Error", "Lap times couldn't be saved!"
                )
            self.serial_data_handler.sendData("stop_tr")
            self.openCompetitionUI(self.competition_name, self.competition_id)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "No lap times to save!")

    def generateLapTimesList(self):
        list_title = SectionTitle("Lap Times")

        restart_lap_btn = Button("Restart Lap", id_tag="RestartLapBtn")
        restart_lap_btn.clicked.connect(
            lambda: self.serial_data_handler.sendData("reset_lap")
        )
        restart_lap_layout = QtWidgets.QHBoxLayout()
        restart_lap_layout.addWidget(restart_lap_btn)
        restart_lap_layout.setAlignment(QtCore.Qt.AlignLeft)

        self.lap_times_list_view = QtWidgets.QListView()
        self.lap_times_list_view.setObjectName("TrackingLapTimesView")
        self.lap_times_list_view.setModel(self.lap_times_list_model)

        delete_time_btn = Button(
            "Delete Time", id_tag="DeleteLapTimeBtn", class_tag="red_btn"
        )
        delete_time_btn.clicked.connect(self.deleteSelectedTimes)

        save_btn = Button("Save", class_tag="green_btn", id_tag="SaveLapTimesBtn")
        save_btn.clicked.connect(self.saveData)

        save_btn_layout = QtWidgets.QHBoxLayout()
        save_btn_layout.setAlignment(QtCore.Qt.AlignRight)
        save_btn_layout.addWidget(save_btn)

        self.lap_times_list = QtWidgets.QVBoxLayout()
        self.lap_times_list.addWidget(list_title)
        self.lap_times_list.addLayout(restart_lap_layout)
        self.lap_times_list.addWidget(self.lap_times_list_view)
        self.lap_times_list.addWidget(delete_time_btn)
        self.lap_times_list.addLayout(save_btn_layout)

    def generateLayout(self):
        self.generateHeader()
        self.generateRobotNameSection()
        self.generateLapTimesList()

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addLayout(self.header)
        main_layout.addLayout(self.robot_name_layout)
        main_layout.addLayout(self.lap_times_list)

    def openTracking(self, data):
        self.competition_name, self.competition_id = data

        # Removes previously held data
        self.lap_times_list_model.lap_times = []  # Clear
        self.robot_name.setText(self.robot_default_name)

        # Send reset signal to PC module
        # Check if PC radio module is connected
        if not self.serial_data_handler.sendData("start_tr"):
            QtWidgets.QMessageBox.critical(
                self, "Error", "Connect PC radio module into USB port!"
            )

            # Go back because tracking is useless without radio module
            self.openCompetitionUI(self.competition_name, self.competition_id)


class LapTimesListModel(QtCore.QAbstractListModel):
    def __init__(self):
        super().__init__()

        self.lap_times = []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            row_number = str(index.row() + 1) + ")  "
            return row_number + formatTime(self.lap_times[index.row()])

    def rowCount(self, index):
        return len(self.lap_times)

    def addTime(self, time):
        self.lap_times.append(time)
        self.layoutChanged.emit()

    def removeTime(self, time_index):
        del self.lap_times[time_index]
        self.layoutChanged.emit()
