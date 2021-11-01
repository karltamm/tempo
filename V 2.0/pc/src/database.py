import sqlite3
from sqlite3 import Error
import time
import math
from datetime import datetime

from assets import getDatabaseFilePath


class CompetitionDB:
    def __init__(self):
        self.con = None  # Database connection object
        self.connect()

    def connect(self):
        try:
            self.con = sqlite3.connect(getDatabaseFilePath("competitions.db"))
            self.makeSureThatTablesExist()
        except Error as error:
            print(error)

    def makeSureThatTablesExist(self):
        try:
            competitions_table_sql = (
                "CREATE TABLE IF NOT EXISTS competitions( "
                "competition_id INTEGER PRIMARY KEY,"
                "competition_name TEXT NOT NULL,"
                "creation_time INTEGER NOT NULL)"
            )

            competition_entries_table_sql = (
                "CREATE TABLE IF NOT EXISTS comp_entries( "
                "entry_id INTEGER PRIMARY KEY,"
                "robot_name TEXT NOT NULL,"
                "robot_id INTEGER,"
                "lap_time INTEGER NOT NULL,"
                "competition_id INTEGER NOT NULL,"
                "creation_time INTEGER NOT NULL)"
            )

            cursor = self.con.cursor()
            cursor.execute(competitions_table_sql)
            cursor.execute(competition_entries_table_sql)
        except Error as error:
            print(error)

    def close(self):
        self.con.close()

    def addCompetition(self, name):
        try:
            competition_sql = (
                "INSERT INTO competitions(competition_name, creation_time) "
                "VALUES(?,?)"
            )

            cursor = self.con.cursor()
            creation_time = math.floor(time.time())
            cursor.execute(competition_sql, (name, creation_time))
            self.con.commit()

            return True  # Competition created successfully
        except Error as error:
            print(error)
            return False  # Error

    def deleteCompetition(self, competition_id):
        try:
            delete_comp_sql = "DELETE FROM competitions WHERE competition_id=?"
            delete_entries_sql = "DELETE FROM comp_entries WHERE competition_id=?"

            cursor = self.con.cursor()
            cursor.execute(delete_comp_sql, (competition_id,))
            cursor.execute(delete_entries_sql, (competition_id,))
            self.con.commit()

            return True  # Competition was deleted successfully
        except Error as error:
            print(error)
            return False  # Error

    def getListOfCompetitions(self):
        try:
            list_of_competitions = []

            get_competions_sql = (
                "SELECT competition_id, competition_name FROM competitions "
                "ORDER BY creation_time DESC"
            )

            cursor = self.con.cursor()
            cursor.execute(get_competions_sql)
            competition_data = cursor.fetchall()

            for competition in competition_data:
                list_of_competitions.append(
                    {"id": competition[0], "name": competition[1]}
                )

            return list_of_competitions
        except Error as error:
            print(error)
            return None

    def addRobotLapTimes(self, competition_id, robot_name, lap_time):
        try:
            entry_sql = (
                "INSERT INTO comp_entries(competition_id,robot_name,lap_time,creation_time)"
                "VALUES(?,?,?,?)"
            )

            cursor = self.con.cursor()
            creation_time = math.floor(time.time())

        
            cursor.execute(
                entry_sql,
                (
                    competition_id,
                    robot_name,
                    lap_time,
                    creation_time,
                ),
            )

            self.con.commit()
            return True  # Entry was added successfully
        except Error as error:
            print(error)
            return False  # Error

    def deleteRobotLapTime(self, entry_id):
        try:
            delete_entry_sql = "DELETE FROM comp_entries WHERE entry_id=?"
            self.con.cursor().execute(delete_entry_sql, (str(entry_id),))
            self.con.commit()
            return True  # Entry was deleted successfully
        except Error as error:
            print(error)
            return False  # Error

    def getCompetitionLeaderboard(self, competition_id):
        leaderboard = []

        try:
            leaderboard_sql = (
                "SELECT entry_id, robot_name, MIN(lap_time), creation_time "
                "FROM comp_entries "
                "WHERE competition_id = ? "
                "GROUP BY robot_name "
                "ORDER BY lap_time ASC "
            )

            cursor = self.con.cursor()
            cursor.execute(leaderboard_sql, (competition_id,))
            entries = cursor.fetchall()
            for entry in entries:
                # print(datetime.fromtimestamp(entry[3]).strftime("%d.%m.%Y"))
                date = datetime.fromtimestamp(entry[3]).strftime("%d.%m.%Y")
                leaderboard.append(
                    {
                        "entry_id": entry[0],
                        "robot_name": entry[1],
                        "lap_time": entry[2],
                        "date": date,
                    }
                )
        except Error as error:
            print(error)

        return leaderboard

    def getRobotEntries(self, robot_name, competition_id):
        entries = []

        try:
            entries_sql = (
                "SELECT entry_id, lap_time, creation_time "
                "FROM comp_entries "
                "WHERE competition_id = ? AND robot_name = ? "
                "ORDER BY lap_time ASC "
            )

            cursor = self.con.cursor()
            cursor.execute(entries_sql, (competition_id, robot_name))
            for entry in cursor.fetchall():
                date = datetime.fromtimestamp(entry[2]).strftime("%d.%m.%Y")
                entries.append(
                    {
                        "entry_id": entry[0],
                        "lap_time": entry[1],
                        "date": date,
                    }
                )
        except Error as error:
            print(error)

        return entries
