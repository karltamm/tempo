from os import curdir
import sqlite3
from sqlite3 import Error
import enum
from sqlite3.dbapi2 import Cursor


class DB_Errors(enum.Enum):
    none = 0
    new_competition = 1
    open_competition = 2
    add_entry = 3
    connection = 4
    table_init = 5
    table_print = 6
    competition_query = 7
    delete_data = 8


class CompetitionDB:
    def __init__(self):
        self.con = None  # Database connection object
        self.errorCallback = lambda error: error
        self.connect()

    def addErrorCallback(self, callback):
        self.errorCallback = callback

    def connect(self):
        self.errorCallback(DB_Errors.none)

        try:
            self.con = sqlite3.connect("../data/competitions.db")
            self.initTables()
        except Error as error:
            self.errorCallback(DB_Errors.connection)
            print(error)

    def initTables(self):
        self.errorCallback(DB_Errors.none)

        try:
            competitions_table_sql = ("CREATE TABLE IF NOT EXISTS competitions( "
                                      "id INTEGER PRIMARY KEY, "
                                      "name TEXT NOT NULL)")

            competition_entries_table_sql = ("CREATE TABLE IF NOT EXISTS comp_entries( "
                                             "id INTEGER PRIMARY KEY, "
                                             "robot_name TEXT NOT NULL, "
                                             "robot_id INTEGER, "
                                             "lap_time INTEGER NOT NULL, "
                                             "comp_id INTEGER NOT NULL)")

            cursor = self.con.cursor()
            cursor.execute(competitions_table_sql)
            cursor.execute(competition_entries_table_sql)
        except Error as error:
            self.errorCallback(DB_Errors.connection)
            print(error)

    def addCompetition(self, name):
        self.errorCallback(DB_Errors.none)

        try:
            competition_sql = "INSERT INTO competitions(name) VALUES(?)"
            cursor = self.con.cursor()

            cursor.execute(competition_sql, (name,))
            self.con.commit()

            return cursor.lastrowid
        except Error as error:
            self.errorCallback(DB_Errors.table_init)
            print(error)
            return None

    def addEntry(self, comp_id, robot_name, lap_time):
        self.errorCallback(DB_Errors.none)

        try:
            entry_sql = ("INSERT INTO comp_entries(comp_id,robot_name,lap_time)"
                         "VALUES(?,?,?)")

            self.con.cursor().execute(entry_sql, (comp_id, robot_name, lap_time))
            self.con.commit()
        except Error as error:
            self.errorCallback(DB_Errors.add_entry)
            print(error)

    def printTable(self, table_name):
        self.errorCallback(DB_Errors.none)

        try:
            sql = "SELECT * FROM " + table_name
            cursor = self.con.cursor()
            cursor.execute(sql)

            print(f"\nTable: {table_name}")

            rows = cursor.fetchall()
            for row in rows:
                print(row)

        except Error as error:
            self.errorCallback(DB_Errors.table_print)
            print(error)

    def competitionExists(self, id):
        self.errorCallback(DB_Errors.none)

        try:
            query = "SELECT * FROM competitions WHERE id=?"
            cursor = self.con.cursor()
            cursor.execute(query, (id,))
            competion = cursor.fetchall()

            if competion:
                return True

            return False
        except Error as error:
            self.errorCallback(DB_Errors.competition_query)
            print(error)

    def clearAllData(self):
        self.errorCallback(DB_Errors.none)

        try:
            delete_competitions = "DELETE FROM competitions"
            delete_entries = "DELETE FROM comp_entries"

            cursor = self.con.cursor()
            cursor.execute(delete_competitions)
            cursor.execute(delete_entries)

            self.con.commit()
        except Error as error:
            self.errorCallback(DB_Errors.delete_data)
            print(error)

    def close(self):
        self.con.close()

    def deleteCompetition(self, competition_id):
        self.errorCallback(DB_Errors.none)

        try:
            delete_comp_sql = "DELETE FROM competitions WHERE id=?"
            delete_entries = "DELETE FROM comp_entries WHERE comp_id=?"
            cursor = self.con.cursor()
            cursor.execute(delete_comp_sql, (competition_id,))
            cursor.execute(delete_entries, (competition_id,))
            self.con.commit()
        except Error as error:
            self.errorCallback(DB_Errors.delete_data)
            print(error)
