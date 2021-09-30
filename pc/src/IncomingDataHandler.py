import serial # Uses pySerial
import serial.tools.list_ports
from PySide6 import QtCore
import time

class IncomingDataHandler(QtCore.QRunnable):
    def __init__(self, renameBot, addTime):
        super().init()
        self.renameBot = renameBot
        self.addTime = addTime
        self.selected_port = None
        self.running = True
        
    
    @QtCore.Slot()
    def run(self):
        while self.running:
            # Opens the serial port with connected arduino
            while self.selected_port is None:
                correct_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                if 'Arduino' in p.description
                ]   # All ports with arduino connected added to list
                if not correct_ports:
                    print("No Arduino found...")
                else:
                    self.selected_port = serial.Serial(correct_ports[0], baudrate=9600, timeout=5) # Open serial port with first arduino in list
                time.sleep(3) # Either waits until looking for arduino again, or gives arduino board enough time to initialize fully before requesting data
   
            # Starts receiving data from the Arduino
            arduinoData = str(self.selected_port.readline().decode('ascii'))
            dataType = arduinoData.split(":")[0] # Gets type of data before ":", E.g. gets "bot_name" from "bot_name:name"
            if (dataType == "bot_name"):
                dataValue = arduinoData.split(":")[1]
                renameBot(dataValue)
            elif (dataType == "lap_time"):
                dataValue = arduinoData.split(":")[1]
                addTime(dataValue)
            arduinoData = "" # Empties received data after using it (wont cause errors with .split(":")[0] on empty string)

    def stopWorker(self):
        self.running = False
