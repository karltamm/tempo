from os import path
import sys
from PySide6 import QtGui, QtWidgets


def getExecutionPath():
    # Execution path is full path! (starts with c:\)
    # If you execute this program as a python script, then execution path would be in src folder
    # If you execute this as exe (made with pyinstaller), then execution path would be in dist folder
    return path.dirname(sys.argv[0])


def getAssetsFolderPath():
    return path.join(getExecutionPath(), "..", "assets")


def loadFont(font_folder, font_name):
    return QtGui.QFontDatabase.addApplicationFont(
        path.join(getAssetsFolderPath(), "fonts", font_folder, font_name + ".ttf")
    )


def getStylesheetPath():
    return path.join(getAssetsFolderPath(), "style.css")


def setFontSmooth():
    # For some reason you don't have to specify a font name.
    # Somehow setHintingPreference applies to every font
    font_obj = QtGui.QFont()
    font_obj.setHintingPreference(QtGui.QFont.HintingPreference.PreferNoHinting)
    QtWidgets.QApplication.instance().setFont(font_obj)


def getDatabaseFilePath(file_name):
    return path.join(getExecutionPath(), "..", "data", file_name)


def getWindowIcon():
    return QtGui.QIcon(path.join(getAssetsFolderPath(), "icon", "icon_ico.ico"))

def getCheckmarkIcon():
    return QtGui.QIcon(QtGui.QPixmap(path.join(getAssetsFolderPath(), "icon", "checkmark.png")))
