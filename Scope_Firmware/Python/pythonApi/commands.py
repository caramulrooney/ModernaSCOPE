from argparse import ArgumentParser
from sensor import Sensor
SPLIT_CHARS = " "

class Commands():
    def __init__(self):
        self.parser = ArgumentParser(prog='ProgramName', description='Device controller command-line interface')
        self.subparsers = self.parser.add_subparsers()
        self.sensor = Sensor()
        self.make_parsers()

    def execute(self, input):
        args = self.parser.parse_args(input.split(SPLIT_CHARS)) # creates a namespace object
        args.func(args) # call the function linked by set_defaults(func = func)

    def make_parsers(self):
        measure_parser = self.subparsers.add_parser("measure", prog = "measure", description =
    """Measure pH of electrodes within a certain range once the measurements have
    settled. Silently run in the background until measurements are settled, then
    print the results in a tabular format.""")
        measure_parser.add_argument('-e', '--electrodes', type = str, default = 'all', help = "Electrode range to measure. Default is all 96 electrodes.")
        measure_parser.add_argument('-n', '--now', action = 'store_true', help = "Do not wait for measurements to settle; report pH measurements now.")
        measure_parser.add_argument('-t', '--time_steps', type = float, help = "Print out the pH values every n seconds until it settles (default: 1 second).")
        measure_parser.add_argument('-m', '--max_time', type = float, help = "Wait at most n seconds for the measurement to settle. Default is all 96 electrodes.")
        measure_parser.add_argument('-v', '--voltage_only', action = 'store_true', help = "Report voltage values, not pH values.")
        measure_parser.set_defaults(func = self.sensor.measure)

        calibrate_parser  =  self.subparsers.add_parser("calibrate", description =
    """Calibrate electrodes with a standard pH buffer. Assume a standard buffer
    solution has already been applied to the specified electrodes. Store the current
    voltage for the specified electrodes in memory and use it as a comparison to
    calculate the pH of those electrodes in the future.

    Each calibration for a new pH value will be stored. If a new calibration is
    performed at a pH value that has already been calibrated, the previous
    calibration will be overwritten.""")
        calibrate_parser.add_argument('-e', '--electrodes', type = str, default = 'all', help = "Electrode range to calibrate. Default is all 96 electrodes.")      # option that takes a value
        calibrate_parser.add_argument('ph', type = float, help = "The pH of the buffer currently applied to the electrodes being calibrated.")      # option that takes a value
        calibrate_parser.set_defaults(func = self.sensor.calibrate)

        show_calibration_parser = self.subparsers.add_parser("show_calibration", prog = "show_calibration", description =
    """Show calibrated voltage values for each calibrated electrode, along with the
    timestamp and temperature of each calibration.""")
        show_calibration_parser.add_argument('-e', '--electrodes', type = str, default = 'all', help = "Electrode range to show calibrated voltages for. Default is all 96 electrodes.")
        show_calibration_parser.add_argument('-p', '--ph', type = float, help = "Each electrode may have multiple calibration voltages for different pH values. Show only the calibration voltage corresponding to a single pH.")
        show_calibration_parser.add_argument('-s', '--sort_by_ph', action = 'store_true', help = "Sort values in ascending order of pH. Default is to sort by timestamp.")
        show_calibration_parser.set_defaults(func = self.sensor.show_calibration)

        clear_calibration_parser = self.subparsers.add_parser("clear_calibration", prog = "clear_calibration", description =
    """Clear the most recent calibration values for the specified electrodes.""")
        clear_calibration_parser.add_argument('-e', '--electrodes', type = str, default = 'all', help = "Electrode range to clear calibrated voltages for. Default is all 96 electrodes.")
        clear_calibration_parser.add_argument('-p', '--ph', type = float, help = "Clear the calibration voltage corresponding to a specified pH.")
        clear_calibration_parser.add_argument('-a', '--all', action = 'store_true', help = "Clear calibration voltages for all pH values for the specified electrodes.")
        clear_calibration_parser.set_defaults(func = self.sensor.clear_calibration)
