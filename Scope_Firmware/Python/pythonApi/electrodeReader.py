# Import libraries
import serial
import json

def request_electrode_data():
    with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser: # TO DO: change serial port
        ser.write(b'e') # send request for electrode data
        response = ser.readline().decode().strip() # read response
        electrode_data = json.loads(response) # parse json data
        print("Electrode voltages: ", electrode_data)

if __name__ == "__main__":
    request_electrode_data()

