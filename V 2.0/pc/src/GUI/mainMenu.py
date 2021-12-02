from PySide6 import QtWidgets
from PySide6 import QtCore

from .myWidgets import Page, Button


class MainMenu(Page):
    def __init__(self, openCompetitionsManager, openPractice):
        super().__init__()

        # Header
        title = QtWidgets.QLabel("Tempo")
        title.setObjectName("AppTitle")

        subtitle = QtWidgets.QLabel("Lap time tracker")
        subtitle.setObjectName("AppSubtitle")

        header = QtWidgets.QVBoxLayout()
        header.addWidget(title)
        header.addWidget(subtitle)

        # Menu options

        competition_btn = Button("Competitions", "OpenCompetitions")
        competition_btn.clicked.connect(openCompetitionsManager)
        
        practice_btn = Button("Practice", "ExitApp") #ExitApp means margin-top:5px;
        practice_btn.clicked.connect(openPractice)

        exit_btn = Button("Exit", "ExitApp", class_tag="red_btn")
        exit_btn.clicked.connect(QtWidgets.QApplication.instance().quit)

        menu_options = QtWidgets.QVBoxLayout()
        menu_options.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        menu_options.addWidget(competition_btn)
        menu_options.addWidget(practice_btn)
        menu_options.addWidget(exit_btn)

        # Main layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.addLayout(header)
        main_layout.addLayout(menu_options)

        self.setLayout(main_layout)
