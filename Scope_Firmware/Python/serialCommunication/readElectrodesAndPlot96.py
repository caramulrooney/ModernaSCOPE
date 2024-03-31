# Import libraries
import serial
import json
import matplotlib.pyplot as plt
from numpy.random import rand

which_electrode = 68 # electrode id to plot
electrode_reading_delay = 1.5 # seconds
measurement_interval = electrode_reading_delay + 1 # seconds

def request_electrode_data(n_tries = 5):
    # with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser: # TO DO: change serial port
    for i in range(n_tries):
        try:
            with serial.Serial('COM4', 115200, timeout=1) as ser: # TO DO: change serial port
                ser.write(b'e') # send request for electrode data
                plt.pause(electrode_reading_delay)
                response = ser.readline().decode().strip() # read response
                print(response)
                electrode_data = json.loads(response) # parse json data
                # print("Electrode voltages: ", electrode_data)
                print("Returning electrode voltages")
                return electrode_data
        except UnicodeDecodeError:
            pass
    print("Returning random numbers")
    return rand(96).tolist()

class Plotter():
    nrows = 8
    ncols = 12
    n_electrodes = nrows * ncols
    row_letters = "ABCDEFGH"

    def __init__(self) -> None:
        self.fig, self.ax = plt.subplots(self.nrows, self.ncols, figsize = (8, 12), sharex = True, sharey = True)
        self.setup_plots()

    def setup_plots(self, ignore_ticks = True):
        self.fig.suptitle("Electrode voltages over time for all 96 electrodes.")
        self.fig.supxlabel("Time (s)")
        self.fig.supylabel("Voltage (V), scaled to the largest voltage in the array")
        for row in range(self.nrows):
            for col in range(self.ncols):
                if row == self.nrows - 1:
                    self.ax[row][col].set_xlabel(col + 1)
                if col == 0:
                    self.ax[row][col].set_ylabel(self.row_letters[row] + " " * 5, rotation = 0)

                if row == self.nrows - 1 and col == 0:
                    continue

                if ignore_ticks:
                    self.ax[row][col].tick_params(
                        axis='x',          # changes apply to the x-axis
                        which='both',      # both major and minor ticks are affected
                        bottom=False,      # ticks along the bottom edge are off
                        top=False,         # ticks along the top edge are off
                        labelbottom=False
                    ) # labels along the bottom edge are off
                    self.ax[row][col].tick_params(
                        axis='y',          # changes apply to the x-axis
                        which='both',      # both major and minor ticks are affected
                        left=False,      # ticks along the bottom edge are off
                        right=False,         # ticks along the top edge are off
                        labelleft=False
                    ) # labels along the bottom edge are off

    def plot_voltages(self, ts, voltages):

        for row in range(self.nrows):
            for col in range(self.ncols):
                electrode_id = col + row * self.ncols
                self.ax[row][col].plot(ts, [vs[electrode_id] for vs in voltages], color = "orange")

        self.fig.canvas.draw_idle()

if __name__ == "__main__":
    plotter = Plotter()
    voltages = []
    ts = []
    now = 0

    while True:
        data = request_electrode_data()
        voltages.append(data)
        now = now + 1
        ts.append(now * measurement_interval)
        plotter.plot_voltages(ts, voltages)
        plt.pause(measurement_interval)



