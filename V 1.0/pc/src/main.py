from PySide6 import QtWidgets
from os import _exit

from GUI.app import MainWindow, loadFont, setFontSmooth
from serialData import SerialDataHandler


# Make sure that this file runs in its folder!
# import os
# import sys
# file_dir_path = os.path.dirname(sys.argv[0])  # sys.argv[0] == current file path
# os.chdir(file_dir_path)

app = QtWidgets.QApplication()

app.setStyle(QtWidgets.QStyleFactory.create("fusion"))

# Headings fonts
loadFont("Roboto Slab", "RobotoSlab-Black")
loadFont("Roboto Slab", "RobotoSlab-Medium")

# Body fonts
loadFont("Roboto", "Roboto-Light")
loadFont("Roboto", "Roboto-Bold")

setFontSmooth()

window = MainWindow()
app.exec()

# App GUI has been closed

_exit(0)  # Stop all processes (like threads)
