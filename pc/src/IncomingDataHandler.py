import serial
import serial.tools.list_ports

arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description  # may need tweaking to match new arduinos
] # All ports with arduino connected added to list

ser = serial.Serial(arduino_ports[0]) # Open serial port with first arduino in list

data = []
data.append(str(ser.readline())) # using ser.readline() assumes each line contains a single reading, sent using Serial.println() on the Arduino
print(data)
