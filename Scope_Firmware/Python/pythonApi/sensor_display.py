from electrode_names import ElectrodeNames
from config import Config
from sensor_interface import SensorInterface
import matplotlib.pyplot as plt
from constants import N_ELECTRODES, N_ROWS, N_COLUMNS, ROW_LETTERS
from threading import Thread
import multiprocessing as multi
from collections import deque
from datetime import datetime

class SensorDisplay():
    running_graphical_display = False
    running_file_display = False

    def __init__(self, sensor_interface: SensorInterface):
        self.sensor_interface = sensor_interface
        self.graphical_data_queue = multi.Queue()

    def start_graphical_display(self):
        # don't start a duplicate thread instance
        if self.running_graphical_display:
            print(f"Graphical display is already running.")
            return
        self.running_graphical_display = True
        multi.Process(target = self.process_run_graphical_display, daemon = True).start()
        Thread(target = self.run_graphical_display, daemon = True).start()

    def start_file_display(self):
        # don't start a duplicate thread instance
        if self.running_file_display:
            print(f"File display is already running. See output in file {Config.voltage_display_filename}")
            return
        self.running_file_display = True
        Thread(target = self.run_files, daemon = True).start()

    def stop_graphical_display(self):
        self.running_graphical_display = False

    def stop_file_display(self):
        self.running_file_display = False

    def process_run_graphical_display(self):
        graphical_display = GraphicalDisplay(self.graphical_data_queue)
        graphical_display.run()

    def run_graphical_display(self):
        # multi.Process(target = graphical_display.run, args = (self.graphical_data_queue,), daemon = True).start()
        while self.running_graphical_display:
            voltages = self.sensor_interface.get_future_voltages_blocking(1)[0]
            print("Graphical display thread")
            self.graphical_data_queue.put(voltages)

    def run_files(self):
        while self.running_file_display:
            voltages = self.sensor_interface.get_future_voltages_blocking(1)[0]
            with open(Config.voltage_display_filename, "w") as display_file:
                display_file.write(ElectrodeNames.electrode_ascii_art(voltages))

class GraphicalDisplay():
    cache_size = 20

    def __init__(self, queue: multi.Queue):
        self.queue = queue
        self.cache = deque([{"ts": datetime.now(), "voltages": [0 for electrode_id in range(N_ELECTRODES)]} for element in range(self.cache_size)])
        self.data_lines = [[None for col in range(N_COLUMNS)] for row in range(N_ROWS)]
        print("initializing GraphicalDisplay object")

    def run(self, electrodes = list(range(N_ELECTRODES))):
        plt.ion()
        self.setup_plots()
        self.start_time = datetime.now()
        self.electrodes = electrodes
        print("running GraphicalDisplay object")
        while True:
            new_data = self.queue.get() # blocking line
            print("GraphicalDisplay received a message!")
            self.__store_voltages_in_cache(new_data)
            self.display_graphs()

    def __store_voltages_in_cache(self, new_voltages):
        if len(self.cache) >= self.cache_size:
            self.cache.popleft()
        # then, always:
        ts = datetime.now()
        self.cache.append({"ts": ts, "voltages": new_voltages})

    def display_graphs(self):
        # plt.clf()
        voltages = [pair["voltages"] for pair in self.cache]
        now = datetime.now()
        ts = [(now - pair["ts"]).total_seconds() for pair in self.cache]

        for row in range(N_ROWS):
            for col in range(N_COLUMNS):
                electrode_id = col + row * N_COLUMNS
                if electrode_id not in self.electrodes:
                    continue
                self.data_lines[row][col].set_ydata([vs[electrode_id] for vs in voltages])
                self.data_lines[row][col].set_xdata(ts)
                self.ax[row][col].relim()
                self.ax[row][col].autoscale()
                # self.fig.canvas.draw()
                # self.ax[row][col].draw()
        self.fig.canvas.draw_idle()
        plt.pause(0.0001)

    def setup_plots(self, ignore_ticks = True):
        self.fig, self.ax = plt.subplots(N_ROWS, N_COLUMNS, figsize = (8, 12), sharex = True, sharey = True)
        self.fig.suptitle("Electrode voltages over time for all 96 electrodes.")
        self.fig.supxlabel("Time (s)")
        self.fig.supylabel("Voltage (V), scaled to the largest voltage in the array")
        for row in range(N_ROWS):
            for col in range(N_COLUMNS):
                if row == N_ROWS - 1:
                    self.ax[row][col].set_xlabel(col + 1)
                if col == 0:
                    self.ax[row][col].set_ylabel(ROW_LETTERS[row] + " " * 5, rotation = 0)

                lines = self.ax[row][col].plot([0] * self.cache_size, [0] * self.cache_size, color = "orange")
                print(row, col)
                print(lines)
                self.data_lines[row][col] = lines[0]
                print(self.data_lines)

                if row == N_ROWS - 1 and col == 0:
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

        # self.fig.canvas.draw_idle()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        # plt.show()

