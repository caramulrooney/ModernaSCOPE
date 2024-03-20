from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.completion import NestedCompleter, WordCompleter
from prompt_toolkit.history import FileHistory
from constants import init_text_art
from commands import Commands
from lexer import CustomLexer, YesNoLexer
from storage import StorageWritePermissionError, CalibrationError
from config import Config

def handle_storage_write_exception(func):
    def inner_func(self, *args, **kwargs):
        try:
            func(self, *args ,**kwargs)
        except StorageWritePermissionError:
            print("Could not open file for writing, likely because the file was open in a different program. Please use the 'write' command to retry, or press enter now.")
            self.retry_file_write()
    return inner_func

def handle_calibration_exception(func):
    def inner_func(self, *args, **kwargs):
        try:
            func(self, *args ,**kwargs)
        except CalibrationError:
            print("No valid calibration points are available. A pH conversion cannot occur.")
    return inner_func

class SessionRunner():
    command_list = {
        "measure": WordCompleter(['-e', '--electrodes', '-n', '--num_measurements', '-t', '--time_interval', '-s', '--show', '-v', '--voltage', ]),
        "calibrate": WordCompleter(['-e', '--electrodes', '-n', '--num_measurements', '-t', '--time_interval', '-s', '--show', '-v', '--voltage', ]),
        "show": WordCompleter(['-i', '--ids', '-e', '--electrodes', '-c', '--calibration', '-c', '--calibration', '-p', '--ph', ]),
        "load": WordCompleter(['-f', '--file', ]),
        "write": WordCompleter(['-f', '--file', ]),
        "conversion_info": WordCompleter(['-m', '--measurement_id', ]),
        "help": None,
        "quit": None,
    }

    def __init__(self):
        self.commands = Commands()
        self.session = PromptSession(history=FileHistory(Config.prompt_history_filename))
        print(init_text_art)

    @handle_storage_write_exception
    def retry_file_write(self):
        while True:
            text = self.session.prompt("Retry now? [Y/n] ", lexer = PygmentsLexer(YesNoLexer)).strip()
            if text == "Y" or text == "":
                self.commands.sensor.storage.write_data()
                print(f"Wrote data successfully.")
                return
            if text == "n":
                return
            print("Invalid response.")

    @handle_storage_write_exception
    @handle_calibration_exception
    def execute(self, text):
        self.commands.execute(text)

    def run_session(self):
        while True:
            text = self.session.prompt("# ",
                lexer = PygmentsLexer(CustomLexer),
                completer = NestedCompleter.from_nested_dict(self.command_list)
            ).strip()
            self.execute(text)
