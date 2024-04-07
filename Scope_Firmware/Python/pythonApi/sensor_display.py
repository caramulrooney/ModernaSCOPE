from electrode_names import ElectrodeNames
from config import Config
from sensor_interface import SensorInterface
import matplotlib.pyplot as plt
from constants import N_ELECTRODES
from threading import Thread

class SensorDisplay():
    nrows = 8
    ncols = 12
    n_electrodes = nrows * ncols
    row_letters = "ABCDEFGH"
    ts = 0
    electrodes = list(range(N_ELECTRODES))
    running_graphical_display = False
    running_file_display = False

    def __init__(self, sensor_interface: SensorInterface):
        self.sensor_interface = sensor_interface

    def start_graphical_display(self):
        Thread(target = self.run_graphical_display, daemon = True).start()

    def start_file_display(self):
        Thread(target = self.run_files, daemon = True).start()

    def stop_graphical_display(self):
        self.running_graphical_display = False

    def stop_file_display(self):
        self.running_file_display = False

    def run_graphical_display(self):
        # don't start a duplicate thread instance
        if self.running_graphical_display:
            return
        self.setup_plots()
        self.running_graphical_display = True
        while self.running_graphical_display:
            self.display_graphs()

    def run_files(self):
        # don't start a duplicate thread instance
        if self.running_file_display:
            print(f"File display is already running. See output in file {Config.voltage_display_filename}")
            return
        self.running_file_display = True
        while self.running_file_display:
            self.write_to_file()

    def write_to_file(self):
        voltages = self.sensor_interface.get_future_voltages_blocking(1)[0]
        with open(Config.voltage_display_filename, "w") as display_file:
            display_file.write(ElectrodeNames.electrode_ascii_art(voltages))

    def display_graphs(self):
        voltages = self.sensor_interface.get_future_voltages_blocking(1)[0]
        self.ts += Config.measurement_interval
        for row in range(self.nrows):
            for col in range(self.ncols):
                electrode_id = col + row * self.ncols
                if electrode_id not in self.electrodes:
                    continue
                self.ax[row][col].plot(self.ts, [vs[electrode_id] for vs in voltages], color = "orange")
        self.fig.canvas.draw_idle()

    def setup_plots(self, ignore_ticks = True):
        self.fig, self.ax = plt.subplots(self.nrows, self.ncols, figsize = (8, 12), sharex = True, sharey = True)
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

