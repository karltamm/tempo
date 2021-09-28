from PySide6 import QtWidgets
from PySide6 import QtCore

from .myWidgets import Page, Button, PageTitle, MyWidget, clearLayout, InputDialog


class CompetitionsList(Page):
    def __init__(self, competition_db, openMainMenu, openCompetitionUI):
        super().__init__()

        self.competition_db = competition_db
        self.openCompetitionUI = openCompetitionUI
        self.openMainMenu = openMainMenu

        self.generateUI()

    def generateUI(self):
        self.generateHeader()
        self.generateListSection()
        self.generateMainLayout()

    def generateHeader(self):
        back_btn = Button("Back", id_tag="BackBtn", class_tag="red_btn")
        back_btn.clicked.connect(self.openMainMenu)

        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignLeft)
        button_layout.addWidget(back_btn)

        page_title = PageTitle("Competitions")

        self.header = QtWidgets.QVBoxLayout()
        self.header.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.header.addLayout(button_layout)
        self.header.addWidget(page_title)

    def generateListSection(self):

        add_competition_btn = Button("Add Competition", id_tag="AddCompetitionBtn")
        add_competition_btn.setProperty("class2", "green_btn")
        add_competition_btn.clicked.connect(self.openCompetitionCreator)

        button_box = QtWidgets.QHBoxLayout()
        button_box.addWidget(add_competition_btn)
        button_box.setAlignment(QtCore.Qt.AlignLeft)

        # Actual list part
        self.competitions_list = (
            QtWidgets.QVBoxLayout()
        )  # You put competition list items into this
        self.competitions_list.setAlignment(QtCore.Qt.AlignTop)

        self.competition_list_widget = MyWidget(
            id_tag="CompetitionList"
        )  # This is needed to use scroll area. "competitions_list" layout is put into this widget

        self.competitions_list_scroll = QtWidgets.QScrollArea()
        self.competitions_list_scroll.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn
        )
        self.competitions_list_scroll.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff
        )
        self.competitions_list_scroll.setWidgetResizable(True)
        self.competitions_list_scroll.setWidget(self.competition_list_widget)

        self.list_section = QtWidgets.QVBoxLayout()
        self.list_section.setAlignment(QtCore.Qt.AlignTop)
        self.list_section.addLayout(button_box)
        self.list_section.addWidget(self.competitions_list_scroll)

    def generateMainLayout(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(main_layout)

        main_layout.addLayout(self.header)
        main_layout.addLayout(self.list_section)

    def getList(self):
        data = self.competition_db.getListOfCompetitions()

        if data != None:
            # Reset list
            clearLayout(self.competitions_list)

            # Populate list
            for competition in data:
                self.competitions_list.addWidget(
                    CompetitionListItem(
                        competition["name"],
                        competition["id"],
                        self.openCompetitionUI,
                        self.deleteCompetition,
                    )
                )
            # for i in range(300):
            #     self.competitions_list.addWidget(
            #         CompetitionListItem(
            #             "Test " + str(i),
            #             1,
            #             self.openCompetitionUI,
            #             self.deleteCompetition,
            #         )
            #     )

            # Add list to view
            self.competition_list_widget.setLayout(self.competitions_list)
        else:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", "List of competitions could not be retrived!"
            )

    def openCompetitionCreator(self):
        InputDialog("Competition Name", self, self.addCompetition)

    def addCompetition(self, name):
        if self.competition_db.addCompetition(name):
            self.getList()  # Update list
        else:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", "Competition could not be created!"
            )

    def deleteCompetition(self, competition_ID):
        if self.competition_db.deleteCompetition(competition_ID):
            self.getList()  # Update list
        else:
            QtWidgets.QMessageBox.critical(
                self, "Database Error", "Competition could not be deleted!"
            )


class CompetitionListItem(QtWidgets.QWidget):
    def __init__(
        self,
        competition_name,
        competition_ID,
        openCompetitionUI,
        deleteCompetition,
    ):
        super().__init__()

        name = QtWidgets.QLabel(competition_name)
        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(name)
        name_layout.setAlignment(QtCore.Qt.AlignLeft)

        open_btn = Button("Open")
        open_btn.clicked.connect(
            lambda: openCompetitionUI(competition_name, competition_ID)
        )
        delete_btn = Button("Delete", class_tag="red_btn")
        delete_btn.clicked.connect(lambda: deleteCompetition(competition_ID))

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(open_btn)
        button_layout.addWidget(delete_btn)
        button_layout.setAlignment(QtCore.Qt.AlignRight)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(name_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)
