from PySide6 import QtWidgets

from GUI.app import MainWindow

import os  # Only for testing
import sys  # Only for testing

# Make sure that this file runs in its folder!
# file_dir_path = os.path.dirname(sys.argv[0])  # sys.argv[0] == current file path
# os.chdir(file_dir_path)

app = QtWidgets.QApplication()
app.setStyle(QtWidgets.QStyleFactory.create("fusion"))
window = MainWindow()
app.exec()
