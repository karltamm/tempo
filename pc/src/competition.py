class Competition:
    def __init__(self, database):
        self.comp_id = None  # Competition ID
        self.db = database  # class CompetitionDB object
        self.db.addErrorCallback(self.databaseErrorCallback)
        self.db_error_id = None

    def new(self, name):
        self.comp_id = self.db.addCompetition(name)

    def resume(self, competition_id):
        self.comp_id = competition_id

    def addEntry(self, tracking_data):
        for lap_time in tracking_data["lap_times"]:
            self.db.addEntry(
                self.comp_id, tracking_data["robot_name"], lap_time)

    def databaseErrorCallback(self, error_id):
        self.db_error_id = error_id
