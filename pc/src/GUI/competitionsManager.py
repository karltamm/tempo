from PySide6 import QtWidgets

from database import CompetitionDB
from .competitionsList import CompetitionsList
from .competitionUI import CompetitionUI
from .trackingUI import TrackingUI


class CompetitionsManager(QtWidgets.QStackedWidget):
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
