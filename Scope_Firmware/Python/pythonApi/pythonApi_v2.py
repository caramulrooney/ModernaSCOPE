from prompt_toolkit import PromptSession
from argparse import ArgumentParser
import inspect
SPLIT_CHARS = " "

session = PromptSession()
parser = ArgumentParser(prog='ProgramName', description='Device controller command-line interface')
subparsers = parser.add_subparsers()



def unpack_namespace(func):
    def inner(**kwargs):
        argspec = inspect.getargspec(func)

        func()


def execute(input):
    args = parser.parse_args(input.split(SPLIT_CHARS))
    print(args)
    args.func(**vars(args))

def measure(electrode, verbose, **kwargs):
    print(f"Inside of measure, {electrode=}, {verbose=}")

def calibrate(**kwargs):
    print("Hellllwoooo!")

def make_parsers():
    measure_parser = subparsers.add_parser("measure")
    measure_parser.add_argument('-e', '--electrode', '--electrodes')      # option that takes a value
    measure_parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag
    measure_parser.set_defaults(func = measure)

    calibrate_parser = subparsers.add_parser("calibrate")
    calibrate_parser.add_argument('-e', '--electrode', '--electrodes')      # option that takes a value
    calibrate_parser.add_argument('-p', '--pH')      # option that takes a value
    calibrate_parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag
    calibrate_parser.set_defaults(func = calibrate)

make_parsers()
text = session.prompt("What would you like to say?\n")
execute(text)

# print(commands.measure.print_help())
