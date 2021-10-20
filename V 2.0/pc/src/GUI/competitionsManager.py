from PySide6 import QtWidgets

from database import CompetitionDB
from .competitionsList import CompetitionsList
from .competitionUI import CompetitionUI
from .trackingUI import TrackingUI
from .robotDataUI import RobotDataUI


class CompetitionsManager(QtWidgets.QStackedWidget):
    def __init__(self, openMainMenu):
        super().__init__()

        self.openMainMenu = openMainMenu
        self.competition_db = CompetitionDB()
        self.prepareUI()

        self.open_competion_id = None
        self.open_competion_name = None

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
            self.openRobotDataUI,
        )
        self.tracking_UI = TrackingUI(self.competition_db, self.openCompetitionUI)
        self.robot_data_UI = RobotDataUI(self.competition_db, self.openCompetitionUI)

        self.addWidget(self.competitions_list)
        self.addWidget(self.competition_UI)
        self.addWidget(self.tracking_UI)
        self.addWidget(self.robot_data_UI)

    def openCompetitionsList(self):
        self.setCurrentWidget(self.competitions_list)
        self.competitions_list.getList()

    def openCompetitionUI(self, competition_name=None, competition_id=None):
        if competition_name:
            self.open_competion_name = competition_name
            self.open_competion_id = competition_id

        self.setCurrentWidget(self.competition_UI)
        self.competition_UI.openCompetition(
            self.open_competion_name, self.open_competion_id
        )

    # def openCompetitionUI(self, competition_name, competition_id):
    #     self.setCurrentWidget(self.competition_UI)
    #     self.competition_UI.openCompetition(competition_name, competition_id)

    def openTrackingUI(self):
        self.setCurrentWidget(self.tracking_UI)
        self.tracking_UI.openTracking(self.competition_UI.competitionInfo())

    def openRobotDataUI(self, robot_name, competition_id):
        self.setCurrentWidget(self.robot_data_UI)
        self.robot_data_UI.openRobotData(robot_name, competition_id)
