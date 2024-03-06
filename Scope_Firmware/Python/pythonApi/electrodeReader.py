# Import libraries
import serial
import json
import matplotlib.pyplot as plt
import time

from drawnow import drawnow

which_electrode = 0

def request_electrode_data():
    # with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser: # TO DO: change serial port
    with serial.Serial('COM4', 115200, timeout=1) as ser: # TO DO: change serial port
        ser.write(b'e') # send request for electrode data
        response = ser.readline().decode().strip() # read response
        electrode_data = json.loads(response) # parse json data
        print("Electrode voltages: ", electrode_data)
        return electrode_data

if __name__ == "__main__":
    # plt.ion()
    voltage_at_electrode = []
    ts = []
    now = 0
    fig, ax1 = plt.subplots(1, 1, figsize = (6, 6))

    while True:
        data = request_electrode_data()
        voltage_at_electrode.append(data[which_electrode])
        ts.append(now)
        now = now + 1

        ax1.scatter(ts, voltage_at_electrode, color = "red")
        ax1.plot(ts, voltage_at_electrode, color = "red")
        ax1.set_xlabel("Measurement index (roughly one per second)")
        ax1.set_ylabel(f"Voltage at electrode {which_electrode}")
        fig.canvas.draw_idle()
        plt.pause(1)



