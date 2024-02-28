from prompt_toolkit import PromptSession
import argparse
import click

session = PromptSession()

parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')

# parser.add_argument('filename')           # positional argument
parser.add_argument('-c', '--count')      # option that takes a value
parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag

a = parser.parse_args(["-c", "5"])
# print(a)

class Commands():
    commands = {}
    functions = {}
    def __init__(self):
        self.measure()
        self.evaluate("measure -c 8 -v")

    def evaluate(self, input):
        args = input.split(" ")
        name = args[0]
        if name in self.commands.keys():
            parsed = self.commands[name].parse_args(args[1:])
            return self.functions[name](**vars(parsed))

    def command(name):
        def decorator(func):
            def inner(self):
                # print(f"command. {name=}")
                return func(self, name)
            return inner
        return decorator

    def parser(*args, **kwargs):
        def decorator(func):
            def inner(self, name):
                self.commands[name] = argparse.ArgumentParser(*args, **kwargs)
                # print(f"parser.")
                self.functions[name] = func
            return inner
        return decorator

    def arg(*args, **kwargs):
        def decorator(func):
            def inner(self, name):
                func_result = func(self, name)
                # print(f"arg. {name=}")
                self.commands[name].add_argument(*args, **kwargs)
                return func_result
            return inner
        return decorator


    @command('measure')
    @arg('-c', '--count')
    @arg('-v', '--verbose', action='store_true')
    @parser(prog='ProgramName', description='What the program does', epilog='Text at the bottom of help')
    def measure(count, verbose):
        print(f"Inside of measure, {count=}, {verbose=}")

commands = Commands()
# text = session.prompt("What would you like to say?\n")
# args = commands.measure.parse_args(text.split(" "))

# print(commands.measure.print_help())
