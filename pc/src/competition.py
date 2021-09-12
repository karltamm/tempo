class Competition:
    def __init__(self, database):
        self.competition_id = None
        self.db = database  # class CompetitionDB object

    def new(self, name):
        self.competition_id = self.db.addCompetition(name)

    def resume(self, competition_id):
        self.competition_id = competition_id

    def delete(self):
        self.db.deleteCompetition(self.competition_id)
        self.competition_id = None

    def addEntry(self, tracking_data):
        for lap_time in tracking_data["lap_times"]:
            self.db.addEntry(
                self.competition_id, tracking_data["robot_name"], lap_time)

    def deleteEntry(self, entry_id):
        self.db.deleteEntry(entry_id)

    def getLeaderboard(self):
        return self.db.getCompetitionLeaderboard(self.competition_id)
