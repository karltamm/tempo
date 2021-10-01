import serial  # Uses pySerial
import serial.tools.list_ports
from PySide6 import QtCore
import time


class IncomingDataHandler(QtCore.QRunnable):
    def __init__(self, renameBot, addTime) -> None:
        super().__init__()
        self.renameBot = renameBot
        self.addTime = addTime
        self.selected_port = None
        self.is_running = True

    @QtCore.Slot()
    def run(self):
        while self.is_running:
            # Opens the serial port with connected arduino
            while self.selected_port is None:
                correct_ports = [
                    p.device
                    for p in serial.tools.list_ports.comports()
                    if "Arduino" in p.description
                ]  # All ports with arduino connected added to list
                if not correct_ports:
                    print("No Arduino found...")
                else:
                    self.selected_port = serial.Serial(
                        correct_ports[0], baudrate=9600, timeout=5
                    )  # Open serial port with first arduino in list
                    print("Connected to Arduino")
                time.sleep(
                    3
                )  # Either waits until looking for arduino again, or gives arduino board enough time to initialize fully before requesting data

            # Starts receiving data from the Arduino
            arduinoData = str(self.selected_port.readline().decode("ascii"))
            dataType = arduinoData.split(":")[
                0
            ]  # Gets type of data before ":", E.g. gets "bot_name" from "bot_name:name"
            if dataType == "bot_name":
                dataValue = arduinoData.split(":")[1]
                self.renameBot(dataValue)
            elif dataType == "lap_time":
                dataValue = arduinoData.split(":")[1]
                self.addTime(dataValue)
            arduinoData = ""  # Empties received data after using it (wont cause errors with .split(":")[0] on empty string)

    def stopWorker(self):
        self.is_running = False


class SerialDataHandler(QtCore.QRunnable):
    def __init__(self, addTime, renameBot) -> None:
        super().__init__()

        self.connection = None
        self.is_running = True

        self.addTime = addTime
        self.renameBot = renameBot

    @QtCore.Slot()
    def run(self):
        # This function runs as a separate thread
        while self.is_running:
            while self.connection is None:
                self.findArduinoPort()
                time.sleep(
                    3
                )  # Don't check every moment if user has plugged in the Arduino, people are slow

            self.checkIncomingData()

    def checkIncomingData(self):
        serial_data = str(self.selected_port.readline().decode("ascii"))
        data_id = serial_data.split(":")[
            0
        ]  # Gets type of data before ":", E.g. gets "bot_name" from "bot_name:name"

        if data_id == "bot_name":
            data_value = serial_data.split(":")[1]
            self.renameBot(data_value)
        elif data_id == "lap_time":
            data_value = serial_data.split(":")[1]
            self.addTime(data_value)

        # serial_data = ""  # Empties received data after using it (wont cause errors with .split(":")[0] on empty string)

    def findArduinoPort(self):
        correct_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if "Arduino" in p.description
        ]

        if correct_ports:
            self.connection = serial.Serial(correct_ports[0], baudrate=9600, timeout=5)
        else:
            print("Arduino is not connected")

    def stop(self):
        self.is_running = False

    def startNewTracking(self):
        # Send time tracking reset signal to PC radio module (arduino) that sends signal to the TimeTracker itself
        if self.connection:
            self.port_connection.write("reset")
            return True  # Success
        else:
            return False  # No connection
