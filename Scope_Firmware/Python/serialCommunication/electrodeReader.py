"""Usage: prog [-e electrode]

Arguments:
-e electrode
"""
from docopt import docopt

# Import libraries
import serial
import json
import matplotlib.pyplot as plt
from numpy.random import rand

arguments = docopt(__doc__)  # parse arguments based on docstring above
print(arguments)
if arguments["-e"] is None:
    which_electrode = 6 # electrode id to plot
else:
    which_electrode = int(arguments["-e"]) # electrode id to plot

measurement_interval = 1 # seconds

def request_electrode_data(n_tries = 5):
    # with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser: # TO DO: change serial port
    for i in range(n_tries):
        try:
            with serial.Serial('COM4', 115200, timeout=1) as ser: # TO DO: change serial port
                ser.write(b'e') # send request for electrode data
                response = ser.readline().decode().strip() # read response
                print(response)
                electrode_data = json.loads(response) # parse json data
                print("Electrode voltages: ", electrode_data)
                return electrode_data
        except (UnicodeDecodeError, serial.SerialException):
            pass
    print("Returning random numbers")
    plt.title("Random data")
    return rand(96).tolist()

if __name__ == "__main__":
    # plt.ion()
    voltage_at_electrode = []
    ts = []
    now = 0
    fig, ax1 = plt.subplots(1, 1, figsize = (8, 3))

    while True:
        data = request_electrode_data()
        voltage_at_electrode.append(data[which_electrode])
        ts.append(now * measurement_interval)
        now = now + 1

        ax1.scatter(ts, voltage_at_electrode, color = "red")
        ax1.plot(ts, voltage_at_electrode, color = "red")
        ax1.set_xlabel(f"Time since start of experiment (s)")
        ax1.set_ylabel(f"Voltage at electrode {which_electrode} (V)")
        fig.canvas.draw_idle()
        plt.pause(measurement_interval)



