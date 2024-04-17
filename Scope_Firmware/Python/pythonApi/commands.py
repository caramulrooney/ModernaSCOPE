from argparse import ArgumentParser, ArgumentError
from constants import N_ELECTRODES, ALL_ELECTRODES_KEYWORD, CLI_SPLIT_CHARS
from config import Config
import inspect
from numpy.random import rand
import numpy as np
import time
from typing import Protocol
from sensor_data import SensorData
from electrode_names import ElectrodeNames
from sensor_interface import SensorInterface
from sensor_display import SensorDisplay

class FloatCombiner(Protocol):
    """
    Type hint class for functions which take any number of floats and return a float, for example `mean`.
    """
    def __call__(self, *args: float) -> float: ...

class Commands():
    """
    Argument parser for primary user input.

    The heavy lifting of parsing is done by `argparse.ArgumentParser`. The available commands are initialized in self.make_parsers(). Each command has a callback function which is defined below.
    """
    def __init__(self, sensor_interface: SensorInterface, sensor_display: SensorDisplay):
        self.sensor_data = SensorData()
        self.sensor_interface = sensor_interface
        self.sensor_display = sensor_display

        self.parser = ArgumentParser(prog="", exit_on_error = False, description =
    """This is the pH sensor command-line interface. To run, type one of the positional arguments followed by parameters and flags as necessary. For example, try running `# measure -vn` to measure the voltages at each of the electrodes. Type any command with the -h flag to see the options for that command.""")
        self.subparsers = self.parser.add_subparsers()
        self.make_parsers(exit_on_error = False)

    def execute(self, input):
        try:
            args = self.parser.parse_args(input.split(CLI_SPLIT_CHARS)) # creates a namespace object
        except (ArgumentError, SystemExit) as ex:
            print(ex)
        else:
            args.func(args) # call the function linked by set_defaults(func = func)

    def help(self, args):
        self.parser.print_help()

    def make_parsers(self, exit_on_error = False):
        help = self.subparsers.add_parser("help", prog = "measure", exit_on_error = exit_on_error, description =
    """Measure pH of electrodes within a certain range once the measurements have
    settled. Silently run in the background until measurements are settled, then
    print the results in a tabular format.""")
        help.set_defaults(func = self.help)

        measure_parser = self.subparsers.add_parser("measure", prog = "measure", exit_on_error = exit_on_error, description =
    """Measure pH of electrodes within a certain range once the measurements have
    settled. Silently run in the background until measurements are settled, then
    print the results in a tabular format.""")
        measure_parser.add_argument('-e', '--electrodes', type = str, default = ALL_ELECTRODES_KEYWORD, help = "Electrode range to measure. Default is all 96 electrodes.")
        measure_parser.add_argument('-n', '--num_measurements', type = int, default = 5, help = "Number of measurements to take and average together. Default is 5 measurements.")
        measure_parser.add_argument('-p', '--past_data', action = 'store_true', help = "Read the past n measurements and, if so many measurements exist already, return immediately.")
        measure_parser.add_argument('-s', '--show', action = 'store_true', help = "Show the pH values after they are measured.")
        measure_parser.add_argument('-v', '--voltage', action = 'store_true', help = "Show the voltage values after they are measured.")
        measure_parser.set_defaults(func = self.measure)

        calibrate_parser  =  self.subparsers.add_parser("calibrate", exit_on_error = exit_on_error, description =
    """Calibrate electrodes with a standard pH buffer. Assume a standard buffer
    solution has already been applied to the specified electrodes. Store the current
    voltage for the specified electrodes in memory and use it as a comparison to
    calculate the pH of those electrodes in the future.

    Each calibration for a new pH value will be stored. If a new calibration is
    performed at a pH value that has already been calibrated, the previous
    calibration will be overwritten.""")
        calibrate_parser.add_argument('ph', type = float, help = "The pH of the buffer currently applied to the electrodes being calibrated.")      # option that takes a value
        calibrate_parser.add_argument('-e', '--electrodes', type = str, default = ALL_ELECTRODES_KEYWORD, help = "Electrode range to calibrate. Default is all 96 electrodes.")      # option that takes a value
        calibrate_parser.add_argument('-n', '--num_measurements', type = int, default = 5, help = "Number of measurements to take and average together. Default is 5 measurements.")
        calibrate_parser.add_argument('-p', '--past_data', action = 'store_true', help = "Read the past n measurements and, if so many measurements exist already, return immediately.")
        calibrate_parser.add_argument('-s', '--show', action = 'store_true', help = "Show the pH values after they are measured.")
        calibrate_parser.add_argument('-v', '--voltage', action = 'store_true', help = "Show the voltage values after they are measured.")
        calibrate_parser.set_defaults(func = self.calibrate)

        quit_parser = self.subparsers.add_parser("quit", prog = "quit", exit_on_error = True, description = """Exit the program.""")
        quit_parser.set_defaults(func = quit)

        show_parser = self.subparsers.add_parser("show", prog = "show", exit_on_error = exit_on_error, description =
    """Display information about the selected electrodes, most recent calibrations, and measurements.""")
        show_parser.add_argument('-i', '--ids', action = 'store_true', help = "Show how the A1-H12 notation is mapped onto the electrode index in the code. This can be useful for debugging or for inspecting the CSV files where calibration and measurement data are stored.")
        show_parser.add_argument('-e', '--electrodes', type = str, default = "", help = "Show which electrodes are selected by providing a range in A1-H12 notation.")
        show_parser.add_argument('-cv', '--calibration_voltage', action = 'store_true', help = "Show the voltages on each of the electrodes during the most recent calibration.")
        show_parser.add_argument('-cp', '--calibration_ph', action = 'store_true', help = "Show the pH on each of the electrodes during the most recent calibration.")
        show_parser.add_argument('-p', '--ph', action = 'store_true', help = "Show the pH on each of the electrodes for the most recent measurement.")
        show_parser.add_argument('-v', '--voltage', action = 'store_true', help = "Show the voltages on each of the electrodes during the most recent measurement.")
        show_parser.set_defaults(func = self.show)

        monitor_parser = self.subparsers.add_parser("monitor", prog = "monitor", exit_on_error = exit_on_error, description =
    """Display sensor voltage readings in a continually updated fashion.""")
        monitor_parser.add_argument('-e', '--electrodes', type = str, default = ALL_ELECTRODES_KEYWORD, help = "Only monitor selected electrodes. Default is all 96 electrodes.")
        monitor_parser.add_argument('-f', '--file', action = 'store_true', help = f"Write continually updated voltage readings to the file specified in the JSON configuration file (currently {Config.voltage_display_filename}).")
        monitor_parser.add_argument('-g', '--graph', action = 'store_true', help = "Display continually updated voltage readings in a new window in graphical form.")
        monitor_parser.set_defaults(func = self.monitor)

        load_parser = self.subparsers.add_parser("load", prog = "load", exit_on_error = exit_on_error, description =
    """Re-load the csv file for calibration data from memory.""")
        load_parser.add_argument('-f', '--file', type = str, default = "", help = "Re-load files from the specified JSON configuration file. Default is the configuration file used to initialize the program.")
        load_parser.set_defaults(func = self.reload_files)

        write_parser = self.subparsers.add_parser("write", prog = "write", exit_on_error = exit_on_error, description =
    """Write the currently stored data to a csv file. This should be done automatically after every measurement and calibration, except when a file write fails because the file was open in another program at the same time.""")
        write_parser.add_argument('-f', '--file', type = str, default = "", help = "Write files to the filenames specified in the JSON configuration file. Default is the configuration file used to initialize the program.")
        write_parser.set_defaults(func = self.write_files)

        conversion_info_parser = self.subparsers.add_parser("conversion_info", prog = "conversion_info", exit_on_error = exit_on_error, description =
    f"""Generate conversion information for a given measurement ID to show which calibration data points were used to convert from a voltage to a pH. Store the resulting information as a CSV file in the folder specified in the configuration file (currently {Config.calibration_map_folder}).""")
        conversion_info_parser.add_argument('-m', '--measurement_id', type = str, default = "", help = "Measurement ID for which to generate conversion information.")
        conversion_info_parser.set_defaults(func = self.generate_conversion_info)

    def unpack_namespace(func):
        """
        Decorator for parsing the arguments provided by `argparse.ArgumentParser`. The ArgumentParser passes a single Namespace object to its designated callback function. This decorator unpacks the namespace and passes the parameters as keyword arguments to the callback function. This allows the callback function to have a signature with explicit parameters.

        Even so, it is important that the decorated function's signature exactly matches the arguments of the relevant subparser in commands.py.
        """
        def inner(self, namespace):
            sig = inspect.signature(func)
            kwargs = vars(namespace)
            kwargs["self"] = self
            args_to_pass = [kwargs[arg] for arg in sig.parameters.keys()]
            func(*args_to_pass)
        return inner

    # callback functions

    @unpack_namespace
    def measure(self, electrodes, num_measurements, past_data, show, voltage):
        """
        Callback function for 'measure' command.
        """
        if Config.debug.cli.received_command.measure:
            print(f"Inside of measure, {electrodes=}, {num_measurements=}, {past_data=}, {show=}, {voltage=}")
        electrode_ids_being_measured = ElectrodeNames.parse_electrode_input(electrodes)
        if Config.debug.cli.received_command.measure:
            print(f"Measuring electrodes [{ElectrodeNames.to_battleship_notation(electrode_ids_being_measured)}].")

        if past_data:
            voltages = self.sensor_interface.get_past_voltages_blocking(num_measurements)
        else:
            voltages = self.sensor_interface.get_future_voltages_blocking(num_measurements)
        # voltages = self.get_voltages_blocking(n_measurements = num_measurements, delay_between_measurements = time_interval)
        if Config.debug.cli:
            print(f"{voltages = }")
        voltages = self.combine_readings_element_wise(voltages)

        # set voltage reading of electrodes not being measured to None
        for electrode_id in range(N_ELECTRODES):
            if electrode_id not in electrode_ids_being_measured:
                voltages[electrode_id] = None

        print("Converting measurement to ph...")
        guid = self.sensor_data.add_measurement(voltages)
        print(f"Storing pH measurement with GUID '{guid}'")
        if voltage:
            self.show_most_recent_measurement_voltage()
            return
        if show:
            self.show_most_recent_measurement_ph()

    @unpack_namespace
    def calibrate(self, ph, electrodes, num_measurements, past_data, show, voltage):
        """
        Callback function for 'calibrate' command.
        """
        if Config.debug.cli.received_command.calibrate:
            print(f"Inside of calibrate, {electrodes=}, {ph=}, {num_measurements=}, {past_data=}, {show=}, {voltage=}")
        electrode_ids_being_calibrated = ElectrodeNames.parse_electrode_input(electrodes)
        if Config.debug.cli.received_command.calibrate:
            print(f"Calibrating electrodes [{ElectrodeNames.to_battleship_notation(electrode_ids_being_calibrated)}].")

        if past_data:
            voltages = self.sensor_interface.get_past_voltages_blocking(num_measurements)
        else:
            voltages = self.sensor_interface.get_future_voltages_blocking(num_measurements)
        # voltages = self.get_voltages_blocking(n_measurements = num_measurements, delay_between_measurements = time_interval)

        if Config.debug:
            print(f"{voltages = }")
        voltages = self.combine_readings_element_wise(voltages)

        # set voltage reading of electrodes not being measured to None
        for electrode_id in range(N_ELECTRODES):
            if electrode_id not in electrode_ids_being_calibrated:
                voltages[electrode_id] = None

        guid = self.sensor_data.add_calibration(ph, voltages)
        print(f"Storing calibration entry with GUID '{guid}'")
        if voltage:
            self.show_most_recent_calibration_voltage()
            return
        if show:
            self.show_most_recent_calibration_ph()

    @unpack_namespace
    def reload_files(self, file):
        """
        Callback function for 'load' command.
        """
        flag = False
        if Config.debug:
            print(f"Inside of reload_files")
        if not len(file) == 0:
            flag = Config.set_config(file, mkdirs = True)
        self.sensor_data = SensorData()
        if flag:
            print(f"Loaded data from the files specified by '{file}'.")
        else:
            print("Loaded data from all files into memory.")

    @unpack_namespace
    def write_files(self, file):
        """
        Callback function for 'write' command.
        """
        flag = False
        if Config.debug:
            print(f"Inside of write_files")
        if not len(file) == 0:
            flag = Config.set_config(file, mkdirs = True)
        self.sensor_data.write_data()
        if flag:
            print(f"Updated data in the files specified by '{file}'.")
        else:
            print("Finished updating all files.")

    @unpack_namespace
    def show(self, ids: bool, electrodes: str, calibration_voltage: bool, calibration_ph: bool, voltage: bool, ph: bool):
        """
        Callback function for 'show' command.
        """
        # show_electrodes: bool = electrodes != ""
        if sum([ids, calibration_voltage, calibration_ph, voltage, ph]) > 1:
            print("Please select only one option at a time.")
            return
        if sum([ids, calibration_voltage, calibration_ph, voltage, ph]) < 1:
            ids = True
        if ids:
            ElectrodeNames.ascii_art_electrode_ids()
            return
        if electrodes:
            electrode_ids = ElectrodeNames.parse_electrode_input(electrodes)
            ElectrodeNames.ascii_art_selected(electrode_ids)
            return
        if calibration_voltage:
            self.show_most_recent_calibration_voltage()
        if calibration_ph:
            self.show_most_recent_calibration_ph()
        if voltage:
            self.show_most_recent_measurement_voltage()
        if ph:
            self.show_most_recent_measurement_ph()

    @unpack_namespace
    def monitor(self, electrodes: str, file: bool, graph: bool):
        """
        Callback function for 'monitor' command.
        """
        self.sensor_display.electrodes = ElectrodeNames.parse_electrode_input(electrodes)
        if file:
            print(f"Displaying voltage readings in file {Config.voltage_display_filename}.")
            self.sensor_display.start_file_display()
        else:
            if self.sensor_display.running_file_display:
                print(f"Stopping file display. To start file display, use 'monitor -f'.")
            else:
                print(f"To start file display, use 'monitor -f'.")
            self.sensor_display.stop_file_display()
        if graph:
            print(f"Displaying graphs in new window.")
            self.sensor_display.start_graphical_display()
        else:
            if self.sensor_display.running_graphical_display:
                print(f"Stopping graphical display. To start graphical display, use 'monitor -g'.")
            else:
                print(f"To start graphical display, use 'monitor -g'.")
            self.sensor_display.stop_graphical_display()

    @unpack_namespace
    def generate_conversion_info(self, measurement_id: str):
        """
        Callback function for 'conversion_info' command.
        """
        self.sensor_data.calculate_ph(measurement_id, write_data = True)

    def show_most_recent_calibration_ph(self):
        """
        Helper function for 'show -cp' command.
        """
        calibration_ph = self.sensor_data.get_most_recent_calibration_ph()
        print(f"Showing the pH value being stored for the most recent calibration run. To see the associated voltages, use 'show -c'.")
        calibration_values = self.sensor_data.get_most_recent_calibration()
        print(ElectrodeNames.electrode_ascii_art([f"{calibration_ph:.2f}" if val is not None else None for val in calibration_values]))

    def show_most_recent_calibration_voltage(self):
        """
        Helper function for 'show -cv' command.
        """
        calibration_ph = self.sensor_data.get_most_recent_calibration_ph()
        print(f"Showing voltages from the most recent calibration run in Volts. The pH value was {calibration_ph:.2f}.")
        calibration_values = self.sensor_data.get_most_recent_calibration()
        print(ElectrodeNames.electrode_ascii_art([f"{val:.2f}V" if val is not None else None for val in calibration_values]))

    def show_most_recent_measurement_voltage(self):
        """
        Helper function for 'show -v' command.
        """
        print(f"Showing voltages from the most recent measurement in Volts. To see the calculated pH values, use 'show -p'.")
        voltage_values = self.sensor_data.get_most_recent_measurement()
        print(ElectrodeNames.electrode_ascii_art([f"{val:.2f}V" if val is not None else None for val in voltage_values]))

    def show_most_recent_measurement_ph(self):
        """
        Helper function for 'show -m' command.
        """
        print(f"Showing pH values from the most recent measurement in pH units. To see the associated voltages, use 'show -v'.")
        ph_values = self.sensor_data.get_most_recent_ph()
        print(ElectrodeNames.electrode_ascii_art([f"{val:.2f}" if val is not None else None for val in ph_values]))

    def get_voltages_single(self) -> list[float]: # TODO: get data from sensor via pySerial
        """
        Talk to the sensor and get a single voltage from each of the electrodes.
        """
        return rand(1, N_ELECTRODES)

    # sensor interface functions

    def combine_readings_element_wise(self, readings: list[list[float]], average_func: FloatCombiner = np.mean) -> list[float]:
        # take the average of all the voltage readings over time for each electrode
        # [
        #     [ N_ELECTRODES ]
        #     [ N_ELECTRODES ]
        #     [ N_ELECTRODES ]
        #           ...
        #      n_measurements
        # ]
        readings_array = np.array(readings)
        if Config.debug:
            print(f"{readings_array = }")
        averaged = average_func(readings_array, axis = 0) # column-wise
        if Config.debug:
            print(f"{averaged = }")
        return list(averaged)

    def get_voltages_blocking(self, n_measurements: int = 2, delay_between_measurements: float = 2, average_func: FloatCombiner = np.mean):
        """
        Perform a certain number of consecutive measurements and report the average voltage at each electrode over the duration of the measurement.
        """
        print(f"Reading {n_measurements} measurements from each electrode over {n_measurements * delay_between_measurements} seconds.")
        voltages = np.zeros((n_measurements, N_ELECTRODES)) # 2-D array, n_measurements tall and N_ELECTRODES wide
        for measurement in range(n_measurements):
            voltages[measurement] = self.get_voltages_single() # set the next row of the array
            time.sleep(delay_between_measurements)
            print(f"\tMeasurement #{measurement + 1} of {n_measurements} completed.")

        # take the average of all the voltage readings over time for each electrode
        averaged = []
        for electrode_id in range(N_ELECTRODES):
            voltages_to_combine = np.transpose(voltages)[electrode_id]
            assert voltages_to_combine.size == n_measurements
            averaged.append(average_func(voltages_to_combine))

        return averaged
