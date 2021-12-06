import serial  # Uses pySerial
import serial.tools.list_ports
from PySide6 import QtCore
import time


class SerialDataHandler(QtCore.QRunnable):
    def __init__(self, translateID=None) -> None:
        super().__init__()

        self.connection = None
        self.is_running = True
        self.timer_connection = False

        
        self.translateID = translateID or (lambda x: None)

    @QtCore.Slot()
    def run(self):
        # This function runs as a separate thread
        while self.is_running:
            while self.connection is None:
                self.findArduinoPort()
                # Don't check every moment whether user has plugged in the Arduino, people are slow
                time.sleep(3)

            self.checkIncomingData()

    def checkIncomingData(self):
        serial_data = str(self.connection.readline().decode("ascii"))

        if ":" in serial_data:
            # E.g. Gets bot_id = "B81B6D", time_ms = "123456" from "B81B6D:123456"
            # And forwards data to tracker
            bot_id = serial_data.split(":")[0].strip("\r\n")
            time_ms = serial_data.split(":")[1].strip("\r\n")

            self.translateID(bot_id, int(time_ms))

        if "Success" in serial_data:  # Timer connection confirmation
            self.timer_connection = True


    def findArduinoPort(self):
        connected_ports = serial.tools.list_ports.comports()

        for port in connected_ports:
            if "CH340" in port.description:
                # "CH340" is chip used by Arduino for USB connections
                # port.device is Windows port (e.g COM1)
                self.connection = serial.Serial(port.device, baudrate=9600, timeout=5)
                break

    def stop(self):
        self.sendData("stop_tr")
        self.is_running = False

    def sendData(self, msg):
        # Send signal to PC radio module (arduino) that sends signal to the TimeTracker itself
        if self.connection:
            self.connection.write((msg + "\n").encode("ascii"))
            return True  # Success
        else:
            return False  # No connection

    def addCallbacks(self, translateID):
        self.translateID = translateID
