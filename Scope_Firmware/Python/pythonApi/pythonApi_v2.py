from prompt_toolkit import PromptSession
from argparse import ArgumentParser
import inspect
SPLIT_CHARS = " "

session = PromptSession()
parser = ArgumentParser(prog='ProgramName', description='Device controller command-line interface')
subparsers = parser.add_subparsers()

def unpack_namespace(func):
    def inner(namespace):
        sig = inspect.signature(func)
        kwargs = vars(namespace)
        args_to_pass = [kwargs[arg] for arg in sig.parameters.keys()]
        func(*args_to_pass)
    return inner


def execute(input):
    args = parser.parse_args(input.split(SPLIT_CHARS)) # creates a namespace object
    args.func(args) # call the function linked by set_defaults(func = func)

@unpack_namespace
def measure(electrodes, now, time_steps, max_time, voltage_only):
    print(f"Inside of measure, {electrodes=}, {now=}, {time_steps=}, {max_time=}, {voltage_only=}")

@unpack_namespace
def calibrate(electrodes, pH):
    print(f"Inside of calibrate, {electrodes=}, {pH=}")

def make_parsers():
    measure_parser = subparsers.add_parser("measure", prog = "measure", description =
"""Measure pH of electrodes within a certain range once the measurements have
settled. Silently run in the background until measurements are settled, then
print the results in a tabular format.""")
    measure_parser.add_argument('-e', '--electrodes', type = str, default = 'all', help = "Electrode range to measure. Default is all 96 electrodes.")
    measure_parser.add_argument('-n', '--now', action = 'store_true', help = "Do not wait for measurements to settle; report pH measurements now.")
    measure_parser.add_argument('-t', '--time_steps', type = float, help = "Print out the pH values every n seconds until it settles (default: 1 second).")
    measure_parser.add_argument('-m', '--max_time', type = float, help = "Wait at most n seconds for the measurement to settle. Default is all 96 electrodes.")
    measure_parser.add_argument('-v', '--voltage_only', action = 'store_true', help = "Report voltage values, not pH values.")
    measure_parser.set_defaults(func = measure)

    calibrate_parser  =  subparsers.add_parser("calibrate", description =
"""Calibrate electrodes with a standard pH buffer. Assume a standard buffer
solution has already been applied to the specified electrodes. Store the current
voltage for the specified electrodes in memory and use it as a comparison to
calculate the pH of those electrodes in the future.

Each calibration for a new pH value will be stored. If a new calibration is
performed at a pH value that has already been calibrated, the previous
calibration will be overwritten.""")
    calibrate_parser.add_argument('-e', '--electrodes', type = str, default = 'all', help = "Electrode range to calibrate. Default is all 96 electrodes.")      # option that takes a value
    calibrate_parser.add_argument('pH', type = float, help = "The pH of the buffer currently applied to the electrodes being calibrated.")      # option that takes a value
    calibrate_parser.set_defaults(func = calibrate)

make_parsers()
# text = session.prompt("What would you like to say?\n")
# text = "measure --electrod 9 --now --max_time 120"
text = "calibrate -h"
execute(text)

