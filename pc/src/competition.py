from database import CompetitionDB


class Competition:
    def __init__(self):
        self.id = None
        self.name = None
        self.db = CompetitionDB()

    def create(self, competition_name):
        self.name = competition_name
        self.id = self.db.addCompetition(competition_name)

    def resume(self, competition_name, competition_id):
        self.name = competition_name
        self.id = competition_id

    def delete(self):
        self.db.deleteCompetition(self.id)
        self.id = None
        self.name = None

    def addEntry(self, tracking_data):
        for lap_time in tracking_data["lap_times"]:
            self.db.addEntry(self.id, tracking_data["robot_name"], lap_time)

    def deleteEntry(self, entry_id):
        self.db.deleteEntry(entry_id)

    def getLeaderboard(self):
        return self.db.getCompetitionLeaderboard(self.id)
