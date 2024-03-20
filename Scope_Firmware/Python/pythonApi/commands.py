from argparse import ArgumentParser, ArgumentError
from sensor import Sensor
from config import Config
SPLIT_CHARS = " "

class Commands():
    def __init__(self):
        self.sensor = Sensor()

        self.parser = ArgumentParser(prog="", exit_on_error = False, description =
    """This is the pH sensor command-line interface. To run, type one of the positional arguments followed by parameters and flags as necessary. For example, try running `# measure -vn` to measure the voltages at each of the electrodes. Type any command with the -h flag to see the options for that command.""")
        self.subparsers = self.parser.add_subparsers()
        self.make_parsers(exit_on_error = False)

    def execute(self, input):
        try:
            args = self.parser.parse_args(input.split(SPLIT_CHARS)) # creates a namespace object
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
        measure_parser.add_argument('-e', '--electrodes', type = str, default = 'all', help = "Electrode range to measure. Default is all 96 electrodes.")
        measure_parser.add_argument('-n', '--num_measurements', type = int, default = 5, help = "Number of measurements to take and average together. Default is 5 measurements.")
        measure_parser.add_argument('-t', '--time_interval', type = float, default = 2, help = "Time interval between measurements (minimum: 2 seconds, default: 2 seconds).")
        measure_parser.add_argument('-s', '--show', action = 'store_true', help = "Show the pH values after they are measured.")
        measure_parser.add_argument('-v', '--voltage', action = 'store_true', help = "Show the voltage values after they are measured.")
        measure_parser.set_defaults(func = self.sensor.measure)

        calibrate_parser  =  self.subparsers.add_parser("calibrate", exit_on_error = exit_on_error, description =
    """Calibrate electrodes with a standard pH buffer. Assume a standard buffer
    solution has already been applied to the specified electrodes. Store the current
    voltage for the specified electrodes in memory and use it as a comparison to
    calculate the pH of those electrodes in the future.

    Each calibration for a new pH value will be stored. If a new calibration is
    performed at a pH value that has already been calibrated, the previous
    calibration will be overwritten.""")
        calibrate_parser.add_argument('ph', type = float, help = "The pH of the buffer currently applied to the electrodes being calibrated.")      # option that takes a value
        calibrate_parser.add_argument('-e', '--electrodes', type = str, default = 'all', help = "Electrode range to calibrate. Default is all 96 electrodes.")      # option that takes a value
        calibrate_parser.add_argument('-n', '--num_measurements', type = int, default = 5, help = "Number of measurements to take and average together. Default is 5 measurements.")
        calibrate_parser.add_argument('-t', '--time_interval', type = float, default = 2, help = "Time interval between measurements (minimum: 2 seconds, default: 2 seconds).")
        calibrate_parser.add_argument('-s', '--show', action = 'store_true', help = "Show the pH values after they are measured.")
        calibrate_parser.add_argument('-v', '--voltage', action = 'store_true', help = "Show the voltage values after they are measured.")
        calibrate_parser.set_defaults(func = self.sensor.calibrate)

        quit_parser = self.subparsers.add_parser("quit", prog = "quit", exit_on_error = True, description = """Exit the program.""")
        quit_parser.set_defaults(func = quit)

        show_parser = self.subparsers.add_parser("show", prog = "show", exit_on_error = exit_on_error, description =
    """Display information about the selected electrodes, most recent calibrations, and measurements.""")
        show_parser.add_argument('-i', '--ids', action = 'store_true', help = "Show how the A1-H12 notation is mapped onto the electrode index in the code. This can be useful for debugging or for inspecting the CSV files where calibration and measurement data are stored.")
        show_parser.add_argument('-e', '--electrodes', type = str, default = "", help = "Show which electrodes are selected by providing a range in A1-H12 notation.")
        show_parser.add_argument('-c', '--calibration', action = 'store_true', help = "Show the voltages on each of the electrodes during the most recent calibration.")
        show_parser.add_argument('-p', '--ph', action = 'store_true', help = "Show the pH on each of the electrodes for the most recent measurement.")
        show_parser.add_argument('-v', '--voltage', action = 'store_true', help = "Show the voltages on each of the electrodes during the most recent measurement.")
        show_parser.set_defaults(func = self.sensor.show)

        load_parser = self.subparsers.add_parser("load", prog = "load", exit_on_error = exit_on_error, description =
    """Re-load the csv file for calibration data from memory.""")
        load_parser.add_argument('-f', '--file', type = str, default = "", help = "Re-load files from the specified JSON configuration file. Default is the configuration file used to initialize the program.")
        load_parser.set_defaults(func = self.sensor.reload_files)

        write_parser = self.subparsers.add_parser("write", prog = "write", exit_on_error = exit_on_error, description =
    """Write the currently stored data to a csv file. This should be done automatically after every measurement and calibration, except when a file write fails because the file was open in another program at the same time.""")
        write_parser.add_argument('-f', '--file', type = str, default = "", help = "Write files to the filenames specified in the JSON configuration file. Default is the configuration file used to initialize the program.")
        write_parser.set_defaults(func = self.sensor.write_files)

        conversion_info_parser = self.subparsers.add_parser("conversion_info", prog = "conversion_info", exit_on_error = exit_on_error, description =
    f"""Generate conversion information for a given measurement ID to show which calibration data points were used to convert from a voltage to a pH. Store the resulting information as a CSV file in the folder specified in the configuration file (currently {Config.calibration_map_folder}).""")
        conversion_info_parser.add_argument('-m', '--measurement_id', type = str, default = "", help = "Measurement ID for which to generate conversion information.")
        conversion_info_parser.set_defaults(func = self.sensor.generate_conversion_info)
