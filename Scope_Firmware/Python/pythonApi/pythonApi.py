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
print(a)

class Commands():
    commands = {}
    def __init__(self):
        self.measure("1", "2")
        print(self.commands["measure"])
        print(self.commands["measure"].parse_args(["-c", "5"]))
        pass

    def command(name):
        def decorator(func):
            def inner(self, *inner_args, **inner_kwargs):
                print(f"command. {name=}")
                return_val = func(self, name, 5, 4)
                print(self.commands["measure"])
                return return_val
                # return func(self, name, *inner_args, **inner_kwargs)
            return inner
        return decorator

    def parser(*args, **kwargs):
        def decorator(func):
            def inner(self, name, *inner_args, **inner_kwargs):
                func_result = func(self, *inner_args, **inner_kwargs)
                self.commands[name] = argparse.ArgumentParser(*args, **kwargs)
                print(f"parser. {inner_args=}, {inner_kwargs=}")
                return func_result
            return inner
        return decorator

    def arg(*args, **kwargs):
        def decorator(func):
            def inner(self, name, *inner_args, **inner_kwargs):
                func_result = func(self, name, *inner_args, **inner_kwargs)
                print(f"arg. {name=}, {inner_args=}, {inner_kwargs=}")
                self.commands[name].add_argument(*args, **kwargs)
                return func_result
            return inner
        return decorator


    @command('measure')
    @arg('-c', '--count')
    @arg('-v', '--verbose', action='store_true')
    @parser(prog='ProgramName', description='What the program does', epilog='Text at the bottom of help')
    def measure(self, c, v):
        print(c, v)

commands = Commands()
# text = session.prompt("What would you like to say?\n")
# args = commands.measure.parse_args(text.split(" "))

# print(commands.measure.print_help())
