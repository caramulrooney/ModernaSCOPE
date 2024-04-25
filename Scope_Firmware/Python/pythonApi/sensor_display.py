from electrode_names import ElectrodeNames
from config import Config
from sensor_interface import SensorInterface
import matplotlib.pyplot as plt
from constants import N_ELECTRODES, N_ROWS, N_COLUMNS, ROW_LETTERS, SECONDS_TO_MILLISECONDS
from threading import Thread
import multiprocessing as multi
from collections import deque
from datetime import datetime
import matplotlib.animation as animation
import pandas as pd
import datetime as dt
from pytz import timezone
from pathlib import Path
from typing import Optional

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

    def make_monitor_data_file(self) -> tuple[pd.DataFrame, Path]:
        """
        Initialize a dataframe to hold measurement data taken during monitoring, including a notes column and one column for the voltage at each electrode during the measurement. Return the empty dataframe.
        """
        columns = [
            "timestamp",
            "seconds_since_start",
            "notes",
        ]
        columns.extend([f"V_electrode_{i}" for i in range(N_ELECTRODES)])
        df = pd.DataFrame(columns = columns).set_index("timestamp")

        timestamp = dt.datetime.now(tz = timezone(Config.timezone))
        monitor_data_file_name = f"monitor_started_at_{timestamp.strftime('%Y_%m_%d_%H_%M_%S_%f')}.csv"
        monitor_data_file_path = Path(Config.monitor_datasets_folder) / monitor_data_file_name

        # save the file as a csv
        try:
            df.to_csv(str(monitor_data_file_path), index = False)
        except PermissionError:
            print("Could not open CSV for wrting because it is open in another program.")
        return df, monitor_data_file_path

    def add_measurement(self, voltages: list[Optional[float]]):
        """
        Insert a new row in self.df_monitor with a list of electrode voltages. Electrode voltages should be passed as a list of 96 numbers, with None for the electrodes that are excluded. Create the necessary metadata for the record, including a unique GUID and timestamp. Automatically write the new row to the CSV file `measurement_data_filename` unless `write_data` is set to `False`. Automatically call self.calculate_ph() to insert a corresponding row in self.ph_result and write that to the CSV file `ph_result_filename` as well.
        """
        assert(len(voltages) == N_ELECTRODES)
        timestamp = dt.datetime.now(tz = timezone(Config.timezone))

        new_row_values = {
            "timestamp": timestamp,
            "seconds_since_start": (timestamp - self.start_time).seconds,
            "notes": "",
        }
        new_row_values.update({f"V_electrode_{i}": [voltages[i]] for i in range(N_ELECTRODES)})

        new_row_df = pd.DataFrame(new_row_values).dropna(axis = "columns").set_index("timestamp")
        self.df_monitor = pd.concat([self.df_monitor if not self.df_monitor.empty else None, new_row_df], axis = "index")

    def get_next_voltages_blocking(self):
        voltages = self.sensor_interface.get_future_voltages_blocking(1)[0]
        self.add_measurement(voltages)
        try:
            self.df_monitor.to_csv(self.df_monitor_filename)
        except PermissionError:
            print(f"{self.name}: Could not write to file '{self.df_monitor_filename}' because it is open in another program. Data will be saved once the other program is closed.")
        return voltages

    def start(self):
        # don't start a duplicate thread instance
        if self.running:
            print(f"{self.name} is already running.")
            return
        self.running = True
        self.df_monitor, self.df_monitor_filename = self.make_monitor_data_file()
        self.start_time = dt.datetime.now(tz = timezone(Config.timezone))

        # start running thread
        Thread(target = self.run, daemon = True).start()

    def stop(self):
        self.running = False

    def run(self):
        # to be implemented by child classes
        pass

class FileDisplayRunner(ThreadedDisplayRunner):
    name = "File display"

    def run(self):
        while self.running:
            voltages = self.get_next_voltages_blocking()
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
        process = multi.Process(target = self.run_process, args = (data_queue, Config.to_tuple_of_filenames()), daemon = True)
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

    def run_process(self, data_queue, config: tuple[str, str]):
        Config.from_tuple_of_filenames(config)
        graphical_display = GraphicalDisplay(data_queue, electrodes = self.electrodes)
        graphical_display.run()

    def run_update_thread(self, data_queue):
        while self.running:
            voltages = self.get_next_voltages_blocking()
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
        ani = animation.FuncAnimation(self.fig, self.display_graphs, repeat = True, interval = 1 * SECONDS_TO_MILLISECONDS / 2, save_count = 10) # TODO: Delete this line and use Config.measurement_interval instead
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
