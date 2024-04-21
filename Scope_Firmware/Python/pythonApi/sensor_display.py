from electrode_names import ElectrodeNames
from config import Config
from sensor_interface import SensorInterface
import matplotlib.pyplot as plt
from constants import N_ELECTRODES, N_ROWS, N_COLUMNS, ROW_LETTERS, SECONDS_TO_MILLISECONDS
from threading import Thread
import multiprocessing as multi
from collections import deque
from datetime import datetime
from tkinter import Tk, Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import matplotlib.animation as animation

class SensorDisplay():
    running_graphical_display = False
    running_file_display = False

    def __init__(self, sensor_interface: SensorInterface):
        self.sensor_interface = sensor_interface
        self.graphical_data_queue = multi.Queue()
        self.graphical_display_runner = GraphicalDisplayRunner(sensor_interface)
        self.file_display_runner = FileDisplayRunner(sensor_interface)

    def start_graphical_display(self):
        self.graphical_display_runner.start()

    def start_file_display(self):
        self.file_display_runner.start()

    def stop_graphical_display(self):
        self.graphical_display_runner.stop()

    def stop_file_display(self):
        self.file_display_runner.stop()

class ThreadedDisplayRunner():
    def __init__(self, sensor_interface: SensorInterface):
        self.sensor_interface = sensor_interface
        self.running = False
        self.electrodes = list(range(N_ELECTRODES))
        self.name = "Generic threaded display class"

    def start(self):
        # don't start a duplicate thread instance
        if self.running:
            print(f"{self.name} is already running.")
            return
        self.running = True
        Thread(target = self.run, daemon = True).start()
        pass

    def stop(self):
        self.running = False

    def run(self):
        # to be implemented by child classes
        pass

class FileDisplayRunner(ThreadedDisplayRunner):
    name = "File display"

    def run(self):
        while self.running:
            voltages = self.sensor_interface.get_future_voltages_blocking(1)[0]
            with open(Config.voltage_display_filename, "w") as display_file:
                voltages_to_display = []
                for electrode_id in range(N_ELECTRODES):
                    if electrode_id in self.electrodes:
                        voltages_to_display.append(voltages[electrode_id])
                    else:
                        voltages_to_display.append(None)
                display_file.write(ElectrodeNames.electrode_ascii_art(voltages_to_display))

class GraphicalDisplayRunner(ThreadedDisplayRunner):
    name = "Graphical display"

    def run(self):
        # start new process to display matplotlib animation
        data_queue = multi.Queue()
        process = multi.Process(target = self.run_process, args = (data_queue, Config()), daemon = True)
        process.start()

        # start new thread with data pipeline
        update_thread = Thread(target = self.run_update_thread, args = (data_queue, ), daemon = True)
        update_thread.start()

        # wait until the process exits, usually due to someone closing the display window
        process.join()
        if Config.debug.threading.monitor.graphical.join.process:
            print("Joined graphical display process.")

        # set self.running to False to exit the while self.running loop inside the update thread
        self.running = False

        # wait until the update thread has finished running
        update_thread.join()
        if Config.debug.threading.monitor.graphical.join.thread:
            print("Joined graphical display thread.")

    def run_process(self, data_queue, config: Config):
        Config.initialize_from_object(config)
        graphical_display = GraphicalDisplay(data_queue, electrodes = self.electrodes)
        graphical_display.run()

    def run_update_thread(self, data_queue):
        while self.running:
            voltages = self.sensor_interface.get_future_voltages_blocking(1)[0]
            if Config.debug.threading.inside_thread.monitor.graphical.update:
                print("Graphical display thread")
            data_queue.put(voltages)

class GraphicalDisplay():
    cache_size = 20

    def __init__(self, queue: multi.Queue, electrodes = list(range(N_ELECTRODES))):
        self.queue = queue
        self.electrodes = electrodes
        self.cache = deque([{"ts": datetime.now(), "voltages": [0 for electrode_id in range(N_ELECTRODES)]} for element in range(self.cache_size)])
        self.data_lines = [[None for col in range(N_COLUMNS)] for row in range(N_ROWS)]
        if Config.debug.threading.initialize.monitor.graphical.object_created:
            print("initializing GraphicalDisplay object")

    def run_update_deque(self):
        while True:
            new_data = self.queue.get() # blocking line
            if Config.debug.threading.inside_thread.monitor.graphical.received_message:
                print("GraphicalDisplay received a message!")
            self.__store_voltages_in_cache(new_data)

    def run(self):
        self.setup_plots()
        self.fig.canvas.mpl_connect('close_event', exit)
        self.start_time = datetime.now()
        Thread(target = self.run_update_deque, daemon = True).start()
        ani = animation.FuncAnimation(self.fig, self.display_graphs, repeat = True, interval = 1 * SECONDS_TO_MILLISECONDS / 2) # TODO: Delete this line and use Config.measurement_interval instead
        # ani = animation.FuncAnimation(self.fig, self.display_graphs, repeat = True, interval = Config.measurement_interval * SECONDS_TO_MILLISECONDS / 2)
        plt.show()

    def __store_voltages_in_cache(self, new_voltages):
        if len(self.cache) >= self.cache_size:
            self.cache.popleft()
        # then, always:
        ts = datetime.now()
        self.cache.append({"ts": ts, "voltages": new_voltages})

    def display_graphs(self, frame):
        voltages = [pair["voltages"] for pair in self.cache]
        now = datetime.now()
        ts = [(pair["ts"] - now).total_seconds() for pair in self.cache]

        for row in range(N_ROWS):
            for col in range(N_COLUMNS):
                electrode_id = col + row * N_COLUMNS
                if electrode_id not in self.electrodes:
                    continue
                self.data_lines[row][col].set_ydata([vs[electrode_id] for vs in voltages])
                self.data_lines[row][col].set_xdata(ts)
                self.ax[row][col].relim()
                self.ax[row][col].autoscale()

    def setup_plots(self, ignore_ticks = True):
        # matplotlib.use('Qt5agg')
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
                self.data_lines[row][col] = lines[0]

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
