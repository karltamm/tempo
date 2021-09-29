import serial # Uses pySerial
import serial.tools.list_ports
from threading import Thread
import time

class IncomingDataHandler(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.selected_port = None
        self.start() # Starts the thread's activity (run function)
    
    def run(self):
        while self.running:
            
            # Open serial port with arduino
            while self.selected_port is None:
                correct_ports = [
                p.device
                for p in serial.tools.list_ports.comports()
                if 'Arduino' in p.description  # may need tweaking to match new arduinos
                ]   # All ports with arduino connected added to list
                if not correct_ports:
                    print("No Arduino found...")
                else:
                    self.selected_port = serial.Serial(correct_ports[0], baudrate=9600, timeout=5) # Open serial port with first arduino in list
                time.sleep(3) # Either waits until looking for arduino again, or gives arduino board enough time to initialize fully before requesting data
                    
            arduinoData = str(self.selected_port.readline().decode('ascii'))
            dataType = arduinoData.split(":")[0] # Gets type of data before ":", E.g. gets "bot_name" from "bot_name:nimi"

data_handler = IncomingDataHandler()

# Infinite loop in another thread for testing
"""
class ThreadingTestClass(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.running = True
        self.start()
    
    def run(self):
        while self.running:
            print("second infinite loop...")
            time.sleep(2)
    
    def stop(self):
        self.running = False

b = ThreadingTestClass()
time.sleep(10)
print("Second infinite loop stopped")
b.stop()
"""