import serial

arduino = serial.Serial('dev/ttyACM0', timeout=5)

data = []
data.append(str(arduino.readline()))
print(data)
